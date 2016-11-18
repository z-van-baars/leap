from constants import colors
import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = pygame.Surface([width, height])
        self.sprite.image.fill(colors["Background Dark Blue"])
        self.sprite.image = self.sprite.image.convert_alpha()
        self.sprite.rect = self.sprite.image.get_rect()


class DisplayLayer(Background):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.sprite.image.fill(colors["Key"])
        self.sprite.image.set_colorkey(colors["Key"])
        self.sprite.image = self.sprite.image.convert_alpha()

    def update(self, new_item):
        self.sprite.image.blit(new_item.sprite.image, [new_item.x, new_item.y])


class RailLayer(DisplayLayer):
    def __init__(self, width, height):
        super().__init__(width, height)

    def update(self, rail):
        self.sprite.image.blit(rail.sprite.image, [0, 0])
