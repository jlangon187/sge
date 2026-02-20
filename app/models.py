from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Empresa(db.Model):
    __tablename__ = 'empresas'
    id_empresa = db.Column(db.Integer, primary_key=True)
    nombrecomercial = db.Column(db.String(255), nullable=False)
    cif = db.Column(db.String(20), nullable=False)
    domicilio = db.Column(db.String(255))
    localidad = db.Column(db.String(100))
    cp = db.Column(db.String(10))
    provincia = db.Column(db.String(50))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))

    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    radio = db.Column(db.Integer, default=100)

    trabajadores = db.relationship('Trabajador', backref='empresa', lazy=True)

class Rol(db.Model):
    __tablename__ = 'roles'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)
    trabajadores = db.relationship('Trabajador', backref='rol', lazy=True)

class Horario(db.Model):
    __tablename__ = 'horarios'
    id_horario = db.Column(db.Integer, primary_key=True)
    nombre_horario = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    trabajadores = db.relationship('Trabajador', backref='horario', lazy=True)
    franjas = db.relationship('Franjas', backref='horario', lazy=True, cascade="all, delete-orphan")

class Dia(db.Model):
    __tablename__ = 'dias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), unique=True, nullable=False)
    franjas = db.relationship('Franjas', backref='dia', lazy=True)

class Franjas(db.Model):
    __tablename__ = 'franjas'
    id = db.Column(db.Integer, primary_key=True)
    id_horario = db.Column(db.Integer, db.ForeignKey('horarios.id_horario'), nullable=False)
    id_dia = db.Column(db.Integer, db.ForeignKey('dias.id'), nullable=False)
    hora_entrada = db.Column(db.Time, nullable=False)
    hora_salida = db.Column(db.Time, nullable=False)

class Trabajador(db.Model):
    __tablename__ = 'trabajadores'
    id_trabajador = db.Column(db.Integer, primary_key=True)
    nif = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telef = db.Column(db.String(20))
    passw = db.Column(db.String(255), nullable=False)

    calle = db.Column(db.String(255))
    localidad = db.Column(db.String(100))
    cp = db.Column(db.String(10))
    provincia = db.Column(db.String(50))

    idEmpresa = db.Column(db.Integer, db.ForeignKey('empresas.id_empresa'), nullable=True)
    idRol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    idHorario = db.Column(db.Integer, db.ForeignKey('horarios.id_horario'), nullable=True)

    fcm_token = db.Column(db.String(255), nullable=True)

    registros = db.relationship('Registro', backref='trabajador', lazy=True, cascade="all, delete-orphan")
    incidencias = db.relationship('Incidencia', backref='trabajador', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.passw = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.passw, password)

class Registro(db.Model):
    __tablename__ = 'registros'
    id_registro = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    hora_entrada = db.Column(db.DateTime, nullable=False)
    hora_salida = db.Column(db.DateTime, nullable=True)

    horas_extra = db.Column(db.Float, default=0.0)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)

    id_trabajador = db.Column(db.Integer, db.ForeignKey('trabajadores.id_trabajador'), nullable=False)

class Incidencia(db.Model):
    __tablename__ = 'incidencias'
    id_incidencia = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(100), nullable=False, default="Incidencia")

    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    descripcion = db.Column(db.Text, nullable=False)

    id_trabajador = db.Column(db.Integer, db.ForeignKey('trabajadores.id_trabajador'), nullable=False)

class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)