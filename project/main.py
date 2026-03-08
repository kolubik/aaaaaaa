from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
from flask_login import login_required, current_user
from app import db
from app.models import Employee, DutyType, Assignment
from app.forms import EmployeeForm, DutyTypeForm, AssignmentForm, ReportForm
from functools import wraps
import csv
from io import StringIO
from datetime import datetime

bp = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('У вас нет прав доступа к этой странице.', 'danger')
            return redirect(url_for('main.employees'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
def index():
    return redirect(url_for('main.employees'))

# ==================== Сотрудники ====================
@bp.route('/employees')
@login_required
def employees():
    employees = Employee.query.order_by(Employee.name).all()
    return render_template('employees.html', employees=employees)

@bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(name=form.name.data, position=form.position.data)
        db.session.add(employee)
        db.session.commit()
        flash('Сотрудник добавлен', 'success')
        return redirect(url_for('main.employees'))
    return render_template('employee_form.html', form=form, title='Добавить сотрудника')

@bp.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)
    if form.validate_on_submit():
        employee.name = form.name.data
        employee.position = form.position.data
        db.session.commit()
        flash('Сотрудник обновлён', 'success')
        return redirect(url_for('main.employees'))
    return render_template('employee_form.html', form=form, title='Редактировать сотрудника')

@bp.route('/employees/delete/<int:id>')
@login_required
@admin_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    if employee.assignments.count() > 0:
        flash('Нельзя удалить сотрудника, у которого есть назначения', 'danger')
        return redirect(url_for('main.employees'))
    db.session.delete(employee)
    db.session.commit()
    flash('Сотрудник удалён', 'success')
    return redirect(url_for('main.employees'))

# ==================== Виды нарядов ====================
@bp.route('/dutytypes')
@login_required
def dutytypes():
    dutytypes = DutyType.query.order_by(DutyType.name).all()
    return render_template('dutytypes.html', dutytypes=dutytypes)

@bp.route('/dutytypes/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_dutytype():
    form = DutyTypeForm()
    if form.validate_on_submit():
        dutytype = DutyType(name=form.name.data, coefficient=form.coefficient.data)
        db.session.add(dutytype)
        db.session.commit()
        flash('Вид наряда добавлен', 'success')
        return redirect(url_for('main.dutytypes'))
    return render_template('dutytype_form.html', form=form, title='Добавить вид наряда')

@bp.route('/dutytypes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_dutytype(id):
    dutytype = DutyType.query.get_or_404(id)
    form = DutyTypeForm(obj=dutytype)
    if form.validate_on_submit():
        dutytype.name = form.name.data
        dutytype.coefficient = form.coefficient.data
        db.session.commit()
        flash('Вид наряда обновлён', 'success')
        return redirect(url_for('main.dutytypes'))
    return render_template('dutytype_form.html', form=form, title='Редактировать вид наряда')

@bp.route('/dutytypes/delete/<int:id>')
@login_required
@admin_required
def delete_dutytype(id):
    dutytype = DutyType.query.get_or_404(id)
    if dutytype.assignments.count() > 0:
        flash('Нельзя удалить вид наряда, который используется в назначениях', 'danger')
        return redirect(url_for('main.dutytypes'))
    db.session.delete(dutytype)
    db.session.commit()
    flash('Вид наряда удалён', 'success')
    return redirect(url_for('main.dutytypes'))

# ==================== Журнал назначений ====================
@bp.route('/assignments')
@login_required
def assignments():
    assignments = Assignment.query.order_by(Assignment.date.desc()).all()
    return render_template('assignments.html', assignments=assignments)

@bp.route('/assignments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_assignment():
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            employee_id=form.employee_id.data,
            duty_type_id=form.duty_type_id.data,
            date=form.date.data,
            quantity=form.quantity.data,
            notes=form.notes.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Назначение добавлено', 'success')
        return redirect(url_for('main.assignments'))
    return render_template('assignment_form.html', form=form, title='Добавить назначение')

@bp.route('/assignments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    form = AssignmentForm(obj=assignment)
    if form.validate_on_submit():
        assignment.employee_id = form.employee_id.data
        assignment.duty_type_id = form.duty_type_id.data
        assignment.date = form.date.data
        assignment.quantity = form.quantity.data
        assignment.notes = form.notes.data
        db.session.commit()
        flash('Назначение обновлено', 'success')
        return redirect(url_for('main.assignments'))
    return render_template('assignment_form.html', form=form, title='Редактировать назначение')

@bp.route('/assignments/delete/<int:id>')
@login_required
@admin_required
def delete_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    db.session.delete(assignment)
    db.session.commit()
    flash('Назначение удалено', 'success')
    return redirect(url_for('main.assignments'))

# ==================== Отчёт ====================
@bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    report_data = None
    employees = None
    dutytypes = None
    start_date = None
    end_date = None
    emp_totals = {}
    duty_totals = {}

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        employees = Employee.query.order_by(Employee.name).all()
        dutytypes = DutyType.query.order_by(DutyType.name).all()

        assignments = Assignment.query.filter(
            Assignment.date >= start_date,
            Assignment.date <= end_date
        ).all()

        data = {}
        for a in assignments:
            key = (a.employee_id, a.duty_type_id)
            value = a.quantity * a.duty_type.coefficient
            data[key] = data.get(key, 0) + value

        report_data = data

        for (emp_id, duty_id), val in data.items():
            emp_totals[emp_id] = emp_totals.get(emp_id, 0) + val
            duty_totals[duty_id] = duty_totals.get(duty_id, 0) + val

    return render_template('report.html', form=form, report_data=report_data,
                           employees=employees, dutytypes=dutytypes,
                           start_date=start_date, end_date=end_date,
                           emp_totals=emp_totals, duty_totals=duty_totals)

@bp.route('/export_csv')
@login_required
@admin_required
def export_csv():
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    if not start or not end:
        flash('Не указан период', 'danger')
        return redirect(url_for('main.report'))

    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    except:
        flash('Неверный формат даты', 'danger')
        return redirect(url_for('main.report'))

    employees = Employee.query.order_by(Employee.name).all()
    dutytypes = DutyType.query.order_by(DutyType.name).all()
    assignments = Assignment.query.filter(
        Assignment.date >= start_date,
        Assignment.date <= end_date
    ).all()

    data = {}
    for a in assignments:
        key = (a.employee_id, a.duty_type_id)
        value = a.quantity * a.duty_type.coefficient
        data[key] = data.get(key, 0) + value

    si = StringIO()
    cw = csv.writer(si)
    header = ['Сотрудник / Вид наряда'] + [d.name for d in dutytypes] + ['Всего']
    cw.writerow(header)

    emp_totals = {}
    for emp in employees:
        row = [emp.name]
        emp_total = 0
        for dt in dutytypes:
            val = data.get((emp.id, dt.id), 0)
            row.append(val)
            emp_total += val
        row.append(emp_total)
        cw.writerow(row)
        emp_totals[emp.id] = emp_total

    footer = ['Всего']
    for dt in dutytypes:
        total = sum(data.get((emp.id, dt.id), 0) for emp in employees)
        footer.append(total)
    footer.append(sum(emp_totals.values()))
    cw.writerow(footer)

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-disposition': f'attachment; filename=report_{start}_{end}.csv'}
    )