from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.employees'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user)
        flash('Вы успешно вошли в систему', 'success')
        return redirect(url_for('main.employees'))
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.employees'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role='viewer')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрированы. Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)