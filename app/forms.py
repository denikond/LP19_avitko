from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, MultipleFileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from wtforms.widgets import TextArea
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повтор пароля', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрировать')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста введите другое имя пользователя.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Некорректный e-mail адрес.')

class NewItem(FlaskForm):
    description = StringField('Описание товара', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired(), NumberRange(min=1, message='Цена не должна быть меньше 1')])
    extended_text = StringField('Доп.информация', widget=TextArea(), validators=[DataRequired()])
    images_ = MultipleFileField('Загрузить фото')
    submit = SubmitField('Добавить объявление')
