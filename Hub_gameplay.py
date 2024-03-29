import pygame_gui
from Base_classes_and_functions import *
from Mine_gameplay import main_mine


def create_walls():
    Wall((48, 50), 2, 320, (150, 150, 150), sprite_group_collisions, all_sprites)
    Wall((690, 50), 2, 320, (150, 150, 150), sprite_group_collisions, all_sprites)
    Wall((50, 48), 640, 2, (150, 150, 150), sprite_group_collisions, all_sprites)
    Wall((50, 370), 640, 2, (150, 150, 150), sprite_group_collisions, all_sprites)
    Wall((4 * 64 + 48, 50), 3, 3 * 64, (0, 0, 0), sprite_group_collisions, all_sprites)
    Wall((50, 3 * 64 + 46), 55, 4, (0, 0, 0), sprite_group_collisions, all_sprites)
    Wall((64 * 2 + 65, 64 * 3 + 46), 2 * 64 - 20, 4, (0, 0, 0), sprite_group_collisions, all_sprites)


def create_roof(sprite_group):
    roof_image = load_image('roof.png')
    roof = pygame.sprite.Sprite(sprite_group)
    roof.image = roof_image
    roof.rect = roof.image.get_rect().move(55, 54)
    return roof


def create_tiles():
    level = load_level('HUB.txt')
    for pos_y in range(len(level)):
        for pos_x in range(len(level[pos_y])):
            if level[pos_y][pos_x] == '.':
                surface = pygame.Surface([64, 64])
                Tile(pos_x, pos_y, surface, all_sprites)

            else:
                surface = pygame.Surface([64, 64])
                Tile(pos_x, pos_y, surface, sprite_group_collisions, all_sprites)
    hub_sprite = pygame.sprite.Sprite(all_sprites)
    hub_sprite.image = load_image('HUBPIC.png')
    hub_sprite.rect = hub_sprite.image.get_rect().move(50, 50)
    return level


def create_interactive_zones():
    global interactive_zone_bed, interactive_zone_bird, interactive_zone_mine
    interactive_zone_bed = Interactive_Zone((50 + 64, 50, 64 * 3, 64 * 2), player, all_sprites)
    interactive_zone_bird = Interactive_Zone((50 + 64 * 7 + 32, 50 + 64 * 2 + 32, 64 * 2, 64 * 2), player, all_sprites)
    interactive_zone_mine = Interactive_Zone((50 + 64 * 5, 50, 64 * 2, 64 * 2), player, all_sprites)

    return Interactive_Zones_container(interactive_zone_bed, interactive_zone_bird, interactive_zone_mine)


def create_conformation_window():
    global conformation_window

    if cur_action == 'bed_interact':
        action_long_desc = 'Go to bed?'
    elif cur_action == 'mine_interact':
        action_long_desc = 'Enter the mine?'
    else:
        action_long_desc = ''

    conformation_window = pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect(50 + 64 * 3, 50 + 64 * 1.5, 261, 200),
        manager=manager,
        window_title='',
        action_long_desc=action_long_desc,
        action_short_name='Ok')


