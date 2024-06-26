from classes import Wall, Diamond, Camera, GreenSnake, Hammer, The_Observer, FirstAid
from add_func import load_image
from main import Player
import pygame
import json
import socket

main_server_port = 9090
IP = "localhost"

# настройка сокета
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
# отключение алгоритма Нейгла
main_socket.bind((IP, main_server_port))  # привязываем сокет к порту
main_socket.setblocking(0)  # отключаем внеплановое ожидание пакетов от игроков
main_socket.listen(10)  # включаем прослушку порта, выставляем ограничение на кол-во игроков

next_player_id = [0, 1, 2, 3, 4]
next_web_id = [0, 1, 2, 3, 4]
ids_to_pdelete = []
ids_to_wdelete = []
players_sockets = {}
web_sockets = {}
FPS = 50
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'diamond': load_image('diamond.png', -1),
    'player': load_image('player.png', -1),
    'enemy': load_image('player.png', -1),
    'observer': load_image('observer.png', -1)
}
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
diamonds_group = pygame.sprite.Group()
first_aid_group = pygame.sprite.Group()
FIELD1 = [
         ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", "g", ".", "#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", "#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", "#", ".", ".", ".", ".", "#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", "q.", ".", ".g", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", "#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".q", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", "#", ".", ".g", ".", ".", ".", ".", "q.", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".#", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", "#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", "q.", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".#", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "g", "#"],
         ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
         ]

