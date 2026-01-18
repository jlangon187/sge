from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TimeField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class EmpresaForm(FlaskForm):
    nombrecomercial = StringField('Nombre Comercial', validators=[DataRequired(), Length(max=255)])
    cif = StringField('CIF', validators=[DataRequired(), Length(max=20)])
    domicilio = StringField('Domicilio', validators=[Length(max=255)])
    localidad = StringField('Localidad', validators=[Length(max=100)])
    cp = StringField('Código Postal', validators=[Length(max=10)])
    provincia = StringField('Provincia', validators=[Length(max=50)])
    email = StringField('Email Corporativo', validators=[Length(max=100)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    submit = SubmitField('Guardar Datos')

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

class RolForm(FlaskForm):
    nombre_rol = StringField('Nombre del Rol', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Guardar Rol')

class HorarioForm(FlaskForm):
    nombre_horario = StringField('Nombre del Horario', validators=[DataRequired(), Length(max=50)])
    descripcion = StringField('Descripción', validators=[Length(max=255)])
    submit = SubmitField('Crear Horario')

class FranjaForm(FlaskForm):
    id_dia = SelectField('Día de la Semana', coerce=int, validators=[DataRequired()])
    hora_entrada = TimeField('Hora Entrada', format='%H:%M', validators=[DataRequired()])
    hora_salida = TimeField('Hora Salida', format='%H:%M', validators=[DataRequired()])

    submit = SubmitField('Añadir Franja')