# -*- coding: utf-8 -*-
# импорты необходимых библиотек и функций
import os
import sys
from datetime import datetime

import pygame

from db_class import DBClass, load_level, load_image, resource_path

# создание констант и глобальных переменных
FPS = 50
diamonds_left = 0
SCREEN_SIZE = WIDTH, HEIGHT = 550, 550
player_hp = 10
screen = pygame.display.set_mode(SCREEN_SIZE)
log_file = open("logs.txt", mode="w+")
log_file.write(f"[{str(datetime.now())[11:16]}]: level imported successful\n")
tile_images = {
               'wall': load_image('box.png'),
               'empty': load_image('grass.png'),
               'diamond': load_image('diamond.png', -1)
               }
player_image = load_image('player.png', -1)
tile_width = tile_height = 50


def load_sound(name):  # функция для подгрузки музыки
    fullname = resource_path(os.path.join('data/sounds', name))
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        terminate(f"Файл с музыкой '{fullname}' не найден")
    pygame.mixer.music.load(fullname)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)


def start_screen(scr, width, height):  # функция для включения стартскрина
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Управление стрелками или WASD",
                  "удар молотом на пробел",
                  "q для быстрого сохранения",
                  "e для быстрой загрузки"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    scr.blit(fon, (0, 0))
    font = pygame.font.Font(None, 47)
    text_coord = 50
    clock = pygame.time.Clock()
    for line in intro_text:  # построчная печать текста
        string_rendered = font.render(line, 1, pygame.Color("#BD0D9E"))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        scr.blit(string_rendered, intro_rect)

    while True:  # ожидание нажатия для окончания стартскрина
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(15)  # ограничение частоты обновления экрана для снижения потребляемых ресурсов


