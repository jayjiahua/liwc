# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/3/29 0029 Jay : Init

import datetime
from flask.ext.wtf import Form
from wtforms import FileField, SubmitField, TextField, StringField, \
    PasswordField, BooleanField, ValidationError, DateField, SelectField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from ..models import *
from flask.ext.login import current_user

def choice_of_roles():
    roles = Role.query.all()
    return [(role.id, role.name) for role in roles if role.permissions != 0xff]

def choice_of_lib():
    # dicts = Dict.query.all()
    # return [(dict.id, dict.name) for dict in dicts if dict.user.is_administrator()]
    if current_user.is_administrator():
        return [(library.id, u"【官方】" + library.name) for library in Library.query.all() if library.user.is_administrator()]
    else:
        return [(library.id, u"【官方】" + library.name) for library in Library.query.all() if library.user.is_administrator()] + \
                [(library.id, u"【个人】" + library.name) for library in current_user.libraries]

def choice_of_user_dict():
    ret = [(-1, u"【默认】使用中科院切词策略")]
    ret += [(dict.id, u"【官方】" + dict.name) for dict in Dict.query.all() if dict.user.is_administrator()]
    if not current_user.is_administrator():
        ret += [(dict.id, u"【个人】" + dict.name) for dict in current_user.dict]
    return ret

class FileForm(Form):
    keyword = StringField(u'关键字', render_kw={"placeholder": u"+表示合取，|表示析取"})
    user_dict = SelectField(u'选择切词&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/main/dict" class="small">添加自定义切词</a>',
                            choices=[], coerce=int)
    library = SelectField(u'选择词库&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/main/library" class="small">添加自定义词库</a>', choices=[], coerce=int, validators=[DataRequired()])

    file = FileField(u'上传文本', validators=[DataRequired()], render_kw={"multiple": "multiple"})
    col_text = IntegerField(u"【文本】所在列数", validators=[DataRequired()], render_kw={"placeholder": u"数字，从0开始计数"})
    var_exact = BooleanField(u'精确搜索')
    submit = SubmitField(u'搜索统计')

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.library.choices = choice_of_lib()
        self.user_dict.choices = choice_of_user_dict()

class ImportForm(Form):
    name = StringField(u'方案名称', validators=[DataRequired()])
    description = StringField(u'方案描述')
    file = FileField(u'上传切词文件&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/main/download/samples/切词文件样例.txt" class="small">下载样例文件</a>', validators=[Required()])

class ExportForm(Form):
    type = StringField(u'导出类别', validators=[DataRequired()], render_kw={"placeholder": u"如\"高兴\""})
    submit = SubmitField(u'导出词典')

class NetworkForm(Form):
    file = FileField(u'选择分析文本', validators=[DataRequired()], render_kw={"multiple": "multiple"})
    id_column = StringField(u'【用户id】所在列数', validators=[DataRequired()], render_kw={"placeholder": u"数字，从0开始计数"})
    text_column = StringField(u'【文本】所在列数', validators=[DataRequired()], render_kw={"placeholder": u"数字，从0开始计数"})
    submit = SubmitField(u'开始分析')

class LoginForm(Form):
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u"记住我")
    submit = SubmitField(u'登录')

class RegistrationForm(Form):
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
            'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField(u'密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    email = StringField(u'电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    fullname = StringField(u'全名', validators=[DataRequired()])
    expired_time = DateField(u'过期时间', validators=[DataRequired()], render_kw={"type": "date", "value": datetime.date.today()})
    forever = BooleanField(u'永不过期')
    role_id = SelectField(u'权限', choices=[], coerce=int)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.role_id.choices = choice_of_roles()

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class EditForm(Form):
    edit_expired_time = DateField(u'过期时间', validators=[DataRequired()], render_kw={"type": "date", "value": datetime.date.today()})
    edit_forever = BooleanField(u'永不过期')

class LibraryForm(Form):
    name = StringField(u'词典名称', validators=[DataRequired()])
    description = StringField(u'词典描述')

    word_dict = FileField(u'【词语-类别】表&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/main/download/samples/【词语-类别】表样例.csv" class="small">下载样例文件</a>', validators=[DataRequired()])
    class_dict = FileField(u'【类别-解释】表&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/main/download/samples/【类别-解释】表样例.csv" class="small">下载样例文件</a>', validators=[DataRequired()])

class EditPasswordForm(Form):
    password = PasswordField(u'原密码', validators=[DataRequired()])
    new_password = PasswordField(u'新密码', validators=[
        DataRequired(), EqualTo('new_password2', message=u'两次密码输入不一致')])
    new_password2 = PasswordField(u'确认密码', validators=[DataRequired()])
    submit = SubmitField(u'确认修改')

    def validate_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError(u'原密码输入错误')

class EditProfileForm(Form):
    email = StringField(u'电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    fullname = StringField(u'全名', validators=[DataRequired()])
    submit = SubmitField(u'确认修改')
