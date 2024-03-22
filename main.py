# импорты необходимых библиотек и функций
import json
import os
from classes import DBClass, Wall, Diamond, Camera, PlayerHP, GreenSnake, Hammer
from add_func import terminate, level_choose_screen, load_level, load_image, load_sound, start_screen, first_connection
from datetime import datetime
import pygame
import socket

ip = 0
port = 0
pygame.init()
online = False
FPS = 140
diamonds_left = 0
SCREEN_SIZE = WIDTH, HEIGHT = 550, 550
player_hp = 10
my_id, all_ids = "0", ["0", "1", "2", "3"]
screen = pygame.display.set_mode(SCREEN_SIZE)
log_file = open("logs.txt", mode="w+")
log_file.write(f"[{str(datetime.now())[11:16]}]: level imported successful\n")
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'diamond': load_image('diamond.png', -1),
    'player': load_image('player.png', -1),
    'enemy': load_image('player.png', -1)
}
tile_width = tile_height = 50
moves = {'x_move': 0,
         'y_move': 0,
         'bite': 0}
# создание групп спрайтов для более удобного обращения со спрайтами
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
diamonds_group = pygame.sprite.Group()


def load_game(data, health=None):
    global player_hp, hp, camera, diamonds_left
    try:
        for sprite in all_sprites:
            sprite.kill()
        # print(data)
        # data = db.get_sprites_info()
        px = 0
        py = 0
        stun = 0
        diamonds_left = 0
        for information in data:
            if information[0] == "Empty":
                pass
                # Empty(all_sprites, tiles_group, information[1] / 50,
                #       information[2] / 50, tile_images['empty'])
            elif information[0] == "Wall":
                Wall(all_sprites, tiles_group, walls_group, information[1] / 50,
                     information[2] / 50, tile_images['wall'])
            elif information[0] == "Player":
                px, py, stun = information[1], information[2], information[5]
                if stun > FPS * 2:
                    stun = FPS * 2
            elif information[0] == "Diamond":
                Diamond(all_sprites, diamonds_group, information[1] / 50,
                        information[2] / 50, tile_images['diamond'])
                diamonds_left += 1
            elif information[0] == "GreenSnake":
                GreenSnake(all_sprites, enemy_group, information[1] / 50, information[2] / 50,
                           load_image("snakes.png"), dirx=information[3], diry=information[4],
                           stun=information[5])
        player = Player(px, py, stun)
        if not online:
            data = db.get_vars_info()
            score = 0
            for information in data:
                if information[0] == "player_hp":
                    player_hp = information[1]
                if information[0] == "score":
                    score = information[1]
        else:
            player_hp = health
            score = 0
        log_file.write(f"[{str(datetime.now())[11:16]}]: game loaded from save file\n")
        camera = Camera()
        hp = PlayerHP(all_sprites, player_group, load_image("hp.png", -1))
        player.score = score
        player.extra_move(-150)
        return player
    except Exception as e:
        print(e)
        log_file.write(f"[{str(datetime.now())[11:16]}]: program have error '{e}'\n")
        terminate()


def ttg_level_num(scr, isst):
    global online, ip, port
    try:
        # mode = str(input("Enter game mode(t/q): "))
        txt = level_choose_screen(scr, isst)
        if not ("." in txt and ":" in txt):
            txt = f"level{txt}.txt"
            pl = generate_level(load_level(txt))
        else:
            ip, port = txt.split(":")
            if ip:
                port = int(port)
                ip = "localhost"
            pl = Player(0, 0)
            online = True
        bd = DBClass('saves.db')
        return bd, pl
    except Exception as f:
        log_file.write(f"[{str(datetime.now())[11:16]}]: program have error '{f}'\n")
        return ttg_level_num(scr, False)


