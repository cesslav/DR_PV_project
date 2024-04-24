import json
import socket
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm, recaptcha
import asyncio
from wtforms import *
from wtforms.validators import *

ip, main_server_port, web_server_port = "localhost", 9090, 9080
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
my_socket.connect((ip, int(main_server_port)))
app = Flask(__name__)
data = "42"
extra_data = "42"
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    fourty_legzka = PasswordField('Количество ножек сороканожки, пробегающей под ближней к '
                                  'двери ножкой кровати в данный момент', validators=[DataRequired()])
    email = EmailField('Адрес электронной почты', validators=[DataRequired()])
    life_essay = TextAreaField("Краткое эссе-изложение о Вашей жизни",
                               validators=[DataRequired(), Length(min=10000, message="Попробуйте передать ваши мысли более развёрнуто", )])
    maya_date = DateField("Дата ближайшего конца света по календарю Майя", format='%d-%m-%Y', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    phone_num = PasswordField('Номер телефона', validators=[DataRequired()])
    sins = StringField('Количество грехов, отягчающих Вашу душу', validators=[DataRequired()])
    sell_my_soul = BooleanField('Продать душу владыке моему, Сатане', validators=[DataRequired()])
    submit = SubmitField('Выйти')


def first_connection(socket, type="player"):
    try:
        socket.send(json.dumps({"type": type}).encode())
        data = json.loads(socket.recv(3072).decode())
        return data
    except Exception as e:
        print(e)
        return first_connection(socket)


@app.route('/')
@app.route('/index')
async def main_page_for_tests_and_stuff():
    data = await async_get_data()
    try:
        return f"""<!doctype html>
                     <html lang="en">
                       <body>
                         <h1>IP:{str(data["ip"])}</h1>
                         <h1>PORT:{str(data["port"])}<h1>
                         <h1>life_time:{str(data["life_time"] / data["FPS"])}<h1>
                         <h1>Free space:{data["free_id"]}<h1>
                         <h1>List of players:{str(data["players"])}<h1>
                       </body>
                     </html>"""
    except Exception as e:
        return extra_data


@app.route('/just_buttons')
async def just_buttons():
    try:
        return render_template('buttons.html')
    except Exception as e:
        return extra_data


async def async_get_data():
    await asyncio.sleep(0)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
    my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
    my_socket.connect((ip, int(main_server_port)))
    return first_connection(my_socket, "web")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('login.html', title='Авторизация', form=form)


app.run(host=ip, port=web_server_port)