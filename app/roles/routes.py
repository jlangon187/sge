from flask import render_template, redirect, url_for, flash, session, request
from . import roles_bp
from .forms import RolForm
from ..models import Rol
from .. import db

@roles_bp.route('/')
def lista_roles():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    roles = Rol.query.all()
    return render_template('roles.html', roles=roles)

@roles_bp.route('/nuevo', methods=['GET', 'POST'])
def crear_rol():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    form = RolForm()
    if form.validate_on_submit():
        if Rol.query.filter_by(nombre_rol=form.nombre.data).first():
            flash(f'El rol {form.nombre.data} ya existe.')
        else:
            nuevo_rol = Rol(nombre_rol=form.nombre.data)
            db.session.add(nuevo_rol)
            db.session.commit()
            flash('Rol creado correctamente.')
            return redirect(url_for('roles.lista_roles'))

    return render_template('rol_form.html', form=form, titulo="Nuevo Rol")

@roles_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_rol(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    rol = Rol.query.get_or_404(id)
    form = RolForm(obj=rol) # Carga el nombre actual

    # Truco: WTForms espera 'nombre', el modelo tiene 'nombre_rol'.
    # Lo asignamos manualmente si es GET para verlo en el input
    if request.method == 'GET':
        form.nombre.data = rol.nombre_rol

    if form.validate_on_submit():
        rol.nombre_rol = form.nombre.data
        db.session.commit()
        flash('Rol actualizado.')
        return redirect(url_for('roles.lista_roles'))

    return render_template('rol_form.html', form=form, titulo="Editar Rol")

@roles_bp.route('/borrar/<int:id>')
def borrar_rol(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    rol = Rol.query.get_or_404(id)

    roles_protegidos = ['Superadministrador', 'Administrador', 'Trabajador']
    if rol.nombre_rol in roles_protegidos:
        flash(f'Error: No se puede eliminar el rol protegido "{rol.nombre_rol}".')
        return redirect(url_for('roles.lista_roles'))

    if rol.trabajadores:
        flash('No se puede borrar un rol que tiene empleados asignados.')
    else:
        db.session.delete(rol)
        db.session.commit()
        flash('Rol eliminado.')

    return redirect(url_for('roles.lista_roles'))