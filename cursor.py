import pygame

def cursor_bunnish():
    pygame.mouse.set_visible(False)  # システムカーソルを非表示にする

def cursor_image():
    pygame.image.load("Assets/Red+.png")

def cursor_position():
    pygame.mouse.get_pos()


"""
class Cursor:
    def __init__(self, file_path, screen):
        self.screen = screen
        self.image = pygame.image.load(file_path).convert_alpha()
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)  # システムカーソルを非表示にする

    def render(self, x, y):
        self.rect.center = (x, y)
        self.screen.blit(self.image, self.rect)
"""