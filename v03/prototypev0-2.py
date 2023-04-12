import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygame
import sys
import time

from carnivore import Carnivore
from environment import *
from herbivore import Herbivore

# General setup for pygame
pygame.init()

# Defining the screen size
width = 1300
height = 600
screen = pygame.display.set_mode((width, height))

# Set up for environment
cell_size = 25
num_cells_x = int(width/cell_size)
num_cells_y = int(height/cell_size)

# env_grid is the numpy array that holds the grass values,
# env_cell_group is the pygame sprite group for drawing the
# grass cells to the screen. Hashing grid is used to store the creatures
# positions to avoid looping through every organism each frame
env_grid, env_cell_group, hashing_grid = create_environment(num_cells_x, num_cells_y, cell_size)

# test genes dictionary
genes1 = {
    'speed': [90, 90],
    'turn-speed': [100*np.pi/180, 100*np.pi/180],
    'fov': [270*np.pi/180, 270*np.pi/180],
    'view-dist': [100, 100],
    'max-energy': [200, 200],
    'metabolism-rate': [0.1, 0.1],
    'find-mate-rate': [0.05, 0.05],
    'max-desire-to-mate': [60, 60],
    'sex': [0, 1], # male = [0, 1] or [1, 0], female = [0, 0]
    'red': [255, 255],
    'green': [0, 0],
    'blue': [0, 0]
    }

genes2 = {
    'speed': [90, 90],
    'turn-speed': [130*np.pi/180, 170*np.pi/180],
    'fov': [90*np.pi/180, 90*np.pi/180],
    'view-dist': [100, 100],
    'max-energy': [200, 200],
    'metabolism-rate': [0.1, 0.1],
    'find-mate-rate': [0.05, 0.05],
    'max-desire-to-mate': [60, 60],
    'sex': [0, 0], # male = [0, 1] or [1, 0], female = [0, 0]
    'red': [0, 0],
    'green': [255, 255],
    'blue': [0, 0]
    }

# test creature
creature_group = pygame.sprite.Group()
#test_male = Herbivore(genes1, np.random.randint(10, 1290), np.random.randint(10, 590), -np.random.randint(0,360)*np.pi/180, hashing_grid)
#test_female = Herbivore(genes2, np.random.randint(10, 1290), np.random.randint(10, 590), -np.random.randint(0,360)*np.pi/180, hashing_grid)
#creature_group.add(test_male)
#creature_group.add(test_female)

for i in range(40):
    genes = {
        'speed': [np.random.uniform(50, 150), np.random.uniform(50, 150)],
        'turn-speed': [np.random.uniform(0, 2*np.pi), np.random.uniform(0, 2*np.pi)],
        'fov': [np.random.uniform(0, 2*np.pi), np.random.uniform(0, 2*np.pi)],
        'view-dist': [np.random.uniform(60, 250), np.random.uniform(60, 250)],
        'max-energy': [np.random.uniform(75, 250), np.random.uniform(75, 250)],
        'metabolism-rate': [np.random.uniform(0.01, 0.5), np.random.uniform(0.01, 0.5)],
        'find-mate-rate': [np.random.uniform(0.1, 5), np.random.uniform(0.1, 5)],
        'max-desire-to-mate': [np.random.uniform(40, 75), np.random.uniform(40, 75)],
        'sex': [np.random.randint(0,2), 0], # male = [0, 1] or [1, 0], female = [0, 0]
        'red': [np.random.randint(0, 256), np.random.randint(0, 256)],
        'green': [np.random.randint(0, 256), np.random.randint(0, 256)],
        'blue': [np.random.randint(0, 256), np.random.randint(0, 256)]
        }
    creature = Herbivore(
        genes,
        np.random.randint(10, 1290), np.random.randint(10, 590),
        -np.random.uniform(0, 2*np.pi),
        hashing_grid
        )
    creature_group.add(creature)

# debug list contains selected creatures and displays their characteristics
# to the screen, like HP, hunger, desire to mate, and FOV
debug_list = []

# List for keeping time and track of number of herbivores
t = 0
time_list = []

num_herbivores = []

# Main simulation loop. Instead of running until user clicks exit, can use conditions
previous_time = time.time()
pause = False
running = True
while running:    
    # Used to ensure framerate independence
    dt = time.time() - previous_time
    previous_time = time.time()
    
    for event in pygame.event.get(): # pygame event handling
        if event.type == pygame.QUIT: # if exit button is clicked
            running = False

        if event.type == pygame.KEYDOWN: # checks for p key being pressed
            if event.key == pygame.K_p:
                pause = not pause # toggles pause
                
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                debug_list = []

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                pause = True
                plt.plot(time_list, num_herbivores)
                plt.show()
            
        if event.type == pygame.MOUSEBUTTONUP: # checks for mouse clicks
            mouse_pos = pygame.mouse.get_pos()

            for creature in creature_group:
                if creature.rect.collidepoint(mouse_pos):
                    # adds selected creature to debug list for drawing
                    # debug statistics
                    debug_list.append(creature)
                '''
                else: # removes creatures from list if they're in debug_list
                    if creature in debug_list:
                        debug_list.remove(creature)
                '''

    if not pause: # if not paused, run simulation
        time_list.append(t)
        num_herbivores.append(len(creature_group))
        
        env_cell_group.update(env_grid) # calls update function for every element in group
        env_grid = advance_grid(env_grid, dt) # advances the grass grid by the growth rules

        creature_group.update(env_grid, hashing_grid, dt, creature_group) # calls update funciton for every organism

        env_cell_group.draw(screen) # calls draw function for every environment grass cell
        creature_group.draw(screen) # calls draw function for every organism

        t += 0.001

    if pause: # if paused only draw, no update
        env_cell_group.draw(screen) # calls draw function for every environment grass cell
        creature_group.draw(screen) # calls draw function for every organism

    # PUT DEBUG DRAW INSTRUCTIONS HERE
    for creature in debug_list:
        creature.debug(screen, debug_list)

    font = pygame.font.Font('freesansbold.ttf', 16)
    words = 'Time: ' + str(round(t,3))
    text = font.render(words, True, (255,255,255), (0,0,0))
    textrect = text.get_rect()
    textrect.topright = (1290,10)
    screen.blit(text, textrect)
        
    pygame.display.flip() # updates the pygame display

    # Data tracking code goes here
    

pygame.quit() # quits pygame module

plt.plot(time_list, num_herbivores)
plt.show()

sys.exit() # exits program
