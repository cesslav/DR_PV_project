# импорты необходимых библиотек и функций
import sqlite3

import pygame

from classes import Camera, PlayerHP, screen, all_sprites, enemy_group, player_group, walls_group, WIDTH, HEIGHT, FPS, \
    load_image, generate_level, load_level, start_screen, terminate

# Вход в программу(нужен на случай добавления внешних функций или переменных в этот файл).
if __name__ == "__main__":
    start_screen(screen, WIDTH, HEIGHT)  # Стартскрин для выбора уровня и предсказуемого начала игры.
    connection = sqlite3.connect("data/inf/saves.db")
    cursor = connection.cursor()
    # Локальные объекты и функции, которые больше нигде не понадобятся.
    clock = pygame.time.Clock()
    running = True
    pygame.display.set_caption("DMPV")
    camera = Camera()
    hp = PlayerHP(load_image('hp.png', -1), 11, 1)
    font1 = pygame.font.Font(None, 20)
    font2 = pygame.font.Font(None, 50)
    # Выбор, загрузка уровня и безопасный выход в случае ошибки
    # (в будущем будет добавлено автоотправление письма-фидбека о баге)
    try:
        player, level_x, level_y = generate_level(load_level(f"level{(int(input('Введите номер уровня: ')))}.txt"))
    except Exception as e:
        print(e)
        terminate("Некорректный номер уровня!")
    # Главный Цикл
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
        # Отрисовка всех спрайтов и надписей в нужном для корректного отображения порядке
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        enemy_group.draw(screen)
        walls_group.draw(screen)
        player_group.draw(screen)
        screen.blit(font1.render(f"SCORE {player.score}", 1, pygame.Color('red')), (0, 25, 100, 10))
        from classes import PLAYER_HP
        if PLAYER_HP == 0:
            screen.blit(font2.render("Game Over", 1,
                                     pygame.Color('red')), (WIDTH // 2 - 25, HEIGHT // 2 - 25, 100, 100))
        pygame.display.flip()
        clock.tick(FPS)
        # Обновление всех спрайтов
        all_sprites.update()
        camera.update(player)
        for sprite in all_sprites:
            if not isinstance(sprite, PlayerHP):
                camera.apply(sprite)
    # корректный выход из программы при завершении цикла
    pygame.quit()


# пример уровня:
#    #####..####
#    #..s......#
#    #.........#
#    #..#...#..#
#    #.........#
#    .....@.....
#    #.........#
#    #..#......#
#    #......d..#
#    #.........#
#    #####..####
