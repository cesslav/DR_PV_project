from classes import DBClass, Empty, Wall, Diamond, Camera, PlayerHP, GreenSnake, Hammer
from add_func import terminate, level_choose_screen, load_level, load_image, load_sound, start_screen
from main import Player
from datetime import datetime
import pygame
import json
import socket
import time
IP = "localhost"
port = 9090

# настройка сокета
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
# отключение алгоритма Нейгла
main_socket.bind((IP, port))  # привязываем сокет к порту
main_socket.setblocking(0)  # отключаем внеплановое ожидание пакетов от игроков
main_socket.listen(4)  # включаем прослушку порта, выставляем ограничение на кол-во игроков

next_id = [0, 1, 2, 3]
players_sockets = {}
FIELD = [
         ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
         ]


def close_player_connection(sock):
    players_sockets[sock][0].close()
    next_id.append(sock)
    players_sockets[sock] = ''


def apply_players_moves(sock):
    data = players_sockets[sock][0].recv(1024)
    data = json.loads(data.decode())
    players_sockets[sock][4] = (players_sockets[sock][4] + data["y_move"]) % len(FIELD)
    players_sockets[sock][3] = (players_sockets[sock][3] + data["x_move"]) % len(FIELD[0])
    if data["bite"] < 0:
        close_player_connection(sock)


def give_answer(sock, field_to_answer):
    data = {"field": field_to_answer,
            "player_info": players_sockets[sock][1:]}
    # data = [field, players_sockets[sock][1:]]
    # print(json.dumps(data))
    players_sockets[sock][0].send(json.dumps(data).encode())


if __name__ == "__main__":
    while True:
        for i in list(players_sockets):
            if not players_sockets[i]:
                del players_sockets[i]
        # блок проверки на наличие запросов на подключение
        try:
            new_socket, address = main_socket.accept()
            print("подключился", address)
            new_socket.setblocking(0)
            # players_sockets.append(new_socket)
            players_sockets[next_id.pop(0)] = [new_socket, 10, 0, 50, 50, True]  # socket, hp, stun, x, y, IsAlive
        except Exception as e:
            pass

        # принимаем информацию от клиентов
        for socket in players_sockets:
            try:
                apply_players_moves(socket)
            except Exception as e:
                pass

        # отправляем ответ
        for socket in players_sockets:
            try:
                give_answer(socket, FIELD)
            except Exception as e:
                print("can't give answer,", e)
                try:
                    close_player_connection(socket)
                except Exception:
                    pass

        time.sleep(0.01)