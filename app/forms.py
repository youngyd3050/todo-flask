from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Optional

class SearchForm(FlaskForm):
    keyword   = StringField('关键词', validators=[Optional()], render_kw={'placeholder': '搜索标题'})
    priority  = SelectField('优先级', choices=[('', '全部'), ('1', '高'), ('2', '中'), ('3', '低')], default='')
    submit    = SubmitField('搜索')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=30)])
    email    = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    confirm  = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit   = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit   = SubmitField('登录')