import pygame


def grass_color_gradient(x):
    """
    Dirt to grass gradient generated from colordesigner.io/gradient-generator.
    Used website because RGB color space is nonlinear apparently and my homemade
    interpolation didn't work

    x is the current grass amount divided by the maximum grass (set to 50)

    (205, 133, 63)
    (193, 134, 50)
    (180, 136, 38)
    (165, 137, 27)
    (150, 138, 16)
    (133, 139, 8)
    (114, 140, 7)
    (94, 140, 13)
    (69, 140, 23)
    (34, 139, 34)

    Smooth interpolation may be possible through some other method.
    Look into HSV or HSL
    """
    if 0 <= x and x < 0.1:
        return (205, 133, 63)
    elif 0.1 <= x and x < 0.2:
        return (193, 134, 50)
    elif 0.2 <= x and x < 0.3:
        return (180, 136, 38)
    elif 0.3 <= x and x < 0.4:
        return (165, 137, 27)
    elif 0.4 <= x and x < 0.5:
        return (150, 138, 16)
    elif 0.5 <= x and x < 0.6:
        return (133, 139, 8)
    elif 0.6 <= x and x < 0.7:
        return (114, 140, 7)
    elif 0.7 <= x and x < 0.8:
        return (94, 140, 13)
    elif 0.8 <= x and x < 0.9:
        return (69, 140, 23)
    elif 0.9 <= x and x <= 1.0:
        return (34, 139, 34)
    else:
        return (205, 133, 63)


class EnvCell(pygame.sprite.Sprite):
    """
    Cells for the environment grass grid. Inherits from pygame sprite class
    for drawing to the screen
    """

    def __init__(self, x, y, cell_size, grass):
        super().__init__()
        self.pos_x = x * cell_size
        self.pos_y = y * cell_size
        self.id_x = x
        self.id_y = y
        self.cell_size = cell_size
        self.grass = grass

        # Pygame stuff for drawing cell to screen
        self.image = pygame.Surface([self.cell_size, self.cell_size])
        self.image.fill(grass_color_gradient(self.grass / 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.pos_x, self.pos_y]

    def update(self, grid):
        # gets the grass amount from the environment grid
        self.grass = grid[self.id_y, self.id_x]

        # updates its color in accordance with the grass_color_gradient function
        self.image.fill(grass_color_gradient(self.grass / 50))

        # NOTE: 50 is the maximum grass amount per cell as decided in the
        # advance_grid function. It's probably best to find a way to pass
        # this variable to the update function to avoid future issues,
        # should we decide we want the maximum grass amount to vary
