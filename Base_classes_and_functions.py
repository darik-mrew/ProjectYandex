import pygame
import sys
import os
import random


def intersection_rectangles(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    ax2 = ax1 + ax2
    ay2 = ay1 + ay2
    bx2 = bx1 + bx2
    by2 = by1 + by2
    s1 = (ax1 >= bx1 and ax1 <= bx2) or (ax2 >= bx1 and ax2 <= bx2)
    s2 = (ay1 >= by1 and ay1 <= by2) or (ay2 >= by1 and ay2 <= by2)
    s3 = (bx1 >= ax1 and bx1 <= ax2) or (bx2 >= ax1 and bx2 <= ax2)
    s4 = (by1 >= ay1 and by1 <= ay2) or (by2 >= ay1 and by2 <= ay2)
    return True if ((s1 and s2) or (s3 and s4)) or ((s1 and s4) or (s3 and s2)) else False


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image, *sprite_groups, hp=None, mode=None):
        super().__init__(*sprite_groups)
        self.image = image
        self.rect = self.image.get_rect().move(
            64 * pos_x + 50, 64 * pos_y + 50)
        self.hp = hp
        self.mode = mode

    def update(self):
        try:
            if [int(self.hp)] and self.hp == 0:
                self.kill()
        except TypeError:
            pass

    def get_damage(self):
        if self.hp:
            self.hp -= 1


class Wall(pygame.sprite.Sprite):
    def __init__(self, start_pos, width, height, sprite_group, all_sprites_group):
        super().__init__(sprite_group, all_sprites_group)
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))
        self.rect = pygame.Rect(start_pos[0], start_pos[1], width, height)


class Interactive_Zone():
    def __init__(self, rect_zone, player, sprite_group):
        self.player = player
        self.rect_x = rect_zone[0]
        self.rect_y = rect_zone[1]
        self.width = rect_zone[2]
        self.height = rect_zone[3]
        self.clue_sprite_group = sprite_group
        self.clue = None

    def create_clue(self):
        self.clue = pygame.sprite.Sprite(self.clue_sprite_group)
        self.clue.image = pygame.Surface([40, 40])
        self.clue.rect = self.clue.image.get_rect()
        font = pygame.font.Font(None, 40)
        text = font.render('E', True, (100, 255, 100))
        self.clue.image.blit(text, (10, 10))
        pygame.draw.rect(self.clue.image, (0, 255, 0), (0, 0, 40, 40), 2)

    def player_in_zone(self):
        if intersection_rectangles(self.rect_x, self.rect_y, self.width, self.height, self.player.rect.x,
                                   self.player.rect.y, self.player.rect.width, self.player.rect.height):
            return True

    def update(self):
        if self.player_in_zone():
            if self.clue is None:
                self.create_clue()
            self.clue.rect.x = self.player.rect.x
            self.clue.rect.y = self.player.rect.y - 50
        else:
            if self.clue is not None:
                self.clue.kill()
            self.clue = None


class Interactive_Zones_container():
    def __init__(self, *interactive_zones):
        self.container = list(interactive_zones)

    def append(self, interactive_zone):
        self.container.append(interactive_zone)

    def update(self):
        for i in self.container:
            i.update()


class Quest_as_window(pygame.sprite.Sprite):
    def __init__(self, images, quantities, reward, coords, sprite_group):
        super().__init__(sprite_group)

        self.image = pygame.Surface([400, 70])
        self.image.fill((0, 0, 0))
        pygame.draw.rect(self.image, (0, 255, 0), (0, 0, 110 * len(images), 70), 2)

        self.rect = self.image.get_rect().move(coords[0], coords[1])

        for x, image in zip(range(41, 330, 110), images):
            self.image.blit(image, (x, 3))

        for x, quantity in zip(range(5, 330, 110), quantities):
            font = pygame.font.Font(None, 80)
            text = font.render(f'{quantity}', True, (100, 255, 100))
            self.image.blit(text, (x, 10))

        font = pygame.font.Font(None, 60)
        text = font.render(f'{reward}', True, (100, 255, 100))
        self.image.blit(text, (250 - text.get_width() // 2, 10))

        pygame.draw.circle(self.image, (248, 219, 22), (302, 32), 30)
        pygame.draw.circle(self.image, (199, 174, 8), (302, 32), 15)


class Quest_as_interface(pygame.sprite.Sprite):  # неправильная отрисовка, координаты должны быть указаны в системе спрайта
    def __init__(self, images, quantities, coords, sprite_group):
        super().__init__(sprite_group)

        self.image = pygame.Surface([520, 40])
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect().move(coords[0], coords[1])

        for x, image, quantity in zip(range(0, 420, 140), images, quantities):
            font = pygame.font.Font(None, 40)
            text = font.render(f'/{quantity}', True, (100, 255, 100))
            self.image.blit(text, (x + 25, 10))

            self.image.blit(image, (x + 60, 5))


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, player_group, all_sprites_group, sprite_group_collisions, image=None):
        super().__init__(player_group, all_sprites_group)
        if image:
            player_image = image
        else:
            player_image = pygame.Surface([64, 64])
            player_image.fill((0, 0, 0))

        self.image = player_image
        self.rect = self.image.get_rect().move(
            64 * pos_x + 49 + 1, 64 * pos_y + 49 + 1)
        self.sprite_group_collisions = sprite_group_collisions
        self.direction_x = 0
        self.direction_y = 0
        self.current_tool = 'pick'

    def set_direction(self, direction_x, direction_y):
        self.direction_x = direction_x
        self.direction_y = direction_y

    def update(self):
        self.rect = self.rect.move(self.direction_x, self.direction_y)
        if pygame.sprite.spritecollideany(self, self.sprite_group_collisions):
            self.rect = self.rect.move(-self.direction_x, -self.direction_y)

    def get_direction(self):
        return (self.direction_x, self.direction_y)

