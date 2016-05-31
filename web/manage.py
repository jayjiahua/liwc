# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/3/29 0029 Jay : Init

#!/usr/bin/env python

import os, sys
from app import create_app
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app import db, app


manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db)

@manager.command
def db_init():
    from app.models import Role, User, Dict, TextTask, MatrixTask, Library
    db.create_all()
    Role.insert_default_roles()
    User.insert_admin()
    user = User(username="admin", password="admin123", fullname=u"超级管理员", role_id=1)
    db.session.add(user)
    db.session.commit()

@manager.command
def reset_task():
    from app.models import TextTask, MatrixTask, TaskStatus
    text_tasks = TextTask.query.filter_by(status=TaskStatus.RUNNING)
    t_count = 0
    for text_task in text_tasks:
        text_task.status = TaskStatus.WAITING
        db.session.add(text_task)
        t_count += 1

    m_count = 0
    matrix_tasks = MatrixTask.query.filter_by(status=TaskStatus.RUNNING)
    for matrix_task in matrix_tasks:
        matrix_task.status = TaskStatus.WAITING
        db.session.add(matrix_task)
        m_count += 1
    db.session.commit()
    print "Reset text: {0}, matrix: {1}".format(t_count, m_count)

@manager.command
def clean_waiting_task():
    from app.models import TextTask, MatrixTask, TaskStatus
    text_tasks = TextTask.query.filter_by(status=TaskStatus.WAITING)

    t_count = 0
    for text_task in text_tasks:
        text_task.status = TaskStatus.FAIL
        db.session.add(text_task)
        t_count += 1

    m_count = 0
    matrix_tasks = MatrixTask.query.filter_by(status=TaskStatus.WAITING)
    for matrix_task in matrix_tasks:
        matrix_task.status = TaskStatus.FAIL
        db.session.add(matrix_task)
        m_count += 1
    db.session.commit()

    print "Reset text: {0}, matrix: {1}".format(t_count, m_count)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # import os, sys
    # os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
    manager.run()
