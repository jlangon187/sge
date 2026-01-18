from flask import render_template, redirect, url_for, flash, session, request
from . import empresas_bp
from .forms import EmpresaForm
from ..models import Empresa
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