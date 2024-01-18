import pygame
import sys
import os
import random
from collections import deque


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


def get_next_nodes_AI(x, y, level):
    check_next_node = lambda x, y: True if 0 <= x <= 9 and 0 <= y <= 4 and level[y][x] != 'b' else False
    ways = [-1, 0], [0, -1], [1, 0], [0, 1]
    return [(x + dx, y + dy) for dx, dy in ways if check_next_node(x + dx, y + dy)]


def bfs(start, goal, graph):
    queue = deque([start])
    visited = {start: None}
    can_find = False

    while queue:
        cur_node = queue.popleft()
        if cur_node == goal:
            can_find = True
            break

        next_nodes = graph[cur_node]
        for next_node in next_nodes:
            if next_node not in visited:
                queue.append(next_node)
                visited[next_node] = cur_node

    if not can_find:
        return None

    path = [goal]
    cur_node = goal
    while cur_node != start:
        cur_node = visited[cur_node]
        path.append(cur_node)

    path = list(reversed(path[:-1]))
    return path


def load_image(name, colorkey=None):
    fullname = os.path.join('data/Images', name)
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

    def take_damage(self):
        if self.hp:
            self.hp -= 1

        if self.hp == 0:
            self.kill()

    def point_in_rect(self, x, y):
        if self.rect.x < x < self.rect.x + self.rect.width and self.rect.y < y < self.rect.y + self.rect.height:
            return True
        return False

    def get_mode(self):
        return self.mode

    def get_hp(self):
        return self.hp

    def get_pos_as_board(self):
        pos_x = (self.rect.x - 50) // 64
        pos_y = (self.rect.y - 50) // 64
        return pos_x, pos_y


class Wall(pygame.sprite.Sprite):
    def __init__(self, start_pos, width, height, color, sprite_group, all_sprites_group):
        super().__init__(sprite_group, all_sprites_group)
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
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


