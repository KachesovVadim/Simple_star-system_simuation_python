import math
import turtle

PARALLAX_X = 0
PARALLAX_Y = 0

class Orbit(turtle.Turtle):
    def __init__(self, position=(0, 0), color = "yellow"):
        super().__init__()

        self.color(color)

        self.penup()        # Turtle func
        self.hideturtle()   # Turtle func

        self.setx(position[0])
        self.sety(position[1])
        
    def update(self, position=(0,0)):
        self.setx(position[0])
        self.sety(position[1])
        self.pendown()

class StarSystemBody(turtle.Turtle): # Non-sun body
    min_display_size = 20 # minimum body radius
    display_log_base = 1.1
    
    def __init__(
            self,
            star_system,
            mass,
            radius = 0,
            position=(0, 0),
            velocity=(0, 0),
            BodyColor = "yellow"):
        
        super().__init__()

        self.mass = mass
        self.setposition(position)
        self.velocity = velocity
        self.star_system = star_system
        
        if radius <= 0:
            self.display_size = max(
                math.log(self.mass, self.display_log_base),
                self.min_display_size,
            ) # Calculate size on screen
        else:
            self.display_size = radius
        
        self.penup()        # Turtle func
        self.hideturtle()   # Turtle func

        self.star_system.add_body(self)

        self.myOrbit = Orbit(position, color = BodyColor)
    
    def draw(self):
        self.clear()
        self.dot(self.display_size)

        if self.star_system.NeedToDrawOrbit: # Draw orbit
            if 3000-self.star_system.DrawTempTicks<100: # Every xxx ticks clear orbits 
                for body in self.star_system.bodies:
                    body.myOrbit.clear()
                self.star_system.DrawTempTicks = 0
            self.myOrbit.update((self.xcor(), self.ycor()))

        # Restore original pos for calculate physics
        self.setx(self.xcor()+PARALLAX_X)
        self.sety(self.ycor()+PARALLAX_Y)

    def move(self):
        self.setx((self.xcor() + self.velocity[0])-PARALLAX_X)
        self.sety((self.ycor() + self.velocity[1])-PARALLAX_Y)

    def __del__(self):
        self.myOrbit.clear()

class Planet(StarSystemBody):
    def __init__(
            self,
            solar_system,
            mass,
            radius = 0,
            position=(0, 0),
            velocity=(0, 0),
            BodyColor = "red"):
        super().__init__(solar_system, mass, radius, position, velocity, BodyColor)
        self.color(BodyColor) 

class Star(StarSystemBody):
    def __init__(
            self,
            star_system,
            mass,
            radius = 0,
            temperatureK = 6000, # Temp in Kelvins
            position=(0, 0),
            velocity=(0, 0)):

        super().__init__(star_system, mass, radius, position, velocity)
        
        if temperatureK<=3000:                              # M class star
            self.color("#8B0000")
        elif temperatureK>3000 and temperatureK<=4500:      # K class star
            self.color("#FF0000")
        elif temperatureK>4500 and temperatureK<=6000:      # G class star
            self.color("#FFD700")
        elif temperatureK>6000 and temperatureK<=8000:      # F class star
            self.color("#FFFF00")
        elif temperatureK>8000 and temperatureK<=10000:     # A class star
            self.color("#E0FFFF")
        elif temperatureK>10000 and temperatureK<=20000:    # B class star
            self.color("#00BFFF")
        elif temperatureK>20000 and temperatureK<=40000:    # O class star
            self.color("#0000CD")
        elif temperatureK>40000:                            # neutron star or hz
            self.color("white")


class StarSystem:
    def __init__(self, width, height):
        self.star_system = turtle.Screen()     # Turtle func
        self.star_system.setup(width, height)  # Turtle func
        self.star_system.tracer(0)             # Turtle func
        self.star_system.bgcolor("#002322")    # Turtle func
        self.bodies = []
        self.DrawTempTicks = 0 # Temporary var for cleaning orbits

        self.ISC_DS = True # If stars collide - destroy system
        self.PRE_CALCULATE_SIM = False # Calculate stable orbits
        self.CALCULATE_ITERATIONS = 0
        self.NeedToDrawOrbit = True
    
    def add_body(self, body):
        self.bodies.append(body)

    def remove_body(self, body):
        body.clear()
        try:
            self.bodies.remove(body)
        except:
            pass
        body.__del__()

    def update_all(self):
        for body in self.bodies:
            body.move()
            body.draw()

        if not self.PRE_CALCULATE_SIM:
            self.star_system.update()

    @staticmethod
    def accelerate_due_to_gravity(
            first: StarSystemBody,
            second: StarSystemBody):

        try:
            force = first.mass * second.mass / first.distance(second) ** 2
        except:
            force=0
        angle = first.towards(second)
        reverse = 1

        for body in first, second:
            try:
                acceleration = force / body.mass
            except:
                acceleration = 0
            acc_x = acceleration * math.cos(math.radians(angle))
            acc_y = acceleration * math.sin(math.radians(angle))
            body.velocity = (
                body.velocity[0] + (reverse * acc_x),
                body.velocity[1] + (reverse * acc_y))
            reverse = -1

    def check_collision(self, first, second):
        if first.distance(second) < first.display_size/2 + second.display_size/2: # if bodies collided
            if isinstance(first, Star) and isinstance(second, Star): 
                if self.ISC_DS == True: # If stars collide - destroy system
                    exit() # If stars collides, kill process
            for body in first, second: # If planet collide a star, destroy planet
                if isinstance(body, Planet):
                    self.remove_body(body)
        
        elif first.distance(second) > 10000 and ((isinstance(first, Star) and isinstance(second, Planet)) or (isinstance(first, Planet) and isinstance(second, Star))): # If planet out of system
            for body in first, second: 
                if isinstance(body, Planet):
                    self.remove_body(body)

    def calculate_all_body_interactions(self):
        bodies_copy = self.bodies.copy()
        for idx, first in enumerate(bodies_copy):
            for second in bodies_copy[idx + 1:]:
                self.accelerate_due_to_gravity(first, second)
                self.check_collision(first, second)

    def calculateCameraPosition(self):
        global PARALLAX_X, PARALLAX_Y
        PARALLAX_X = 0
        PARALLAX_Y = 0
        
        stars_copy = []
        stars_pos = []
        for body in self.bodies:
            if isinstance(body, Star):
                stars_copy.append(body)
                stars_pos.append(body.pos())
        
        if len(stars_copy) == 1: # If 1 star in system
            PARALLAX_X += stars_pos[0][0]
            PARALLAX_Y += stars_pos[0][1]

        elif len(stars_copy) == 0: # if 0 stars
            pass
        
        else: # If 1<stars in system
            for coordinate in stars_pos:
                PARALLAX_X += coordinate[0]/2
                PARALLAX_Y += coordinate[1]/2