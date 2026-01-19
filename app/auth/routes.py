from flask import render_template, redirect, url_for, flash, session, request
from . import auth_bp
from .forms import LoginForm
from ..models import Trabajador

# --- LOGIN ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if 'user_id' in session:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        usuario = Trabajador.query.filter_by(email=form.email.data).first()

        if usuario and usuario.check_password(form.password.data):

            if usuario.rol.nombre_rol == 'Superadministrador':
                session['user_id'] = usuario.id_trabajador
                session['user_name'] = usuario.nombre
                session['user_role'] = 'Superadministrador'
                session['empresa_id'] = None
                session['empresa_nombre'] = "Zona Superadmin"

                flash(f'Bienvenido Superadmin {usuario.nombre}')
                return redirect(url_for('main.index'))

            elif usuario.rol.nombre_rol == 'Administrador':
                if not usuario.idEmpresa:
                    flash('Error: Tu usuario no tiene una empresa asignada. Contacta con soporte.')
                    return render_template('login.html', form=form)

                session['user_id'] = usuario.id_trabajador
                session['user_name'] = usuario.nombre
                session['user_role'] = usuario.rol.nombre_rol
                session['empresa_id'] = usuario.idEmpresa
                session['empresa_nombre'] = usuario.empresa.nombrecomercial if usuario.empresa else "Empresa Desconocida"

                return redirect(url_for('main.index'))

            else:
                flash('Acceso denegado: Tu rol no tiene permisos para acceder al panel.')
                return render_template('login.html', form=form)

        else:
            flash('Email o contraseña incorrectos.')

    return render_template('login.html', form=form)

# --- LOGOUT ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.')
    return redirect(url_for('main.index'))