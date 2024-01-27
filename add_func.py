# -*- coding: utf-8 -*-
import os
import sys
import pygame


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


def load_sound(name):  # функция для подгрузки музыки
    fullname = resource_path(os.path.join('data/sounds', name))
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        terminate(f"Файл с музыкой '{fullname}' не найден")
    pygame.mixer.music.load(fullname)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)


def level_choose_screen(scr, corr=True):  # функция для включения стартскрина
    scr.fill((0, 0, 0))
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
        for line in intro_text:  # построчная печать текста
            string_rendered = font.render(line, 1, pygame.Color("#BD0D9E"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            scr.blit(string_rendered, intro_rect)
        # pygame.time.wait(1000)
        pygame.display.flip()
        clock.tick(15)  # ограничение частоты обновления экрана для снижения потребляемых ресурсов


def terminate(text=""):  # экстренный выход из программы
    pygame.quit()
    sys.exit(text)


def load_level(filename):  # функция для предварительной обработки уровня
    filename = resource_path("data/levels/" + filename)
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


def load_image(name, colorkey=None):  # функция для подгрузки изображений
    fullname = resource_path(os.path.join('data/images', name))
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        pygame.quit()
        sys.exit(f"Файл с изображением '{fullname}' не найден")
    image = pygame.image.load(fullname)
    if colorkey is not None:
        # image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image
