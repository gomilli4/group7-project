import matplotlib.pyplot as plt
import numpy as np
import pygame
import random
import time

from animal import Animal
from envcell import EnvCell
from grid_functions import get_neighbor_values

# Constants
max_grass_height = 50
grass_growth_rate = 30
env_width = 50
env_height = 25
cell_size = 25


def create_environment(num_cells_x, num_cells_y):
    # Creates grid of zeroes, aka no grass
    grass_grid = np.full((num_cells_x, num_cells_y), max_grass_height)

    # Sprite group contains pygame sprite objects. Used for drawing groups of sprites
    # in one line vs having to use for loops in main simulation loop below
    env_cell_group = pygame.sprite.Group()

    # Generating environment cells
    for x_pos in range(num_cells_x):
        for y_pos in range(num_cells_y):
            cell = EnvCell(x_pos, y_pos, cell_size, max_grass_height)
            env_cell_group.add(cell)

    return grass_grid, env_cell_group


def grow_grass(grass_grid, timestep):
    """
    Code from CSME 201. Used to update the environment grid. The updated
    grid is used by the environment pygame sprite group to update their
    color on the screen
    """
    new_grid = np.zeros_like(grass_grid)

    for x in range(grass_grid.shape[0]):
        for y in range(grass_grid.shape[1]):
            """
            If cell has no grass and no neighbors with grass, it doesn't grow
            If cell has no grass and neighbors with grass, it will start to grow
            If cell has grass, it will grow until it reaches max_grass
            """
            if grass_grid[x, y] == 0:
                if 50 in get_neighbor_values(x, y, grass_grid):
                    new_grid[x, y] = 0 + grass_growth_rate * timestep

            elif grass_grid[x, y] < max_grass_height:
                next_value = grass_grid[x, y] + grass_growth_rate * timestep
                if next_value > max_grass_height:
                    next_value = max_grass_height
                new_grid[x, y] = next_value

            else:
                new_grid[x, y] = grass_grid[x, y]

    return new_grid


# General setup for pygame
pygame.init()

# Defining the screen size
screen = pygame.display.set_mode((env_width * cell_size, env_height * cell_size))

# env_grid is the numpy array that holds the grass values,
# env_cell_group is the pygame sprite group for drawing the
# grass cells to the screen
grass_grid, env_cell_group = create_environment(env_width, env_height)

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
        "max-energy": 100,
        "metabolism-rate": 5,
        "find-mate-rate": 3,
        "max-desire-to-mate": random.randint(
            0, 50
        ),  # To mate desire of two species must added up must be above 60
        "sex": random.randint(0, 1),  # male = [0, 1] or [1, 0], female = [0, 0]
        "species": species_type,  # 2 different types of species with number 0 = prey, and 1 = predator
        "color": colors[species_type],
    }
    return genes


def reproduce(Animal1, Animal2):
    """
    Function that reproduces species
    Parameters: Amimal1: Parent 1, Animal2: Parent2
    Return: Child of parents
    """
    child = Animal(
        genes=Animal1.genes,
        x=random.randint(0, env_width)*cell_size,
        y=random.randint(0, env_height)*cell_size,
        orientation=-45 * np.pi / 180,
        strength=random.randint(5, 20),
    )
    Animal1.genes["max-desire-to-mate"] = -1000
    Animal2.genes["max-desire-to-mate"] = -1000
    child.genes["max-desire-to-mate"] = 0  # Resets to prevent constant reproduction

    return mutation(child)


def mutation(child):
    """
    Function that may mutate newly produced child
    Parameters: Child: Child that was just produced from reproduce function
    Returns: Child that may have been mutated
    """
    # color  mutation
    if random.random() < 0.25:  # 0 represents no mutation and 75% chance of ocurring, #1 represents 25% of occurring
        child.genes["color"] = np.random.choice(
            ["blue", "red", "yellow", "purple", "black"],
            p=[0.35, 0.35, 0.15, 0.10, 0.05],
        )
        child.picture.fill(
            child.genes["color"], special_flags=pygame.BLEND_MULT
        )  # This changes the color being displayed in the simulation

    # Turn speed mutation
    if random.random() < 0.25:  # 0 represents no mutation and 75% chance of ocurring, #1 represents 25% of occurring
        child.genes["turn-speed"] = (
            random.randint(50, 101) * np.pi / 180,
            random.randint(50, 101) * np.pi / 180,
        )

    # Speed mutation
    if random.random() < 0.25:
        child.genes["speed"] = [random.randint(50, 150), random.randint(50, 150)]

    return child


# test creature
count = 0
creature_group = pygame.sprite.Group()

# Adds a hundred animals to environment
for i in range(100):
    creature_group.add(
        Animal(
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
    timestep = time.time() - previous_time
    previous_time = time.time()

    for event in pygame.event.get():  # pygame event handling
        if event.type == pygame.QUIT:  # if exit button is clicked

            pygame.quit()  # quits pygame module
            loop = False

    if not loop:
        break

    env_cell_group.update(grass_grid)
    grass_grid = grow_grass(grass_grid, timestep)

    creature_group.update(grass_grid, timestep)

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

                        # Checks to see if the species[i] is a predator and species[j] is prey since predators have the value 1 while prey have the value 0
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
                            creature_group.sprites()[i],
                            creature_group.sprites()[j],
                        )
                        creature_group.add(child)

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
