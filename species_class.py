from random import randrange

class Species:
    def ___init__(self,type,speed,strength,view_radius):
        self.type = type
        self.speed = speed
        self.strength = strength
        self.view_radius = view_radius
    
    def speed_adjustment(self):
        adjustment = randrange(10)
        self.speed = self.speed+adjustment
    
    def strength_adjustment(self):
        adjustment = randrange(10)
        self.strength = self.strength+adjustment
        