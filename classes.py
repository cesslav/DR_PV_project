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
        self.dx = 0
        self.dy = 0
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

    def save(self):
        return self.__class__.__name__, None, None, None, None, None, 1


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


class PlayerHP(pygame.sprite.Sprite):
    def __init__(self, all_sprites, player_group, sheet, columns=11, rows=1):
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

    def update(self, player_hp):
        self.cur_frame = 10 - player_hp
        self.image = self.frames[self.cur_frame]

    def save(self):
        return self.__class__.__name__, None, None, None, None, None, 1


class GreenSnake(pygame.sprite.Sprite):
    def __init__(self, all_sprites, enemy_group, x, y, img, tile_width=50, dirx=1, diry=0, stun=0, snake_type=None):
        super().__init__(all_sprites, enemy_group)
        self.tile_width = tile_width
        self.frames = []
        sheet = img
        self.cut_sheet(sheet)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * self.tile_width, y * self.tile_width)
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

    def move(self, walls_group):
        m = self.direction_x * self.tile_width
        n = self.direction_y * self.tile_width
        self.rect = self.rect.move(m, n)
        if pygame.sprite.spritecollide(self, walls_group, False):
            self.rect = self.rect.move(-2 * m, -2 * n)
            self.direction_x = -self.direction_x
            self.direction_y = -self.direction_y

    def update(self, walls_group):
        self.update_load += 1
        if self.update_load % 30 == 0:
            self.move(walls_group)
            if self.direction_x == 1:
                self.cur_frame = (self.cur_frame - 1) % 8  # движение вправо (колонки с 9 по 2)
            elif self.direction_x == -1:
                self.cur_frame = (self.cur_frame + 1) % 8  # движение влево (колонки с 9 по 2)
            self.image = self.frames[self.cur_frame]
            if self.direction_x == 1:  # отражаем по горизонтали
                self.image = pygame.transform.flip(self.image, True, False)
