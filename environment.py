import numpy as np
import pygame

max_grass = 50.0
grow_rate = 3

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

    Args:
    - x (double): Value of grass to be colored.
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

def create_environment(num_cells_x, num_cells_y, cell_size):
    """
    Initializes the environment and creates the cells

    Args:
    - num_cells_x (int): Number of cells in the x-axis.
    - num_cells_y (int): Number of cells in the y-axis.
    - cell_size (int): Size of each cell.
    """
    env_grid = np.full((num_cells_y, num_cells_x), max_grass)

    hashing_grid = np.zeros((num_cells_y, num_cells_x), dtype=object)

    # Sprite group contains pygame sprite objects. Used for drawing groups of sprites
    # in one line vs having to use for loops in main simulation loop below
    env_cell_group = pygame.sprite.Group()

    # Generating environment cells
    for x in range(num_cells_x):
        for y in range(num_cells_y):
            hashing_grid[y, x] = []
            cell = Env_Cell(x * cell_size, y * cell_size, x, y, cell_size)
            env_cell_group.add(cell)

    return env_grid, env_cell_group, hashing_grid

def on_board(self, x, y, grid):
    """
    Check if neighboring cells are within the bounds of the simulation.

    Args:
    - x (int): Row index.
    - y (int): Column index.
    - grid (numpy.ndarray): The grid to check against.

    Returns:
    - bool: True if neighboring cell is within the grid, False otherwise.
    """
    if x <= grid.shape[0] - 1 and x >= 0 and y <= grid.shape[1] - 1 and y >= 0:
        return True
    else:
        return False

def get_neighbor_values(x, y, board):
    """
    Code from CMSE 201, used to check the values of the neighboring cells.
    As per the grass growing rules, if a neighbor cell has an amount
    of grass > 0, the cell starts growing grass itself

    Args:
    - x (int): x-coordinate of the cell.
    - y (int): y-coordinate of the cell.
    - board (numpy.ndarray): Board representing the environment.

    Returns:
    - neighbor_values (list): List of values of neighboring cells.
    """
    neighborhood = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]

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

    Args:
    - grid (numpy.ndarray): Grid representing the environment.
    - dt (float): Time step for updating the grid.

    Returns:
    - new_grid (numpy.ndarray): Updated grid with grass growth.
    """
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
                    new_grid[x, y] = grow_rate * dt

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
    """
    Cells for the environment grass grid. Inherits from pygame sprite class
    for drawing to the screen
    """
    def __init__(self, x, y, id_x, id_y, size):
        """
        Initializes an instance of Env_Cell.
        
        Args:
        - x (int): x-coordinate of the cell's top-left corner.
        - y (int): y-coordinate of the cell's top-left corner.
        - id_x (int): x-index of the cell in the grid.
        - id_y (int): y-index of the cell in the grid.
        - size (int): Size of the cell (width and height).
        """
        super().__init__()
        self.pos_x = x
        self.pos_y = y
        self.id_x = id_x
        self.id_y = id_y
        self.size = size
        self.grass = 50 # Initialize to maximum grass height

        # Pygame stuff for drawing cell to screen
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(grass_color_gradient(self.grass / 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.pos_x, self.pos_y]

    def update(self, grid):
        """
        Updates the cell's attributes based on the current state of the environment grid.

        Args:
        - grid (numpy array): Grid representing the environment.
        """
        # gets the grass amount from the environment grid
        self.grass = grid[self.id_y, self.id_x]

        # updates its color in accordance with the grass_color_gradient function
        self.image.fill(grass_color_gradient(self.grass / 50))

        # NOTE: 50 is the maximum grass amount per cell as decided in the
        # advance_grid function. It's probably best to find a way to pass
        # this variable to the update function to avoid future issues,
        # should we decide we want the maximum grass amount to vary