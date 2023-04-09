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

    def offspring(self,mate):
        type = self.type
        avg_speed = (self.speed + mate.speed)/2
        avg_strength = (self.strength+mate.strength)/2
        avg_view = (self.view_radius+mate.view_radius)/2
        return Species(type,avg_speed,avg_strength,avg_view)