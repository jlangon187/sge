from flask import render_template, session, redirect, url_for
from . import main_bp
from ..models import Trabajador, Empresa, Rol, Horario

@main_bp.route('/')
def index():

    if 'user_id' not in session:
        return render_template('index.html', logged_in=False)

    usuario = Trabajador.query.get(session['user_id'])

    # --- LÓGICA PARA SUPERADMINISTRADOR ---
    if session.get('user_role') == 'Superadministrador':
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
            return render_template('index.html', logged_in=True, es_super=False, empresa=None, stats=None, usuario=usuario)

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