from flask import render_template, redirect, url_for, flash, session, request
from . import roles_bp
from .forms import RolForm
from ..models import Rol
from .. import db

@roles_bp.route('/')
def lista_roles():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    roles = Rol.query.all()
    return render_template('roles.html', roles=roles)

@roles_bp.route('/nuevo', methods=['GET', 'POST'])
def crear_rol():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
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
            return redirect(url_for('roles.lista_roles'))
    return render_template('rol_form.html', form=form, titulo="Nuevo Rol")

@roles_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_rol(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
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
            return redirect(url_for('roles.lista_roles'))
    if request.method == 'GET':
        form.nombre_rol.data = rol.nombre_rol
    return render_template('rol_form.html', form=form, titulo="Editar Rol")

@roles_bp.route('/borrar/<int:id>')
def borrar_rol(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    rol = Rol.query.get_or_404(id)
    if len(rol.trabajadores) > 0:
        flash(f'Error: No se puede eliminar el rol "{rol.nombre_rol}" porque tiene empleados asignados.')
    else:
        db.session.delete(rol)
        db.session.commit()
        flash('Rol eliminado correctamente.')
    return redirect(url_for('roles.lista_roles'))