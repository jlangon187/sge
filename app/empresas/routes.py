from flask import render_template, redirect, url_for, flash, session, request
from datetime import datetime, date, timedelta
from . import empresas_bp
from .forms import EmpresaForm
from ..models import Empresa, Trabajador, Registro, Incidencia, Rol
from .. import db

@empresas_bp.route('/mi-empresa', methods=['GET', 'POST'])
def gestion_empresa():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empresa_id = session.get('empresa_id')
    if not empresa_id: return redirect(url_for('main.index'))

    empresa = Empresa.query.get_or_404(empresa_id)
    form = EmpresaForm(obj=empresa)

    if form.validate_on_submit():
        form.populate_obj(empresa)
        db.session.commit()
        session['empresa_nombre'] = empresa.nombrecomercial
        flash('Datos de la empresa actualizados.')
        return redirect(url_for('empresas.gestion_empresa'))

    return render_template('empresa.html', form=form, empresa=empresa)

@empresas_bp.route('/listado')
def lista_empresas():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    empresas = Empresa.query.all()
    return render_template('empresas_list.html', empresas=empresas)

@empresas_bp.route('/nueva', methods=['GET', 'POST'])
def crear_empresa_admin():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    form = EmpresaForm()
    if form.validate_on_submit():
        nueva_empresa = Empresa()
        form.populate_obj(nueva_empresa)
        db.session.add(nueva_empresa)
        db.session.commit()
        flash('Empresa creada correctamente.')
        return redirect(url_for('empresas.lista_empresas'))

    return render_template('empresa_form_admin.html', form=form)

@empresas_bp.route('/seleccionar/<int:id>')
def seleccionar_empresa(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    empresa = Empresa.query.get_or_404(id)
    session['empresa_id'] = empresa.id_empresa
    session['empresa_nombre'] = empresa.nombrecomercial
    flash(f'Gestionando ahora: {empresa.nombrecomercial}')
    return redirect(url_for('empresas.gestion_empresa'))

@empresas_bp.route('/borrar/<int:id>')
def borrar_empresa_admin(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    if session.get('user_role') != 'Superadministrador':
        return redirect(url_for('main.index'))

    empresa = Empresa.query.get_or_404(id)
    if empresa.trabajadores:
        flash('No se puede borrar una empresa con empleados.')
    else:
        db.session.delete(empresa)
        db.session.commit()
        flash('Empresa eliminada.')

    return redirect(url_for('empresas.lista_empresas'))

@empresas_bp.route('/incidencias')
def ver_incidencias():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empresa_id = session.get('empresa_id')
    if not empresa_id: return redirect(url_for('main.index'))

    empleado_id = request.args.get('empleado', type=int)
    fecha_filtro = request.args.get('fecha')

    query = Incidencia.query.join(Trabajador).filter(Trabajador.idEmpresa == empresa_id)

    if empleado_id:
        query = query.filter(Incidencia.id_trabajador == empleado_id)

    if fecha_filtro:
        fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
        query = query.filter(db.func.date(Incidencia.fecha_hora) == fecha_obj)

    incidencias = query.order_by(Incidencia.fecha_hora.desc()).all()
    empleados = Trabajador.query.filter_by(idEmpresa=empresa_id).all()

    return render_template('incidencias_list.html', incidencias=incidencias, empleados=empleados, sel_empleado=empleado_id, sel_fecha=fecha_filtro)


@empresas_bp.route('/registros')
def ver_registros():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    empresa_id = session.get('empresa_id')
    if not empresa_id: return redirect(url_for('main.index'))

    # Filtros
    empleado_id = request.args.get('empleado', type=int)
    fecha_desde = request.args.get('desde')
    fecha_hasta = request.args.get('hasta')

    # Consulta Base
    query = Registro.query.join(Trabajador).filter(Trabajador.idEmpresa == empresa_id)

    if empleado_id:
        query = query.filter(Registro.id_trabajador == empleado_id)
    if fecha_desde:
        query = query.filter(Registro.fecha >= datetime.strptime(fecha_desde, '%Y-%m-%d').date())
    if fecha_hasta:
        query = query.filter(Registro.fecha <= datetime.strptime(fecha_hasta, '%Y-%m-%d').date())

    registros_db = query.order_by(Registro.hora_entrada.desc()).all()

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

        balance = 0
        if reg.hora_salida:
            balance = horas_reales - horas_teoricas

        registros_procesados.append({
            'registro': reg,
            'reales': horas_reales,
            'teoricas': horas_teoricas,
            'balance': balance
        })

        total_horas_trabajadas += horas_reales
        if balance > 0:
            total_horas_extra += balance

    empleados = Trabajador.query.filter_by(idEmpresa=empresa_id).all()

    return render_template('registros_list.html',
                           registros=registros_procesados,
                           empleados=empleados,
                           sel_empleado=empleado_id,
                           sel_desde=fecha_desde,
                           sel_hasta=fecha_hasta,
                           total_trabajadas=total_horas_trabajadas,
                           total_extra=total_horas_extra)