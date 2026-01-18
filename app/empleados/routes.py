from flask import render_template, redirect, url_for, flash, session, request
from . import empleados_bp
from .forms import EmpleadoForm, EmpleadoEditForm, ChangePasswordForm
from ..models import Trabajador, Rol, Horario
from .. import db

# --- LISTADO DE EMPLEADOS ---
@empleados_bp.route('/empleados')
def lista_empleados():
    if 'user_id' not in session: return redirect(url_for('login'))
    empresa_id_activa = session.get('empresa_id')
    empleados = Trabajador.query.filter_by(idEmpresa=empresa_id_activa).all()

    return render_template('empleados.html', empleados=empleados)

# --- CREAR EMPLEADO ---
@empleados_bp.route('/empleados/nuevo', methods=['GET', 'POST'])
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
@empleados_bp.route('/empleados/editar/<int:id>', methods=['GET', 'POST'])
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
@empleados_bp.route('/empleados/cambiar-password/<int:id>', methods=['POST'])
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
@empleados_bp.route('/empleados/borrar/<int:id>')
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