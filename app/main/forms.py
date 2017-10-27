from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(FlaskForm):
    """文本字段，确保提交不为空"""
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')
