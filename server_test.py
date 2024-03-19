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
FPS = 100
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'diamond': load_image('diamond.png', -1),
    'player': load_image('player.png', -1),
    'enemy': load_image('player.png', -1)
}
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
diamonds_group = pygame.sprite.Group()
FIELD = [
         ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", "g", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
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
    players_sockets[sock][4] = (players_sockets[sock][4] + data["y_move"] * 50) % len(FIELD)
    players_sockets[sock][3] = (players_sockets[sock][3] + data["x_move"] * 50) % len(FIELD[0])
    if data["bite"] < 0:
        close_player_connection(sock)


def give_answer(sock):
    sprites = []
    for i in all_sprites:
        sprites.append([i.save()])
    data = {"field": sprites,
            "player_info": players_sockets[sock][1:]}
    # data = [field, players_sockets[sock][1:]]
    players_sockets[sock][0].send(json.dumps(data).encode())


def generate_level(level):  # наполнение уровня
    global diamonds_left
    player_x = 0
    player_y = 0
    diamonds_left = 0
    if isinstance(level[0], str):
        for y in range(len(level)):  # создание спрайтов уровня
            for x in range(len(level[y])):
                if '.' in level[y][x]:
                    Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                if '#' in level[y][x]:
                    Wall(all_sprites, tiles_group, walls_group, x, y, tile_images['wall'])
                if '@' in level[y][x]:
                    Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    player_x, player_y = x, y
                if 'd' in level[y][x]:
                    Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    Diamond(all_sprites, diamonds_group, x, y, tile_images['diamond'])
                    diamonds_left += 1
                if 'g' in level[y][x]:
                    Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    GreenSnake(all_sprites, enemy_group, x, y, load_image("snakes.png"), snake_type='g')
                if 'q' in level[y][x]:
                    Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    GreenSnake(all_sprites, enemy_group, x, y, load_image("snakes.png"), snake_type='q')
                if 'M' in level[y][x]:
                    Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    Hammer(all_sprites, tiles_group, x, y,
                           load_image('warhammer.png', -1))
    else:
        for string_num in range(len(level)):
            for cell_num in range(len(level[string_num])):
                if '.' in level[string_num][cell_num]:
                    Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                if '#' in level[string_num][cell_num]:
                    Wall(all_sprites, tiles_group, walls_group, string_num, cell_num, tile_images['wall'])
                if 'd' in level[string_num][cell_num]:
                    Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    Diamond(all_sprites, diamonds_group, string_num, cell_num, tile_images['diamond'])
                    diamonds_left += 1
                if 'g' in level[string_num][cell_num]:
                    Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    GreenSnake(all_sprites, enemy_group, string_num, cell_num, load_image("snakes.png"), snake_type='g')
                if 'q' in level[string_num][cell_num]:
                    Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    GreenSnake(all_sprites, enemy_group, string_num, cell_num, load_image("snakes.png"), snake_type='q')
                if 'M' in level[string_num][cell_num]:
                    Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    Hammer(all_sprites, tiles_group, string_num, cell_num,
                           load_image('warhammer.png', -1))
    # вернем игрока, а также размер поля в клетках
    new_player = Player(player_x, player_y)  # создание игрока
    return new_player


pygame.init()
running, clock = True, pygame.time.Clock()
generate_level(FIELD)

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
            new_id = next_id.pop(0)
            Player(50, 50)
            players_sockets[new_id] = [new_socket, new_id, 10]  # socket, id, Class(x, y), hp
        except Exception as e:
            pass

        for sprite in all_sprites:
            if sprite in enemy_group:
                sprite.update(walls_group)
            elif sprite in player_group:
                sprite.update(0)
            else:
                sprite.update()

        # принимаем информацию от клиентов
        for socket in players_sockets:
            try:
                apply_players_moves(socket)
            except Exception as e:
                pass

        # отправляем ответ
        for socket in players_sockets:
            try:
                give_answer(socket)
            except Exception as e:
                print("can't give answer,", e)
                try:
                    close_player_connection(socket)
                except Exception:
                    pass

        clock.tick(0.1)