FIELD = [["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", "g", ".", ".", "#", "g", ".", ".", ".", "#"],
         ["#", ".", ".", ".", "#", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", "#", "#", ".", "#"],
         ["#", ".", ".", "#", ".", "q", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", ".", ".", ".", "#", "q", ".", "#", ".", "#"],
         ["#", "#", "#", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", ".", "#", ".", ".", ".", ".", ".", ".", ".", "#"],
         ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"]]


def close_player_connection(sock):
    players_sockets[sock][1].kill()
    players_sockets[sock][0].close()
    next_player_id.append(sock)


def apply_players_moves(sock, eg, wg):
    players_sockets[sock][3] = players_sockets[sock][1].update(players_sockets[sock][3])
    data = players_sockets[sock][0].recv(256)
    data = json.loads(data.decode())
    players_sockets[sock][3] = (players_sockets[sock][1].
                                move(data['x_move'] * 50,
                                     data['y_move'] * 50,
                                     players_sockets[sock][3],
                                     eg, wg))
    if int(data['bite']) < 0:
        close_player_connection(sock)
    elif int(data['bite']) > 0:
        players_sockets[sock][1].hammer_strike(eg)


def give_answer(sock):
    if players_sockets[sock][3]:
        sprites = []
        for i in all_sprites:
            if not isinstance(i, The_Observer):
                sprites.append(i.save())
        data = {"field": sprites,
                "player_info": players_sockets[sock][2:],
                "ticks": pygame.time.get_ticks()}
        players_sockets[sock][0].send(json.dumps(data).encode())
    else:
        ids_to_pdelete.append(sock)


def generate_level(level):  # наполнение уровня
    diamonds_left = 0
    if isinstance(level[0], str):
        for y in range(len(level)):  # создание спрайтов уровня
            for x in range(len(level[y])):
                if '#' in level[y][x]:
                    Wall(all_sprites, walls_group, x, y, tile_images['wall'])
                if 'd' in level[y][x]:
                    Diamond(all_sprites, diamonds_group, x, y, tile_images['diamond'])
                    diamonds_left += 1
                if 'g' in level[y][x]:
                    GreenSnake(all_sprites, enemy_group, x, y, load_image("snakes.png"), snake_type='g')
                if 'q' in level[y][x]:
                    GreenSnake(all_sprites, enemy_group, x, y, load_image("snakes.png"), snake_type='q')
                if 'M' in level[y][x]:
                    Hammer(all_sprites, x, y, load_image('warhammer.png', -1))
                if '+' in level[y][x]:
                    FirstAid(x, y, first_aid_group, all_sprites, tile_images['firstaid'])  # Создаем спрайт аптечки
    else:
        for string_num in range(len(level)):
            for cell_num in range(len(level[string_num])):
                if '#' in level[string_num][cell_num]:
                    Wall(all_sprites, walls_group, string_num, cell_num, tile_images['wall'])
                if 'd' in level[string_num][cell_num]:
                    Diamond(all_sprites, diamonds_group, string_num, cell_num, tile_images['diamond'])
                    diamonds_left += 1
                if 'g' in level[string_num][cell_num]:
                    GreenSnake(all_sprites, enemy_group, string_num, cell_num, load_image("snakes.png"), snake_type='g')
                if 'q' in level[string_num][cell_num]:
                    GreenSnake(all_sprites, enemy_group, string_num, cell_num, load_image("snakes.png"), snake_type='q')
                if 'M' in level[string_num][cell_num]:
                    Hammer(all_sprites, string_num, cell_num, load_image('warhammer.png', -1))
                if '+' in level[string_num][cell_num]:
                    FirstAid(string_num, cell_num, first_aid_group, all_sprites, load_image('health_pack.png', -1))


def save_server_info():
    sprites = []
    players = []
    for i in all_sprites:
        if not isinstance(i, The_Observer):
            sprites.append(i.save())

    for i in players_sockets:
        players.append(players_sockets[i])

    with open("server_info.txt", mode="w+") as info:
        info.write(f'{IP}\n'
                   f'{main_server_port}\n'
                   f'{sprites}\n'
                   f'{pygame.time.get_ticks()}\n'
                   f'{FPS}\n'
                   f'{next_player_id}\n'
                   f'{players}')

        data = {"ip": IP,
                "port": main_server_port,
                # "sprites": sprites,
                "life_time": pygame.time.get_ticks(),
                "FPS": FPS,
                "free_id": next_player_id,
                "players": players}

        return data



pygame.init()
running, clock = True, pygame.time.Clock()
generate_level(FIELD)
screen = pygame.display.set_mode((550, 550))
camera = Camera()


if __name__ == "__main__":
    while running:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for i in ids_to_pdelete:
                try:
                    close_player_connection(i)
                    del players_sockets[i]
                except Exception:
                    pass
            ids_to_pdelete.clear()

            web_data = save_server_info()
            # блок проверки на наличие запросов на подключение
            try:
                new_socket, address = main_socket.accept()
                new_socket.setblocking(0)
                data = json.loads(new_socket.recv(128).decode())
                print(data)
                if data["type"] == "player":
                    # players_sockets.append(new_socket)
                    new_id = next_player_id.pop(0)
                    new_player = Player(1, 1, id=new_id)
                    players_sockets[new_id] = [new_socket, new_player, new_id, 10]  # socket, id, Class(x, y), hp
                    all_sprites.add(players_sockets[new_id][1])
                elif data["type"] == "web":
                    new_socket.send(json.dumps(web_data).encode())
                    new_socket.close()
                    print(web_data)
            except Exception as e:
                # print(e)
                pass

            for sprite in all_sprites:
                if sprite in enemy_group:
                    sprite.update(walls_group, FPS)
                else:
                    sprite.update()

            # принимаем информацию от клиентов
            for socket in players_sockets:
                try:
                    apply_players_moves(socket, enemy_group, walls_group)
                except Exception as e:
                    pass

            # отправляем ответ
            for socket in players_sockets:
                try:
                    give_answer(socket)
                except Exception as e:
                    print("can't give answer,", e)
                    ids_to_pdelete.append(socket)

            for socket in web_sockets:
                try:
                    web_sockets[socket][0].send(json.dumps(web_data).encode())
                except Exception as e:
                    print(e)

            screen.fill((0, 0, 0))
            all_sprites.draw(screen)
            enemy_group.draw(screen)
            walls_group.draw(screen)
            player_group.draw(screen)
            first_aid_group.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

        except Exception as e:
            print("ERROR!", e)
