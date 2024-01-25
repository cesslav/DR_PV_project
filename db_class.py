import os
import sqlite3
import sys
from datetime import datetime

import pygame


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


class DBClass:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def add_to_leaderboard(self, time, diamonds_collected, user_name="John Doe"):
        lead_id = self.cursor.execute("""
            SELECT ID
            FROM leaders
            """).fetchall()
        max_id = []
        for i in lead_id:
            max_id.append(i[0])
        max_id = max(max_id) + 1
        self.cursor.execute("""
            INSERT INTO Leaders
            VALUES (?,?,?,?,?)
            """, (max_id, user_name,
                  str(datetime.now())[11:16],
                  time, diamonds_collected))
        self.connection.commit()
        # log_file.write(f"[{str(datetime.now())[11:16]}]: winner added to leaderboard as {user_name}\n")

    def save_game_vars(self, player_hp, score):
        self.cursor.execute("""
                                    INSERT INTO GameVars
                                    VALUES (?,?,?)
                                    """, (1, "player_hp", player_hp))
        self.cursor.execute("""
                                        INSERT INTO GameVars
                                        VALUES (?,?,?)
                                        """, (1, "score", score))
        self.connection.commit()

    def save_game_sprite(self, sprite_inf):
        self.cursor.execute("""
                                INSERT INTO ObjectProp
                                VALUES (?,?,?,?,?,?,?)
                                """, sprite_inf)
        self.connection.commit()

    def clear_db(self):
        self.cursor.execute("""DELETE FROM SavesData WHERE Save_Id = 1""")
        self.cursor.execute("""DELETE FROM GameVars WHERE Save_ID = 1""")
        self.cursor.execute("""DELETE FROM ObjectProp WHERE Save_ID = 1""")
        self.cursor.execute("""
                    INSERT INTO SavesData
                    VALUES (?,?,?)
                    """, (1, str(datetime.now())[11:16], "quick save"))
        self.connection.commit()

    def get_sprites_info(self):
        data = self.cursor.execute("""
            SELECT ObjectType, ObjectX, ObjectY, ObjectDirX, ObjectDirY, ObjectState
            FROM ObjectProp
            WHERE Save_Id = 1
            """).fetchall()
        return data

    def get_vars_info(self):
        data = self.cursor.execute("""
                SELECT VarName, VarVal
                FROM GameVars
                WHERE Save_Id = 1
                """).fetchall()
        return data