def generate_level(level):  # наполнение уровня
    global diamonds_left
    player_x = 0
    player_y = 0
    diamonds_left = 0
    if isinstance(level[0], str):
        for y in range(len(level)):  # создание спрайтов уровня
            for x in range(len(level[y])):
                if '.' in level[y][x]:
                    pass
                    # Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                if '#' in level[y][x]:
                    Wall(all_sprites, tiles_group, walls_group, x, y, tile_images['wall'])
                if '@' in level[y][x]:
                    # Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    player_x, player_y = x, y
                if 'd' in level[y][x]:
                    # Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    Diamond(all_sprites, diamonds_group, x, y, tile_images['diamond'])
                    diamonds_left += 1
                if 'g' in level[y][x]:
                    # Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    GreenSnake(all_sprites, enemy_group, x, y, load_image("snakes.png"), snake_type='g')
                if 'q' in level[y][x]:
                    # Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    GreenSnake(all_sprites, enemy_group, x, y, load_image("snakes.png"), snake_type='q')
                if 'M' in level[y][x]:
                    #Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                    Hammer(all_sprites, tiles_group, x, y,
                           load_image('warhammer.png', -1))
    else:
        for string_num in range(len(level)):
            for cell_num in range(len(level[string_num])):
                if '.' in level[string_num][cell_num]:
                    # Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    pass
                if '#' in level[string_num][cell_num]:
                    Wall(all_sprites, tiles_group, walls_group, string_num, cell_num, tile_images['wall'])
                if my_id in level[string_num][cell_num]:
                    # Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    player_x, player_y = string_num, cell_num
                if all_ids | set(level[string_num][cell_num]):
                    Player(string_num, cell_num)
                if 'd' in level[string_num][cell_num]:
                    # Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    Diamond(all_sprites, diamonds_group, string_num, cell_num, tile_images['diamond'])
                    diamonds_left += 1
                if 'g' in level[string_num][cell_num]:
                    # Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    GreenSnake(all_sprites, enemy_group, string_num, cell_num, load_image("snakes.png"), snake_type='g')
                if 'q' in level[string_num][cell_num]:
                    # Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    GreenSnake(all_sprites, enemy_group, string_num, cell_num, load_image("snakes.png"), snake_type='q')
                if 'M' in level[string_num][cell_num]:
                    # Empty(all_sprites, tiles_group, string_num, cell_num, tile_images['empty'])
                    Hammer(all_sprites, tiles_group, string_num, cell_num,
                           load_image('warhammer.png', -1))
    # вернем игрока, а также размер поля в клетках
    # создание игрока
    return Player(player_x, player_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, stun=0):
        super().__init__(player_group, all_sprites)
        self.image = tile_images["player"]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.last_moves = [(0, 0)]
        self.score = 0
        self.stun = stun
        self.hammer_timer = 0
        self.hammer_duration = 1000  # В миллисекундах, здесь 1000 мс = 1 секунда

    def hammer_strike(self):
        # Проверяем, активен ли таймер молотков
        if self.hammer_timer == 0:
            # Если таймер не активен, создаем молоток
            # Создание молотка на 1 клетку перед игроком в направлении его последнего движения
            hammer_x = self.rect.x + self.last_moves[-1][0]
            hammer_y = self.rect.y + self.last_moves[-1][1]
            hammer = Hammer(all_sprites, tiles_group, hammer_x // tile_width, hammer_y // tile_height,
                            load_image('warhammer.png', -1))
            # Применяем эффект оглушения к змеям вокруг молотка
            for snake in pygame.sprite.spritecollide(hammer, enemy_group, False):
                snake.apply_stun(2)  # Применение эффекта оглушения на 2 секунды
            # Применяем эффект оглушения к самому игроку
            self.apply_stun(1)
            # Активируем таймер
            self.hammer_timer = pygame.time.get_ticks()

    def move(self, m, n, hp, enemy_group=enemy_group, walls_group=walls_group, diamonds_group=diamonds_group):
        global diamonds_left
        if hp > 0 and self.stun <= 0:
            # Проверка на наличие стана
            if self.stun <= 0:
                self.rect = self.rect.move(m, n)
                self.last_moves.append((m, n))
                if pygame.sprite.spritecollideany(self, enemy_group) and self.stun <= 0:
                    if m or n:
                        self.rect = self.rect.move(-m, -n)
                        hp -= 2
                        self.stun = FPS * 0.75
                        log_file.write(f"[{str(datetime.now())[11:16]}]: player has damaged\n")
                    else:
                        self.rect = self.rect.move(self.last_moves[-1])
                        self.last_moves.remove(self.last_moves[-1])
                        hp -= 2
                        self.stun = FPS * 0.75
                        log_file.write(f"[{str(datetime.now())[11:16]}]: player has damaged\n")
                if pygame.sprite.spritecollideany(self, walls_group):
                    if m or n:
                        self.rect = self.rect.move(-m, -n)
                    else:
                        self.rect = self.rect.move(self.last_moves[-1])
                        self.last_moves.remove(self.last_moves[-1])
                if pygame.sprite.spritecollide(self, diamonds_group, True):
                    self.score += 1
                    diamonds_left -= 1
                    log_file.write(f"[{str(datetime.now())[11:16]}]: player picked diamond\n")
        return hp

    def apply_stun(self, duration):
        self.stun = duration * 50  # Преобразуем секунды в кадры

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, self.stun, 1

    def extra_move(self, m):
        self.rect = self.rect.move(m, m)

    def death(self):
        global player_hp
        player_hp = 0
        return self.score

    def update(self, ph=0):
        global player_hp
        if pygame.sprite.spritecollideany(self, enemy_group) and self.stun <= 0:
            self.rect = self.rect.move(-self.last_moves[-1][0], -self.last_moves[-1][1])
            self.last_moves.remove(self.last_moves[-1])
            player_hp -= 2
            self.stun = FPS * 0.75
            log_file.write(f"[{str(datetime.now())[11:16]}]: player has damaged\n")
        if player_hp < 0:
            player_hp = 0
        if not self.last_moves:
            self.last_moves = [(0, 0)]
        if self.stun > 0:
            self.stun -= 1
        if self.hammer_timer > 0:
            # Если таймер активен, проверяем прошло ли 1 секунда
            current_time = pygame.time.get_ticks()
            if current_time - self.hammer_timer >= self.hammer_duration:
                # Если прошло, убираем молотки
                for sprite in all_sprites.copy():
                    if isinstance(sprite, Hammer):
                        sprite.kill()
                # Сбрасываем таймер
                self.hammer_timer = 0
            else:
                # Если таймер активен и молотки присутствуют, игрок не может двигаться
                return


