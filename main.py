import sys

import pygame

from classes import Camera, PlayerHP, screen, all_sprites, enemy_group, player_group, walls_group, WIDTH, HEIGHT, FPS, \
    load_image, generate_level, load_level, start_screen

if __name__ == "__main__":
    start_screen(screen, WIDTH, HEIGHT)
    clock = pygame.time.Clock()
    running = True
    pygame.display.set_caption("Жруг")
    camera = Camera()
    font1 = pygame.font.Font(None, 20)
    font2 = pygame.font.Font(None, 50)
    try:
        player, level_x, level_y = generate_level(load_level(f"level{(int(input('Введите номер уровня: ')))}.txt"))
    except Exception as e:
        print(e)
        sys.exit("Некорректный номер уровня!")
    hp = PlayerHP(load_image('hp.png', -1), 11, 1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.move(50, 0)
                if event.key == pygame.K_LEFT:
                    player.move(-50, 0)
                if event.key == pygame.K_UP:
                    player.move(0, -50)
                if event.key == pygame.K_DOWN:
                    player.move(0, 50)
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        enemy_group.draw(screen)
        walls_group.draw(screen)
        player_group.draw(screen)
        screen.blit(font1.render(f"SCORE {player.score}", 1, pygame.Color('red')), (0, 25, 100, 10))
        from classes import PLAYER_HP
        if PLAYER_HP == 0:
            screen.blit(font2.render("Game Over", 1,
                                     pygame.Color('red')), (WIDTH // 2 - 25, HEIGHT // 2 - 25, 100, 100))
        camera.update(player)
        for sprite in all_sprites:
            if not isinstance(sprite, PlayerHP):
                camera.apply(sprite)
        pygame.display.flip()
        clock.tick(FPS)
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
