from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=4, message="La contraseña debe tener al menos 4 caracteres.")
    ])
    confirm_password = PasswordField('Repetir Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas no coinciden.')
    ])
    submit = SubmitField('Cambiar Contraseña')