if __name__ == "__main__":
    pygame.init()
    start_screen(screen, WIDTH, HEIGHT)  # Стартскрин для выбора уровня и предсказуемого начала игры.
    # Локальные объекты и функции, которые больше нигде не понадобятся.
    pygame.display.set_caption("DRPV")
    pygame.display.set_icon(load_image("ico.ico", -1))
    hp = PlayerHP(all_sprites, player_group, load_image('hp.png', -1))
    font1, font2 = pygame.font.Font(None, 20), pygame.font.Font(None, 50)
    death_switch, running, s = True, True, pygame.mixer.Sound(os.path.join('data/sounds', "game_over.mp3"))
    # Выбор, загрузка уровня и безопасный выход в случае ошибки
    # (в будущем будет добавлено автоотправление письма-фидбека о баге)
    log_file.write(f"[{str(datetime.now())[11:16]}]: game start\n")
    db, player = ttg_level_num(screen, True)
    camera, clock = Camera(), pygame.time.Clock()
    # Главный Цикл
    time_delta = pygame.time.get_ticks()
    # load_sound("background.mp3")
    log_file.write(f"[{str(datetime.now())[11:16]}]: level imported successful\n")
    if not online:
        background_image = pygame.transform.scale(load_image('grass_background.jpg'), (WIDTH, HEIGHT))
    else:
        background_image = pygame.transform.scale(load_image('grass_background_online.jpg'), (WIDTH, HEIGHT))

    if online:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # делаем переменную, ссылающуюся на сокет сервера
        my_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # отключаем создание крупных пакетов
        # отключение алгоритма Нейгла
        my_socket.connect((ip, port))
        my_id = first_connection(my_socket)
        all_ids.remove(my_id)
        all_ids = set(all_ids)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and player_hp > 0 and diamonds_left > 0 and not online:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.move(50, 0)
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.move(-50, 0)
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    player.move(0, -50)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    player.move(0, 50)
                if event.key == pygame.K_SPACE:
                    player.hammer_strike()
                if event.key == pygame.K_ESCAPE:
                    start_screen(screen, WIDTH, HEIGHT)
                if event.key == pygame.K_q:
                    db.clear_db()
                    for sprite in all_sprites:
                        if not isinstance(sprite, Camera) and not isinstance(sprite, PlayerHP):
                            db.save_game_sprite(sprite.save())
                    db.save_game_vars(player_hp, player.score)
                if event.key == pygame.K_e:
                    load_game(db.get_sprites_info())
            elif event.type == pygame.KEYUP and online:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    moves['x_move'] = moves['x_move'] + 1
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    moves['x_move'] = moves['x_move'] - 1
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    moves['y_move'] = moves['y_move'] - 1
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    moves['y_move'] = moves['y_move'] + 1
                if event.key == pygame.K_SPACE:
                    moves['bite'] = moves['bite'] + 1
                if event.key == pygame.K_ESCAPE:
                    moves['bite'] = moves['bite'] - 100
        # Отрисовка всех спрайтов и надписей в нужном для корректного отображения порядке
        if online:
            try:
                data = my_socket.recv(8192)
                data = data.decode()
                if data:
                    data = json.loads(data)
                    player = load_game(data["field"], data["player_info"][1])
                    player_group.add(player)
            except Exception as e:
                pass

        for sprite in all_sprites:
            if not isinstance(sprite, PlayerHP):
                camera.apply(sprite, online)
        camera.update(player)
        screen.blit(background_image, (0, 0))
        all_sprites.draw(screen)
        enemy_group.draw(screen)
        walls_group.draw(screen)
        player_group.draw(screen)

        if diamonds_left != 0 and not online:
            screen.blit(font1.render(f"TIME {(pygame.time.get_ticks() - time_delta) / 1000}",
                                     True, pygame.Color('red')), (0, 25, 100, 10))
        elif diamonds_left == 0 and not online:
            screen.blit(font1.render(f"TIME {time_delta}",
                                     True, pygame.Color('red')), (0, 25, 100, 10))
            screen.blit(font2.render("YOU WIN!", True,
                                     pygame.Color('red')), (WIDTH // 2 - 100, HEIGHT // 2 - 100, 100, 100))
        if (player_hp == 0 and diamonds_left != 0 and not online) or (player_hp == 0 and online):
            screen.blit(font2.render("Game Over", True,
                                     pygame.Color('red')), (WIDTH // 2 - 100, HEIGHT // 2 - 100, 100, 100))
            if death_switch:
                pygame.mixer.music.stop()
                s.play()
                death_switch = False
                log_file.write(f"[{str(datetime.now())[11:16]}]: game over, player is dead\n")
        pygame.display.flip()
        clock.tick(FPS)
        # Обновление всех спрайтов
        if not online:
            for sprite in all_sprites:
                if sprite in enemy_group:
                    sprite.update(walls_group)
                elif sprite in player_group:
                    sprite.update(player_hp)
                else:
                    sprite.update()
        else:
            my_socket.send(json.dumps(moves).encode())
            moves = {'x_move': 0,
                     'y_move': 0,
                     'bite': 0}
        if diamonds_left == 0:
            player.death()
            if death_switch:
                db.add_to_leaderboard((pygame.time.get_ticks() - time_delta) / 1000, player.score)
                log_file.write(f"[{str(datetime.now())[11:16]}]: game over, player is win\n")
                log_file.write(f"[{str(datetime.now())[11:16]}]: game end "
                               f"with time {(pygame.time.get_ticks() - time_delta) / 1000}\n")
                death_switch = False
                time_delta = (pygame.time.get_ticks() - time_delta) / 1000
    # корректный выход из программы при завершении цикла
    pygame.quit()
