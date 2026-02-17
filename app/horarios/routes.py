from flask import render_template, redirect, url_for, flash, session, request
from . import horarios_bp
from .forms import HorarioForm, FranjaForm
from ..models import Horario, Franjas, Dia
from .. import db

# --- LISTADO DE HORARIOS ---
@horarios_bp.route('/')
def lista_horarios():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    horarios = Horario.query.all()
    return render_template('horarios.html', horarios=horarios)

# --- CREAR NUEVO HORARIO ---
@horarios_bp.route('/nuevo', methods=['GET', 'POST'])
def crear_horario():
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    form = HorarioForm()
    if form.validate_on_submit():
        nuevo_horario = Horario(
            nombre_horario=form.nombre_horario.data,
            descripcion=form.descripcion.data
        )
        db.session.add(nuevo_horario)
        db.session.commit()
        flash('Horario creado. Ahora añade las franjas.')
        return redirect(url_for('horarios.detalle_horario', id=nuevo_horario.id_horario))

    return render_template('horario_form.html', form=form, titulo="Nuevo Horario")

# --- BORRAR HORARIO ---
@horarios_bp.route('/borrar/<int:id>')
def borrar_horario(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    horario = Horario.query.get_or_404(id)

    if len(horario.trabajadores) > 0:
        flash(f'Error: No se puede borrar "{horario.nombre_horario}" porque hay empleados asignados.')
    else:
        try:
            for franja in horario.franjas:
                db.session.delete(franja)

            db.session.delete(horario)
            db.session.commit()
            flash('Horario y sus franjas eliminados correctamente.')
        except Exception as e:
            db.session.rollback()
            flash(f'Error interno al borrar: {str(e)}')

    return redirect(url_for('horarios.lista_horarios'))

# --- DETALLE Y GESTIÓN DE FRANJAS ---
@horarios_bp.route('/<int:id>', methods=['GET', 'POST'])
def detalle_horario(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    horario = Horario.query.get_or_404(id)
    form = FranjaForm()
    # Cargamos los días dinámicamente
    form.id_dia.choices = [(d.id, d.nombre) for d in Dia.query.order_by(Dia.id).all()]

    if form.validate_on_submit():
        nuevo_inicio = form.hora_entrada.data
        nuevo_fin = form.hora_salida.data
        dia_seleccionado = form.id_dia.data

        # Validación 1: Hora lógica
        if nuevo_inicio >= nuevo_fin:
            flash('Error: La hora de salida debe ser posterior a la hora de entrada.')
        else:
            # Validación 2: Solapamiento
            franjas_existentes = Franjas.query.filter_by(id_horario=id, id_dia=dia_seleccionado).all()
            solapamiento = False
            for f in franjas_existentes:
                if (nuevo_inicio < f.hora_salida) and (nuevo_fin > f.hora_entrada):
                    solapamiento = True
                    break

            if solapamiento:
                flash('Error: La franja se solapa con otra existente.')
            else:
                nueva_franja = Franjas(
                    id_horario=id,
                    id_dia=dia_seleccionado,
                    hora_entrada=nuevo_inicio,
                    hora_salida=nuevo_fin
                )
                db.session.add(nueva_franja)
                db.session.commit()
                flash('Franja añadida correctamente.')
                return redirect(url_for('horarios.detalle_horario', id=id))

    franjas = Franjas.query.filter_by(id_horario=id).join(Dia).order_by(Dia.id, Franjas.hora_entrada).all()
    return render_template('horario_detalle.html', horario=horario, franjas=franjas, form=form)

# --- EDITAR FRANJA ---
@horarios_bp.route('/franjas/editar/<int:id>', methods=['GET', 'POST'])
def editar_franja(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    franja = Franjas.query.get_or_404(id)
    form = FranjaForm(obj=franja)
    form.submit.label.text = 'Guardar Cambios'
    form.id_dia.choices = [(d.id, d.nombre) for d in Dia.query.order_by(Dia.id).all()]

    if form.validate_on_submit():
        nuevo_inicio = form.hora_entrada.data
        nuevo_fin = form.hora_salida.data
        dia_seleccionado = form.id_dia.data

        if nuevo_inicio >= nuevo_fin:
            flash('Error: La hora de salida debe ser posterior a la de entrada.')
        else:
            franjas_existentes = Franjas.query.filter(
                Franjas.id_horario == franja.id_horario,
                Franjas.id_dia == dia_seleccionado,
                Franjas.id != id
            ).all()

            solapamiento = False
            for f in franjas_existentes:
                if (nuevo_inicio < f.hora_salida) and (nuevo_fin > f.hora_entrada):
                    solapamiento = True
                    break

            if solapamiento:
                flash('Error: La modificación provoca un solapamiento.')
            else:
                franja.id_dia = dia_seleccionado
                franja.hora_entrada = nuevo_inicio
                franja.hora_salida = nuevo_fin
                db.session.commit()
                flash('Franja modificada correctamente.')
                return redirect(url_for('horarios.detalle_horario', id=franja.id_horario))

    if request.method == 'GET':
        form.id_dia.data = franja.id_dia
        form.hora_entrada.data = franja.hora_entrada
        form.hora_salida.data = franja.hora_salida

    return render_template('franja_editar.html', form=form, franja=franja)

# --- BORRAR FRANJA ---
@horarios_bp.route('/franjas/borrar/<int:id>')
def borrar_franja(id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))

    franja = Franjas.query.get_or_404(id)
    id_horario_retorno = franja.id_horario

    db.session.delete(franja)
    db.session.commit()
    flash('Franja eliminada correctamente.')

    return redirect(url_for('horarios.detalle_horario', id=id_horario_retorno))