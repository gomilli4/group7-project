import numpy as np
import pygame

class Carnivore(pygame.sprite.Sprite):
    """
    Represents a predator in this simulation.
    """
    def __init__(self, genes, x, y, orientation, hashing_grid):
        """
        Initialize a new instance of the predator agent.

        Args:
        - genes (dict): A dictionary containing genetic information of the predator.
        - x (float): The x-coordinate of the predator's position.
        - y (float): The y-coordinate of the predator's position.
        - orientation (float): The angle of orientation of the predator.
        - hashing_grid (numpy.ndarray): A 2D numpy array representing the grid used for hashing.
        """
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
        self.desire_to_mate = 0
        self.can_mate = False
        self.can_mate_counter = 0 # used as timer to determine when creature can mate again
        self.can_mate_counter_limit = 30
        self.dead = False
        self.ptype = 'predator'
        self.sex = 0
        if np.mean(self.genes['sex']) > 0:
            self.sex = 1 # 1 = male
        elif np.mean(self.genes['sex']) == 0:
            self.sex = 0 # 0 = female
        self.age = 0
        self.max_age = np.random.randint(900, 1100)
        self.maturity = 200 # creatures can't mate before maturity
        

        # pygame drawing information
        self.picture = pygame.image.load('base-carnivore.png').convert_alpha() # converting makes draw time faster I guess
        self.picture = pygame.transform.scale(self.picture, (25, 25))
        # base-herbivore.png is white so the next line
        # tints it to the be color determined by it's genes
        self.picture.fill(self.color, special_flags=pygame.BLEND_MULT)

        self.image = self.rotate(self.picture, -self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = [int(self.pos[0]), int(self.pos[1])]

        # state machine
        """
        eating = 0
        finding mate = 1
        wandering = 3
        """
        self.state = 3
        self.hungry = False
        self.wander_counter = 0
        self.wander_counter_max = 500 # defines the counter for wandering in random direction
        self.random_x = np.random.randint(10, 1290)
        self.random_y = np.random.randint(10, 590)
        self.target = None
        self.neighbor_cells = []

    def rotate(self, surface, angle):
        """
        This function exists because pygame's built in rotation functions
        don't work well. They degrade the image quality and eventually
        crash the program. See documentation for more information

        Args:
        - surface (pygame.Surface): The surface to be rotated.
        - angle (float): The angle of rotation in radians.

        Returns:
        - pygame.Surface: The rotated surface.
        """
        rotated_surface = pygame.transform.rotozoom(surface, angle*180/np.pi, 1)
        return rotated_surface

    def update_state(self, hashing_grid):
        """
        Update the state of the predator.

        Args:
        - hashing_grid (numpy.ndarray): The spatial hashing grid used for neighbor detection.

        Returns:
        - None
        """
        metabolism_rate = np.mean(self.genes["metabolism-rate"])
        self.energy -= metabolism_rate
        if self.energy <= 0:
            self.dead = True
            return

        find_mate_rate = np.mean(self.genes["find-mate-rate"])
        self.desire_to_mate += find_mate_rate
        max_desire = np.mean(self.genes["max-desire-to-mate"])
        if self.desire_to_mate >= max_desire:
            self.desire_to_mate = max_desire

        self.max_energy = np.mean(self.genes["max-energy"])
        hunger = self.max_energy - self.energy

        """
        Gets position in spatial_hashing grid then finds neighbors
        according to view distance.
        neighbor_cells contains list of list of nearby creature objects
        to loop through
        """
        column = int(self.pos[0] / 25)
        row = int(self.pos[1] / 25)
        self.neighbor_cells = self.get_neighbor_values(row, column, hashing_grid)

        if hunger >= self.desire_to_mate and self.energy <= 0.5 * self.max_energy:
            self.state = 0
            self.hungry = True

        if (
            hunger < self.desire_to_mate
            and not self.hungry
            and self.can_mate
            and self.age >= self.maturity
        ):  # and not see predator
            self.state = 1

        if hunger < self.desire_to_mate and not self.hungry and not self.can_mate:
            self.state = 3
            if self.age >= self.maturity:
                if self.can_mate_counter >= self.can_mate_counter_limit:
                    self.can_mate = True
                    self.can_mate_counter = 0
                else:
                    self.can_mate_counter += 1


    def act(self, grid, dt, hashing_grid, group):
        """
        Performs an action based on the current state of the predator.

        State Values:
        0 - Hunting: Tries to eat prey.
        1 - Mating: Tries to reproduce with a mate.
        3 - Random Wander: Wanders around randomly.
        
        Args:
        - grid (numpy.ndarray): The grid of grass.
        - dt (float): The time step for the simulation.
        - hashing_grid (numpy.ndarray): The hashing grid for spatial partitioning.
        - group (pygame.sprite.Group): The sprite group of carnivores the creature belongs to.
        """
        if self.state == 0:
            max_energy = np.mean(self.genes["max-energy"])
            self.target = None
            for cell in self.neighbor_cells:
                for creature in cell:
                    if creature.ptype == "prey":
                        vec_to_creature = creature.pos - self.pos
                        dist_to_creature = np.linalg.norm(vec_to_creature)
                        fov = np.mean(self.genes["fov"]) / 2
                        view_dist = np.mean(self.genes["view-dist"])

                        if np.arccos(
                            np.dot(vec_to_creature, self.normal) <= fov
                            and dist_to_creature <= view_dist
                        ):
                            if self.target == None:
                                self.target = creature
                            else:
                                current_nearest_dist = np.linalg.norm(
                                    self.target.pos - self.pos
                                )
                                new_potential_dist = np.linalg.norm(creature.pos - self.pos)
                                if current_nearest_dist < new_potential_dist:
                                    self.target = creature

            if self.target != None:
                self.look_at(self.target.pos, dt)
                vec_to_target = self.target.pos - self.pos
                dist_to_target = np.linalg.norm(vec_to_target)
                if dist_to_target <= 40:
                    self.energy += 200
                    if self.energy >= max_energy:
                        self.energy = max_energy
                        self.hungry = False
                    self.target.dead = True

            else:  # if no prey nearby, just wander around looking for one
                if self.wander_counter % self.wander_counter_max == 0:
                    self.random_x = np.random.randint(10, 1290)
                    self.random_y = np.random.randint(10, 590)
                    self.wander_counter_max = np.random.randint(100, 750)
                self.look_at(np.array([self.random_x, self.random_y]), dt)
            self.wander_counter += 1

        if self.state == 1:
            """
            Look for mate within view distance
            If potential mate in view, move towards them
            If close enough and can mate and is old enough, request mate
            Female makes baby and adds it to creature_group
            """
            nearest_potential_mate = None
            for cell in self.neighbor_cells:
                for creature in cell:
                    if (
                        creature != self
                        and creature.sex != self.sex
                        and creature.ptype == "predator"
                    ):
                        vec_to_creature = creature.pos - self.pos
                        dist_to_creature = np.linalg.norm(vec_to_creature)
                        vec_to_creature_norm = vec_to_creature / dist_to_creature
                        fov = np.mean(self.genes["fov"]) / 2
                        view_dist = np.mean(self.genes["view-dist"])

                        if np.arccos(
                            np.dot(vec_to_creature, self.normal) <= fov
                            and dist_to_creature <= view_dist
                        ):
                            if nearest_potential_mate == None:
                                nearest_potential_mate = creature
                            else:
                                current_nearest_dist = np.linalg.norm(
                                    nearest_potential_mate.pos - self.pos
                                )
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
                    self.desire_to_mate = 0
                    self.can_mate = False
                    self.state = 3

            else:  # if no potential mates nearby, just wander around looking for one
                if self.wander_counter % self.wander_counter_max == 0:
                    self.random_x = np.random.randint(10, 1290)
                    self.random_y = np.random.randint(10, 590)
                    self.wander_counter_max = np.random.randint(100, 750)
                self.look_at(np.array([self.random_x, self.random_y]), dt)
            self.wander_counter += 1

        if self.state == 3:  # wander state, same as everywhere else
            if self.wander_counter % self.wander_counter_max == 0:
                self.random_x = np.random.randint(10, 1290)
                self.random_y = np.random.randint(10, 590)
                self.wander_counter_max = np.random.randint(100, 750)
            self.look_at(np.array([self.random_x, self.random_y]), dt)
            self.wander_counter += 1


    def request_mate(self, mate, hashing_grid, group):
        """
        Sends a request to another predator to made

        Args:
        - mate (Carnivore): The potential mate to request mating with.
        - hashing_grid (numpy.ndarray): The hashing grid used for spatial partitioning.
        - group (pygame.sprite.Group): The sprite group of carnivores this is a part of.

        Returns:
        - None
        """
        gamete = self.form_gamete()
        mate.receive_request(self, gamete, hashing_grid, group)

    def form_gamete(self):
        """
        Creatures are haploid, so have 2 copies of each gene on 2 different
        chromosomes. This function mimics "crossing over" in meisois
        and returns a half complete set of genes that will be combined with
        other parent's half set

        Returns:
        - dict: A dictionary representing a half complete set of genes.
        """
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

    def receive_request(self, mate, paternal_gamete, hashing_grid, group):
        """
        If it's old enough and can mate and is in the find_mate state it will
        form a gamete and pass the two sets of genes to the create_offspring
        function

        Args:
        - mate (Carnivore): The mate object that sent the mating request.
        - paternal_gamete (dict): The paternal gamete containing half of the mate's genes.
        - hashing_grid (numpy.ndarray):The hashing grid object for spatial organization.
        - group (pygame.sprite.Group): The group of creatures to which both the creature and mate belong.
        """
        if self.age >= self.maturity and self.can_mate and self.state == 1:
            maternal_gamete = self.form_gamete()
            self.create_offspring(paternal_gamete, maternal_gamete, hashing_grid, group)
            self.desire_to_mate = 0
            self.can_mate = False
            self.state = 3

    def create_offspring(self, p, m, hashing_grid, group):
        """
        Combines both sets of genes, creates a new Herbivore object,
        and adds it to creature_group to start being drawn and updated

        Args:
        - p (dict): Paternal gamete containing genes from the father.
        - m (dict): Maternal gamete containing genes from the mother.
        - hashing_grid (numpy.ndarray): The hashing grid object for spatial organization.
        - group (pygame.sprite.Group): The sprite group of creatures to which the offspring will be added.
        """
        genes = {
            'speed': [p['speed'], m['speed']],
            'turn-speed': [p['turn-speed'], m['turn-speed']],
            'fov': [p['fov'], m['fov']],
            'view-dist': [p['view-dist'], m['view-dist']],
            'max-energy': [p['max-energy'], m['max-energy']],
            'metabolism-rate': [p['metabolism-rate'], m['metabolism-rate']],
            'find-mate-rate': [p['find-mate-rate'], m['find-mate-rate']],
            'max-desire-to-mate': [p['max-desire-to-mate'], m['max-desire-to-mate']],
            'sex': [p['sex'], m['sex']],
            'red': [p['red'], m['red']],
            'green': [p['green'], m['green']],
            'blue': [p['blue'], m['blue']]
            }
        offspring = Carnivore(genes, self.pos[0]+1, self.pos[1]+1, self.angle, hashing_grid)
        group.add(offspring)
        
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

    def get_neighbor_values(self, x, y, board):
        """
        Code mostly from CMSE 201. Instead of checking immediate cell
        neighbors, the number of grid squares to search through is
        calculated using the creature's view distance

        Args:
        - x (int): X-coordinate of the current cell.
        - y (int): Y-coordinate of the current cell.
        - board (numpy.ndarray): The grid to retrieve neighbor values from.

        Returns:
        - list: List of values of neighboring cells on the grid.
        """
        view_dist = np.mean(self.genes["view-dist"])
        dist = int(np.ceil(view_dist / 25))

        neighborhood = []
        for row in range(2 * dist + 1):
            for column in range(2 * dist + 1):
                num_row = row - dist
                num_column = column - dist
                neighborhood.append((x + num_row, y + num_column))

        # this code runs just like code from CMSE 201
        neighbor_values = []
        for neighbor in neighborhood:
            if self.on_board(neighbor[0], neighbor[1], board):
                neighbor_values.append(board[neighbor[0], neighbor[1]])

        return neighbor_values

    def look_at(self, target, dt):
        """
        Defines vector to target, then normalizes it (gives it length of 1).
        np.sign returns + or -, so the sign variable determines whether the
        angle between the target point and creature is positive or negative.

        Args:
        - target (numpy array): The target point to face.
        - dt (float): The time step for the update.

        Returns:
        - None
        """
        vec_to_target = target - self.pos
        vec_to_target_norm = vec_to_target / np.linalg.norm(vec_to_target)

        # using the sign variable, the angle_to variable is determined to be
        # + or -
        sign = np.sign(np.cross(self.normal, vec_to_target_norm))
        angle_to = sign * np.arccos(np.dot(self.normal, vec_to_target_norm))

        # defines the creature's turn speed from it's genes, then
        # adds the angle to the creature's orientation angle to turn
        # it toward the target point
        turn_speed = np.mean(self.genes["turn-speed"])
        self.angle = self.angle + sign * turn_speed * dt

    def update(self, grid, hashing_grid, dt, group):
        """
        Updates the state of the carnivore and its position based on its genes and environment.

        Args:
        - grid (numpy.ndarray): The grid representing the environment and grass.
        - hashing_grid (numpy.ndarray): The grid used for spatial partitioning of creatures.
        - dt (float): The time step for the update.
        - group (pygame.sprite.Group): The sprite group that the creature belongs to.

        Returns:
        - None
        """
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
            self.kill() # removes creature from all pygame sprite groups
            hashing_grid[row, column].remove(self) # removes creature from hashing grid
            
    def debug(self, screen, debug_list):
        """
        The code below draws the creature's FOV and displays energy and mating statistics.

        Args:
        - screen (pygame.display): The screen to draw on.
        - debug_list (list): List of creatures for debugging purposes.

        Returns:
        - None
        """
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

        """
        The code below displays the creature's energy and desire to mate
        statistics
        """
        energy = self.energy
        max_energy = np.mean(self.genes['max-energy'])

        desire_mate = self.desire_to_mate
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