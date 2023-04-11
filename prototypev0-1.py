import numpy as np
import pygame
import sys
import time
import matplotlib.pyplot as plt
import random

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
    env_grid = np.zeros((num_cells_y, num_cells_x))
    env_grid[0, 0] = 50
    env_grid[15, 30] = 50

    # Sprite group contains pygame sprite objects. Used for drawing groups of sprites
    # in one line vs having to use for loops in main simulation loop below
    env_cell_group = pygame.sprite.Group()

    # Generating environment cells
    for j in range(num_cells_x):
        for i in range(num_cells_y):
            cell = Env_Cell(j*cell_size, i*cell_size, j, i, cell_size, cell_size, env_grid[i, j])
            env_cell_group.add(cell)
    
    return env_grid, env_cell_group

def onBoard(i,j,grid):
    '''
    Code from CMSE 201, used for checking if neighboring cells are on the board
    '''
    if i <= grid.shape[0]-1 and i >= 0 and j <= grid.shape[1]-1 and j >= 0:
        return True
    else:
        return False

def getNeighborValues(i,j, board):
    '''
    Code from CMSE 201, used to check the values of the neighboring cells.
    As per the grass growing rules, if a neighbor cell has an amount
    of grass > 0, the cell starts growing grass itself
    '''
    neighborhood = [(i-1, j), (i, j-1), (i+1, j), (i, j+1)]
    
    neighbor_values = []
    for neighbor in neighborhood:
        if onBoard(neighbor[0], neighbor[1], board):
            neighbor_values.append(board[neighbor[0], neighbor[1]])
    
    return neighbor_values

def advance_grid(grid, dt):
    '''
    Code from CSME 201. Used to update the environment grid. The updated
    grid is used by the environment pygame sprite group to update their
    color on the screen
    '''
    max_grass = 50
    grow_rate = 30
    
    new_grid = np.zeros_like(grid)

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            '''
            If cell has no grass and no neighbors with grass, it doesn't grow
            If cell has no grass and neighbors with grass, it will start to grow
            If cell has grass, it will grow until it reaches max_grass
            '''
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
    
class Creature:
    '''
    General behavioral functions can go here
    '''
    pass

