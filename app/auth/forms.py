from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..models import User


class LoginForm(Form):
    '''
    登陆表单:
        需要邮箱账号，密码，记住我，和提交按钮
    '''
    email = StringField('Email', validators=[
                        Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login In')


class RegistrationForm(Form):
    email = StringField('Email', validators=[
                        Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