def level_choose_screen(scr, corr=True):  # функция для включения стартскрина
    screen.fill((0, 0, 0))
    intro_text = [f"ВВОД:",
                  f"Выберите уровень:",
                  f"Для ввода нажимайте",
                  f"клавиши цифр",
                  f"Для подтверждения",
                  f"нажмите ENTER"]
    font = pygame.font.Font(None, 47)
    text_coord = 50
    ret_num = ""
    clock = pygame.time.Clock()
    for line in intro_text:  # построчная печать текста
        string_rendered = font.render(line, 1, pygame.Color("#BD0D9E"))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        scr.blit(string_rendered, intro_rect)
    print(intro_text)
    while True:  # ожидание нажатия для окончания стартскрина
        # screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return int(ret_num)
                elif event.key == pygame.K_0:
                    ret_num = ret_num + "0"
                elif event.key == pygame.K_1:
                    ret_num = ret_num + "1"
                elif event.key == pygame.K_2:
                    ret_num = ret_num + "2"
                elif event.key == pygame.K_3:
                    ret_num = ret_num + "3"
                elif event.key == pygame.K_4:
                    ret_num = ret_num + "4"
                elif event.key == pygame.K_5:
                    ret_num = ret_num + "5"
                elif event.key == pygame.K_6:
                    ret_num = ret_num + "6"
                elif event.key == pygame.K_7:
                    ret_num = ret_num + "7"
                elif event.key == pygame.K_8:
                    ret_num = ret_num + "8"
                elif event.key == pygame.K_9:
                    ret_num = ret_num + "9"
                elif event.key == pygame.K_BACKSPACE:
                    ret_num = ret_num[:-1]
        scr.fill("black")
        if corr:
            intro_text = [f"ВВОД: {ret_num}",
                          f"Выберите уровень:",
                          f"Для ввода нажимайте",
                          f"клавиши цифр",
                          f"Для подтверждения",
                          f"нажмите ENTER"]
        else:
            intro_text = [f"ВВОД: {ret_num}",
                          f"Выберите уровень:",
                          f"Для ввода нажимайте",
                          f"клавиши цифр",
                          f"Для подтверждения",
                          f"нажмите ENTER",
                          f"некорректный номер уровня"]
        text_coord = 50
        print(ret_num)
        for line in intro_text:  # построчная печать текста
            string_rendered = font.render(line, 1, pygame.Color("#BD0D9E"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            scr.blit(string_rendered, intro_rect)
        print(intro_text)
        # pygame.time.wait(1000)
        pygame.display.flip()
        clock.tick(15)  # ограничение частоты обновления экрана для снижения потребляемых ресурсов


def ttg_level_num(screen, isst):
    try:
        # mode = str(input("Enter game mode(t/q): "))
        player, level_x, level_y = generate_level(load_level(f"level{level_choose_screen(screen, isst)}.txt"))
        db = DBClass('saves.db')
        return db, player, level_x, level_y
    except Exception as e:
        log_file.write(f"[{str(datetime.now())[11:16]}]: program have error '{e}'\n")
        return ttg_level_num(False)


def generate_level(level):  # наполнение уровня
    global diamonds_left
    px = 0
    py = 0
    diamonds_left = 0
    new_player, x, y = None, None, None
    for y in range(len(level)):  # создание спрайтов уровня
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Empty('empty', x, y)
            elif level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '@':
                Empty('empty', x, y)
                px, py = x, y
            elif level[y][x] == 'd':
                Empty('empty', x, y)
                Diamond(x, y)
                diamonds_left += 1
            elif level[y][x] == 'g':
                Empty('empty', x, y)
                GreenSnake(x, y, snake_type='g')
            elif level[y][x] == 'q':
                Empty('empty', x, y)
                GreenSnake(x, y, snake_type='q')
    # вернем игрока, а также размер поля в клетках
    new_player = Player(px, py)  # создание игрока
    return new_player, x, y


def terminate(text=""):  # экстренный выход из программы
    pygame.quit()
    sys.exit(text)


# создание групп спрайтов для более удобного обращения со спрайтами
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
diamonds_group = pygame.sprite.Group()


class GreenSnake(pygame.sprite.Sprite):
    def __init__(self, x, y, dirx=1, diry=0, stun=0, snake_type=None):
        super().__init__(all_sprites, enemy_group)
        self.frames = []
        sheet = load_image('snakes.png', -1)
        self.cut_sheet(sheet)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_width, y * tile_height)
        self.direction_x = dirx
        self.direction_y = diry
        # Убираем случайное изменение направления
        if snake_type:
            if snake_type == 'q':
                self.direction_x = 0  # Направление по горизонтали для 'q'
                self.direction_y = 1  # Направление вверх для 'q'
            else:
                self.direction_x = 1  # Направление вправо для 'g'
                self.direction_y = 0  # Направление по вертикали для 'g'

        self.update_load = 0
        self.stun = stun

    def cut_sheet(self, sheet, columns=9, rows=12):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, self.direction_x, self.direction_y, self.stun, 1

    def move(self):
        m = self.direction_x * tile_width
        n = self.direction_y * tile_height
        self.rect = self.rect.move(m, n)
        if pygame.sprite.spritecollide(self, walls_group, False):
            self.rect = self.rect.move(-2 * m, -2 * n)
            self.direction_x = -self.direction_x
            self.direction_y = -self.direction_y

    def update(self):
        self.update_load += 1
        if self.update_load % 30 == 0:
            self.move()
            if self.direction_x == 1:
                self.cur_frame = (self.cur_frame - 1) % 8  # движение вправо (колонки с 9 по 2)
            elif self.direction_x == -1:
                self.cur_frame = (self.cur_frame + 1) % 8  # движение влево (колонки с 9 по 2)
            self.image = self.frames[self.cur_frame]
            if self.direction_x == 1:  # отражаем по горизонтали, если нужно
                self.image = pygame.transform.flip(self.image, True, False)


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.add(walls_group)

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, None, 1


class Diamond(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, diamonds_group)
        self.image = tile_images['diamond']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, None, 1


class Empty(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, None, 1


class PlayerHP(pygame.sprite.Sprite):
    def __init__(self, sheet=load_image('hp.png', -1), columns=11, rows=1):
        super().__init__(all_sprites, player_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(0, 0)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = 10 - player_hp
        self.image = self.frames[self.cur_frame]
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, stun=0, loading=FPS * 2):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.last_moves = [(0, 0)]
        self.score = 0
        self.stun = stun
        self.loading = loading

    def move(self, m, n):
        global player_hp
        global diamonds_left
        if player_hp > 0 and self.stun < FPS * 0.5 and self.loading == 0:
            self.rect = self.rect.move(m, n)
            self.last_moves.append((m, n))
            if pygame.sprite.spritecollideany(self, enemy_group) and self.stun <= 0:
                if m or n:
                    self.rect = self.rect.move(-m, -n)
                    player_hp -= 1
                    self.stun = FPS * 1
                    log_file.write(f"[{str(datetime.now())[11:16]}]: player has damaged\n")
                else:
                    self.rect = self.rect.move(self.last_moves[-1])
                    self.last_moves.remove(self.last_moves[-1])
                    player_hp -= 1
                    self.stun = FPS * 1
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

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, self.stun, 1

    def extra_move(self, m):
        self.rect = self.rect.move(m, m)

    def death(self):
        global player_hp
        player_hp = 0

    def update(self):
        global player_hp
        if pygame.sprite.spritecollideany(self, enemy_group) and self.stun <= 0:
            self.rect = self.rect.move(-self.last_moves[-1][0], -self.last_moves[-1][1])
            self.last_moves.remove(self.last_moves[-1])
            player_hp -= 1
            self.stun = FPS * 1
            log_file.write(f"[{str(datetime.now())[11:16]}]: player has damaged\n")
        if player_hp < 0:
            player_hp = 0
        if not self.last_moves:
            self.last_moves = [(0, 0)]
        if self.stun > 0 and self.loading == 0:
            self.stun -= 1
        if self.loading > 0:
            self.loading -= 1


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = -3
        self.dy = -3

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

        if -1 > obj.rect.x:
            obj.rect.x += WIDTH
        elif obj.rect.x > WIDTH - 1:
            obj.rect.x -= WIDTH
        if -1 > obj.rect.y:
            obj.rect.y += HEIGHT
        elif obj.rect.y > HEIGHT - 1:
            obj.rect.y -= HEIGHT

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


pygame.init()
start_screen(screen, WIDTH, HEIGHT)  # Стартскрин для выбора уровня и предсказуемого начала игры.
# Локальные объекты и функции, которые больше нигде не понадобятся.
s = pygame.mixer.Sound(os.path.join('data/sounds', "game_over.mp3"))
clock = pygame.time.Clock()
pygame.display.set_caption("DMPV")
pygame.display.set_icon(load_image("player.png", -1))
hp = PlayerHP(load_image('hp.png', -1), 11, 1)
font1, font2 = pygame.font.Font(None, 20), pygame.font.Font(None, 50)
death_switch, running = True, True
# Выбор, загрузка уровня и безопасный выход в случае ошибки
# (в будущем будет добавлено автоотправление письма-фидбека о баге)
log_file.write(f"[{str(datetime.now())[11:16]}]: game start\n")
db, player, level_x, level_y = ttg_level_num(screen, True)
camera = Camera()
# Главный Цикл
time_delta = pygame.time.get_ticks()
load_sound("background.mp3")
log_file.write(f"[{str(datetime.now())[11:16]}]: level imported successful\n")
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.move(50, 0)
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.move(-50, 0)
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                player.move(0, -50)
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.move(0, 50)
            if event.key == pygame.K_ESCAPE:
                start_screen(screen, WIDTH, HEIGHT)
            if event.key == pygame.K_q:
                db.clear_db()
                for sprite in all_sprites:
                    if not isinstance(sprite, Camera) and not isinstance(sprite, PlayerHP):
                        db.save_game_sprite(sprite.save())
                db.save_game_vars(player_hp, player.score)
            if event.key == pygame.K_e:
                try:
                    for sprite in all_sprites:
                        sprite.kill()
                    # pygame.quit()
                    # pygame.init()
                    # screen = pygame.display.set_mode(SCREEN_SIZE)
                    data = db.get_sprites_info()
                    px = 0
                    py = 0
                    stun = 0
                    diamonds_left = 0
                    for information in data:
                        if information[0] == "Empty":
                            Empty('empty', information[1] / 50, information[2] / 50)
                        elif information[0] == "Wall":
                            Wall('wall', information[1] / 50, information[2] / 50)
                        elif information[0] == "Player":
                            px, py, stun = information[1], information[2], information[5]
                            if stun > FPS * 2:
                                stun = FPS * 2
                        elif information[0] == "Diamond":
                            Diamond(information[1] / 50, information[2] / 50)
                            diamonds_left += 1
                        elif information[0] == "GreenSnake":
                            GreenSnake(information[1] / 50, information[2] / 50,
                                       information[3], information[4], information[5])
                    player = Player(px, py, stun, 2*FPS)
                    data = db.get_vars_info()
                    for information in data:
                        if information[0] == "player_hp":
                            player_hp = information[1]
                        if information[0] == "score":
                            score = information[1]
                    log_file.write(f"[{str(datetime.now())[11:16]}]: game loaded from save file\n")
                    camera = Camera()
                    hp = PlayerHP()
                    player.score = score
                    player.extra_move(-150)
                except Exception as e:
                    print(e)
                    terminate()
    # Отрисовка всех спрайтов и надписей в нужном для корректного отображения порядке
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    enemy_group.draw(screen)
    walls_group.draw(screen)
    player_group.draw(screen)
    if diamonds_left != 0:
        screen.blit(font1.render(f"TIME {(pygame.time.get_ticks() - time_delta) / 1000}",
                                 1, pygame.Color('red')), (0, 25, 100, 10))
    else:
        screen.blit(font1.render(f"TIME {time_delta}",
                                 1, pygame.Color('red')), (0, 25, 100, 10))
        screen.blit(font2.render("YOU WIN!", 1,
                                 pygame.Color('red')), (WIDTH // 2 - 100, HEIGHT // 2 - 100, 100, 100))
    if player_hp == 0 and diamonds_left != 0:
        screen.blit(font2.render("Game Over", 1,
                                 pygame.Color('red')), (WIDTH // 2 - 100, HEIGHT // 2 - 100, 100, 100))
        if death_switch:
            pygame.mixer.music.stop()
            s.play()
            death_switch = False
            log_file.write(f"[{str(datetime.now())[11:16]}]: game over, player is dead\n")
    pygame.display.flip()
    clock.tick(FPS)
    # Обновление всех спрайтов
    all_sprites.update()
    camera.update(player)
    for sprite in all_sprites:
        if not isinstance(sprite, PlayerHP):
            camera.apply(sprite)
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
