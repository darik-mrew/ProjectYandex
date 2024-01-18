import copy

from pygame.transform import scale
import pygame_gui
from Base_classes_and_functions import *


def get_neighbours(x, y, matrix):
    neighbours = []
    for i in range(y - 1, y + 2):
        for j in range(x - 1, x + 2):
            if i == len(matrix) or i < 0 or j == len(matrix[0]) or j < 0 or (i == y and j == x):
                pass
            else:
                neighbours.append((j, i, matrix[i][j]))
    return neighbours


def get_player_start_coords(entrance_x, entrance_y):
    player_start_x = (8 if entrance_x == 9 else (1 if entrance_x == 0 else entrance_x))
    player_start_y = (3 if entrance_y == 4 else (1 if entrance_y == 0 else entrance_y))
    return player_start_x, player_start_y


def get_quest():
    with open('data/Quest.txt') as txt_file:
        data = [i.strip() for i in txt_file.readlines()]
    modes = [i.split()[0] for i in data[:-2]]
    quantities = [int(i.split()[1]) for i in data[:-2]]
    current_quantities = [int(i.split()[2]) for i in data[:-2]]
    return modes, quantities, current_quantities


def write_quest_stats_in_file(modes, quantities, current_quantities):
    with open('data/Quest.txt') as txt_file:
        data = [i.strip() for i in txt_file.readlines()]
        reward_string = data[-2]
        completed_status_string = data[-1]

    with open('data/Quest.txt', 'w') as txt_file:
        for mode, quantity, current_quantity in zip(modes, quantities, current_quantities):
            txt_file.write(' '.join([str(i) for i in [mode, quantity, current_quantity]]) + '\n')
        txt_file.write(reward_string + '\n')
        txt_file.write(completed_status_string)


def create_level(entrance_x, entrance_y):
    objects = {'r': 0.6, 'm': 0.04, 'g': 0.04, 'a': 0.02, 'i': 0.3}
    level = [random.choices(list(objects.keys()), weights=list(objects.values()), k=10) for _ in range(5)]

    for y in range(len(level)):
        for x in range(len(level[0])):
            if level[y][x] in ['m', 'g', 'a']:
                for neighbour in get_neighbours(x, y, level):
                    if neighbour[2] != level[y][x] and random.random() <= 0.1:
                        level[neighbour[1]][neighbour[0]] = copy.copy(level[y][x]) + '*'

    for y in range(len(level)):
        for x in range(len(level[0])):
            if '*' in level[y][x]:
                level[y][x] = level[y][x][:-1]

    for y in range(len(level)):
        for x in range(len(level[0])):
            if level[y][x] == 'i' and random.random() <= 0.1:
                level[y][x] = 's'

    level[entrance_y][entrance_x] = 'e'
    for neighbour in get_neighbours(entrance_x, entrance_y, level):
        level[neighbour[1]][neighbour[0]] = 'i'

    out_x, out_y = entrance_x, entrance_y
    while out_x == entrance_x and out_y == entrance_y:
        out_x = random.choice([0, 5, 9])
        out_y = random.choice([0, 4]) if out_x == 5 else 2
    level[out_y][out_x] = 'o'

    return level, (out_x, out_y)


def create_matrix_to_AI(level):
    for y in range(len(level)):
        for x in range(len(level[0])):
            if level[y][x] in ['s', 'w', 'z', 'p']:
                level[y][x] = 'i'
            if level[y][x] != 'i':
                level[y][x] = 'b'
    return level


def create_heart(all_sprites, heart_group):
    heart = pygame.sprite.Sprite(all_sprites, heart_group)
    image = scale(load_image('heart.png'), (40, 40))
    heart.image = image
    heart.rect = image.get_rect().move(50, 375)


def draw_quantity_of_hp_points(hp):
    screen.blit(pygame.Surface([60, 60]), (100, 375))

    font = pygame.font.Font(None, 40)
    text = font.render(f'{hp}', True, (100, 255, 100))
    screen.blit(text, (100, 382))


def create_quest_interface(all_sprites):   # # #
    loot_images_dict = {'s': scale(load_image('skeleton.png'), (40, 40)),
                        'm': scale(load_image('copper.png'), (40, 40)), 'g': scale(load_image('gold.png'), (40, 40)),
                        'a': scale(load_image('diamond.png'), (40, 40))}
    modes, quantities = get_quest()[:-1]
    images = [loot_images_dict[mode] for mode in modes]
    Quest_as_interface(images, quantities, (310, 375), all_sprites)


