from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from config import Config
from extensions import db
from models import Empresa, Rol, Horario, Dia, Trabajador, Franjas
from forms import LoginForm, EmpresaForm, EmpleadoForm, RolForm, HorarioForm, FranjaForm, EmpleadoEditForm, ChangePasswordForm

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    Bootstrap(app)

    @app.route('/')
    def index():
        # Si no hay usuario logueado, mostramos una pantalla de bienvenida simple o login
        if 'user_id' not in session:
            return render_template('index.html', logged_in=False)

        # Obtenemos datos del usuario actual
        usuario = Trabajador.query.get(session['user_id'])

        # --- LÓGICA PARA SUPERADMINISTRADOR ---
        if session.get('user_role') == 'Superadministrador':
            # Métricas globales del sistema
            stats = {
                'total_empresas': Empresa.query.count(),
                'total_usuarios': Trabajador.query.count(),
                'total_roles': Rol.query.count(),
                'total_horarios': Horario.query.count()
            }
            return render_template('index.html', logged_in=True, es_super=True, stats=stats, usuario=usuario)

        # --- LÓGICA PARA ADMINISTRADOR / TRABAJADOR ---
        else:
            empresa_id = session.get('empresa_id')

            if not empresa_id:
                return render_template('index.html', logged_in=True, es_super=False, empresa=None, usuario=usuario)

            empresa_actual = Empresa.query.get(empresa_id)

            total_empleados = Trabajador.query.filter_by(idEmpresa=empresa_id).count()

            empleados_sin_horario = Trabajador.query.filter_by(idEmpresa=empresa_id, idHorario=None).count()

            stats = {
                'empleados': total_empleados,
                'pendientes_horario': empleados_sin_horario
            }

            return render_template('index.html',
                                   logged_in=True,
                                   es_super=False,
                                   empresa=empresa_actual,
                                   stats=stats,
                                   usuario=usuario)

    # --- LOGIN AUTOMÁTICO ---
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Si ya está logueado, lo mandamos al inicio
        if 'user_id' in session:
            return redirect(url_for('index'))

        form = LoginForm()

        if form.validate_on_submit():
            # Buscamos al usuario solo por EMAIL
            usuario = Trabajador.query.filter_by(email=form.email.data).first()

            if usuario and usuario.passw == form.password.data:

                # --- CASO 1: SUPERADMINISTRADOR ---
                if usuario.rol.nombre_rol == 'Superadministrador':
                    session['user_id'] = usuario.id_trabajador
                    session['user_name'] = usuario.nombre
                    session['user_role'] = 'Superadministrador'

                    # El Superadmin NO tiene empresa fija en el login
                    session['empresa_id'] = None
                    session['empresa_nombre'] = "Zona Superadmin"

                    flash(f'Bienvenido Superadmin {usuario.nombre}')
                    return redirect(url_for('index'))

                # --- CASO 2: ADMINISTRADOR (O TRABAJADOR) ---
                elif usuario.rol.nombre_rol == 'Administrador': # Puedes añadir 'Trabajador' aquí si quieres que entren

                    # Verificamos que tenga una empresa asignada en la BBDD
                    if not usuario.idEmpresa:
                        flash('Error: Tu usuario no tiene una empresa asignada. Contacta con soporte.')
                        return render_template('login.html', form=form)

                    session['user_id'] = usuario.id_trabajador
                    session['user_name'] = usuario.nombre
                    session['user_role'] = usuario.rol.nombre_rol

                    # ASIGNACIÓN AUTOMÁTICA DE SU EMPRESA
                    session['empresa_id'] = usuario.idEmpresa
                    session['empresa_nombre'] = usuario.empresa.nombrecomercial if usuario.empresa else "Empresa Desconocida"

                    return redirect(url_for('index'))

                # --- ROL NO PERMITIDO ---
                else:
                    flash('Acceso denegado: Tu rol no tiene permisos para acceder al panel.')
                    return render_template('login.html', form=form)

            else:
                flash('Email o contraseña incorrectos.')

        return render_template('login.html', form=form)

    # --- LOGOUT ---
    @app.route('/logout')
    def logout():
        session.clear()
        flash('Has cerrado sesión correctamente.')
        return redirect(url_for('index'))

    # --- GESTIÓN DE EMPRESA ---
    @app.route('/empresa', methods=['GET', 'POST'])
    def gestion_empresa():
        if 'user_id' not in session: return redirect(url_for('login'))

        # 1. Recuperamos el ID de forma segura con .get() para evitar KeyErrors
        empresa_id = session.get('empresa_id')

        # 2. Si no hay empresa ID (es None), rebotamos al usuario
        if not empresa_id:
            flash('Atención: No hay ninguna empresa seleccionada.')
            if session.get('user_role') == 'Superadministrador':
                return redirect(url_for('lista_empresas'))
            else:
                # Si es un admin normal sin empresa, es un error de datos, lo mandamos al login/inicio
                return redirect(url_for('login'))

        # 3. Buscamos la empresa. Si no existe en la BD, lanza un error 404 controlado
        empresa = Empresa.query.get_or_404(empresa_id)

        form = EmpresaForm()

        if form.validate_on_submit():
            empresa.nombrecomercial = form.nombrecomercial.data
            empresa.cif = form.cif.data
            empresa.domicilio = form.domicilio.data
            empresa.localidad = form.localidad.data
            empresa.cp = form.cp.data
            empresa.provincia = form.provincia.data
            empresa.email = form.email.data
            empresa.telefono = form.telefono.data

            db.session.commit()

            session['empresa_nombre'] = empresa.nombrecomercial

            flash('Datos completos de la empresa actualizados.')
            return redirect(url_for('index'))

        if request.method == 'GET':
            # Aquí ya es seguro asignar datos porque 'empresa' existe sí o sí
            form.nombrecomercial.data = empresa.nombrecomercial
            form.cif.data = empresa.cif
            form.domicilio.data = empresa.domicilio
            form.localidad.data = empresa.localidad
            form.cp.data = empresa.cp
            form.provincia.data = empresa.provincia
            form.email.data = empresa.email
            form.telefono.data = empresa.telefono

        return render_template('empresa.html', form=form)

    # --- LISTADO DE EMPLEADOS ---
    @app.route('/empleados')
    def lista_empleados():
        if 'user_id' not in session: return redirect(url_for('login'))
        empresa_id_activa = session.get('empresa_id')
        empleados = Trabajador.query.filter_by(idEmpresa=empresa_id_activa).all()

        return render_template('empleados.html', empleados=empleados)

    # --- CREAR EMPLEADO ---
    @app.route('/empleados/nuevo', methods=['GET', 'POST'])
    def crear_empleado():
        if 'user_id' not in session: return redirect(url_for('login'))
        form = EmpleadoForm()
        form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]
        form.id_horario.choices = [(h.id_horario, h.nombre_horario) for h in Horario.query.all()]

        if form.validate_on_submit():
            existe_nif = Trabajador.query.filter_by(nif=form.nif.data).first()
            if existe_nif:
                flash(f'Error: El NIF {form.nif.data} ya está registrado en el sistema.')
                return render_template('empleado_form.html', form=form, titulo="Nuevo Empleado")

            existe_email = Trabajador.query.filter_by(email=form.email.data).first()
            if existe_email:
                flash(f'Error: El email {form.email.data} ya está en uso.')
                return render_template('empleado_form.html', form=form, titulo="Nuevo Empleado")

            empresa_id = session.get('empresa_id')

            nuevo_emp = Trabajador(
                nif=form.nif.data, nombre=form.nombre.data, apellidos=form.apellidos.data,
                email=form.email.data, telef=form.telef.data, passw=form.passw.data,
                calle=form.calle.data, localidad=form.localidad.data,
                cp=form.cp.data, provincia=form.provincia.data,
                idRol=form.id_rol.data,
                idEmpresa=empresa_id,
                idHorario=form.id_horario.data
                )
            db.session.add(nuevo_emp)
            db.session.commit()
            flash('Empleado creado con dirección.')
            return redirect(url_for('lista_empleados'))
        return render_template('empleado_form.html', form=form, titulo="Nuevo Empleado")

    # --- EDITAR EMPLEADO ---
    @app.route('/empleados/editar/<int:id>', methods=['GET', 'POST'])
    def editar_empleado(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        empleado = Trabajador.query.get_or_404(id)

        if session.get('user_role') != 'Superadministrador' and empleado.idEmpresa != session['empresa_id']:
             flash("Error: No tienes permiso para editar este empleado.")
             return redirect(url_for('lista_empleados'))

        form = EmpleadoEditForm(obj=empleado) # 'obj=empleado' rellena los campos automáticamente

        form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]
        form.id_horario.choices = [(h.id_horario, h.nombre_horario) for h in Horario.query.all()]

        form_pass = ChangePasswordForm()

        if form.validate_on_submit():
            existe_nif = Trabajador.query.filter(Trabajador.nif == form.nif.data, Trabajador.id_trabajador != id).first()
            if existe_nif:
                flash(f'Error: El NIF {form.nif.data} ya pertenece a otro empleado.')
                return render_template('empleado_form.html', form=form, form_pass=form_pass, titulo="Editar Empleado", editando=True, empleado=empleado)

            existe_email = Trabajador.query.filter(Trabajador.email == form.email.data, Trabajador.id_trabajador != id).first()
            if existe_email:
                flash(f'Error: El email {form.email.data} ya está en uso.')
                return render_template('empleado_form.html', form=form, form_pass=form_pass, titulo="Editar Empleado", editando=True, empleado=empleado)

            form.populate_obj(empleado)

            db.session.commit()
            flash('Datos del empleado actualizados correctamente.')
            return redirect(url_for('lista_empleados'))

        return render_template('empleado_form.html', form=form, form_pass=form_pass, titulo="Editar Empleado", editando=True, empleado=empleado)

    # --- CAMBIAR CONTRASEÑA ---
    @app.route('/empleados/cambiar-password/<int:id>', methods=['POST'])
    def cambiar_password_empleado(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        empleado = Trabajador.query.get_or_404(id)
        form = ChangePasswordForm()

        if form.validate_on_submit():
            empleado.passw = form.password.data
            db.session.commit()
            flash('La contraseña se ha cambiado correctamente.')
        else:
            flash('Error al cambiar la contraseña. Asegúrate de que no esté vacía.')

        return redirect(url_for('editar_empleado', id=id))

    # --- BORRAR EMPLEADO ---
    @app.route('/empleados/borrar/<int:id>')
    def borrar_empleado(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        empleado = Trabajador.query.get_or_404(id)

        if empleado.idEmpresa != session['empresa_id']:
             flash("Error: Este empleado no pertenece a la empresa activa.")
             return redirect(url_for('lista_empleados'))

        if empleado.rol.nombre_rol == 'Superadministrador':
            flash('CRÍTICO: No está permitido eliminar a un Superadministrador.')
            return redirect(url_for('lista_empleados'))

        if id == session['user_id']:
            flash('No puedes borrar tu propio usuario.')
            return redirect(url_for('lista_empleados'))

        db.session.delete(empleado)
        db.session.commit()
        flash('Empleado eliminado.')
        return redirect(url_for('lista_empleados'))

    # --- LISTADO DE ROLES ---
    @app.route('/roles')
    def lista_roles():
        if 'user_id' not in session: return redirect(url_for('login'))

        roles = Rol.query.all()
        return render_template('roles.html', roles=roles)

    # --- CREAR ROL ---
    @app.route('/roles/nuevo', methods=['GET', 'POST'])
    def crear_rol():
        if 'user_id' not in session: return redirect(url_for('login'))

        form = RolForm()
        if form.validate_on_submit():
            existe = Rol.query.filter_by(nombre_rol=form.nombre_rol.data).first()
            if existe:
                flash('Error: Ya existe un rol con ese nombre.')
            else:
                nuevo_rol = Rol(nombre_rol=form.nombre_rol.data)
                db.session.add(nuevo_rol)
                db.session.commit()
                flash('Rol creado correctamente.')
                return redirect(url_for('lista_roles'))

        return render_template('rol_form.html', form=form, titulo="Nuevo Rol")

    # --- EDITAR ROL ---
    @app.route('/roles/editar/<int:id>', methods=['GET', 'POST'])
    def editar_rol(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        rol = Rol.query.get_or_404(id)
        form = RolForm()

        if form.validate_on_submit():
            existe = Rol.query.filter(Rol.nombre_rol == form.nombre_rol.data, Rol.id_rol != id).first()
            if existe:
                flash('Error: Ese nombre ya está en uso por otro rol.')
            else:
                rol.nombre_rol = form.nombre_rol.data
                db.session.commit()
                flash('Rol actualizado.')
                return redirect(url_for('lista_roles'))

        if request.method == 'GET':
            form.nombre_rol.data = rol.nombre_rol

        return render_template('rol_form.html', form=form, titulo="Editar Rol")

    # --- BORRAR ROL ---
    @app.route('/roles/borrar/<int:id>')
    def borrar_rol(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        rol = Rol.query.get_or_404(id)

        if len(rol.trabajadores) > 0:
            flash(f'Error: No se puede eliminar el rol "{rol.nombre_rol}" porque tiene {len(rol.trabajadores)} empleados asignados.')
        else:
            db.session.delete(rol)
            db.session.commit()
            flash('Rol eliminado correctamente.')

        return redirect(url_for('lista_roles'))

    # --- LISTADO DE HORARIOS ---
    @app.route('/horarios')
    def lista_horarios():
        if 'user_id' not in session: return redirect(url_for('login'))

        horarios = Horario.query.all()
        return render_template('horarios.html', horarios=horarios)

    # --- CREAR NUEVO HORARIO ---
    @app.route('/horarios/nuevo', methods=['GET', 'POST'])
    def crear_horario():
        if 'user_id' not in session: return redirect(url_for('login'))

        form = HorarioForm()
        if form.validate_on_submit():
            nuevo_horario = Horario(
                nombre_horario=form.nombre_horario.data,
                descripcion=form.descripcion.data
            )
            db.session.add(nuevo_horario)
            db.session.commit()
            flash('Horario creado. Ahora añade las franjas.')
            return redirect(url_for('detalle_horario', id=nuevo_horario.id_horario))

        return render_template('horario_form.html', form=form, titulo="Nuevo Horario")

    # --- BORRAR HORARIO ---
    @app.route('/horarios/borrar/<int:id>')
    def borrar_horario(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        horario = Horario.query.get_or_404(id)

        if len(horario.trabajadores) > 0:
            flash(f'Error: No se puede borrar "{horario.nombre_horario}" porque hay empleados asignados.')
        else:
            try:
                for franja in horario.franjas:
                    db.session.delete(franja)

                db.session.delete(horario)
                db.session.commit()
                flash('Horario y sus franjas eliminados correctamente.')
            except Exception as e:
                db.session.rollback()
                flash(f'Error interno al borrar: {str(e)}')

        return redirect(url_for('lista_horarios'))

    # --- DETALLE DE HORARIO Y GESTIÓN DE FRANJAS ---
    @app.route('/horarios/<int:id>', methods=['GET', 'POST'])
    def detalle_horario(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        horario = Horario.query.get_or_404(id)
        form = FranjaForm()
        form.id_dia.choices = [(d.id, d.nombre) for d in Dia.query.all()]

        if form.validate_on_submit():
            nuevo_inicio = form.hora_entrada.data
            nuevo_fin = form.hora_salida.data
            dia_seleccionado = form.id_dia.data

            if nuevo_inicio >= nuevo_fin:
                flash('Error: La hora de salida debe ser posterior a la hora de entrada.')
                franjas = Franjas.query.filter_by(id_horario=id).join(Dia).order_by(Dia.id, Franjas.hora_entrada).all()
                return render_template('horario_detalle.html', horario=horario, franjas=franjas, form=form)

            franjas_existentes = Franjas.query.filter_by(id_horario=id, id_dia=dia_seleccionado).all()

            solapamiento = False
            for f in franjas_existentes:
                if (nuevo_inicio < f.hora_salida) and (nuevo_fin > f.hora_entrada):
                    solapamiento = True
                    break

            if solapamiento:
                flash('Error: La franja se solapa con otra existente.')
            else:
                nueva_franja = Franjas(
                    id_horario=id,
                    id_dia=dia_seleccionado,
                    hora_entrada=nuevo_inicio,
                    hora_salida=nuevo_fin
                )
                db.session.add(nueva_franja)
                db.session.commit()
                flash('Franja añadida correctamente.')
                return redirect(url_for('detalle_horario', id=id))

        franjas = Franjas.query.filter_by(id_horario=id).join(Dia).order_by(Dia.id, Franjas.hora_entrada).all()
        return render_template('horario_detalle.html', horario=horario, franjas=franjas, form=form)

    # --- EDITAR FRANJA EXISTENTE ---
    @app.route('/franjas/editar/<int:id>', methods=['GET', 'POST'])
    def editar_franja(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        franja = Franjas.query.get_or_404(id)
        form = FranjaForm()

        form.submit.label.text = 'Guardar Cambios'

        form.id_dia.choices = [(d.id, d.nombre) for d in Dia.query.all()]

        if form.validate_on_submit():
            nuevo_inicio = form.hora_entrada.data
            nuevo_fin = form.hora_salida.data
            dia_seleccionado = form.id_dia.data

            if nuevo_inicio >= nuevo_fin:
                flash('Error: La hora de salida debe ser posterior a la de entrada.')
                return render_template('franja_editar.html', form=form, franja=franja)

            franjas_existentes = Franjas.query.filter(
                Franjas.id_horario == franja.id_horario,
                Franjas.id_dia == dia_seleccionado,
                Franjas.id != id
            ).all()

            solapamiento = False
            for f in franjas_existentes:
                if (nuevo_inicio < f.hora_salida) and (nuevo_fin > f.hora_entrada):
                    solapamiento = True
                    break

            if solapamiento:
                flash('Error: La modificación provoca un solapamiento con otra franja.')
            else:
                franja.id_dia = dia_seleccionado
                franja.hora_entrada = nuevo_inicio
                franja.hora_salida = nuevo_fin
                db.session.commit()
                flash('Franja modificada correctamente.')
                return redirect(url_for('detalle_horario', id=franja.id_horario))

        if request.method == 'GET':
            form.id_dia.data = franja.id_dia
            form.hora_entrada.data = franja.hora_entrada
            form.hora_salida.data = franja.hora_salida

        return render_template('franja_editar.html', form=form, franja=franja)

# --- BORRAR FRANJA ---
    @app.route('/franjas/borrar/<int:id>')
    def borrar_franja(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        franja = Franjas.query.get_or_404(id)

        id_horario_retorno = franja.id_horario

        db.session.delete(franja)
        db.session.commit()
        flash('Franja eliminada correctamente.')

        return redirect(url_for('detalle_horario', id=id_horario_retorno))

    # --- CREAR EMPRESA ---
    @app.route('/admin/empresas/nueva', methods=['GET', 'POST'])
    def crear_empresa_admin():
        if 'user_id' not in session: return redirect(url_for('login'))

        usuario = Trabajador.query.get(session['user_id'])
        if usuario.rol.nombre_rol != 'Superadministrador':
            return redirect(url_for('index'))

        form = EmpresaForm()
        if form.validate_on_submit():
            nueva_empresa = Empresa(
                nombrecomercial=form.nombrecomercial.data,
                cif=form.cif.data,
                domicilio=form.domicilio.data,
                localidad=form.localidad.data,
                cp=form.cp.data,
                provincia=form.provincia.data,
                email=form.email.data,
                telefono=form.telefono.data
            )
            db.session.add(nueva_empresa)
            db.session.commit()
            flash('Nueva empresa registrada.')
            return redirect(url_for('lista_empresas'))

        return render_template('empresa_form_admin.html', form=form, titulo="Nueva Empresa")

    # --- BORRAR EMPRESA ---
    @app.route('/admin/empresas/borrar/<int:id>')
    def borrar_empresa_admin(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        usuario = Trabajador.query.get(session['user_id'])
        if usuario.rol.nombre_rol != 'Superadministrador':
            return redirect(url_for('index'))

        empresa = Empresa.query.get_or_404(id)

        if len(empresa.empleados) > 0:
            flash(f'Error: La empresa "{empresa.nombrecomercial}" tiene empleados. No se puede eliminar.')
        else:
            db.session.delete(empresa)
            db.session.commit()
            flash('Empresa eliminada correctamente.')

        return redirect(url_for('lista_empresas'))

    # --- GESTIÓN DE SUPERADMINISTRADORES ---
    @app.route('/admin/superadmins')
    def lista_superadmins():
        if 'user_id' not in session: return redirect(url_for('login'))

        usuario = Trabajador.query.get(session['user_id'])
        if usuario.rol.nombre_rol != 'Superadministrador':
            flash('Acceso denegado.')
            return redirect(url_for('index'))

        superadmins = Trabajador.query.join(Rol).filter(Rol.nombre_rol == 'Superadministrador').all()
        return render_template('admin_superadmins.html', superadmins=superadmins)

    # --- CREAR SUPERADMINISTRADOR (CORREGIDO) ---
    @app.route('/admin/superadmins/nuevo', methods=['GET', 'POST'])
    def crear_superadmin():
        if 'user_id' not in session: return redirect(url_for('login'))

        usuario_actual = Trabajador.query.get(session['user_id'])
        if usuario_actual.rol.nombre_rol != 'Superadministrador':
            return redirect(url_for('index'))

        form = EmpleadoForm()

        # --- CORRECCIÓN 1: CARGAR LAS OPCIONES DE LOS DESPLEGABLES ---
        # Si no hacemos esto, la lista sale vacía y el formulario falla
        form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]
        # Cargamos TODOS los horarios del sistema (ya que el superadmin es global)
        form.id_horario.choices = [(h.id_horario, h.nombre_horario) for h in Horario.query.all()]
        # -------------------------------------------------------------

        if form.validate_on_submit():
            if Trabajador.query.filter_by(nif=form.nif.data).first():
                flash(f'Error: El NIF {form.nif.data} ya existe.')
                return render_template('empleado_form.html', form=form, titulo="Nuevo Superadmin")

            if Trabajador.query.filter_by(email=form.email.data).first():
                flash(f'Error: El Email {form.email.data} ya existe.')
                return render_template('empleado_form.html', form=form, titulo="Nuevo Superadmin")

            rol_super = Rol.query.filter_by(nombre_rol='Superadministrador').first()

            nuevo_super = Trabajador(
                nif=form.nif.data,
                nombre=form.nombre.data,
                apellidos=form.apellidos.data,
                email=form.email.data,
                telef=form.telef.data,
                passw=form.passw.data,
                calle=form.calle.data,
                localidad=form.localidad.data,
                cp=form.cp.data,
                provincia=form.provincia.data,

                # Forzamos que sea Superadmin
                idRol=rol_super.id_rol,

                # --- CORRECCIÓN 2: EMPRESA A NULL ---
                # Un Superadmin global no pertenece a ninguna empresa específica
                idEmpresa=None,

                # Usamos el horario que hayas seleccionado en el formulario
                idHorario=form.id_horario.data
            )

            db.session.add(nuevo_super)
            db.session.commit()
            flash('Nuevo Superadministrador registrado correctamente.')
            return redirect(url_for('lista_superadmins'))

        # Si es GET, pre-seleccionamos el rol de Superadmin para que sea más cómodo
        rol_super = Rol.query.filter_by(nombre_rol='Superadministrador').first()
        if request.method == 'GET' and rol_super:
            form.id_rol.data = rol_super.id_rol

        return render_template('empleado_form.html', form=form, titulo="Nuevo Superadmin")

    # --- EDITAR SUPERADMINISTRADOR (CORREGIDO) ---
    @app.route('/admin/superadmins/editar/<int:id>', methods=['GET', 'POST'])
    def editar_superadmin(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        # Seguridad: Solo un Superadmin puede editar a otro
        usuario_actual = Trabajador.query.get(session['user_id'])
        if usuario_actual.rol.nombre_rol != 'Superadministrador':
            return redirect(url_for('index'))

        superadmin_edit = Trabajador.query.get_or_404(id)

        # 1. USAMOS EL FORMULARIO DE EDICIÓN (SIN CONTRASEÑA)
        form = EmpleadoEditForm(obj=superadmin_edit)

        # 2. CARGAMOS LOS DESPLEGABLES (SOLUCIÓN AL ERROR DE HORARIOS)
        form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]
        form.id_horario.choices = [(h.id_horario, h.nombre_horario) for h in Horario.query.all()]

        # 3. PREPARAMOS EL FORMULARIO DE CAMBIO DE CONTRASEÑA (PARA EL MODAL)
        form_pass = ChangePasswordForm()

        if form.validate_on_submit():
            # Validaciones de duplicados (excluyendo al propio usuario)
            existe_nif = Trabajador.query.filter(Trabajador.nif == form.nif.data, Trabajador.id_trabajador != id).first()
            if existe_nif:
                flash(f'Error: El NIF {form.nif.data} ya pertenece a otro usuario.')
                return render_template('empleado_form.html', form=form, form_pass=form_pass, titulo="Editar Superadmin", editando=True, empleado=superadmin_edit)

            existe_email = Trabajador.query.filter(Trabajador.email == form.email.data, Trabajador.id_trabajador != id).first()
            if existe_email:
                flash(f'Error: El email {form.email.data} ya está en uso.')
                return render_template('empleado_form.html', form=form, form_pass=form_pass, titulo="Editar Superadmin", editando=True, empleado=superadmin_edit)

            # Guardamos los cambios (form.populate_obj copia todo menos lo que no esté en el form, como el pass)
            form.populate_obj(superadmin_edit)

            # Aseguramos que idEmpresa siga siendo None (por si acaso el formulario intentara asignar algo)
            superadmin_edit.idEmpresa = None

            db.session.commit()
            flash('Datos del Superadministrador actualizados.')
            return redirect(url_for('lista_superadmins'))

        # Renderizamos la misma plantilla que usamos para empleados
        # 'editando=True' activa el modo de visualización con el botón de cambiar contraseña
        return render_template('empleado_form.html',
                               form=form,
                               form_pass=form_pass,
                               titulo="Editar Superadmin",
                               editando=True,
                               empleado=superadmin_edit)

    # --- BORRAR SUPERADMINISTRADOR ---
    @app.route('/admin/superadmins/borrar/<int:id>')
    def borrar_superadmin(id):
        if 'user_id' not in session: return redirect(url_for('login'))

        usuario_actual = Trabajador.query.get(session['user_id'])
        if usuario_actual.rol.nombre_rol != 'Superadministrador':
            return redirect(url_for('index'))

        if id == session['user_id']:
            flash('Error: No puedes borrar tu propia cuenta de Superadministrador desde aquí.')
            return redirect(url_for('lista_superadmins'))

        superadmin_borrar = Trabajador.query.get_or_404(id)
        db.session.delete(superadmin_borrar)
        db.session.commit()
        flash('Superadministrador eliminado.')

        return redirect(url_for('lista_superadmins'))

    # --- SUPERADMIN: LISTAR TODAS LAS EMPRESAS ---
    @app.route('/superadmin/empresas')
    def lista_empresas():
        # Seguridad: Solo Superadmin
        if 'user_id' not in session or session.get('user_role') != 'Superadministrador':
            return redirect(url_for('login'))

        empresas = Empresa.query.all()
        return render_template('empresas_list.html', empresas=empresas)

    # --- SUPERADMIN: SELECCIONAR EMPRESA (CONTEXT SWITCHING) ---
    @app.route('/superadmin/seleccionar/<int:id>')
    def seleccionar_empresa(id):
        if 'user_id' not in session or session.get('user_role') != 'Superadministrador':
            return redirect(url_for('login'))

        empresa = Empresa.query.get_or_404(id)

        # AQUÍ OCURRE LA MAGIA:
        # Asignamos temporalmente esta empresa a la sesión del Superadmin
        session['empresa_id'] = empresa.id_empresa
        session['empresa_nombre'] = empresa.nombrecomercial

        flash(f'Ahora estás gestionando: {empresa.nombrecomercial}')

        # Le mandamos directamente al panel de esa empresa
        return redirect(url_for('gestion_empresa'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run()