class Quest_as_interface(pygame.sprite.Sprite):
    def __init__(self, images, quantities, coords, sprite_group):
        super().__init__(sprite_group)

        self.image = pygame.Surface([520, 40])
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect().move(coords[0], coords[1])

        for x, image, quantity in zip(range(0, 420, 140), images, quantities):
            font = pygame.font.Font(None, 40)
            text = font.render(f'/{quantity}', True, (100, 255, 100))
            self.image.blit(text, (x + 25, 10))

            self.image.blit(image, (x + 60, 0))


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, player_group, all_sprites_group, sprite_group_collisions, image=None, hp=None):
        super().__init__(player_group, all_sprites_group)
        if image:
            player_image = image
        else:
            player_image = pygame.surface([64, 64])
            player_image.fill((0, 0, 0))

        self.image = player_image
        self.rect = self.image.get_rect().move(
            64 * pos_x + 49 + 1, 64 * pos_y + 49 + 1)
        self.sprite_group_collisions = sprite_group_collisions
        self.direction_x = 0
        self.direction_y = 0
        self.current_tool = 'pick'
        self.hit_direction_x = 0
        self.hit_direction_y = 0
        with open('data/characteristics.txt') as txt_file:
            data = [i.strip() for i in txt_file.readlines()]
        self.axe_damage = int(data[1].split()[1])
        if hp is None:
            self.hp = int(data[0].split()[1])
        else:
            self.hp = hp
        self.velocity = 2

        self.anim_images = []
        for i in range(1, 4):
            image = pygame.image.load(
                f"data/images/dwfw/dwfw{i}.png").convert_alpha()
            self.anim_images.append(image)

        self.anim_left_images = []
        for i in range(1, 4):
            image = pygame.image.load(
                f"data/images/dwrightleft/dwrightleft{i}.png").convert_alpha()
            self.anim_left_images.append(image)

        self.anim_right_images = []
        for i in range(1, 4):
            image = pygame.image.load(
                f"data/images/dwrightleft/dwrightleft{i}.png").convert_alpha()
            image = pygame.transform.flip(image, True, False)
            self.anim_right_images.append(image)

        self.anim_back_images = []
        for i in range(1, 4):
            image = pygame.image.load(
                f"data/images/dwback/dwback{i}.png").convert_alpha()
            self.anim_back_images.append(image)

        self.anim_idle_image = pygame.image.load(
            "data/images/dwstay/defdw_pickaxe.png").convert_alpha()

        self.anim_frame = 0
        self.anim_tick = 0
        self.anim_speed = 10

    def set_direction(self, direction_x, direction_y):
        self.direction_x = direction_x
        self.direction_y = direction_y

    def set_hit_direction(self, x, y):
        self.hit_direction_x = x
        self.hit_direction_y = y

    def update(self):
        self.rect = self.rect.move(
            self.direction_x * self.velocity, self.direction_y * self.velocity)
        if pygame.sprite.spritecollideany(self, self.sprite_group_collisions):
            self.rect = self.rect.move(
                -self.direction_x * self.velocity, -self.direction_y * self.velocity)
        if self.direction_x == 0 and self.direction_y == 0:
            self.animate_idle()
        elif self.direction_x > 0:
            self.animate_right_movement()
        elif self.direction_x < 0:
            self.animate_left_movement()
        elif self.direction_y < 0:
            self.animate_back_movement()
        else:
            self.animate_movement()

    def animate_movement(self):
        self.anim_tick += 1
        if self.anim_tick >= self.anim_speed:
            self.anim_tick = 0
            self.anim_frame += 1
            if self.anim_frame >= len(self.anim_images):
                self.anim_frame = 0

        self.image = self.anim_images[self.anim_frame]

    def animate_left_movement(self):
        self.anim_tick += 1
        if self.anim_tick >= self.anim_speed:
            self.anim_tick = 0
            self.anim_frame += 1
            if self.anim_frame >= len(self.anim_left_images):
                self.anim_frame = 0

        self.image = self.anim_left_images[self.anim_frame]

    def animate_right_movement(self):
        self.anim_tick += 1
        if self.anim_tick >= self.anim_speed:
            self.anim_tick = 0
            self.anim_frame += 1
            if self.anim_frame >= len(self.anim_right_images):
                self.anim_frame = 0

        self.image = self.anim_right_images[self.anim_frame]

    def animate_idle(self):
        self.image = self.anim_idle_image

    def animate_back_movement(self):
        self.anim_tick += 1
        if self.anim_tick >= self.anim_speed:
            self.anim_tick = 0
            self.anim_frame += 1
            if self.anim_frame >= len(self.anim_back_images):
                self.anim_frame = 0

        self.image = self.anim_back_images[self.anim_frame]

    def take_damage(self):
        if self.hp:
            self.hp -= 1

        if self.hp == 0:
            self.kill()

    def get_direction(self):
        return self.direction_x, self.direction_y

    def get_hit_direction(self):
        return self.hit_direction_x, self.hit_direction_y

    def get_centre_coords(self):
        return self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2

    def get_current_tool(self):
        return self.current_tool

    def get_axe_damage(self):
        return self.axe_damage

    def get_hp(self):
        return self.hp

    def change_current_tool(self):
        self.current_tool = 'axe' if self.current_tool == 'pick' else 'pick'

    def point_in_rect(self, x, y):
        if self.rect.x < x < self.rect.x + self.rect.width and self.rect.y < y < self.rect.y + self.rect.height:
            return True
        return False

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.animate_movement()
            elif event.key == pygame.K_a:
                self.animate_left_movement()
            elif event.key == pygame.K_d:
                self.animate_right_movement()
            elif event.key == pygame.K_w:
                self.animate_back_movement()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                self.animate_idle()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, hp, mode, player, *sprite_groups):
        super().__init__(*sprite_groups)

        surface = pygame.Surface([32, 32])
        surface.fill((200, 200, 200))
        self.image = surface

        self.rect = self.image.get_rect()
        self.rect = self.rect.move(64 * pos_x + 50 + (64 // 2 - self.rect.width // 2), 64 * pos_y + 50 +
                                   (64 // 2 - self.rect.height // 2))
        self.direction_x = 0
        self.direction_y = 0
        self.hit_direction_x = 0
        self.hit_direction_y = 0
        self.route = []
        self.hp = hp
        self.mode = mode
        self.VELOCITY = 1
        self.timer = 0
        self.last_hit_time = 0
        self.cooldown = False
        self.player = player

    def set_direction(self, direction_x, direction_y):
        self.direction_x = direction_x
        self.direction_y = direction_y

    def set_hit_direction(self, x, y):
        self.hit_direction_x = x
        self.hit_direction_y = y

    def get_direction(self):
        return (self.direction_x, self.direction_y)

    def get_hit_direction(self):
        return self.hit_direction_x, self.hit_direction_y

    def get_centre_coords(self):
        return self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2

    def get_pos_as_board(self):   # отсчет с нуля
        pos_x = (self.rect.x + self.rect.width // 2 - 50) // 64
        pos_y = (self.rect.y + self.rect.height // 2 - 50) // 64
        return pos_x, pos_y

    def take_damage(self, damage):
        self.hp -= damage

        if self.hp <= 0:
            self.kill()

    def get_mode(self):
        return self.mode

    def get_hp(self):
        return self.hp

    def update(self):
        if self.route and not self.cooldown:
            if self.get_centre_coords() == (self.route[0][0] * 64 + 50 + 32, self.route[0][1] * 64 + 50 + 32):
                self.route = self.route[1:]
            elif self.get_pos_as_board() == self.route[-1]:
                self.route = []

            if self.route != []:
                direction_x, direction_y = 0, 0
                if self.get_centre_coords()[0] != self.route[0][0] * 64 + 50 + 32:
                    direction_x = (self.route[0][0] * 64 + 50 + 32 - self.get_centre_coords()[0]) / \
                        abs(self.route[0][0] * 64 + 50 + 32 - self.get_centre_coords()[0])
                if self.get_centre_coords()[1] != self.route[0][1] * 64 + 50 + 32:
                    direction_y = (self.route[0][1] * 64 + 50 + 32 - self.get_centre_coords()[1]) / \
                        abs(self.route[0][1] * 64 + 50 + 32 - self.get_centre_coords()[1])

                self.set_direction(direction_x * self.VELOCITY, direction_y * self.VELOCITY)
                self.set_hit_direction(direction_x, direction_y)
                self.rect = self.rect.move(self.direction_x, self.direction_y)

        if self.timer - self.last_hit_time > 1000 and self.cooldown:
            self.cooldown = False
            self.hit()

        if self.route == [] and not self.cooldown:
            self.stun_lock()

        self.timer = pygame.time.get_ticks()

    def hit(self):
        if abs(self.player.get_centre_coords()[0] - self.get_centre_coords()[0]) <= 64 and \
                abs(self.player.get_centre_coords()[1] - self.get_centre_coords()[1]) <= 64:
            self.player.take_damage()

    def stun_lock(self):
        self.set_direction(0, 0)
        self.cooldown = True
        self.last_hit_time = pygame.time.get_ticks()

    def point_in_rect(self, x, y):
        if self.rect.x < x < self.rect.x + self.rect.width and self.rect.y < y < self.rect.y + self.rect.height:
            return True
        return False

    def determine_the_route(self, level, player_coords):
        graph = {}

        for y, row in enumerate(level):
            for x, col in enumerate(row):
                if col != 'b':
                    graph[(x, y)] = graph.get((x, y), []) + get_next_nodes_AI(x, y, level)

        self.route = bfs(self.get_pos_as_board(), player_coords, graph)
