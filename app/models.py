from . import db

# 1. Tabla Empresa
class Empresa(db.Model):
    __tablename__ = 'empresa'
    id_empresa = db.Column(db.Integer, primary_key=True)
    nombrecomercial = db.Column(db.String(255))
    cif = db.Column(db.String(20))
    domicilio = db.Column(db.String(255))
    localidad = db.Column(db.String(100))
    cp = db.Column(db.String(10))
    provincia = db.Column(db.String(50))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))

    empleados = db.relationship('Trabajador', backref='empresa', lazy=True)

# 2. Tabla Rol
class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50))

    trabajadores = db.relationship('Trabajador', backref='rol', lazy=True)

# 3. Tabla Horario
class Horario(db.Model):
    __tablename__ = 'horario'
    id_horario = db.Column(db.Integer, primary_key=True)
    nombre_horario = db.Column(db.String(50))
    descripcion = db.Column(db.String(255))

    trabajadores = db.relationship('Trabajador', backref='horario', lazy=True)
    franjas = db.relationship('Franjas', backref='horario', lazy=True)

# 4. Tabla Dia
class Dia(db.Model):
    __tablename__ = 'dia'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20))

    franjas = db.relationship('Franjas', backref='dia', lazy=True)

# 5. Tabla Trabajador
class Trabajador(db.Model):
    __tablename__ = 'trabajador'
    id_trabajador = db.Column(db.Integer, primary_key=True)
    nif = db.Column(db.String(20), unique=True)
    nombre = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    passw = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True)
    telef = db.Column(db.String(20))
    calle = db.Column(db.String(255))
    localidad = db.Column(db.String(100))
    cp = db.Column(db.String(10))
    provincia = db.Column(db.String(50))

    idEmpresa = db.Column(db.Integer, db.ForeignKey('empresa.id_empresa'))
    idHorario = db.Column(db.Integer, db.ForeignKey('horario.id_horario'))
    idRol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'))

# 6. Tabla Franjas
class Franjas(db.Model):
    __tablename__ = 'franjas'

    # 1. Clave primaria nueva
    id = db.Column(db.Integer, primary_key=True)

    # 2. Claves foráneas (SIN primary_key=True)
    id_horario = db.Column(db.Integer, db.ForeignKey('horario.id_horario'), nullable=False)
    id_dia = db.Column(db.Integer, db.ForeignKey('dia.id'), nullable=False)

    # 3. Datos de hora
    hora_entrada = db.Column(db.Time, nullable=False)
    hora_salida = db.Column(db.Time, nullable=False)