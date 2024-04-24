import json
import socket
from add_func import first_connection
from flask import Flask
import asyncio


ip, main_server_port, web_server_port = "localhost", 9090, 9080
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
my_socket.connect((ip, int(main_server_port)))
app = Flask(__name__)
data = "42"


@app.route('/')
@app.route('/index')
async def main_page():
    data = await async_get_data()
    # return "42"
    try:
        return (f'{data["ip"]}\n'
                f'{data["port"]}\n'
                # f'{data["sprites"]}\n'
                f'{data["life_time"] / data["FPS"]}\n'
                f'{data["free_id"]}\n'
                f'{data["players"]}')
    except Exception as e:
        print(e)
        return "42"


async def async_get_data():
    await asyncio.sleep(0)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
    my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
    my_socket.connect((ip, int(main_server_port)))
    return first_connection(my_socket, "web")


app.run(host=ip, port=web_server_port)