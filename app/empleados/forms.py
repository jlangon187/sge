from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length

class EmpleadoForm(FlaskForm):
    nif = StringField('NIF', validators=[DataRequired(), Length(max=20)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    telef = StringField('Teléfono', validators=[Length(max=20)])
    calle = StringField('Calle', validators=[Length(max=255)])
    localidad = StringField('Localidad', validators=[Length(max=100)])
    cp = StringField('CP', validators=[Length(max=10)])
    provincia = StringField('Provincia', validators=[Length(max=50)])

    passw = PasswordField('Contraseña', validators=[DataRequired(), Length(max=255)])
    id_rol = SelectField('Rol Asignado', coerce=int, validators=[DataRequired()])
    id_horario = SelectField('Horario Laboral', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Empleado')

class EmpleadoEditForm(EmpleadoForm):
    passw = None  # Eliminamos el campo contraseña de la edición normal

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Guardar Nueva Contraseña')