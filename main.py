# импорты необходимых библиотек и функций
from datetime import datetime
import os
import pygame
from classes import Camera, PlayerHP, screen, all_sprites, enemy_group, player_group, \
    walls_group, WIDTH, HEIGHT, FPS, load_image, generate_level, load_level, start_screen, \
    terminate, save_game, load_game, load_sound, add_to_leaderboard, log_file


# Вход в программу(нужен на случай добавления внешних функций или переменных в этот файл).
if __name__ == "__main__":
    start_screen(screen, WIDTH, HEIGHT)  # Стартскрин для выбора уровня и предсказуемого начала игры.
    # Локальные объекты и функции, которые больше нигде не понадобятся.
    # pygame.mixer.music.load("/data/sounds/background.mp3")
    s = pygame.mixer.Sound(os.path.join('data/sounds', "game_over.mp3"))
    clock = pygame.time.Clock()
    running = True
    pygame.display.set_caption("DMPV")
    pygame.display.set_icon(load_image("player.png", -1))
    camera = Camera()
    hp = PlayerHP(load_image('hp.png', -1), 11, 1)
    font1 = pygame.font.Font(None, 20)
    font2 = pygame.font.Font(None, 50)
    death_switch = True
    # Выбор, загрузка уровня и безопасный выход в случае ошибки
    # (в будущем будет добавлено автоотправление письма-фидбека о баге)
    log_file.write(f"[{str(datetime.now())[11:16]}]: game start\n")
    try:
        player, level_x, level_y = generate_level(load_level(f"level{(int(input('Введите номер уровня: ')))}.txt"))
    except Exception as e:
        log_file.write(f"[{str(datetime.now())[11:16]}]: program finished with error {e}\n")
        log_file.close()
        print(e)
        terminate("Некорректный номер уровня!")
    # Главный Цикл
    time_delta = pygame.time.get_ticks()
    load_sound("background.mp3")
    log_file.write(f"[{str(datetime.now())[11:16]}]: level imported successful\n")
    while running:
        from classes import diamonds_left, player_hp
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
                    save_game(player.score)
                if event.key == pygame.K_e:
                    camera, player, hp, player.score = load_game()
                    player.extra_move(-150)
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
                add_to_leaderboard((pygame.time.get_ticks() - time_delta) / 1000, player.score)
                log_file.write(f"[{str(datetime.now())[11:16]}]: game over, player is win\n")
                log_file.write(f"[{str(datetime.now())[11:16]}]: game end "
                               f"with time {(pygame.time.get_ticks() - time_delta) / 1000}\n")
                death_switch = False
                time_delta = (pygame.time.get_ticks() - time_delta) / 1000
    # корректный выход из программы при завершении цикла
    pygame.quit()
