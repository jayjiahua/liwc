# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/3/29 0029 Jay : Init

from . import main
from .forms import *
from flask import render_template, Response, stream_with_context, redirect, \
    flash, request, url_for, abort, jsonify, make_response
from werkzeug.utils import secure_filename
from flask.ext.login import login_required, logout_user, login_user
from flask.helpers import send_file
from sqlalchemy import or_
from ..decorators import admin_required
from app import db
from ..models import *
from flask.ext.login import current_user
from .util import push_text_task, push_matrix_task, merge_columns, merge_rows

import os
import uuid
import csv


_basedir = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/").split("/")
basedir = "/".join(_basedir[:-2])


txt_dir = '/app/uploads/txt/'
dict_dir = '/app/uploads/dict/'
matrix_dir = '/app/uploads/matrix/'
library_dir = '/app/uploads/library/'

word_count_dir = "/".join(_basedir[:-2]) + '/nlpir/Export/wordCount.csv'
single_count_dir = "/".join(_basedir[:-2]) + '/nlpir/Export/splitwordCount.csv'



@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main.route('/analyse', methods=['GET', 'POST'])
@login_required
def analyse():
    form = FileForm()

    if form.validate_on_submit():
        files = request.files.getlist("file")

        for file in files:
            filename = file.filename

            real_filename = uuid.uuid4().hex + '.csv'

            file_path = txt_dir + real_filename
            abs_file_path = basedir + file_path
            file.save(abs_file_path)

            library = Library.query.get(form.library.data)
            loc_worddict = basedir + library.word_dict
            loc_classdict = basedir + library.class_dict

            dict_id = form.user_dict.data
            user_dict = None
            if dict_id and dict_id != -1:
                user_dict = Dict.query.get(form.user_dict.data)
                loc_userdict = basedir + user_dict.filename
            else:
                loc_userdict = None


            prefix = ''
            if form.keyword.data:
                prefix = u"(keyword: {0})".format(form.keyword.data)

            task = TextTask(name=prefix+filename,
                        keyword=form.keyword.data,
                        filename=file_path,
                        user_id=current_user.id,
                        library_name=library.name,
                        user_dict_name=user_dict.name if user_dict else None)

            db.session.add(task)
            db.session.commit()

            push_text_task(loc_userdict, loc_worddict, loc_classdict, abs_file_path, form.keyword.data, task.id, form.col_text.data, filename)

        flash(u"您的任务已经加入到队列，可能需要较长的时间，请耐心等候。")
        # ret_filename = msg.split(".")[0] + "(import)_" + form.keyword.data.replace("+", "_").replace("|", "_") + ".csv"
        return redirect(url_for('main.tasks'))
        # return send_file(ret_filename, attachment_filename="result-"+form.keyword.data+"-"+ filename, as_attachment=True)
    return render_template('analyse.html', form=form)

@main.route('/dict', methods=['GET', 'POST'])
@login_required
def import_dict():
    form = ImportForm()
    if form.validate_on_submit():
        real_filename = uuid.uuid4().hex + '.csv'

        file_path = dict_dir + real_filename

        form.file.data.save(basedir + file_path)

        dict = Dict(name=form.name.data,
                    description=form.description.data,
                    filename=file_path,
                    user_id=current_user.id)

        db.session.add(dict)
        db.session.commit()
        flash(u"添加方案成功")
        return redirect(url_for('main.import_dict'))
    official_dict = [dict for dict in Dict.query.all() if dict.user.is_administrator()]
    return render_template('import_dict.html', form=form, official_dict=official_dict)

@main.route('/dict', methods=['DELETE'])
@login_required
def delete_dict():
    dicts = request.form.get("dicts")
    count = 0
    for dict_id in dicts.split(","):
        dict = Dict.query.get(dict_id)
        if dict and dict.user_id == current_user.id:
            db.session.delete(dict)
            count += 1
        db.session.commit()
    flash(u'成功删除{0}个方案'.format(count))
    return "success"


