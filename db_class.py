import sqlite3
from datetime import datetime

import pygame


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


class Wall(pygame.sprite.Sprite):
    def __init__(self, all_sprites, tiles_group, walls_group, pos_x, pos_y, img, tile_width=50):
        super().__init__(tiles_group, all_sprites)
        tile_height = tile_width
        self.image = img
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.add(walls_group)

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, None, 1


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, width=550, height=550):
        self.dx = -3
        self.dy = -3
        self.width = width
        self.height = height

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

        if -1 > obj.rect.x:
            obj.rect.x += self.width
        elif obj.rect.x > self.width - 1:
            obj.rect.x -= self.width
        if -1 > obj.rect.y:
            obj.rect.y += self.height
        elif obj.rect.y > self.height - 1:
            obj.rect.y -= self.height

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - self.width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - self.height // 2)


class Empty(pygame.sprite.Sprite):
    def __init__(self, all_sprites, tiles_group, pos_x, pos_y, img, tile_width=50):
        super().__init__(tiles_group, all_sprites)
        self.image = img
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y)

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, None, 1


class Diamond(pygame.sprite.Sprite):
    def __init__(self, all_sprites, diamonds_group, pos_x, pos_y, img, tile_width=50):
        super().__init__(all_sprites, diamonds_group)
        self.image = img
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_width * pos_y)

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, None, 1
