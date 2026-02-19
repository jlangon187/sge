from flask import render_template, redirect, url_for, flash, session, request
from flask_jwt_extended import decode_token
from jwt.exceptions import ExpiredSignatureError, DecodeError
from . import auth_bp
from .forms import LoginForm, ResetPasswordForm
from ..models import Trabajador, db

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


# --- RESET PASSWORD ---
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_web(token):
    try:
        # Intentamos decodificarlo. Si ha caducado o es falso, saltará una excepción.
        decoded_token = decode_token(token)
        user_id = decoded_token['sub'] # 'sub' es la identidad (ID del trabajador)
    except ExpiredSignatureError:
        flash('El enlace ha caducado. Por favor, solicita uno nuevo desde la App.')
        return redirect(url_for('auth.login')) # O redirigir a una página de error
    except (DecodeError, Exception):
        flash('Enlace inválido.')
        return redirect(url_for('auth.login'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        # 3. Si el usuario envía la nueva contraseña
        usuario = Trabajador.query.get(user_id)
        if usuario:
            usuario.set_password(form.password.data)
            db.session.commit()
            flash('¡Contraseña actualizada! Ya puedes iniciar sesión en la App.')
            return render_template('reset_success.html') # Crearemos esta página simple
        else:
            flash('Usuario no encontrado.')

    return render_template('reset_password.html', form=form)