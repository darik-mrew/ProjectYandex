import pygame_gui
from Hub_gameplay import main_hub
from Base_classes_and_functions import *


def create_button():
    all_sprites = pygame.sprite.Group()

    button = pygame.sprite.Sprite(all_sprites)
    button.rect = pygame.Rect(200 - 10, 150 - 10, 360, 140)
    button.image = pygame.Surface([360, 140])
    pygame.draw.rect(button.image, (100, 255, 100), (0, 0, button.rect.width, button.rect.height), 5)

    hovered_space = pygame.sprite.Sprite(all_sprites)
    hovered_space.rect = pygame.Rect(195, 145, 350, 130)
    hovered_space.image = pygame.Surface([350, 130])
    hovered_space.image.fill((0, 0, 0))

    return all_sprites, hovered_space


if __name__ == '__main__':
    pygame.init()
    size = width, height = 740, 420
    screen = pygame.display.set_mode(size)
    manager = pygame_gui.UIManager((width, height))
    clock = pygame.time.Clock()

    is_hovered = False
    all_sprites, hovered_space = create_button()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

            if event.type == pygame.MOUSEMOTION and 200 < event.pos[0] < width - 200 and 150 < event.pos[1] <\
                    height - 150:
                is_hovered = True
            else:
                is_hovered = False

            if event.type == pygame.MOUSEBUTTONDOWN and 200 < event.pos[0] < width - 200 and 150 < event.pos[1] <\
                    height - 150:
                main_hub()

        screen.fill((0, 0, 0))

        if is_hovered:
            hovered_space.image.fill((0, 100, 0))
        else:
            hovered_space.image.fill((0, 0, 0))
        font = pygame.font.Font(None, 100)
        text = font.render('Wake up?', True, (100, 255, 100))
        hovered_space.image.blit(text, (10, 30))
        font = pygame.font.Font(None, 90)
        text = font.render('Smeshnulik: the game', True, (100, 255, 100))
        screen.blit(text, (40, 50))

        all_sprites.draw(screen)

        pygame.display.flip()
