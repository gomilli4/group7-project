import numpy as np
import pygame
import sys
import time
import organisms as org
from environment import *
import matplotlib.pyplot as plt
import pandas as pd

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

'''
Commented block was used for original test creatures.
These genes seem to be relatively stable so keeping
them for reference

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
    
# test creatures
#test_male = org.Herbivore(genes1, np.random.randint(10, 1290), np.random.randint(10, 590), -np.random.randint(0,360)*np.pi/180, hashing_grid)
#test_female = org.Herbivore(genes2, np.random.randint(10, 1290), np.random.randint(10, 590), -np.random.randint(0,360)*np.pi/180, hashing_grid)
#creature_group.add(test_male)
#creature_group.add(test_female)
'''

creature_group = pygame.sprite.Group()

for i in range(50):
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
    creature = org.Herbivore(
        genes,
        np.random.randint(10, 1290), np.random.randint(10, 590),
        -np.random.uniform(0, 2*np.pi),
        hashing_grid
        )
    creature_group.add(creature)

for i in range(50):
    genes = {
        'speed': [np.random.uniform(80, 200), np.random.uniform(80, 200)],
        'turn-speed': [np.random.uniform(np.pi/2, 2*np.pi), np.random.uniform(np.pi/2, 2*np.pi)],
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
    creature = org.Carnivore(
        genes,
        np.random.randint(10, 1290), np.random.randint(10, 590),
        -np.random.uniform(0, 2*np.pi),
        hashing_grid
        )
    creature_group.add(creature)

# debug list contains selected creatures and displays their characteristics
# to the screen, like HP, hunger, desire to mate, and FOV
debug_list = []

# Data tracking lists
t = 0
time_list = []
num_herbivores = []
num_carnivores = []
avg_speed = []
avg_turn_speed = []
avg_fov = []
avg_view_dist = []
avg_max_energy = []
avg_metabolism_rate = []
avg_find_mate_rate = []
avg_max_desire_to_mate = []

# Main simulation loop. Instead of running until user clicks exit, can use conditions
# previous_time = time.time()
pause = False
running = True
plot_timer = 1
#clock = pygame.time.Clock()
while running:
    #clock.tick()
    # Used to ensure framerate independence
    # NOTE!! I think framerate independence was causing a fatal bug
    # when python starts lagging with large agent numbers so I replaced
    # it with static dt value
    dt = 0.025 #time.time() - previous_time
    #previous_time = time.time()
    
    for event in pygame.event.get(): # pygame event handling
        if event.type == pygame.QUIT: # if exit button is clicked
            running = False

        if event.type == pygame.KEYDOWN: # checks for p key being pressed
            if event.key == pygame.K_p:
                pause = not pause # toggles pause
                
        if event.type == pygame.KEYDOWN: # clears the debug list
            if event.key == pygame.K_a:
                debug_list = []

        # saves herbivore count and population statistics to csv file
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                dict_to_df = {
                    'time': time_list,
                    'num-herbivores': num_herbivores,
                    'num-carnivores': num_carnivores,
                    'speed': avg_speed,
                    'turn-speed': avg_turn_speed,
                    'fov': avg_fov,
                    'view-dist': avg_view_dist,
                    'max-energy': avg_max_energy,
                    'metabolism-rate': avg_metabolism_rate,
                    'find-mate-rate': avg_find_mate_rate,
                    'max-desire-to-mate': avg_max_desire_to_mate
                    }
                df = pd.DataFrame(dict_to_df)
                location = location = 'tests/testopen/data.csv'
                df.to_csv(location)
            
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
        herb_count = 0
        carn_count = 0
        for creature in creature_group:
            if creature.ptype == 'prey':
                herb_count += 1
            elif creature.ptype == 'predator':
                carn_count += 1
        num_herbivores.append(herb_count)
        num_carnivores.append(carn_count)

        # defining variables that will be summed up based on
        # creature stats to be 0
        speed = 0
        turn_speed = 0
        fov = 0
        view_dist = 0
        max_energy = 0
        metabolism_rate = 0
        find_mate_rate = 0
        max_desire_to_mate = 0

        # looping through every creature and adding its gene
        # values to the respective variable
        for creature in creature_group:
            if creature.ptype == 'prey':
                speed += np.mean(creature.genes['speed'])
                turn_speed += np.mean(creature.genes['turn-speed'])
                fov += np.mean(creature.genes['fov'])
                view_dist += np.mean(creature.genes['view-dist'])
                max_energy += np.mean(creature.genes['max-energy'])
                metabolism_rate += np.mean(creature.genes['metabolism-rate'])
                find_mate_rate += np.mean(creature.genes['find-mate-rate'])
                max_desire_to_mate += np.mean(creature.genes['max-desire-to-mate'])

        # appending the averaged genes to the appropriate list
        n = len(creature_group)
        if n > 0:
            avg_speed.append(speed/n)
            avg_turn_speed.append(turn_speed/n)
            avg_fov.append(fov/n)
            avg_view_dist.append(view_dist/n)
            avg_max_energy.append(max_energy/n)
            avg_metabolism_rate.append(metabolism_rate/n)
            avg_find_mate_rate.append(find_mate_rate/n)
            avg_max_desire_to_mate.append(max_desire_to_mate/n)
        else:
            avg_speed.append(0)
            avg_turn_speed.append(0)
            avg_fov.append(0)
            avg_view_dist.append(0)
            avg_max_energy.append(0)
            avg_metabolism_rate.append(0)
            avg_find_mate_rate.append(0)
            avg_max_desire_to_mate.append(0)
        
        
        env_cell_group.update(env_grid) # calls update function for every element in group
        env_grid = advance_grid(env_grid, dt) # advances the grass grid by the growth rules

        creature_group.update(env_grid, hashing_grid, dt, creature_group) # calls update funciton for every organism

        env_cell_group.draw(screen) # calls draw function for every environment grass cell
        creature_group.draw(screen) # calls draw function for every organism

        t += 0.001 # counter for plots

        # used for automatically saving data to csv every 1000 frames
        if plot_timer % 1000 == 0:
            dict_to_df = {
                'time': time_list,
                'num-herbivores': num_herbivores,
                'num-carnivores': num_carnivores,
                'speed': avg_speed,
                'turn-speed': avg_turn_speed,
                'fov': avg_fov,
                'view-dist': avg_view_dist,
                'max-energy': avg_max_energy,
                'metabolism-rate': avg_metabolism_rate,
                'find-mate-rate': avg_find_mate_rate,
                'max-desire-to-mate': avg_max_desire_to_mate
                }
            df = pd.DataFrame(dict_to_df)
            location = location = 'tests/testopen/data.csv'
            df.to_csv(location)
        plot_timer += 1

    if pause: # if paused only draw, no update
        env_cell_group.draw(screen) # calls draw function for every environment grass cell
        creature_group.draw(screen) # calls draw function for every organism

    # PUT DEBUG DRAW INSTRUCTIONS HERE
    for creature in debug_list:
        creature.debug(screen, debug_list)

    font = pygame.font.Font('freesansbold.ttf', 16)
    words = 'Time: ' + str(round(t,3))
    #words = 'FPS: ' + str(clock.get_fps())
    text = font.render(words, True, (255,255,255), (0,0,0))
    textrect = text.get_rect()
    textrect.topright = (1290,10)
    screen.blit(text, textrect)
        
    pygame.display.flip() # updates the pygame display
    

pygame.quit() # quits pygame module

dict_to_df = {
    'time': time_list,
    'num-herbivores': num_herbivores,
    'num-carnivores': num_carnivores,
    'speed': avg_speed,
    'turn-speed': avg_turn_speed,
    'fov': avg_fov,
    'view-dist': avg_view_dist,
    'max-energy': avg_max_energy,
    'metabolism-rate': avg_metabolism_rate,
    'find-mate-rate': avg_find_mate_rate,
    'max-desire-to-mate': avg_max_desire_to_mate
    }
df = pd.DataFrame(dict_to_df)
location = location = 'tests/testopen/data.csv'
df.to_csv(location)

sys.exit() # exits program
