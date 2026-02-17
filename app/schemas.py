from marshmallow import Schema, fields

class UserLoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class EmpresaUbicacionSchema(Schema):
    nombrecomercial = fields.Str()
    latitud = fields.Float()
    longitud = fields.Float()
    radio = fields.Int()

class PerfilSchema(Schema):
    id_trabajador = fields.Int(dump_only=True)
    nombre = fields.Str(dump_only=True)
    apellidos = fields.Str(dump_only=True)
    email = fields.Str(dump_only=True)

    empresa = fields.Nested(EmpresaUbicacionSchema, dump_only=True)

class RegistroSchema(Schema):
    id_registro = fields.Int(dump_only=True)
    fecha = fields.Date(dump_only=True)
    hora_entrada = fields.DateTime(dump_only=True)
    hora_salida = fields.DateTime(dump_only=True)

class FichajeSchema(Schema):
    latitud = fields.Float(required=True)
    longitud = fields.Float(required=True)