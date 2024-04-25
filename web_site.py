import json
import socket
from flask import Flask, render_template, redirect  # , Markup
import asyncio
from classes import LoginForm
from add_func import first_connection

ip, main_server_port, web_server_port = "localhost", 9090, 9080
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
my_socket.connect((ip, int(main_server_port)))
app = Flask(__name__)
data = "42"
extra_data = "42"
app.config['SECRET_KEY'] = 'secret_key'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdPoMYpAAAAAFc4nKB8BPwQ24j1y66prsP35aBp'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdPoMYpAAAAAC9epaQXHvREW2kXWlnsAdQW8ONN'


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


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('login2.html', title='Авторизация', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def logout():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('login2.html', title='Регистрация', form=form)


@app.route('/captcha')
async def captcha():
    try:
        return render_template('captcha.html')
    except Exception as e:
        return extra_data


app.run(host=ip, port=web_server_port)