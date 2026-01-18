from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class RolForm(FlaskForm):
    nombre_rol = StringField('Nombre del Rol', validators=[DataRequired()])
    submit = SubmitField('Guardar')