def draw_necessary_items_current_quantities(quantities):
    for x, quantity in zip(range(310, 710, 140), quantities):
        font = pygame.font.Font(None, 40)
        text = font.render(f'{quantity}', True, (100, 255, 100))
        screen.blit(pygame.Surface([25, 40]), (x, 375 + 5))
        screen.blit(text, (x + 10, 375 + 10))


def create_tiles(player, level, all_sprites, sprite_group_collisions, enemies_group, stones_and_ores):
    cod_to_image = {'s': (None, 5), 'm': (load_image('copperblock.png'), 1),
                    'g': (load_image('goldblock.png'), 2), 'a': (load_image('diamblock.png'), 3),
                    'i': (load_image('emptyspace.png'), None), 'e': (load_image('door.png'), None),
                    'o': (load_image('door.png'), None),
                    'r': ([load_image('block3.png'), load_image('block2.png'), load_image('block1.png')], 1)}

    for pos_y in range(len(level)):
        for pos_x in range(len(level[pos_y])):
            sprite_groups = [all_sprites]
            if level[pos_y][pos_x] == 's':
                image = cod_to_image['i'][0]
                Tile(pos_x, pos_y, image, sprite_groups)

                sprite_groups.append(enemies_group)
                hp = cod_to_image[level[pos_y][pos_x]][1]
                Enemy(pos_x, pos_y, hp, level[pos_y][pos_x], player, all_sprites, enemies_group)
            else:
                if level[pos_y][pos_x] != 'i':
                    sprite_groups.extend([sprite_group_collisions, stones_and_ores])

                if level[pos_y][pos_x] == 'r':
                    hp = random.randint(1, 3)
                    image = cod_to_image[level[pos_y][pos_x]][0][hp - 1]
                else:
                    hp = cod_to_image[level[pos_y][pos_x]][1]
                    image = cod_to_image[level[pos_y][pos_x]][0]

                Tile(pos_x, pos_y, image, sprite_groups, hp=hp, mode=level[pos_y][pos_x])


def create_walls(sprite_group_collisions, all_sprites):
    Wall((48, 50), 2, 320, (150, 150, 150), sprite_group_collisions, all_sprites)
    Wall((690, 50), 2, 320, (150, 150, 150), sprite_group_collisions, all_sprites)
    Wall((50, 48), 640, 2, (150, 150, 150), sprite_group_collisions, all_sprites)
    Wall((50, 370), 640, 2, (150, 150, 150), sprite_group_collisions, all_sprites)


def create_interactive_zone_out(out_x, out_y, player, sprite_group):
    interactive_zone_entrance = Interactive_Zone((50 + 64 * (out_x - 1) + 32, 50 + 64 * (out_y - 1) + 32, 64 * 2, 64
                                                  * 2), player, sprite_group)

    return interactive_zone_entrance


# экран, часы менеджер интерфейса
pygame.init()
size = width, height = 740, 420
screen = pygame.display.set_mode(size)
manager = pygame_gui.UIManager((width, height))
clock = pygame.time.Clock()
# константы
running = True
FPS = 60
player_hit_cooldown = 700


