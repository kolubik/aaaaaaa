from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user
from app import db
from app.models import User
from main import admin_required

bp = Blueprint('admin', __name__)

@bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/make_admin/<int:id>')
@login_required
@admin_required
def make_admin(id):
    user = User.query.get_or_404(id)
    if user.role == 'admin':
        flash('Пользователь уже администратор', 'info')
    else:
        user.role = 'admin'
        db.session.commit()
        flash(f'Пользователь {user.username} теперь администратор', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/users/remove_admin/<int:id>')
@login_required
@admin_required
def remove_admin(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Вы не можете снять админские права с самого себя', 'danger')
        return redirect(url_for('admin.users'))
    if user.role == 'viewer':
        flash('Пользователь не является администратором', 'info')
    else:
        user.role = 'viewer'
        db.session.commit()
        flash(f'У пользователя {user.username} отозваны права администратора', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/users/delete/<int:id>')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Вы не можете удалить самого себя', 'danger')
        return redirect(url_for('admin.users'))
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Нельзя удалить последнего администратора', 'danger')
            return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'Пользователь {user.username} удалён', 'success')
    return redirect(url_for('admin.users'))