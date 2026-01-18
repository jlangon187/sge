from flask import render_template, redirect, url_for, flash, session, request
from . import superadmins_bp
# Importamos los formularios desde el módulo de empleados para reutilizarlos
from ..empleados.forms import EmpleadoForm, EmpleadoEditForm, ChangePasswordForm
from ..models import Trabajador, Rol, Horario
from .. import db

# --- LISTADO DE SUPERADMINS ---
@superadmins_bp.route('/')
def lista_superadmins():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    usuario = Trabajador.query.get(session['user_id'])
    # Doble chequeo de seguridad
    if usuario.rol.nombre_rol != 'Superadministrador':
        flash('Acceso denegado.')
        return redirect(url_for('main.index'))

    superadmins = Trabajador.query.join(Rol).filter(Rol.nombre_rol == 'Superadministrador').all()
    return render_template('admin_superadmins.html', superadmins=superadmins)

# --- CREAR SUPERADMIN ---
@superadmins_bp.route('/nuevo', methods=['GET', 'POST'])
def crear_superadmin():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    usuario_actual = Trabajador.query.get(session['user_id'])
    if usuario_actual.rol.nombre_rol != 'Superadministrador':
        return redirect(url_for('main.index'))

    form = EmpleadoForm()

    # Cargar opciones dinámicas (Importante)
    form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]
    form.id_horario.choices = [(h.id_horario, h.nombre_horario) for h in Horario.query.all()]

    if form.validate_on_submit():
        # Validar duplicados
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
            idRol=rol_super.id_rol,   # Forzamos rol Superadmin
            idEmpresa=None,           # Superadmin no tiene empresa
            idHorario=form.id_horario.data
        )

        db.session.add(nuevo_super)
        db.session.commit()
        flash('Nuevo Superadministrador registrado correctamente.')
        return redirect(url_for('superadmins.lista_superadmins'))

    # Pre-seleccionar rol Superadmin
    rol_super = Rol.query.filter_by(nombre_rol='Superadministrador').first()
    if request.method == 'GET' and rol_super:
        form.id_rol.data = rol_super.id_rol

    return render_template('empleado_form.html', form=form, titulo="Nuevo Superadmin")

# --- EDITAR SUPERADMIN ---
@superadmins_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_superadmin(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    usuario_actual = Trabajador.query.get(session['user_id'])
    if usuario_actual.rol.nombre_rol != 'Superadministrador':
        return redirect(url_for('main.index'))

    superadmin_edit = Trabajador.query.get_or_404(id)

    # Usamos EmpleadoEditForm (sin password required)
    form = EmpleadoEditForm(obj=superadmin_edit)
    form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]
    form.id_horario.choices = [(h.id_horario, h.nombre_horario) for h in Horario.query.all()]

    form_pass = ChangePasswordForm()

    if form.validate_on_submit():
        # Validar duplicados (excluyendo al propio usuario)
        existe_nif = Trabajador.query.filter(Trabajador.nif == form.nif.data, Trabajador.id_trabajador != id).first()
        if existe_nif:
            flash(f'Error: El NIF ya pertenece a otro usuario.')
            return render_template('empleado_form.html', form=form, form_pass=form_pass, titulo="Editar Superadmin", editando=True, empleado=superadmin_edit)

        form.populate_obj(superadmin_edit)
        superadmin_edit.idEmpresa = None # Seguridad extra

        db.session.commit()
        flash('Datos actualizados.')
        return redirect(url_for('superadmins.lista_superadmins'))

    return render_template('empleado_form.html', form=form, form_pass=form_pass, titulo="Editar Superadmin", editando=True, empleado=superadmin_edit)

# --- BORRAR SUPERADMIN ---
@superadmins_bp.route('/borrar/<int:id>')
def borrar_superadmin(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    usuario_actual = Trabajador.query.get(session['user_id'])
    if usuario_actual.rol.nombre_rol != 'Superadministrador':
        return redirect(url_for('main.index'))

    if id == session['user_id']:
        flash('Error: No puedes borrar tu propia cuenta.')
        return redirect(url_for('superadmins.lista_superadmins'))

    superadmin_borrar = Trabajador.query.get_or_404(id)
    db.session.delete(superadmin_borrar)
    db.session.commit()
    flash('Superadministrador eliminado.')

    return redirect(url_for('superadmins.lista_superadmins'))