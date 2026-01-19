from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class EmpresaForm(FlaskForm):

    nombrecomercial = StringField('Nombre Comercial', validators=[DataRequired(), Length(max=255)])
    cif = StringField('CIF', validators=[DataRequired(), Length(max=20)])


    domicilio = StringField('Domicilio', validators=[Length(max=255)])
    localidad = StringField('Localidad', validators=[Length(max=100)])
    cp = StringField('Código Postal', validators=[Length(max=10)])
    provincia = StringField('Provincia', validators=[Length(max=50)])
    email = StringField('Email Corporativo', validators=[Length(max=100)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    latitud = FloatField('Latitud', validators=[Optional()])
    longitud = FloatField('Longitud', validators=[Optional()])
    radio = IntegerField('Radio (metros)', validators=[Optional(), NumberRange(min=10)], default=100)

    submit = SubmitField('Guardar Configuración')