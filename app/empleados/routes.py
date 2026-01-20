from flask import render_template, redirect, url_for, flash, session, request
from . import empleados_bp
from .forms import EmpleadoForm, EmpleadoEditForm, ChangePasswordForm
from ..models import Trabajador, Empresa, Rol, Horario
from .. import db

@empleados_bp.route('/')
def lista_empleados():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empresa_id = session.get('empresa_id')
    if not empresa_id:
        flash('No tienes una empresa asignada.')
        return redirect(url_for('main.index'))

    empleados = Trabajador.query.filter_by(idEmpresa=empresa_id).all()
    return render_template('empleados.html', empleados=empleados)

@empleados_bp.route('/nuevo', methods=['GET', 'POST'])
def crear_empleado():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empresa_id = session.get('empresa_id')
    if not empresa_id: return redirect(url_for('main.index'))

    form = EmpleadoForm()

    # Cargar opciones en los select
    form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]
    form.id_horario.choices = [(h.id_horario, h.nombre_horario) for h in Horario.query.all()]

    if form.validate_on_submit():
        if Trabajador.query.filter_by(nif=form.nif.data).first():
            flash(f'Error: El NIF {form.nif.data} ya existe.')
        elif Trabajador.query.filter_by(email=form.email.data).first():
            flash(f'Error: El Email {form.email.data} ya existe.')
        else:
            nuevo_empleado = Trabajador(
                nif=form.nif.data,
                nombre=form.nombre.data,
                apellidos=form.apellidos.data,
                email=form.email.data,
                telef=form.telef.data,
                calle=form.calle.data,
                localidad=form.localidad.data,
                cp=form.cp.data,
                provincia=form.provincia.data,
                idEmpresa=empresa_id,
                # ASIGNACIÓN MANUAL OBLIGATORIA
                idRol=form.id_rol.data,
                idHorario=form.id_horario.data
            )
            # Hash password
            nuevo_empleado.set_password(form.passw.data)

            db.session.add(nuevo_empleado)
            db.session.commit()
            flash('Empleado creado correctamente.')
            return redirect(url_for('empleados.lista_empleados'))

    return render_template('empleado_form.html', form=form, titulo="Nuevo Empleado")

@empleados_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_empleado(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empleado = Trabajador.query.get_or_404(id)
    if empleado.idEmpresa != session.get('empresa_id'):
        flash('Acceso no autorizado.')
        return redirect(url_for('empleados.lista_empleados'))

    form = EmpleadoEditForm(obj=empleado)
    form.id_rol.choices = [(r.id_rol, r.nombre_rol) for r in Rol.query.all()]
    form.id_horario.choices = [(h.id_horario, h.nombre_horario) for h in Horario.query.all()]

    form_pass = ChangePasswordForm()

    if request.method == 'GET':
        form.id_rol.data = empleado.idRol
        form.id_horario.data = empleado.idHorario

    if form.validate_on_submit():
        existe = Trabajador.query.filter(Trabajador.nif == form.nif.data, Trabajador.id_trabajador != id).first()
        if existe:
            flash('Error: NIF duplicado.')
        else:
            form.populate_obj(empleado)

            empleado.idRol = form.id_rol.data
            empleado.idHorario = form.id_horario.data

            db.session.commit()
            flash('Datos actualizados.')
            return redirect(url_for('empleados.lista_empleados'))

    return render_template('empleado_form.html', form=form, form_pass=form_pass, titulo="Editar Empleado", editando=True, empleado=empleado)

@empleados_bp.route('/cambiar-password/<int:id>', methods=['POST'])
def cambiar_password_empleado(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empleado = Trabajador.query.get_or_404(id)
    if empleado.idEmpresa != session.get('empresa_id') and session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    form = ChangePasswordForm()
    if form.validate_on_submit():
        empleado.set_password(form.password.data)
        db.session.commit()
        flash(f'Contraseña de {empleado.nombre} actualizada correctamente.')
    else:
        flash('Error al cambiar la contraseña. Mínimo 4 caracteres.')

    if session.get('user_role') == 'Superadministrador' and empleado.rol.nombre_rol == 'Superadministrador':
         return redirect(url_for('superadmins.editar_superadmin', id=id))

    return redirect(url_for('empleados.editar_empleado', id=id))

@empleados_bp.route('/borrar/<int:id>')
def borrar_empleado(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empleado = Trabajador.query.get_or_404(id)
    if empleado.idEmpresa != session.get('empresa_id'):
        flash('No autorizado.')
        return redirect(url_for('empleados.lista_empleados'))

    db.session.delete(empleado)
    db.session.commit()
    flash('Empleado eliminado.')
    return redirect(url_for('empleados.lista_empleados'))