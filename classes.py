# Импорт необходимых библиотек
import os
import sys

import pygame


# Создание вспомогательных функций
def load_image(name, colorkey=None):  # функция для подгрузки изображений
    fullname = os.path.join('data/images', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen(scr, width, height):  # функция для включения стартскрина
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Управление стрелками или WASD",
                  "удар молотом на пробел"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    scr.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    clock = pygame.time.Clock()
    for line in intro_text:  # построчная печать текста
        string_rendered = font.render(line, 1, pygame.Color('black'))
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
        clock.tick(24)  # ограничение частоты обновления экрана для снижения потребляемых ресурсов


def load_level(filename):  # функция для предварительной обработки уровня
    filename = "data/levels/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):  # наполнение уровня
    px = 0
    py = 0
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
            elif level[y][x] == 'g':
                Empty('empty', x, y)
                GreenSnake(1, 1, x, y)
    # вернем игрока, а также размер поля в клетках
    new_player = Player(px, py)  # создание игрока
    return new_player, x, y


def terminate(text=""):  # экстренный выход из программы
    pygame.quit()
    sys.exit(text)


# создание констант и инициализация библиотеки pygame
FPS = 50
SCREEN_SIZE = WIDTH, HEIGHT = 550, 550
PLAYER_HP = 10
screen = pygame.display.set_mode(SCREEN_SIZE)
tile_images = {
               'wall': load_image('box.png'),
               'empty': load_image('grass.png'),
               'diamond': load_image('diamond.png', -1)
               }
player_image = load_image('player.png')
tile_width = tile_height = 50
pygame.init()

# создание групп спрайтов для более удобного обращения со спрайтами
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
diamonds_group = pygame.sprite.Group()


class GreenSnake(pygame.sprite.Sprite):
    def __init__(self, columns, rows, x, y):
        super().__init__(all_sprites, enemy_group)
        self.frames = []
        sheet = load_image('box.png', -1)
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_width, y * tile_height)
        self.direction_x = 1
        self.direction_y = 0
        self.update_load = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

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


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.add(walls_group)


class Diamond(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, diamonds_group)
        self.image = tile_images['diamond']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Empty(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class PlayerHP(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows):
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
        self.cur_frame = 10 - PLAYER_HP
        self.image = self.frames[self.cur_frame]
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 6)
        self.last_moves = [(0, 0)]
        self.score = 0
        self.stun = FPS * 3

    def move(self, m, n):
        global PLAYER_HP
        if PLAYER_HP > 0:
            self.rect = self.rect.move(m, n)
            self.last_moves.append((m, n))
            if pygame.sprite.spritecollideany(self, enemy_group) and self.stun <= 0:
                if m or n:
                    self.rect = self.rect.move(-m, -n)
                    PLAYER_HP -= 1
                    self.stun = FPS * 3
                else:
                    self.rect = self.rect.move(self.last_moves[-1])
                    self.last_moves.remove(self.last_moves[-1])
                    PLAYER_HP -= 1
                    self.stun = FPS * 3
            if pygame.sprite.spritecollideany(self, walls_group):
                if m or n:
                    self.rect = self.rect.move(-m, -n)
                else:
                    self.rect = self.rect.move(self.last_moves[-1])
                    self.last_moves.remove(self.last_moves[-1])
            if pygame.sprite.spritecollide(self, diamonds_group, True):
                self.score += 1

    def update(self):
        global PLAYER_HP
        if pygame.sprite.spritecollideany(self, enemy_group) and self.stun <= 0:
            self.rect = self.rect.move(-self.last_moves[-1][0], -self.last_moves[-1][1])
            self.last_moves.remove(self.last_moves[-1])
            PLAYER_HP -= 1
            self.stun = FPS * 3
        if PLAYER_HP < 0:
            PLAYER_HP = 0
        if not self.last_moves:
            self.last_moves = [(0, 0)]
        if self.stun > 0:
            self.stun -= 1
        print(self.stun)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

        if -5 > obj.rect.x:
            obj.rect.x += WIDTH
        elif obj.rect.x > WIDTH - 5:
            obj.rect.x -= WIDTH
        if -5 > obj.rect.y:
            obj.rect.y += HEIGHT
        elif obj.rect.y > HEIGHT - 5:
            obj.rect.y -= HEIGHT

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
