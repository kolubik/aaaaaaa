from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print('Администратор уже существует.')
    else:
        username = input('Введите имя администратора: ')
        password = input('Введите пароль: ')
        user = User(username=username, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print('Администратор создан.')