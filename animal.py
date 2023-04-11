import numpy as np
import pygame

from grid_functions import on_board


class Animal(pygame.sprite.Sprite):
    def __init__(self, genes, x, y, orientation, strength=0):
        super().__init__()
        # position information
        self.angle = orientation
        self.normal = np.array([np.cos(self.angle), np.sin(self.angle)])
        self.pos = np.array([x, y])

        # genome information
        self.genes = genes
        self.strength = strength
        self.color = genes["color"]

        # defining state variables
        self.energy = np.mean(
            self.genes["max-energy"]
        )  # averaging value from both chromosomes
        self.hunger = np.mean(self.genes["max-energy"]) - self.energy
        self.desire_mate = 0

        # pygame drawing information
        self.picture = pygame.image.load(
            "hawk.png"
        ).convert_alpha()  # converting makes draw time faster I guess
        self.picture = pygame.transform.scale(self.picture, (20, 20))
        # base-herbivore.png is white so the next line
        # tints it to the be color determined by it's genes
        self.picture.fill(self.color, special_flags=pygame.BLEND_MULT)

        self.image = self.rotate(self.picture, -self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = [round(self.pos[0]), round(self.pos[1])]

    def rotate(self, surface, angle):
        """
        This function exists because pygame's built in rotation functions
        don't work well. They degrade the image quality and eventually
        crash the program. See documentation for more information
        """
        rotated_surface = pygame.transform.rotozoom(surface, angle * 180 / np.pi, 1)
        return rotated_surface

    def update(self, grid, timestep):
        # updates the angle by the turn speed
        self.angle += np.mean(self.genes["turn-speed"]) * timestep

        # updates its orientation vector with new angle
        self.normal = np.array([np.cos(self.angle), np.sin(self.angle)])

        # updates its position with its speed and new normal vector
        self.pos = self.pos + self.normal * np.mean(self.genes["speed"]) * timestep

        # rotates the image according to new angle
        self.image = self.rotate(self.picture, -self.angle)
        self.rect = self.image.get_rect()

        # updates the draw position based on new position vector
        self.rect.center = [round(self.pos[0]), round(self.pos[1])]

        # eat the grass
        x = int(self.pos[0] / 25)
        y = int(self.pos[1] / 25)
        if (on_board(x, y, grid)):
            if grid[x, y] == 50:
                grid[x, y] = 0
