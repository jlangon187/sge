from flask import render_template, redirect, url_for, flash, session, request
from . import empresas_bp
from .forms import EmpresaForm
from datetime import datetime, date, timedelta
from ..models import Registro, Incidencia, Trabajador, Empresa
from .. import db

# 1. GESTIÓN DE MI EMPRESA (Admin) - Ruta: /empresas/mi-empresa
@empresas_bp.route('/mi-empresa', methods=['GET', 'POST'])
def gestion_empresa():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empresa_id = session.get('empresa_id')
    if not empresa_id:
        flash('Atención: No hay ninguna empresa seleccionada.')
        if session.get('user_role') == 'Superadministrador':
            return redirect(url_for('empresas.lista_empresas'))
        return redirect(url_for('auth.login'))

    empresa = Empresa.query.get_or_404(empresa_id)
    form = EmpresaForm(obj=empresa)

    if form.validate_on_submit():
        form.populate_obj(empresa)
        db.session.commit()
        session['empresa_nombre'] = empresa.nombrecomercial
        flash('Datos de la empresa actualizados.')
        return redirect(url_for('main.index'))

    return render_template('empresa.html', form=form)

# 2. LISTADO GLOBAL (Superadmin) - Ruta: /empresas/listado
@empresas_bp.route('/listado')
def lista_empresas():
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))
    empresas = Empresa.query.all()
    return render_template('empresas_list.html', empresas=empresas)

# 3. CREAR EMPRESA (Superadmin) - Ruta: /empresas/nueva
@empresas_bp.route('/nueva', methods=['GET', 'POST'])
def crear_empresa_admin():
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    form = EmpresaForm()
    if form.validate_on_submit():
        # Crear instancia usando los datos del formulario
        nueva_empresa = Empresa()
        form.populate_obj(nueva_empresa) # Magia de WTForms

        db.session.add(nueva_empresa)
        db.session.commit()
        flash('Nueva empresa registrada.')
        return redirect(url_for('empresas.lista_empresas'))

    return render_template('empresa_form_admin.html', form=form)

# 4. BORRAR EMPRESA - Ruta: /empresas/borrar/<id>
@empresas_bp.route('/borrar/<int:id>')
def borrar_empresa_admin(id):
    if session.get('user_role') != 'Superadministrador': return redirect(url_for('main.index'))

    empresa = Empresa.query.get_or_404(id)
    if len(empresa.empleados) > 0:
        flash(f'Error: La empresa "{empresa.nombrecomercial}" tiene empleados.')
    else:
        db.session.delete(empresa)
        db.session.commit()
        flash('Empresa eliminada.')
    return redirect(url_for('empresas.lista_empresas'))

# 5. SELECCIONAR EMPRESA (Context Switch)
@empresas_bp.route('/seleccionar/<int:id>')
def seleccionar_empresa(id):
    if session.get('user_role') != 'Superadministrador': return redirect(url_for('auth.login'))

    empresa = Empresa.query.get_or_404(id)
    session['empresa_id'] = empresa.id_empresa
    session['empresa_nombre'] = empresa.nombrecomercial
    flash(f'Gestionando: {empresa.nombrecomercial}')
    return redirect(url_for('empresas.gestion_empresa'))

# --- LISTADO DE REGISTROS ---
@empresas_bp.route('/registros')
def ver_registros():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empresa_id = session.get('empresa_id')
    if not empresa_id: return redirect(url_for('main.index'))

    # Filtros desde la URL (GET)
    empleado_id = request.args.get('empleado', type=int)
    fecha_desde = request.args.get('desde')
    fecha_hasta = request.args.get('hasta')

    # Consulta Base
    query = Registro.query.join(Trabajador).filter(Trabajador.idEmpresa == empresa_id)

    # Aplicar filtros si existen
    if empleado_id:
        query = query.filter(Registro.id_trabajador == empleado_id)

    if fecha_desde:
        query = query.filter(Registro.fecha >= datetime.strptime(fecha_desde, '%Y-%m-%d').date())

    if fecha_hasta:
        query = query.filter(Registro.fecha <= datetime.strptime(fecha_hasta, '%Y-%m-%d').date())

    # Ordenar por fecha descendente (lo más nuevo primero)
    registros = query.order_by(Registro.hora_entrada.desc()).all()

    # Para el desplegable del filtro
    empleados = Trabajador.query.filter_by(idEmpresa=empresa_id).all()

    return render_template('registros_list.html',
                           registros=registros,
                           empleados=empleados,
                           sel_empleado=empleado_id,
                           sel_desde=fecha_desde,
                           sel_hasta=fecha_hasta)

# --- LISTADO DE INCIDENCIAS ---
@empresas_bp.route('/incidencias')
def ver_incidencias():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empresa_id = session.get('empresa_id')
    if not empresa_id: return redirect(url_for('main.index'))

    # Filtros
    empleado_id = request.args.get('empleado', type=int)
    fecha_filtro = request.args.get('fecha')

    query = Incidencia.query.join(Trabajador).filter(Trabajador.idEmpresa == empresa_id)

    if empleado_id:
        query = query.filter(Incidencia.id_trabajador == empleado_id)

    if fecha_filtro:
        # Filtrar por día exacto
        fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
        # Truco para filtrar DATETIME por DATE:
        query = query.filter(db.func.date(Incidencia.fecha_hora) == fecha_obj)

    incidencias = query.order_by(Incidencia.fecha_hora.desc()).all()
    empleados = Trabajador.query.filter_by(idEmpresa=empresa_id).all()

    return render_template('incidencias_list.html',
                           incidencias=incidencias,
                           empleados=empleados,
                           sel_empleado=empleado_id,
                           sel_fecha=fecha_filtro)