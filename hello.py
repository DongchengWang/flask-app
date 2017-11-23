# -*- coding:utf-8-*-
# !/usr/bin/env python3
# 单文件版的flask应用，TODO:remove this file
import os
from flask import session, redirect, url_for, flash
from flask_script import Manager, Shell


from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

from flask_migrate import Migrate, MigrateCommand

from flask_mail import Message
from threading import Thread


basedir = os.path.abspath(os.path.dirname(__file__))
# 初始化
app = Flask(__name__)
manager = Manager(app)

app.config['SECRET_KEY'] = 'hard to guess string'
# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# 邮件系统
app.config['MAIL_SERVER'] = 'smtp.126.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# 设置默认的邮件账户前缀
app.config['FLASKY_MAIL_SUBJEXT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <luffy12345@126.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))

# 发送邮件给用户


def send_mail(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' +
                  subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

# 异步发送邮件


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


class NameForm(FlaskForm):
    # 文本字段，确保提交不为空
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

# 数据库操作


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

# 首页


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        # 判断是否提交不同的字段
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            # 每当表单接受新名字，都回想管理员发送邮件
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'],
                          'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))

    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form, name=session.get('name'), known=session.get('known', False))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)



# 数据库迁移
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
