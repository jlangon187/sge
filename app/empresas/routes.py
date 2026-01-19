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

# 5. SELECCIONAR EMPRESA
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

    empleado_id = request.args.get('empleado', type=int)
    fecha_desde = request.args.get('desde')
    fecha_hasta = request.args.get('hasta')

    query = Registro.query.join(Trabajador).filter(Trabajador.idEmpresa == empresa_id)

    if empleado_id:
        query = query.filter(Registro.id_trabajador == empleado_id)

    if fecha_desde:
        query = query.filter(Registro.fecha >= datetime.strptime(fecha_desde, '%Y-%m-%d').date())

    if fecha_hasta:
        query = query.filter(Registro.fecha <= datetime.strptime(fecha_hasta, '%Y-%m-%d').date())

    registros_db = query.order_by(Registro.hora_entrada.desc()).all()

    # --- PROCESAMIENTO DE HORAS EXTRA ---
    registros_procesados = []
    total_horas_trabajadas = 0
    total_horas_extra = 0

    for reg in registros_db:
        horas_reales = 0
        if reg.hora_salida:
            diferencia = reg.hora_salida - reg.hora_entrada
            horas_reales = diferencia.total_seconds() / 3600

        horas_teoricas = 0
        if reg.trabajador.horario:
            dia_semana_id = reg.fecha.weekday() + 1

            franjas_dia = [f for f in reg.trabajador.horario.franjas if f.id_dia == dia_semana_id]

            for f in franjas_dia:
                inicio = datetime.combine(date.min, f.hora_entrada)
                fin = datetime.combine(date.min, f.hora_salida)
                duracion_franja = (fin - inicio).total_seconds() / 3600
                horas_teoricas += duracion_franja

        horas_extra = 0
        if horas_reales > horas_teoricas and horas_teoricas > 0:
            horas_extra = horas_reales - horas_teoricas

        registros_procesados.append({
            'registro': reg,
            'reales': horas_reales,
            'teoricas': horas_teoricas,
            'extra': horas_extra
        })

        total_horas_trabajadas += horas_reales
        total_horas_extra += horas_extra

    empleados = Trabajador.query.filter_by(idEmpresa=empresa_id).all()

    return render_template('registros_list.html',
                           registros=registros_procesados,
                           empleados=empleados,
                           sel_empleado=empleado_id,
                           sel_desde=fecha_desde,
                           sel_hasta=fecha_hasta,
                           total_trabajadas=total_horas_trabajadas,
                           total_extra=total_horas_extra)

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