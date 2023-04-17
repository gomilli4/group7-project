import numpy as np
import pygame
import pandas as pd

class Herbivore(pygame.sprite.Sprite):
    def __init__(self, genes, x, y, orientation, hashing_grid):
        super().__init__()
        # position information
        self.angle = orientation
        self.normal = np.array([np.cos(self.angle), np.sin(self.angle)])
        self.pos = np.array([x, y])

        # adding self to hashing grid
        column = int(self.pos[0]/25)
        row = int(self.pos[1]/25)
        hashing_grid[row, column].append(self)

        # genome information
        self.genes = genes
        self.color = [
            round(np.mean(self.genes['red'])),
            round(np.mean(self.genes['green'])),
            round(np.mean(self.genes['blue'])),
            100 # alpha channel
            ]
        
        # defining state variables
        self.energy = np.mean(self.genes['max-energy']) # averaging value from both chromosomes
        self.desire_mate = 0
        self.can_mate = False
        self.can_mate_counter = 0 # used as timer to determine when creature can mate again
        self.can_mate_counter_limit = 30
        self.dead = False
        self.ptype = 'prey'
        self.sex = 0
        if np.mean(self.genes['sex']) > 0:
            self.sex = 1 # 1 = male
        elif np.mean(self.genes['sex']) == 0:
            self.sex = 0 # 0 = female
        self.age = 0
        self.max_age = np.random.randint(900, 1100)
        self.maturity = 50 # creatures can't mate before maturity
        

        # pygame drawing information
        self.picture = pygame.image.load('base-herbivore.png').convert_alpha() # converting makes draw time faster I guess
        self.picture = pygame.transform.scale(self.picture, (30, 30))
        # base-herbivore.png is white so the next line
        # tints it to the be color determined by it's genes
        self.picture.fill(self.color, special_flags=pygame.BLEND_MULT)

        self.image = self.rotate(self.picture, -self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = [int(self.pos[0]), int(self.pos[1])]

        # state machine
        '''
        eating = 0
        finding mate = 1
        fleeing = 2
        wandering = 3
        '''
        self.state = 3
        self.doing = False
        self.counter = 0
        self.counter_max = 500 # defines the counter for wandering in random direction
        self.random_x = np.random.randint(10, 1290)
        self.random_y = np.random.randint(10, 590)
        self.target = None
        self.neighbor_cells = []

    def rotate(self, surface, angle):
        '''
        This function exists because pygame's built in rotation functions
        don't work well. They degrade the image quality and eventually
        crash the program. See documentation for more information
        '''
        rotated_surface = pygame.transform.rotozoom(surface, angle*180/np.pi, 1)
        return rotated_surface

    def update_state(self, hashing_grid):
        metabolism_rate = np.mean(self.genes['metabolism-rate'])
        self.energy -= metabolism_rate
        if self.energy <= 0:
            self.energy = 0
            self.dead = True

        find_mate_rate = np.mean(self.genes['find-mate-rate'])
        self.desire_mate += find_mate_rate
        max_desire = np.mean(self.genes['max-desire-to-mate'])
        if self.desire_mate >= max_desire:
            self.desire_mate = max_desire

        self.max_energy = np.mean(self.genes['max-energy'])
        hunger = self.max_energy - self.energy

        '''
        Gets position in spatial_hashing grid then finds neighbors
        according to view distance.
        neighbor_cells contains list of list of nearby creature objects
        to loop through
        '''
        column = int(self.pos[0]/25)
        row = int(self.pos[1]/25)
        self.neighbor_cells = self.getNeighborValues(row, column, hashing_grid)

        if hunger >= self.desire_mate and self.energy <= 0.28*self.max_energy: # and not see predator
            self.state = 0
            self.doing = True
        
        if hunger < self.desire_mate and not self.doing and self.can_mate and self.age >= self.maturity: # and not see predator
            self.state = 1

        if hunger < self.desire_mate and not self.doing and not self.can_mate:
            self.state = 3
            if self.age >= self.maturity:
                if self.can_mate_counter >= self.can_mate_counter_limit:
                    self.can_mate = True
                    self.can_mate_counter = 0
                else:
                    self.can_mate_counter += 1
        
        # if see predator, state = 2

    def act(self, grid, dt, hashing_grid, group):
        if self.state == 0:
            # eat the grass
            column = int(self.pos[0]/25)
            row = int(self.pos[1]/25)
            grass_amount = grid[row, column]
            grid[row, column] = 0
            self.energy += grass_amount/5
            max_energy = np.mean(self.genes['max-energy'])
            if self.energy >= max_energy:
                self.energy = max_energy
                self.doing = False

            '''
            The next bit of code sets up alters the random timer. When the
            timer ticks, the creature picks a new random point to move toward
            to simulate it wandering looking for food
            '''
            if self.counter % self.counter_max == 0:
                self.random_x = np.random.randint(10, 1290)
                self.random_y = np.random.randint(10, 590)
                self.counter_max = np.random.randint(100, 750)
            self.look_at(np.array([self.random_x, self.random_y]), dt)
            self.counter += 1

        if self.state == 1:
            '''
            Look for mate within view distance
            If potential mate in view, move towards them
            If close enough and can mate and is old enough, request mate
            Female makes baby and adds it to creature_group
            '''
            nearest_potential_mate = None
            for cell in self.neighbor_cells:
                for creature in cell:
                    if creature != self and creature.sex != self.sex and creature.ptype == 'prey':
                        vec_to_creature = creature.pos - self.pos
                        dist_to_creature = np.linalg.norm(vec_to_creature)
                        vec_to_creature_norm = vec_to_creature/dist_to_creature
                        fov = np.mean(self.genes['fov'])/2
                        view_dist = np.mean(self.genes['view-dist'])
                        
                        if np.arccos(np.dot(vec_to_creature, self.normal) <= fov and dist_to_creature <= view_dist):
                            if nearest_potential_mate == None:
                                nearest_potential_mate = creature
                            else:
                                current_nearest_dist = np.linalg.norm(nearest_potential_mate.pos - self.pos)
                                new_potential_dist = np.linalg.norm(creature.pos - self.pos)
                                if current_nearest_dist < new_potential_dist:
                                    nearest_potential_mate = creature
                                
            self.target = nearest_potential_mate
            if self.target != None:
                self.look_at(self.target.pos, dt)
                vec_to_target = self.target.pos - self.pos
                dist_to_target = np.linalg.norm(vec_to_target)
                if dist_to_target <= 10 and self.sex == 1 and self.can_mate:
                    self.request_mate(self.target, hashing_grid, group)
                    self.desire_mate = 0
                    self.can_mate = False
                    self.state = 3
                
            else: # if no potential mates nearby, just wander around looking for one
                if self.counter % self.counter_max == 0:
                    self.random_x = np.random.randint(10, 1290)
                    self.random_y = np.random.randint(10, 590)
                    self.counter_max = np.random.randint(100, 750)
                self.look_at(np.array([self.random_x, self.random_y]), dt)
            self.counter += 1

        if self.state == 3: # wander state, same as everywhere else
            if self.counter % self.counter_max == 0:
                self.random_x = np.random.randint(10, 1290)
                self.random_y = np.random.randint(10, 590)
                self.counter_max = np.random.randint(100, 750)
            self.look_at(np.array([self.random_x, self.random_y]), dt)
            self.counter += 1

    def request_mate(self, mate, hashing_grid, group):
        litter_size = 2
        litter = []
        for i in range(litter_size):
            gamete = self.form_gamete()
            litter.append(gamete)
        mate.receive_request(self, litter, hashing_grid, group)

    def form_gamete(self):
        '''
        Creatures are haploid, so have 2 copies of each gene on 2 different
        chromosomes. This function mimics "crossing over" in meisois
        and returns a half complete set of genes that will be combined with
        other parent's half set
        '''
        haploid_cell = {
            'speed': np.random.choice(self.genes['speed']),
            'turn-speed': np.random.choice(self.genes['turn-speed']),
            'fov': np.random.choice(self.genes['fov']),
            'view-dist': np.random.choice(self.genes['view-dist']),
            'max-energy': np.random.choice(self.genes['max-energy']),
            'metabolism-rate': np.random.choice(self.genes['metabolism-rate']),
            'find-mate-rate': np.random.choice(self.genes['find-mate-rate']),
            'max-desire-to-mate': np.random.choice(self.genes['max-desire-to-mate']),
            'sex': np.random.choice(self.genes['sex']),
            'red': np.random.choice(self.genes['red']),
            'green': np.random.choice(self.genes['green']),
            'blue': np.random.choice(self.genes['blue'])
            }

        # defines different list of genes because some genes can't be mutated
        # in the same way as others
        mutations1 = ['speed','turn-speed','fov']
        mutations2 = ['view-dist','max-energy','metabolism-rate','find-mate-rate','max-desire-to-mate']
        mutations3 = ['sex']
        mutations4 = ['red','green','blue']

        # picks random key then applies mutation to it
        mutation_chance = np.random.randint(1,5+1)
        if mutation_chance > 4: # 20% chance of mutation
            key = np.random.choice(list(haploid_cell.keys()))
            if key in mutations1:
                haploid_cell[key] += np.random.uniform(-2,2)
            elif key in mutations2:
                haploid_cell[key] = max(0, haploid_cell[key] + np.random.uniform(-2,2))
            elif key in mutations3:
                haploid_cell[key] = np.random.randint(0,2)
            elif key in mutations4:
                haploid_cell[key] = (haploid_cell[key] + np.random.randint(-10, 10)) % 256
        
        return haploid_cell

    def receive_request(self, mate, paternal_litter, hashing_grid, group):
        '''
        If it's old enough and can mate and is in the find_mate state it will
        form a gamete and pass the two sets of genes to the create_offspring
        function
        '''
        if self.age >= self.maturity and self.can_mate and self.state == 1:
            maternal_litter = []
            for i in range(len(paternal_litter)):
                maternal_gamete = self.form_gamete()
                maternal_litter.append(maternal_gamete)
            self.create_offspring(paternal_litter, maternal_litter, hashing_grid, group)
            self.desire_mate = 0
            self.can_mate = False
            self.state = 3

    def create_offspring(self, p, m, hashing_grid, group):
        '''
        Combines both sets of genes, creates a new Herbivore object,
        and adds it to creature_group to start being drawn and updated
        '''
        for i in range(len(p)):
            genes = {
                'speed': [p[i]['speed'], m[i]['speed']],
                'turn-speed': [p[i]['turn-speed'], m[i]['turn-speed']],
                'fov': [p[i]['fov'], m[i]['fov']],
                'view-dist': [p[i]['view-dist'], m[i]['view-dist']],
                'max-energy': [p[i]['max-energy'], m[i]['max-energy']],
                'metabolism-rate': [p[i]['metabolism-rate'], m[i]['metabolism-rate']],
                'find-mate-rate': [p[i]['find-mate-rate'], m[i]['find-mate-rate']],
                'max-desire-to-mate': [p[i]['max-desire-to-mate'], m[i]['max-desire-to-mate']],
                'sex': [p[i]['sex'], m[i]['sex']],
                'red': [p[i]['red'], m[i]['red']],
                'green': [p[i]['green'], m[i]['green']],
                'blue': [p[i]['blue'], m[i]['blue']]
                }
            offspring = Herbivore(genes, self.pos[0]+1+i, self.pos[1]+1+i, self.angle, hashing_grid)
            group.add(offspring)
        # self, genes, x, y, orientation, hashing_grid
        
    def onBoard(self, i, j, grid):
        '''
        Code from CMSE 201, used for checking if neighboring cells are on the board
        '''
        if i <= grid.shape[0]-1 and i >= 0 and j <= grid.shape[1]-1 and j >= 0:
            return True
        else:
            return False

    def getNeighborValues(self, i, j, board):
        '''
        Code mostly from CMSE 201. Instead of checking immediate cell
        neighbors, the number of grid squares to search through is
        calculated using the creature's view distance
        '''
        view_dist = np.mean(self.genes['view-dist'])
        dist = int(np.ceil(view_dist/25))

        neighborhood = []
        for row in range(2*dist + 1):
            for column in range(2*dist + 1):
                num_row = row - dist
                num_column = column - dist
                
                neighborhood.append((i+num_row, j+num_column))

        # this code runs just like code from CMSE 201
        neighbor_values = []
        for neighbor in neighborhood:
            if self.onBoard(neighbor[0], neighbor[1], board):
                neighbor_values.append(board[neighbor[0], neighbor[1]])

        return neighbor_values

    def look_at(self, target, dt):
        '''
        Defines vector to target, then normalizes it (gives it length of 1).
        np.sign returns + or -, so the sign variable determines whether the
        angle between the target point and creature is positive or negative.
        '''
        vec_to_target = target - self.pos
        vec_to_target_norm = vec_to_target/np.linalg.norm(vec_to_target)

        # using the sign variable, the angle_to variable is determined to be
        # + or -
        sign = np.sign(np.cross(self.normal, vec_to_target_norm))
        angle_to = sign*np.arccos(np.dot(self.normal, vec_to_target_norm))

        # defines the creature's turn speed from it's genes, then
        # adds the angle to the creature's orientation angle to turn
        # it toward the target point
        turn_speed = np.mean(self.genes['turn-speed'])
        self.angle = self.angle + sign*turn_speed*dt

    def update(self, grid, hashing_grid, dt, group):
        self.update_state(hashing_grid)
        self.act(grid, dt, hashing_grid, group)
        
        # remove self from hashing grid
        column = int(self.pos[0]/25)
        row = int(self.pos[1]/25)
        hashing_grid[row, column].remove(self)
        
        # updates the angle by the turn speed
        #self.angle += np.mean(self.genes['turn-speed']) * dt

        # updates its orientation vector with new angle
        self.normal = np.array([np.cos(self.angle), np.sin(self.angle)])

        # updates its position with its speed and new normal vector
        self.pos = self.pos + self.normal * np.mean(self.genes['speed']) * dt

        # bounces creature off walls instead of letting them go out of bounds
        if self.pos[1] <= 10 or self.pos[1] >= 590:
            self.angle = -self.angle
            # next bit of code redefines the random point it wanders toward
            # everytime it bounces
            self.random_x = np.random.randint(10, 1290)
            self.random_y = np.random.randint(10, 590)
            
        if self.pos[0] <= 10 or self.pos[0] >= 1290:
            self.angle = np.pi - self.angle
            # same thing as above
            self.random_x = np.random.randint(10, 1290)
            self.random_y = np.random.randint(10, 590)

        # rotates the image according to new angle
        self.image = self.rotate(self.picture, -self.angle)
        
        # updates the draw position based on new position vector
        self.rect.center = [int(self.pos[0]), int(self.pos[1])]

        # add self to hashing grid in new position
        column = int(self.pos[0]/25)
        row = int(self.pos[1]/25)
        hashing_grid[row, column].append(self)

        # aging and death handling
        self.age += 0.1
        if self.age >= self.max_age:
            self.dead = True

        if self.dead:
            '''
            if output file doesn't exist, create it and write genes to file
            if output file does exist, append genes to file
            '''
            dict_to_df = {
                'age-at-death': [self.age],
                'speed': [np.mean(self.genes['speed'])],
                'turn-speed': [np.mean(self.genes['turn-speed'])],
                'fov': [np.mean(self.genes['fov'])],
                'view-dist': [np.mean(self.genes['view-dist'])],
                'max-energy': [np.mean(self.genes['max-energy'])],
                'metabolism-rate': [np.mean(self.genes['metabolism-rate'])],
                'find-mate-rate': [np.mean(self.genes['find-mate-rate'])],
                'max-desire-to-mate': [np.mean(self.genes['max-desire-to-mate'])]
                }
            df = pd.DataFrame(dict_to_df)
            location = location = 'prey-genes-data.csv'
            df.to_csv(location, mode='a')
            
            self.kill() # removes creature from all pygame sprite groups
            hashing_grid[row, column].remove(self) # removes creature from hashing grid
            

    def debug(self, screen, debug_list):
        '''
        The code below draws the creature's FOV
        '''
        # collecting FOV and view distance from genes
        view_angle = np.mean(self.genes['fov'])/2
        view_dist = np.mean(self.genes['view-dist'])

        # defining left and right angles to draw lines along relative
        # to creature's orientation
        right = np.array([np.cos(self.angle + view_angle), np.sin(self.angle + view_angle)])
        left = np.array([np.cos(self.angle - view_angle), np.sin(self.angle - view_angle)])

        # defining the start point as the creature's position and
        # the end points as the left and right FOV boundaries
        start_pos = self.pos
        right_end_pos = self.pos + view_dist*right
        left_end_pos = self.pos + view_dist*left

        # drawing the lines
        pygame.draw.line(screen, (255,255,255), start_pos, right_end_pos)
        pygame.draw.line(screen, (255,255,255), start_pos, left_end_pos)

        # computes the arc segments to show full field of view
        arc_list = []
        segments = 10
        for i in range(segments + 1):
            point = self.pos + view_dist*np.array([np.cos(self.angle + view_angle), np.sin(self.angle + view_angle)])
            view_angle -= np.mean(self.genes['fov'])/segments
            arc_list.append(point)
        pygame.draw.lines(screen, (255,255,255), False, arc_list) # draws list of points

        '''
        The code below displays the creature's energy and desire to mate
        statistics
        '''
        energy = self.energy
        max_energy = np.mean(self.genes['max-energy'])

        desire_mate = self.desire_mate
        max_desire = np.mean(self.genes['max-desire-to-mate'])
        
        bar_length = 100
        energy_bar_ratio = max_energy/bar_length
        desire_bar_ratio = max_desire/bar_length

        pygame.draw.rect(screen, (255,234,0), (10, 10, energy/energy_bar_ratio, 10))
        pygame.draw.rect(screen, (255,255,255), (10, 10, bar_length, 10), 2)

        pygame.draw.rect(screen, (255,105,180), (10, 25, desire_mate/desire_bar_ratio, 10))
        pygame.draw.rect(screen, (255,255,255), (10, 25, bar_length, 10), 2)

        # Draws random point the creature is wandering toward
        pygame.draw.circle(screen, (255,255,255), (self.random_x, self.random_y), 3)

        # Draws the current state of the creature and its sex
        font = pygame.font.Font('freesansbold.ttf', 16)
        words = 'State: ' + str(self.state)
        text = font.render(words, True, (255,255,255), (0,0,0))
        textrect = text.get_rect()
        textrect.topleft = (10,40)
        screen.blit(text, textrect)

        font = pygame.font.Font('freesansbold.ttf', 16)
        words = 'Sex: ' + str(self.sex)
        text = font.render(words, True, (255,255,255), (0,0,0))
        textrect = text.get_rect()
        textrect.topleft = (10,55)
        screen.blit(text, textrect)

        font = pygame.font.Font('freesansbold.ttf', 16)
        words = 'Age: ' + str(round(self.age,2))
        text = font.render(words, True, (255,255,255), (0,0,0))
        textrect = text.get_rect()
        textrect.topleft = (10,70)
        screen.blit(text, textrect)

        # death handling
        if self.dead:
            debug_list.remove(self) # removes creature from debug_list