@main.route('/network', methods=['GET', 'POST'])
@login_required
def network():
    form = NetworkForm()
    if form.validate_on_submit():
        files = request.files.getlist("file")

        for file in files:
            filename = file.filename

            real_filename = uuid.uuid4().hex + '.csv'

            file_path = matrix_dir + real_filename
            abs_file_path = basedir + file_path
            file.save(abs_file_path)

            task = MatrixTask(name=filename,
                              filename=file_path,
                              user_id=current_user.id)
            db.session.add(task)
            db.session.commit()

            push_matrix_task(abs_file_path, form.id_column.data, form.text_column.data, task.id)

        flash(u"您的任务已经加入到队列，可能需要较长的时间，请耐心等候。")
        # ret_filename = msg.split(".")[0] + "(import)_" + form.keyword.data.replace("+", "_").replace("|", "_") + ".csv"
        return redirect(url_for('main.tasks') + "#matrix_tasks")
    return render_template('network.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            if user.is_expired():
                flash('该用户已经过期，登录失败，请联系管理员进行续期')
            else:
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash(u'用户名或密码输入错误')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def user_manage():
    register_form = RegistrationForm()
    edit_form = EditForm()
    if register_form.validate_on_submit():
        user = User()
        user.username = register_form.username.data
        user.password = register_form.password.data
        user.email = register_form.email.data
        user.fullname = register_form.fullname.data
        if register_form.forever.data:
            user.expire_at = None
        else:
            user.expire_at = register_form.expired_time.data
        user.role_id = register_form.role_id.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.user_manage'))
    users = User.query.all()
    return render_template('user_management.html', users=users, register_form=register_form, edit_form=edit_form)

@main.route('/users', methods=['DELETE'])
@login_required
@admin_required
def user_delete():
    users = request.form.get("users")
    count = 0
    for user_id in users.split(","):
        user = User.query.get(user_id)
        if user and not user.is_administrator():
            db.session.delete(user)
            count += 1
        db.session.commit()
    flash(u'成功删除{0}个用户'.format(count))
    return "success"

@main.route('/user/<int:id>', methods=['POST'])
@login_required
@admin_required
def user_edit(id):
    user = User.query.get(id)
    if not user:
        abort(404)
    if user.is_administrator():
        abort(403)
    form = EditForm()
    if form.validate_on_submit():
        if form.edit_forever.data:
            user.expire_at = None
        else:
            user.expire_at = form.edit_expired_time.data
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('main.user_manage'))

@main.route('/tasks', methods=['GET'])
@login_required
def tasks():
    running_tasks = current_user.text_tasks.filter(or_(TextTask.status == TaskStatus.RUNNING,
                                                  TextTask.status == TaskStatus.WAITING)
                                              ).order_by(TextTask.create_time).all()
    finished_tasks = current_user.text_tasks.filter(or_(TextTask.status == TaskStatus.SUCCESS,
                                                  TextTask.status == TaskStatus.FAIL)
                                               ).order_by(TextTask.create_time.desc()).all()
    running_matrix_tasks = current_user.matrix_tasks.filter(or_(MatrixTask.status == TaskStatus.RUNNING,
                                                  MatrixTask.status == TaskStatus.WAITING)
                                              ).order_by(MatrixTask.create_time).all()
    finished_matrix_tasks = current_user.matrix_tasks.filter(or_(MatrixTask.status == TaskStatus.SUCCESS,
                                                  MatrixTask.status == TaskStatus.FAIL)
                                               ).order_by(MatrixTask.create_time.desc()).all()
    return render_template('task_list.html',
                           running_tasks=running_tasks,
                           finished_tasks=finished_tasks,
                           running_matrix_tasks=running_matrix_tasks,
                           finished_matrix_tasks=finished_matrix_tasks)


@main.route('/tasks/delete', methods=['POST'])
@login_required
def delete_fail_tasks():
    current_user.text_tasks.filter(TextTask.status == TaskStatus.FAIL).delete()
    current_user.matrix_tasks.filter(MatrixTask.status == TaskStatus.FAIL).delete()
    db.session.commit()
    flash(u"清理失败任务成功")
    return redirect(url_for("main.tasks"))

def get_keyword(keyword):
    return keyword.replace("+", "_").replace("|", "_")

