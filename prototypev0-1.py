import matplotlib.pyplot as plt
import numpy as np
import pygame
import random
import time

from envcell import EnvCell
from herbivore import Herbivore


def create_environment(num_cells_x, num_cells_y, cell_size):
    env_grid = np.zeros((num_cells_y, num_cells_x))
    env_grid[0, 0] = 50
    env_grid[15, 30] = 50

    # Sprite group contains pygame sprite objects. Used for drawing groups of sprites
    # in one line vs having to use for loops in main simulation loop below
    env_cell_group = pygame.sprite.Group()

    # Generating environment cells
    for j in range(num_cells_x):
        for i in range(num_cells_y):
            cell = EnvCell(
                j * cell_size, i * cell_size, j, i, cell_size, cell_size, env_grid[i, j]
            )
            env_cell_group.add(cell)

    return env_grid, env_cell_group


def onBoard(i, j, grid):
    """
    Code from CMSE 201, used for checking if neighboring cells are on the board
    """
    if i <= grid.shape[0] - 1 and i >= 0 and j <= grid.shape[1] - 1 and j >= 0:
        return True
    else:
        return False


def getNeighborValues(i, j, board):
    """
    Code from CMSE 201, used to check the values of the neighboring cells.
    As per the grass growing rules, if a neighbor cell has an amount
    of grass > 0, the cell starts growing grass itself
    """
    neighborhood = [(i - 1, j), (i, j - 1), (i + 1, j), (i, j + 1)]

    neighbor_values = []
    for neighbor in neighborhood:
        if onBoard(neighbor[0], neighbor[1], board):
            neighbor_values.append(board[neighbor[0], neighbor[1]])

    return neighbor_values


def advance_grid(grid, dt):
    """
    Code from CSME 201. Used to update the environment grid. The updated
    grid is used by the environment pygame sprite group to update their
    color on the screen
    """
    max_grass = 50
    grow_rate = 30

    new_grid = np.zeros_like(grid)

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            """
            If cell has no grass and no neighbors with grass, it doesn't grow
            If cell has no grass and neighbors with grass, it will start to grow
            If cell has grass, it will grow until it reaches max_grass
            """
            if grid[i, j] == 0:
                neighbor_values = getNeighborValues(i, j, grid)
                for value in neighbor_values:
                    if value > 0:
                        new_grid[i, j] = 0 + grow_rate * dt
                        break

            if grid[i, j] > 0 and grid[i, j] < max_grass:
                next_value = grid[i, j] + grow_rate * dt
                if next_value > max_grass:
                    new_grid[i, j] = max_grass
                else:
                    new_grid[i, j] += grid[i, j] + grow_rate * dt

            if grid[i, j] >= max_grass:
                new_grid[i, j] = max_grass

    return new_grid


# General setup for pygame
pygame.init()

# Defining the screen size
width = 1300
height = 600
screen = pygame.display.set_mode((width, height))

# Set up for environment
cell_size = 25
num_cells_x = round(width / cell_size)
num_cells_y = round(height / cell_size)

# env_grid is the numpy array that holds the grass values,
# env_cell_group is the pygame sprite group for drawing the
# grass cells to the screen
env_grid, env_cell_group = create_environment(num_cells_x, num_cells_y, cell_size)

# test genes dictionary


def random_genes():
    colors = ["blue", "red"]
    species_type = random.randint(0, 1)
    genes = {
        "speed": [random.randint(50, 150), random.randint(50, 150)],
        "turn-speed": [
            random.randint(50, 101) * np.pi / 180,
            random.randint(50, 101) * np.pi / 180,
        ],
        "fov": [180 * np.pi / 180, 180 * np.pi / 180],
        "view-dist": [60, 60],
        "max-energy": [100, 100],
        "metabolism-rate": [5, 5],
        "find-mate-rate": [3, 3],
        "max-desire-to-mate": random.randint(
            0, 50
        ),  # To mate desire of two species must added up must be above 60
        "sex": random.randint(0, 1),  # male = [0, 1] or [1, 0], female = [0, 0]
        "species": species_type,  # 2 different types of species with number 0 = prey, and 1 = predator
        "color": colors[species_type],
    }
    return genes


def reproduce(Herbivore1, Herbivore2):
    child = Herbivore(
        genes=random_genes(),
        x=random.randint(0, 3000) / 3,
        y=random.randint(0, 1000) / 3,
        orientation=-45 * np.pi / 180,
        strength=random.randint(5, 20),
    )
    Herbivore1.genes["max-desire-to-mate"] = -1000
    Herbivore2.genes["max-desire-to-mate"] = -1000
    child.genes["max-desire-to-mate"] = 0  # Resets to prevent constant reproduction
    child.genes["color"] = Herbivore1.genes[
        "color"
    ]  # Make sures child has some color as parents
    child.genes["species"] = Herbivore1.genes[
        "species"
    ]  # Make sures child is same species
    return child


