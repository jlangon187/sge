from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TimeField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class HorarioForm(FlaskForm):
    nombre_horario = StringField('Nombre del Horario', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    submit = SubmitField('Crear Horario')

class FranjaForm(FlaskForm):
    id_dia = SelectField('Día de la Semana', coerce=int, validators=[DataRequired()])
    hora_entrada = TimeField('Hora Entrada', validators=[DataRequired()])
    hora_salida = TimeField('Hora Salida', validators=[DataRequired()])
    submit = SubmitField('Añadir Franja')