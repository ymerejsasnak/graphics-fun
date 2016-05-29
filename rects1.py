
''' random shit to try:
-screenwrap/torus
-right click to make circle that shrinks until gone, then makes random smaller children
around it, that grow then shrink, etc (all go to center of screen if space pressed)
-middle click for a line(s) that....?

use background color in new surface and alpha values to fade things?
'''


import pygame
import math
import random as r


SCR_WIDTH = 1200
SCR_HEIGHT = 800
CENTER = SCR_WIDTH // 2, SCR_HEIGHT // 2

BG_COLOR = (0, 0, 0)

# used for all objects
MAX_SIZE = 30
MIN_SIZE = 5

MAX_SIZE_RANGE = 10
MAX_DRIFT_RANGE = 10

MAX_SPEED = 2.5
MIN_SPEED = 0.5

COLOR_CHANGE = 1



class Square:
    
    def __init__(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.direction = r.randrange(360)
        self.drift_range = r.randrange(MAX_DRIFT_RANGE)
        self.size_range = r.randrange(MAX_SIZE_RANGE)
        self.speed = r.uniform(MIN_SPEED, MAX_SPEED)
                
        self.size_change = r.uniform(0.2, 0.5)
        
        self.size = r.randint(MIN_SIZE, MAX_SIZE)
        
        self.red = r.randint(150, 200)
        self.green = r.randint(0, 50)
        self.blue = r.randint(0,25)
        self.red_change = COLOR_CHANGE
        
    def update(self, flag):
        # move
        self.x += math.cos(self.direction * (math.pi / 180)) * self.speed
        self.y += math.sin(self.direction * (math.pi / 180)) * self.speed
        
        # movement drift if flag not set
        if not flag:
            self.direction += r.randint(-self.drift_range, self.drift_range)
            
        # wrap around smoothly
        if self.x < 0 - self.size // 2:
            self.x = SCR_WIDTH + self.size // 2
        elif self.x > SCR_WIDTH + self.size // 2:
            self.x = 0 - self.size // 2
        if self.y < 0 - self.size // 2:
            self.y = SCR_HEIGHT + self.size // 2
        elif self.y > SCR_HEIGHT + self.size // 2:
            self.y = 0 - self.size // 2        
        
        # change size (up to max, down to min, then switch)
        if flag:
            if self.size > MAX_SIZE or self.size < MIN_SIZE:
                self.size_change = -self.size_change
                if self.size < MIN_SIZE:
                    self.direction = r.randrange(360)
            self.size += self.size_change
            
        # change redness
        if self.red == 250 or self.red == 100:
            self.red_change = -self.red_change
        self.red += self.red_change
                  
    def draw(self, surface):
        # x y is center of rect in this object so...
        x = self.x - self.size // 2
        y = self.y - self.size // 2
        pygame.draw.rect(surface, (self.red, self.green, self.blue), (x, y, self.size, self.size))
    

def run():
    # Initialize game and create screen object.
    pygame.init()
    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    pygame.display.set_caption('random stuff')
    
    running = True
    
    # determines if screen is filled w/ background color between flips
    fill_flag = True
    # determines if square1 just floats around, or changes size and direction
    change_flag = False
    
    
    objects = []
    
    # Start the main loop for the game.
    while running:
        
        if fill_flag:
            screen.fill(BG_COLOR)
    
        for obj in objects:
            obj.update(change_flag)
            obj.draw(screen)
            
        # Watch for keyboard and mouse events.
        # Enter: turn on/off bg fill (visually: animation vs drawing)
        # Space: change behavior of objects
        # Esc: clear ALL objects
        # Left mouse button: create object 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                objects.append(Square())
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                change_flag = not change_flag
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                fill_flag = not fill_flag
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                objects = []
                
                    
        # Make the most recently drawn screen visible
        pygame.display.flip()

run()