# test creature
count = 0
creature_group = pygame.sprite.Group()

# Adds a hundred animals to environment
for i in range(100):
    creature_group.add(
        Herbivore(
            random_genes(),
            random.randint(0, 3000) / 3,
            random.randint(0, 1000) / 3,
            -45 * np.pi / 180,
            strength=random.randint(5, 20),
        )
    )
    count += 1


# Main simulation loop. Instead of running until user clicks exit, can use conditions
previous_time = time.time()
carrying_capacity = random.randint(count * 2, count * 4)
data_list = []  # List containing prey,predator counts and time
time_count = 0
loop = True
while True:

    # Used to ensure framerate independence
    dt = time.time() - previous_time
    previous_time = time.time()

    for event in pygame.event.get():  # pygame event handling
        if event.type == pygame.QUIT:  # if exit button is clicked

            pygame.quit()  # quits pygame module
            # sys.exit() # exits program
            loop = False

    if not loop:
        break
    env_cell_group.update(env_grid)
    env_grid = advance_grid(env_grid, dt)

    creature_group.update(env_grid, dt)

    # These counts are meant for demonstrating stable predator prey relationships

    prey_count = 0
    predator_count = 0

    if count > 1:  # To prevent indexing errors
        for i in range(count):
            # Compares every animal within environment to each other
            for j in range(i + 1, count):
                if (
                    creature_group.sprites()[i].genes["species"]
                    != creature_group.sprites()[j].genes["species"]
                ):  # Compares species type
                    # Checks to see if two species are close to each other
                    if (
                        abs(
                            creature_group.sprites()[i].pos[0]
                            - creature_group.sprites()[j].pos[0]
                        )
                        < 50
                    ) and (
                        abs(
                            creature_group.sprites()[i].pos[1]
                            - creature_group.sprites()[j].pos[1]
                        )
                        < 50
                    ):

                        # Chceks to see if the species[i] is a predator and species[j] is prey since predators have the value 1 while prey have the value 0
                        if (
                            creature_group.sprites()[i].genes["species"]
                            > creature_group.sprites()[j].genes["species"]
                        ):
                            # Checks to see if predator is faster than prey because if so then prey is killed
                            if (
                                creature_group.sprites()[i].genes["speed"]
                                > creature_group.sprites()[j].genes["speed"]
                            ):
                                creature_group.remove(creature_group.sprites()[j])
                                count -= 1
                                break
                        elif (
                            creature_group.sprites()[i].genes["species"]
                            < creature_group.sprites()[j].genes["species"]
                        ):
                            if (
                                creature_group.sprites()[i].genes["speed"]
                                < creature_group.sprites()[j].genes["speed"]
                            ):
                                creature_group.remove(creature_group.sprites()[i])
                                count -= 1
                                break

                # Check for reproduction
                if (
                    creature_group.sprites()[i].genes["species"]
                    == creature_group.sprites()[j].genes["species"]
                ):
                    if (
                        creature_group.sprites()[i].genes["max-desire-to-mate"]
                        + creature_group.sprites()[j].genes["max-desire-to-mate"]
                    ) > 60:
                        child = reproduce(
                            Herbivore1=creature_group.sprites()[i],
                            Herbivore2=creature_group.sprites()[j],
                        )
                        creature_group.add(child)
                        print("Reproduce Done")

    for i in creature_group.sprites():
        i.genes["max-desire-to-mate"] += random.randint(5, 20)

    for i in creature_group.sprites():
        if i.genes["species"] == 0:
            prey_count += 1
        else:
            predator_count += 1
    print(predator_count)
    # This list is used for modeling predator prey relations
    data_list.append([prey_count, predator_count, time_count])

    time_count += 1

    env_cell_group.draw(screen)
    creature_group.draw(screen)

    env_cell_group.draw(screen)
    creature_group.draw(screen)

    pygame.display.flip()


# plt_1 = plt.figure(figsize=(30, 30))
# plt.plot(data_list[:][2],data_list[:][0])
predator_count = []
prey_count = []
time_count = []
for i in data_list:
    predator_count.append(i[1])
    prey_count.append(i[0])
    time_count.append(i[2])

# plt.plot(time_count,prey_count)
# plt.xlabel = "Time"
# plt.ylabel = "Prey_count"

# plt.plot(time_count,predator_count)
# plt.xlabel = "Time"
# plt.ylabel = "Predator_count"

# plt.show()
