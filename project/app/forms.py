from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, FloatField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional
from app.models import User, Employee, DutyType

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Это имя уже занято.')

class EmployeeForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    position = StringField('Должность', validators=[Optional()])
    submit = SubmitField('Сохранить')

class DutyTypeForm(FlaskForm):
    name = StringField('Название наряда', validators=[DataRequired()])
    coefficient = FloatField('Коэффициент', validators=[DataRequired()], default=1.0)
    submit = SubmitField('Сохранить')

class AssignmentForm(FlaskForm):
    employee_id = SelectField('Сотрудник', coerce=int, validators=[DataRequired()])
    duty_type_id = SelectField('Вид наряда', coerce=int, validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()], format='%Y-%m-%d')
    quantity = FloatField('Количество', validators=[DataRequired()], default=1.0)
    notes = TextAreaField('Примечание', validators=[Optional()])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        self.employee_id.choices = [(e.id, e.name) for e in Employee.query.order_by(Employee.name).all()]
        self.duty_type_id.choices = [(d.id, d.name) for d in DutyType.query.order_by(DutyType.name).all()]

class ReportForm(FlaskForm):
    start_date = DateField('Начальная дата', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('Конечная дата', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Сформировать отчёт')