class Herbivore(pygame.sprite.Sprite, Creature):
    def __init__(self, genes, x, y, orientation,strength = 0):
        super().__init__()
        # position information
        self.angle = orientation
        self.normal = np.array([np.cos(self.angle), np.sin(self.angle)])
        self.pos = np.array([x, y])

        # genome information
        self.genes = genes
        self.strength = strength
        
        
        # defining state variables
        self.energy = np.mean(self.genes['max-energy']) # averaging value from both chromosomes
        self.hunger = np.mean(self.genes['max-energy']) - self.energy
        self.desire_mate = 0

        # pygame drawing information
        self.picture = pygame.image.load('base-herbivore.png').convert_alpha() # converting makes draw time faster I guess
        self.picture = pygame.transform.scale(self.picture, (20, 20))
        # base-herbivore.png is white so the next line
        # tints it to the be color determined by it's genes
        self.picture.fill(self.genes["color"], special_flags=pygame.BLEND_MULT)

        self.image = self.rotate(self.picture, -self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = [round(self.pos[0]), round(self.pos[1])]

    def rotate(self, surface, angle):
        '''
        This function exists because pygame's built in rotation functions
        don't work well. They degrade the image quality and eventually
        crash the program. See documentation for more information
        '''
        rotated_surface = pygame.transform.rotozoom(surface, angle*180/np.pi, 1)
        return rotated_surface

    def update(self, grid, dt):
        # updates the angle by the turn speed
        self.angle += np.mean(self.genes['turn-speed']) * dt

        # updates its orientation vector with new angle
        self.normal = np.array([np.cos(self.angle), np.sin(self.angle)])

        # updates its position with its speed and new normal vector
        self.pos = self.pos + self.normal * np.mean(self.genes['speed']) * dt

        # rotates the image according to new angle
        self.image = self.rotate(self.picture, -self.angle)
        self.rect = self.image.get_rect()

        # updates the draw position based on new position vector
        self.rect.center = [round(self.pos[0]), round(self.pos[1])]

        # eat the grass
        column = int(self.pos[0]/25)
        row = int(self.pos[1]/25)
        grid[row, column] = 0 # I'm honestly not sure yet why the row and column is switched, still have to look closer

# General setup for pygame
pygame.init()

# Defining the screen size
width = 1300
height = 600
screen = pygame.display.set_mode((width, height))

# Set up for environment
cell_size = 25
num_cells_x = round(width/cell_size)
num_cells_y = round(height/cell_size)

# env_grid is the numpy array that holds the grass values,
# env_cell_group is the pygame sprite group for drawing the
# grass cells to the screen
env_grid, env_cell_group = create_environment(num_cells_x, num_cells_y, cell_size)

# test genes dictionary

def random_genes():
    colors = ["blue","red"]
    species_type = random.randint(0,1)
    genes = {
    'speed': [random.randint(50, 150), random.randint(50, 150)],
    'turn-speed': [random.randint(50, 101)*np.pi/180, random.randint(50, 101)*np.pi/180],
    'fov': [180*np.pi/180, 180*np.pi/180],
    'view-dist': [60, 60],
    'max-energy': 100,
    'metabolism-rate': 5,
    'find-mate-rate': 3,
    'max-desire-to-mate': random.randint(0,50), #To mate desire of two species must added up must be above 60
    'sex': random.randint(0,1), # male = [0, 1] or [1, 0], female = [0, 0]
    
    'species': species_type, #2 different types of species with number 0 = prey, and 1 = predator
    'color': colors[species_type],
   
    }
    return genes


def reproduce(Herbivore1,Herbivore2):

    child = Herbivore(genes=Herbivore1.genes,x=random.randint(0, 3000)/3,y=random.randint(0, 1000)/3,orientation=-45*np.pi/180,strength=random.randint(5,20))
    Herbivore1.genes['max-desire-to-mate'] = -1000
    Herbivore2.genes['max-desire-to-mate'] = -1000
    child.genes['max-desire-to-mate'] = 0 #Resets to prevent constant reproduction
    
    return mutation(child)

def mutation(child):
    
    #color  mutation
    if (np.random.choice([0,1], p=[0.75,0.25])): #0 represents no mutation and 75% chance of ocurring, #1 represents 25% of occurring
        child.genes['color'] = np.random.choice(["blue","red","yellow","purple","black"], p=[0.35,0.35,0.15,0.10,0.05])
        child.picture.fill(child.genes["color"], special_flags=pygame.BLEND_MULT) #This changes the color being displayed in the simulation
    
    #Turn speed mutation
    if (np.random.choice([0,1], p=[0.75,0.25])): #0 represents no mutation and 75% chance of ocurring, #1 represents 25% of occurring
        child.genes['turn-speed'] = random.randint(50, 101)*np.pi/180, random.randint(50, 101)*np.pi/180
    #Speed mutation
    if (np.random.choice([0,1], p=[0.75,0.25])):
        child.genes['speed'] = [random.randint(50, 150), random.randint(50, 150)]
    

    return child

# test creature
count = 0
creature_group = pygame.sprite.Group()

#Adds a hundred animals to environment
for i in range(100):
    creature_group.add(Herbivore(random_genes(), random.randint(0, 3000)/3, random.randint(0, 1000)/3, -45*np.pi/180,strength=random.randint(5,20)))
    count += 1


    
# Main simulation loop. Instead of running until user clicks exit, can use conditions
previous_time = time.time()
carrying_capacity = random.randint(count*2,count*4)
data_list = [] #List containing prey,predator counts and time 
time_count = 0
loop = True
while True:
    
    # Used to ensure framerate independence
    dt = time.time() - previous_time
    previous_time = time.time()
    
    for event in pygame.event.get(): # pygame event handling
        if event.type == pygame.QUIT: # if exit button is clicked
            
            pygame.quit() # quits pygame module
            #sys.exit() # exits program
            loop = False

    if (not loop):
        break
    env_cell_group.update(env_grid)
    env_grid = advance_grid(env_grid, dt)

    creature_group.update(env_grid, dt)
    
    #These counts are meant for demonstrating stable predator prey relationships
    
    prey_count = 0
    predator_count = 0 
    
    if (count > 1): #To prevent indexing errors
        for i in range(count):
            #Compares every animal within environment to each other
            for j in range(i+1,count):
                if (creature_group.sprites()[i].genes["species"] != creature_group.sprites()[j].genes["species"]): #Compares species type
                    #Checks to see if two species are close to each other
                    if ((abs(creature_group.sprites()[i].pos[0]-creature_group.sprites()[j].pos[0]) < 50) and (abs(creature_group.sprites()[i].pos[1]-creature_group.sprites()[j].pos[1]) < 50)):


                        #Chceks to see if the species[i] is a predator and species[j] is prey since predators have the value 1 while prey have the value 0
                        if (creature_group.sprites()[i].genes["species"] > creature_group.sprites()[j].genes["species"]):
                            #Checks to see if predator is faster than prey because if so then prey is killed
                            if (creature_group.sprites()[i].genes["speed"] > creature_group.sprites()[j].genes["speed"]):
                                creature_group.remove(creature_group.sprites()[j])
                                count -= 1
                                break
                
                        elif(creature_group.sprites()[i].genes["species"] < creature_group.sprites()[j].genes["species"]):
                            if (creature_group.sprites()[i].genes["speed"] < creature_group.sprites()[j].genes["speed"]):
                                creature_group.remove(creature_group.sprites()[i])
                                count -= 1
                                break
                        
                #Check for reproduction
                if (creature_group.sprites()[i].genes["species"] == creature_group.sprites()[j].genes["species"]):
                    if ((creature_group.sprites()[i].genes['max-desire-to-mate']+creature_group.sprites()[j].genes['max-desire-to-mate']) > 60):
                        child = reproduce(Herbivore1=creature_group.sprites()[i],Herbivore2=creature_group.sprites()[j])
                        creature_group.add(child)

    for i in creature_group.sprites():
        i.genes["max-desire-to-mate"] += random.randint(5,20)

    for i in creature_group.sprites():
        if (i.genes["species"] == 0):
            prey_count += 1
        else:
            predator_count += 1
    #This list is used for modeling predator prey relations
    data_list.append([prey_count,predator_count,time_count])

    time_count += 1

    env_cell_group.draw(screen)
    creature_group.draw(screen)

    env_cell_group.draw(screen)
    creature_group.draw(screen)
    
    pygame.display.flip()


#plt_1 = plt.figure(figsize=(30, 30))
#plt.plot(data_list[:][2],data_list[:][0])
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

