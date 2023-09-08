import time, random, sys
from turtle import color
from PlanetSystem import StarSystem, Star, Planet

class HighPrecisionWallTime(): # Custom fps lock
    def __init__(self):
        self.t_start = time.perf_counter()

    def sample(self):
        Delay = self.t_start
        self.t_start = time.perf_counter() 
        return self.t_start - Delay

HighAccuracyTimer = HighPrecisionWallTime() 


########################### PROGRAM CONFIGURATION ##########################

FPS = 60 # Custom FPS lock
seed = 0 # Seed for random. 0 - random seed

############################################################################

if seed == 0:
    seed = random.randrange(sys.maxsize)
print("Current seed:", seed)
random.seed(seed)

if FPS > 1000 or FPS <=0:
    FPS=60

########################### SYSTEM CONFIGURATION ###########################

star_system = StarSystem(width=800, height=800)
star_system.ISC_DS = False # If stars collide - destroy system
star_system.PRE_CALCULATE_SIM = True
star_system.CALCULATE_ITERATIONS = 4000 # 4000 - stable orbits
star_system.NeedToDrawOrbit = True

############################################################################


stars = (
    Star(star_system, mass=20000, radius = 50, temperatureK=22000, position=(0, 300), velocity=(-4, 0)),
    #Star(star_system, mass=20000, temperatureK=4000, position=(0, -300), velocity=(4, 0)),
)

# Random Params
massR = (1, 20)
posR = (-1200, 1200)
velR = (-5,5)
ColorR = ("#8B0000", "#CD5C5C", "#ADFF2F", "#98FB98", "#3CB371", "#808000", "#FF1493", "#FFA07A", "#FF4500", "#20B2AA", "#008080", "#5F9EA0", "#E6E6FA", "#8B008B", "#FFFAFA", "#FFF8DC", "#DAA520", "#A52A2A", "#808080", "#696969", "#808080")

for i in range(100): # Planets to generate
    Planet(
        star_system,
        mass=random.randint(massR[0],massR[1]), 
        position=(random.randint(posR[0], posR[1]), random.randint(posR[0], posR[1])),
        velocity=(random.randint(velR[0], velR[1]), random.randint(velR[0], velR[1])),
        BodyColor=random.choice(ColorR))

if star_system.PRE_CALCULATE_SIM: # Calculate stable orbits
    for i in range(star_system.CALCULATE_ITERATIONS):
        star_system.calculate_all_body_interactions()
        star_system.calculateCameraPosition()
        star_system.update_all()
    star_system.PRE_CALCULATE_SIM = False 

while True:
    HighAccuracyTimer.sample() # Custom fps lock
    
    star_system.calculate_all_body_interactions()
    star_system.calculateCameraPosition()
    star_system.update_all()
    star_system.DrawTempTicks+=1 

    # Custom fps lock
    Delay = HighAccuracyTimer.sample()
    if Delay <= 1000/FPS: # ms
        time.sleep(((1000/FPS)-Delay)/1000)