def create_quest_window():
    global first_button, second_button, third_button, pause
    pause = True

    window = pygame.sprite.Sprite(interactive_windows_group)
    window.image = pygame.Surface([440, 290])
    window.image.fill((0, 0, 0))
    pygame.draw.rect(window.image, (0, 255, 0), (0, 0, 440, 290), 2)
    window.rect = window.image.get_rect().move(width // 2 - 440 // 2, height * 0.1)

    quests = [generate_quest(), generate_quest(), generate_quest()]

    for y, quest in zip(range(20, 290, 90), quests):
        images = [loot_images_dict[i] for i in quest[0]]

        Quest_as_window(images, quest[1], quest[2], (width // 2 - 440 // 2 + 10, height * 0.1 + y),
                        interactive_windows_group)

    first_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(width // 2 - 440 // 2 + 362, height * 0.1 + 20, 58, 64),
        text='Take',
        manager=manager)

    second_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(width // 2 - 440 // 2 + 362, height * 0.1 + 20 + 90, 58, 64),
        text='Take',
        manager=manager)

    third_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(width // 2 - 440 // 2 + 362, height * 0.1 + 20 + 180, 58, 64),
        text='Take',
        manager=manager)

    return quests


def create_shop_window():
    global first_button, second_button, third_button, pause
    pause = True

    window = pygame.sprite.Sprite(interactive_windows_group)
    window.image = pygame.Surface([280, 215])
    window.image.fill((0, 0, 0))
    pygame.draw.rect(window.image, (0, 255, 0), (0, 0, 280, 215), 2)
    window.rect = window.image.get_rect().move(width // 2 - 200 // 2, height * 0.1)

    pygame.draw.rect(window.image, (0, 255, 0), (19, 19, 65, 65), 2)
    pygame.draw.rect(window.image, (0, 255, 0), (19, 103, 65, 65), 2)

    window.image.blit(load_image('armor.png'), (20, 19))
    window.image.blit(load_image('axe.png'), (20, 100))

    if characteristics['DAMAGE'] == 4:
        first_button = None
    else:
        first_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(width // 2 - 200 // 2 + 94, height * 0.1 + 20, 170, 64),
            text=f'Upgrade: {damage_coins_dict[characteristics["DAMAGE"]]} coins',
            manager=manager)

    if characteristics["HP"] == 7:
        second_button = None
    else:
        second_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(width // 2 - 200 // 2 + 94, height * 0.1 + 104, 170, 64),
            text=f'Upgrade: {hp_coins_dict[characteristics["HP"]]} coins',
            manager=manager)

    third_button = None

    font = pygame.font.Font(None, 25)
    text = font.render(f"You have {characteristics['COINS']} coins", True, (100, 255, 100))
    window.image.blit(text, (15, 185))


def create_bird_dialog_window():
    global first_button, second_button, third_button, pause
    pause = True

    window = pygame.sprite.Sprite(interactive_windows_group)
    window.image = pygame.Surface([380, 60])
    window.image.fill((0, 0, 0))
    pygame.draw.rect(window.image, (0, 255, 0), (0, 0, 380, 60), 2)
    window.rect = window.image.get_rect().move(width // 2 - 380 // 2, height // 2 - 60 // 2)

    first_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(width // 2 - 380 // 2 + 20, height // 2 - 60 // 2 + 10, 100, 40),
        text='Shop',
        manager=manager)

    second_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(width // 2 - 380 // 2 + 140, height // 2 - 60 // 2 + 10, 100, 40),
        text='Quests',
        manager=manager)

    third_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(width // 2 - 380 // 2 + 260, height // 2 - 60 // 2 + 10, 100, 40),
        text='Cancel',
        manager=manager)


def cancel_interactive_window():
    global first_button, second_button, third_button, cur_action, conformation_window

    interactive_windows_group.empty()
    cur_action = ''
    if first_button:
        first_button.kill()
    if second_button:
        second_button.kill()
    if third_button:
        third_button.kill()
    if conformation_window:
        conformation_window.kill()
    first_button = None
    second_button = None
    third_button = None


def generate_quest():
    length = random.randrange(1, 3)
    items = random.sample(possible_loot, k=length)
    quantities = [random.randrange(1, 9) if items[j] != 's' else random.randrange(1, 3) for j in range(length)]
    reward = sum([(2 if items[i] == 's' else 1) * quantities[i] for i in range(len(items))])

    return [items, quantities, reward]


def write_characteristics_in_txt():
    with open('data/Characteristics.txt', 'w') as file:
        file.write(f'HP: {characteristics["HP"]}\n')
        file.write(f'DAMAGE: {characteristics["DAMAGE"]}\n')
        file.write(f'COINS: {characteristics["COINS"]}\n')


# экран, часы менеджер интерфейса
pygame.init()
size = width, height = 740, 420
screen = pygame.display.set_mode(size)
manager = pygame_gui.UIManager((width, height))
clock = pygame.time.Clock()
# глобальные переменные
running = True
VELOCITY = 3
FPS = 60
possible_loot = ['s', 'm', 'g', 'a']
loot_images_dict = {'s': load_image('skeleton.png'), 'm': load_image('copper.png'), 'g': load_image('gold.png'),
                    'a': load_image('diamond.png')}

chosen_quest = None
with open('data/Characteristics.txt') as txt_file:
    characteristics = {i.strip().split(': ')[0]: int(i.strip().split(': ')[1]) for i in txt_file.readlines()}
damage_coins_dict = {1: 5, 2: 10, 3: 20}
hp_coins_dict = {3: 10, 5: 15}
cur_action = ''
# всплывающие окна, кнопки
first_button = None
second_button = None
third_button = None
conformation_window = None
# создание групп спрайтов
all_sprites = pygame.sprite.Group()
tiles_empty = pygame.sprite.Group()
player_group = pygame.sprite.Group()
sprite_group_collisions = pygame.sprite.Group()
roof_group = pygame.sprite.Group()
interactive_windows_group = pygame.sprite.Group()
# создание уровня
create_walls()
level = create_tiles()
create_roof(roof_group)
player = Player(1, 1, player_group, all_sprites, sprite_group_collisions, load_image('main character.png', -1))
all_interactive_zones = create_interactive_zones()


def main_hub():
    global running, cur_action, first_button, second_button, third_button, chosen_quest, conformation_window

    time_delta = clock.tick(FPS) / 1000.0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    with open('data/Quest.txt') as txt_file:
                        data = [i.strip() for i in txt_file.readlines()]
                        if len(data) != 0:
                            reward = int(data[-2].split()[1])
                            completed = (True if data[-1].split()[1] == 'true' else False)
                        else:
                            reward = 0
                            completed = False

                    if interactive_zone_bird.player_in_zone() and completed:
                        characteristics['COINS'] += reward
                        pygame_gui.windows.UIConfirmationDialog(
                            rect=pygame.Rect(50 + 64 * 3, 50 + 64 * 1.5, 260, 200),
                            manager=manager,
                            window_title='',
                            action_long_desc=f'You earned {reward} coins!',
                            action_short_name='Ok')
                        cur_action = ''
                        write_characteristics_in_txt()
                        with open('data/Quest.txt', 'w') as txt_file:
                            txt_file.write(f'reward {reward}\n')
                            txt_file.write('completed false')
                    elif interactive_zone_bird.player_in_zone():
                        player.set_direction(0, 0)

                        cancel_interactive_window()
                        cur_action = 'bird_interact'
                        create_bird_dialog_window()

                    if interactive_zone_bed.player_in_zone():
                        player.set_direction(0, 0)

                        cancel_interactive_window()
                        cur_action = 'bed_interact'
                        create_conformation_window()

                    if interactive_zone_mine.player_in_zone():
                        player.set_direction(0, 0)

                        cancel_interactive_window()
                        cur_action = 'mine_interact'
                        create_conformation_window()
                if event.key == pygame.K_ESCAPE:
                    cancel_interactive_window()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    player.set_direction(player.get_direction()[0], 0)
                if event.key == pygame.K_d:
                    player.set_direction(0, player.get_direction()[1])
                if event.key == pygame.K_s:
                    player.set_direction(player.get_direction()[0], 0)
                if event.key == pygame.K_a:
                    player.set_direction(0, player.get_direction()[1])

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    if cur_action == 'bed_interact':
                        terminate()
                    if cur_action == 'mine_interact':
                        if chosen_quest is not None:
                            with open('data/Quest.txt', 'w') as txt_file:
                                for item, quantity in zip(chosen_quest[0], chosen_quest[1]):
                                    txt_file.write(item + ' ' + str(quantity) + ' 0\n')
                                txt_file.write('reward ' + str(chosen_quest[2]) + '\n')
                                txt_file.write('completed false')
                            main_mine(5, 0)
                            chosen_quest = None
                            player.rect.x = 100
                            player.rect.y = 100
                        else:
                            conformation_window = pygame_gui.windows.UIConfirmationDialog(
                                rect=pygame.Rect(50 + 64 * 3, 50 + 64 * 1.5, 260, 200),
                                manager=manager,
                                window_title='',
                                action_long_desc="You haven't chosen a quest yet!",
                                action_short_name='Ok')
                            cur_action = ''

                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if cur_action == 'bird_interact' and event.ui_element == first_button:
                        cancel_interactive_window()
                        cur_action = 'shop_dialog'
                        create_shop_window()
                    if cur_action == 'bird_interact' and event.ui_element == second_button:
                        if chosen_quest is None:
                            cancel_interactive_window()
                            first_quest, second_quest, third_quest = tuple(create_quest_window())
                            cur_action = 'quest_dialog'
                        else:
                            cancel_interactive_window()
                            cur_action = ''
                            pygame_gui.windows.UIMessageWindow(
                                rect=pygame.Rect(width // 2 - 200 // 2, height * 0.1, 260, 200),
                                html_message='You have already accepted the task!',
                                window_title='',
                                manager=manager)
                    if cur_action == 'bird_interact' and event.ui_element == third_button:
                        cancel_interactive_window()
                        cur_action = ''
                    if cur_action == 'quest_dialog' and event.ui_element == first_button:
                        chosen_quest = first_quest
                        cancel_interactive_window()
                        cur_action = ''
                    if cur_action == 'quest_dialog' and event.ui_element == second_button:
                        chosen_quest = second_quest
                        cancel_interactive_window()
                        cur_action = ''
                    if cur_action == 'quest_dialog' and event.ui_element == third_button:
                        chosen_quest = third_quest
                        cancel_interactive_window()
                        cur_action = ''
                    if cur_action == 'shop_dialog' and ((first_button and event.ui_element == first_button)
                                                        or (second_button and event.ui_element == second_button)):
                        dict_parameter = ('DAMAGE' if event.ui_element == first_button else 'HP')
                        dict_in_use = (damage_coins_dict if dict_parameter == 'DAMAGE' else hp_coins_dict)
                        max_value = (4 if dict_parameter == 'DAMAGE' else 7)

                        if dict_in_use[characteristics[dict_parameter]] <= characteristics['COINS']:
                            characteristics['COINS'] -= dict_in_use[characteristics[dict_parameter]]
                            characteristics[dict_parameter] += (1 if dict_parameter == 'DAMAGE' else 2)

                            pygame.draw.rect(interactive_windows_group.sprites()[0].image, (0, 0, 0), (9, 185, 200, 20))
                            font = pygame.font.Font(None, 25)
                            text = font.render(f"You have {characteristics['COINS']} coins", True, (100, 255, 100))
                            interactive_windows_group.sprites()[0].image.blit(text, (15, 185))

                            write_characteristics_in_txt()

                            pygame_gui.windows.UIMessageWindow(
                                rect=pygame.Rect(width // 2 - 260 // 2, height // 2 - 200 // 2, 260, 200),
                                html_message=f'You have upgraded your {dict_parameter}!',
                                window_title='')

                            if characteristics[dict_parameter] == max_value:
                                event.ui_element.kill()
                                event.ui_element = None
                            else:
                                event.ui_element.set_text(
                                    f'Upgrade: {dict_in_use[characteristics[dict_parameter]]} coins')
                        else:
                            conformation_window = pygame_gui.windows.UIMessageWindow(
                                rect=pygame.Rect(width // 2 - 260 // 2, height // 2 - 200 // 2, 260, 200),
                                html_message="You don't have enough coins!",
                                window_title='',
                                manager=manager)

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

        screen.fill((0, 0, 0))

        manager.update(time_delta)
        all_sprites.update()
        interactive_windows_group.update()
        all_interactive_zones.update()

        all_sprites.draw(screen)
        if not pygame.sprite.spritecollideany(player, roof_group):
            roof_group.draw(screen)
        interactive_windows_group.draw(screen)
        manager.draw_ui(screen)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main_hub()