@main.route('/download/analyse/<string:file_type>', methods=['GET'])
@login_required
def download_result(file_type):
    filename = request.args.get("file")
    task = TextTask.query.filter_by(filename=filename).first()
    if not task:
        abort(404)
    if task.user_id != current_user.id:
        abort(403)
    real_filename = basedir
    display_filename = task.name
    if file_type == "origin":
        real_filename += filename
        display_filename = u"(原文件)" + display_filename
    elif file_type == "result":
        real_filename += filename[:filename.rfind(".")] + "_target(import)_" + get_keyword(task.keyword) + ".csv"
        display_filename = u"(分析结果)" + display_filename
    elif file_type == "statistics":
        real_filename += filename[:filename.rfind(".")] + "_target(total).csv"
        display_filename = u"(分析统计)" + display_filename
    elif file_type == "wordCount":
        real_filename += filename[:filename.rfind(".")] + "(wordCount).csv"
        display_filename = u"(词频统计)" + display_filename
    elif file_type == "singleCount":
        real_filename += filename[:filename.rfind(".")] + "(singleCount).csv"
        display_filename = u"(字频统计)" + display_filename
    else:
        abort(404)
    return send_file(real_filename, attachment_filename=display_filename.encode("utf-8"), as_attachment=True)

@main.route('/download/matrix/<string:file_type>', methods=['GET'])
@login_required
def download_matrix_result(file_type):
    filename = request.args.get("file")
    task = MatrixTask.query.filter_by(filename=filename).first()
    if not task:
        abort(404)
    if task.user_id != current_user.id:
        abort(403)
    real_filename = basedir

    display_filename = task.name
    if file_type == "origin":
        real_filename += filename
        display_filename = u"(原文件)" + display_filename
    elif file_type == "map":
        real_filename += filename[:filename.rfind("/")] + "/map_" + filename[filename.rfind("/")+1:]
        display_filename = u"(邻接表)" + display_filename
    elif file_type == "matrix":
        real_filename += filename[:filename.rfind("/")] + "/matrix_map_" + filename[filename.rfind("/")+1:]
        display_filename = u"(邻接矩阵)" + display_filename
    else:
        abort(404)
    return send_file(real_filename, attachment_filename=display_filename.encode("utf-8"), as_attachment=True)

@main.route('/download/dict', methods=['GET'])
@login_required
def download_dict():
    filename = request.args.get("file")
    dict = Dict.query.filter_by(filename=filename).first()
    if not dict:
        abort(404)
    if dict.user_id != current_user.id:
        abort(403)
    real_filename = basedir + dict.filename
    display_filename = dict.name + ".txt"
    return send_file(real_filename, attachment_filename=display_filename.encode("utf-8"), as_attachment=True)

@main.route('/download/library', methods=['GET'])
@login_required
def download_library():
    filename = request.args.get("file")
    library = Library.query.filter(or_(Library.class_dict == filename, Library.word_dict == filename)).first()
    if not library:
        abort(404)
    if library.user_id != current_user.id:
        abort(403)
    real_filename = basedir + filename
    if filename == library.word_dict:
        display_filename = u"【词语-类别】" + library.name + '.csv'
    else:
        display_filename = u"【类别-解释】" + library.name + '.csv'
    return send_file(real_filename, attachment_filename=display_filename.encode("utf-8"), as_attachment=True)


@main.route('/library', methods=['GET', 'POST'])
@login_required
def import_library():
    form = LibraryForm()
    if form.validate_on_submit():
        real_word_filename = uuid.uuid4().hex + '.csv'
        real_class_filename = uuid.uuid4().hex + '.csv'

        word_file_path = library_dir + real_word_filename
        class_file_path = library_dir + real_class_filename

        form.word_dict.data.save(basedir + word_file_path)
        form.class_dict.data.save(basedir + class_file_path)

        library = Library(name=form.name.data,
                    description=form.description.data,
                    word_dict=word_file_path,
                    class_dict=class_file_path,
                    user_id=current_user.id)

        db.session.add(library)
        db.session.commit()
        flash(u"上传词库成功")
        return redirect(url_for('main.import_library'))
    official_libraries = [library for library in Library.query.all() if library.user.is_administrator()]
    return render_template('library.html', form=form, official_libraries=official_libraries)