def main(entrance_x, entrance_y, player_hp=None):
    global running

    # определение характеристик героя
    with open('data/Characteristics.txt') as txt_file:
        characteristics = {i.strip().split(': ')[0]: int(i.strip().split(': ')[1]) for i in txt_file.readlines()}
    # всплывающее окно, переход на другую локацию
    conformation_window = None
    # определение текущего задания
    modes, quantities, current_quantities = get_quest()
    # создание групп спрайтов
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    sprite_group_collisions = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()
    stones_and_ores = pygame.sprite.Group()
    hearts_group = pygame.sprite.Group()
    # создание уровня
    level, out_coords = create_level(entrance_x, entrance_y)
    create_walls(sprite_group_collisions, all_sprites)
    create_heart(all_sprites, hearts_group)
    create_quest_interface(all_sprites)
    player_x, player_y = get_player_start_coords(entrance_x, entrance_y)
    player = Player(player_x, player_y, player_group, all_sprites, sprite_group_collisions,
                    load_image('main character.png', -1), hp=player_hp)
    create_tiles(player, level, all_sprites, sprite_group_collisions, enemies_group, stones_and_ores)
    interactive_zone_out = create_interactive_zone_out(out_coords[0], out_coords[1], player, all_sprites)

    AI_matrix = create_matrix_to_AI(level)
    for enemy in enemies_group.sprites():
        enemy.determine_the_route(AI_matrix, (player_x, player_y))

    time_delta = clock.tick(FPS) / 1000.0
    player_last_hit_time = -700

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if interactive_zone_out.player_in_zone():
                        entrance_x = (9 if out_coords[0] == 0 else (0 if out_coords[0] == 9 else out_coords[0]))
                        entrance_y = (4 if out_coords[1] == 0 else (0 if out_coords[1] == 4 else out_coords[1]))
                        write_quest_stats_in_file(modes, quantities, current_quantities)
                        main(entrance_x, entrance_y, player.get_hp())

            if event.type == pygame.MOUSEWHEEL:
                player.change_current_tool()

            if event.type == pygame.MOUSEBUTTONDOWN and event.type != pygame.MOUSEWHEEL and\
                    pygame.time.get_ticks() - player_last_hit_time > player_hit_cooldown:
                player_last_hit_time = pygame.time.get_ticks()

                player_centre_coords = player.get_centre_coords()
                player_hit_direction = player.get_hit_direction()
                point_of_hit_coords_1 = tuple(coord + 64 * hit_direction for coord, hit_direction in
                                              zip(player_centre_coords, player_hit_direction))
                point_of_hit_coords_2 = tuple(coord + 32 * hit_direction for coord, hit_direction in
                                              zip(player_centre_coords, player_hit_direction))
                point_of_hit_coords_3 = tuple(coord + 0 * hit_direction for coord, hit_direction in
                                              zip(player_centre_coords, player_hit_direction))

                if player.get_current_tool() == 'pick':
                    for tile in stones_and_ores.sprites():
                        if tile.point_in_rect(*point_of_hit_coords_1) or tile.point_in_rect(*point_of_hit_coords_2) or\
                                tile.point_in_rect(*point_of_hit_coords_3):
                            if tile.get_hp() == 1:
                                AI_matrix[tile.get_pos_as_board()[1]][tile.get_pos_as_board()[0]] = 'i'
                                Tile(*tile.get_pos_as_board(), load_image('emptyspace.png'), all_sprites)

                                for enemy in enemies_group.sprites():
                                    enemy.determine_the_route(AI_matrix, (player_x, player_y))

                                if tile.get_mode() in modes:
                                    current_quantities[modes.index(tile.get_mode())] += 1
                            tile.take_damage()

                elif player.get_current_tool() == 'axe':
                    for enemy in enemies_group.sprites():
                        if enemy.point_in_rect(*point_of_hit_coords_1) or enemy.point_in_rect(*point_of_hit_coords_2)\
                                or enemy.point_in_rect(*point_of_hit_coords_3):
                            if enemy.get_hp() <= player.get_axe_damage() and enemy.get_mode() in modes:
                                current_quantities[modes.index(enemy.get_mode())] += 1
                            enemy.stun_lock()
                            enemy.take_damage(player.get_axe_damage())

            manager.process_events(event)

        if pygame.key.get_pressed()[pygame.K_w]:
            player.set_direction(player.get_direction()[0], -1)
            player.set_hit_direction(0, -1)
        if pygame.key.get_pressed()[pygame.K_d]:
            player.set_direction(1, player.get_direction()[1])
            player.set_hit_direction(1, 0)
        if pygame.key.get_pressed()[pygame.K_s]:
            player.set_direction(player.get_direction()[0], 1)
            player.set_hit_direction(0, 1)
        if pygame.key.get_pressed()[pygame.K_a]:
            player.set_direction(-1, player.get_direction()[1])
            player.set_hit_direction(-1, 0)

        if (player.get_centre_coords()[0] - 50) // 64 != player_x or (player.get_centre_coords()[1] - 50) // 64\
                != player_y:
            player_x, player_y = (player.get_centre_coords()[0] - 50) // 64, (player.get_centre_coords()[1] - 50) // 64

            for enemy in enemies_group.sprites():
                enemy.determine_the_route(AI_matrix, (player_x, player_y))

        screen.fill((0, 0, 0))

        manager.update(time_delta)
        interactive_zone_out.update()
        all_sprites.update()

        all_sprites.draw(screen)
        enemies_group.draw(screen)
        player_group.draw(screen)
        draw_necessary_items_current_quantities(current_quantities)
        draw_quantity_of_hp_points(player.get_hp())

        manager.draw_ui(screen)

        pygame.display.flip()
        clock.tick(FPS)


main(5, 0)
