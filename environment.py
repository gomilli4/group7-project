import numpy as np
import pygame

def grass_color_gradient(x):
    '''
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
    '''
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

def create_environment(num_cells_x, num_cells_y, cell_size):
    """
    Initializes the environement and creates the cells
    """
    env_grid = np.ones((num_cells_y, num_cells_x))
    env_grid = env_grid * 50

    hashing_grid = np.zeros((num_cells_y, num_cells_x), dtype=object)

    # Sprite group contains pygame sprite objects. Used for drawing groups of sprites
    # in one line vs having to use for loops in main simulation loop below
    env_cell_group = pygame.sprite.Group()

    # Generating environment cells
    for j in range(num_cells_x):
        for i in range(num_cells_y):
            hashing_grid[i, j] = []
            cell = Env_Cell(j * cell_size, i * cell_size, j, i, cell_size, cell_size, env_grid[i, j])
            env_cell_group.add(cell)

    return env_grid, env_cell_group, hashing_grid

def on_board(i, j, grid):
    """
    Code from CMSE 201, used for checking if neighboring cells are on the board
    """
    if i <= grid.shape[0] - 1 and i >= 0 and j <= grid.shape[1] - 1 and j >= 0:
        return True
    else:
        return False

def get_neighbor_values(i, j, board):
    """
    Code from CMSE 201, used to check the values of the neighboring cells.
    As per the grass growing rules, if a neighbor cell has an amount
    of grass > 0, the cell starts growing grass itself
    """
    neighborhood = [(i - 1, j), (i, j - 1), (i + 1, j), (i, j + 1)]

    neighbor_values = []
    for neighbor in neighborhood:
        if on_board(neighbor[0], neighbor[1], board):
            neighbor_values.append(board[neighbor[0], neighbor[1]])

    return neighbor_values

def advance_grid(grid, dt):
    """
    Code from CSME 201. Used to update the environment grid. The updated
    grid is used by the environment pygame sprite group to update their
    color on the screen
    """
    max_grass = 50
    grow_rate = 2

    new_grid = np.zeros_like(grid)

    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            """
            If cell has no grass and no neighbors with grass, it doesn't grow
            If cell has no grass and neighbors with grass, it will start to grow
            If cell has grass, it will grow until it reaches max_grass
            """
            if grid[x, y] == 0:
                if max_grass in get_neighbor_values(x, y, grid):
                    new_grid[x, y] = 0 + grow_rate * dt

            elif grid[x, y] > 0 and grid[x, y] < max_grass:
                next_value = grid[x, y] + grow_rate * dt
                if next_value > max_grass:
                    new_grid[x, y] = max_grass
                else:
                    new_grid[x, y] += grid[x, y] + grow_rate * dt

            elif grid[x, y] >= max_grass:
                new_grid[x, y] = max_grass

    return new_grid

class Env_Cell(pygame.sprite.Sprite):
    '''
    Cells for the environment grass grid. Inherits from pygame sprite class
    for drawing to the screen
    '''
    def __init__(self, x, y, id_x, id_y, width, height, grass):
        super().__init__()
        self.pos_x = x
        self.pos_y = y
        self.id_x = id_x
        self.id_y = id_y
        self.width = width
        self.height = height
        self.grass = grass
        
        # Pygame stuff for drawing cell to screen
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(grass_color_gradient(self.grass/50))
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.pos_x, self.pos_y]
    
    def update(self, grid):
        # gets the grass amount from the environment grid
        self.grass = grid[self.id_y, self.id_x]
        
        # updates its color in accordance with the grass_color_gradient function
        self.image.fill(grass_color_gradient(self.grass/50))
        
        # NOTE: 50 is the maximum grass amount per cell as decided in the
        # advance_grid function. It's probably best to find a way to pass
        # this variable to the update function to avoid future issues,
        # should we decide we want the maximum grass amount to vary
