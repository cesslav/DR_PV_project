# -*- coding: utf-8 -*-
# импорты необходимых библиотек и функций
import os
from classes import DBClass, Empty, Wall, Diamond, Camera, PlayerHP, GreenSnake
from add_func import terminate, level_choose_screen, load_level, load_image, load_sound, start_screen
from datetime import datetime
import pygame


pygame.init()
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


# создание групп спрайтов для более удобного обращения со спрайтами
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
diamonds_group = pygame.sprite.Group()


def ttg_level_num(scr, isst):
    try:
        # mode = str(input("Enter game mode(t/q): "))
        pl, x, y = generate_level(load_level(f"level{level_choose_screen(scr, isst)}.txt"))
        bd = DBClass('saves.db')
        return bd, pl, x, y
    except Exception as f:
        log_file.write(f"[{str(datetime.now())[11:16]}]: program have error '{f}'\n")
        return ttg_level_num(scr, False)


def generate_level(level):  # наполнение уровня
    global diamonds_left
    player_x = 0
    player_y = 0
    diamonds_left = 0
    new_player, x, y = None, None, None
    for y in range(len(level)):  # создание спрайтов уровня
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
            elif level[y][x] == '#':
                Wall(all_sprites, tiles_group, walls_group, x, y, tile_images['wall'])
            elif level[y][x] == '@':
                Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                player_x, player_y = x, y
            elif level[y][x] == 'd':
                Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                Diamond(all_sprites, diamonds_group, x, y, tile_images['diamond'])
                diamonds_left += 1
            elif level[y][x] == 'g':
                Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                GreenSnake(all_sprites, enemy_group, x, y, load_image("snakes.png"), snake_type='g')
            elif level[y][x] == 'q':
                Empty(all_sprites, tiles_group, x, y, tile_images['empty'])
                GreenSnake(all_sprites, enemy_group, x, y, load_image("snakes.png"), snake_type='q')
    # вернем игрока, а также размер поля в клетках
    new_player = Player(player_x, player_y)  # создание игрока
    return new_player, x, y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, stan=0, loading=FPS * 2):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.last_moves = [(0, 0)]
        self.score = 0
        self.stun = stan
        self.loading = loading

    def move(self, m, n):
        global player_hp
        global diamonds_left
        if player_hp > 0 and self.stun < FPS * 0.25 and self.loading == 0:
            self.rect = self.rect.move(m, n)
            self.last_moves.append((m, n))
            if pygame.sprite.spritecollideany(self, enemy_group) and self.stun <= 0:
                if m or n:
                    self.rect = self.rect.move(-m, -n)
                    player_hp -= 2
                    self.stun = FPS * 0.75
                    log_file.write(f"[{str(datetime.now())[11:16]}]: player has damaged\n")
                else:
                    self.rect = self.rect.move(self.last_moves[-1])
                    self.last_moves.remove(self.last_moves[-1])
                    player_hp -= 2
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

    def save(self):
        return self.__class__.__name__, self.rect.x, self.rect.y, None, None, self.stun, 1

    def extra_move(self, m):
        self.rect = self.rect.move(m, m)

    def death(self):
        global player_hp
        player_hp = 0
        return self.score

    def update(self, ph):
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
        if self.stun > 0 and self.loading == 0:
            self.stun -= 1
        if self.loading > 0:
            self.loading -= 1


pygame.init()
start_screen(screen, WIDTH, HEIGHT)  # Стартскрин для выбора уровня и предсказуемого начала игры.
# Локальные объекты и функции, которые больше нигде не понадобятся.
pygame.display.set_caption("DMPV")
pygame.display.set_icon(load_image("player.png", -1))
hp = PlayerHP(all_sprites, player_group, load_image('hp.png', -1))
font1, font2 = pygame.font.Font(None, 20), pygame.font.Font(None, 50)
death_switch, running, s = True, True, pygame.mixer.Sound(os.path.join('data/sounds', "game_over.mp3"))
# Выбор, загрузка уровня и безопасный выход в случае ошибки
# (в будущем будет добавлено автоотправление письма-фидбека о баге)
log_file.write(f"[{str(datetime.now())[11:16]}]: game start\n")
db, player, level_x, level_y = ttg_level_num(screen, True)
camera, clock = Camera(), pygame.time.Clock()
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
                            Empty(all_sprites, tiles_group, information[1] / 50,
                                  information[2] / 50, tile_images['empty'])
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
                    player = Player(px, py, stun, 2*FPS)
                    data = db.get_vars_info()
                    score = 0
                    for information in data:
                        if information[0] == "player_hp":
                            player_hp = information[1]
                        if information[0] == "score":
                            score = information[1]
                    log_file.write(f"[{str(datetime.now())[11:16]}]: game loaded from save file\n")
                    camera = Camera()
                    hp = PlayerHP(all_sprites, player_group, load_image("hp.png", -1))
                    player.score = score
                    player.extra_move(-150)
                except Exception as e:
                    log_file.write(f"[{str(datetime.now())[11:16]}]: program have error '{e}'\n")
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
    # all_sprites.update()
    for sprite in all_sprites:
        if sprite in enemy_group:
            sprite.update(walls_group)
        elif sprite in player_group:
            sprite.update(player_hp)
        else:
            sprite.update()
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