@main.route('/library', methods=['DELETE'])
@login_required
def delete_library():
    librarys = request.form.get("libs")
    count = 0
    for library_id in librarys.split(","):
        library = Library.query.get(library_id)
        if library and library.user_id == current_user.id:
            db.session.delete(library)
            count += 1
        db.session.commit()
    flash(u'成功删除{0}个词库'.format(count))
    return "success"


@main.route('/download/samples/<string:filename>', methods=['GET'])
@login_required
def download_samples(filename):
    return send_file(basedir + "/app/static/samples/"+filename, attachment_filename=filename.encode("utf-8"), as_attachment=True)

@main.route('/ranking', methods=['GET'])
def ranking():
    limit = request.args.get("limit", 20, type=int)
    type = request.args.get("type")

    freader = None
    if type == "word":
        freader = csv.reader(open(word_count_dir,'r'),dialect='excel')
    elif type == "single":
        freader = csv.reader(open(single_count_dir,'r'),dialect='excel')
    else:
        abort(404)
    result = []
    for line in freader:
        try:
            if (len(line[0]) >= 4 or type == "single") and int(line[-1]) > 0:
                result.append({"word" :line[0].decode("gbk"), "times": int(line[-1])})
        except:
            pass
    result.sort(key=lambda d: d["times"], reverse=True)
    return jsonify(dict(data=result[:limit]))


@main.route('/user/password', methods=['GET', 'POST'])
@login_required
def edit_password():
    form = EditPasswordForm()
    if form.validate_on_submit():

        current_user.password = form.new_password.data
        db.session.add(current_user)
        db.session.commit()
        flash(u"密码修改成功")
        return redirect(url_for("main.edit_password"))
    return render_template("edit_user.html", title=u"修改密码", form=form)

@main.route('/user/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.fullname = form.fullname.data
        db.session.add(current_user)
        db.session.commit()
        flash(u"资料修改成功")
        return redirect(url_for("main.edit_profile"))
    form.email.data = current_user.email
    form.fullname.data = current_user.fullname
    return render_template("edit_user.html", title=u"修改资料", form=form)

@main.route('/download/table/word', methods=['GET'])
@login_required
def download_word_table():
    return send_file(word_count_dir, attachment_filename="词频分析.csv", as_attachment=True)

@main.route('/download/table/single', methods=['GET'])
@login_required
def download_single_table():
    return send_file(single_count_dir, attachment_filename="字频分析.csv", as_attachment=True)

@main.route('/merge_text_download', methods=['GET'])
@login_required
def merge_text_download():
    task_ids = request.args.get("task_ids")
    task_ids = task_ids.split(",")
    file_type = request.args.get("file_type")

    file_path_list = []
    attachment_filename = ''
    for task_id in task_ids:
        real_filename = basedir
        task = TextTask.query.get(task_id)
        if not task or task.status != TaskStatus.SUCCESS:
            continue
        if task.user_id != current_user.id:
            abort(403)

        filename = task.filename
        if file_type == "result":
            real_filename += filename[:filename.rfind(".")] + "_target(import)_" + get_keyword(task.keyword) + ".csv"
            attachment_filename = "分析结果合并.csv"
        elif file_type == "statistics":
            real_filename += filename[:filename.rfind(".")] + "_target(total).csv"
            attachment_filename = "统计结果合并.csv"
        elif file_type == "wordCount":
            real_filename += filename[:filename.rfind(".")] + "(wordCount).csv"
            attachment_filename = "词频表合并.csv"
        elif file_type == "singleCount":
            attachment_filename = "字频表合并.csv"
            real_filename += filename[:filename.rfind(".")] + "(singleCount).csv"
        else:
            abort(404)
        file_path_list.append((real_filename, task.name))

    result_file = None
    if file_type in ["result", "statistics"]:
        result_file = merge_rows(file_path_list)
    elif file_type in ["wordCount", "singleCount"]:
        result_file = merge_columns(file_path_list)

    response = make_response(result_file)
    response.headers['Content-Type'] = 'application/vnd.ms-excel'
    response.headers['Content-Disposition'] = 'attachment; filename=' + attachment_filename
    return response
    # return send_file(result_file, attachment_filename=attachment_filename, as_attachment=True)
