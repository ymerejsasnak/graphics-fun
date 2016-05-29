
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

BG_COLOR = (200, 200, 200)

# for squares
MAX_SIZE = 30
MIN_SIZE = 10
MAX_SIZE_RANGE = 10

# for circles
MAX_RADIUS = 20
RADIUS_VARIATION = 10
SHRINK_RATE = .05
PULSE_MEDIAN = .5
BURST_RANGE = 40
MAX_CHILDREN = 10

# for all objects
MAX_DRIFT_RANGE = 10
MAX_SPEED = 1.5
MIN_SPEED = 0.5
COLOR_CHANGE = 1
SHADOW_COLOR = (150, 150, 150)
SHADOW_OFFSET_X = 15
SHADOW_OFFSET_Y = 10



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
        self.green = r.randint(20, 100)
        # blue determined by red (255 - red)
        self.red_change = COLOR_CHANGE
        
        self.alive = True # unused...just here so this and circles can be in same objects list
        
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
        
        return []
                  
    def draw(self, surface):
        # x y is center of rect in this object so...
        x = self.x - self.size // 2
        y = self.y - self.size // 2
        pygame.draw.rect(surface, (self.red, self.green, 255 - self.red), (x, y, self.size, self.size))
    
    # draw shadows seperately so shadows aren't drawn on other objects
    def draw_shadow(self, surface):
        # x y is center of rect in this object so...
        x = self.x - self.size // 2
        y = self.y - self.size // 2
        pygame.draw.rect(surface, SHADOW_COLOR, (x + SHADOW_OFFSET_X, y + SHADOW_OFFSET_Y, self.size, self.size))


class Circle():
    
    def __init__(self, xy_pos, child=False):
        self.x, self.y = xy_pos
        self.direction = r.randrange(360)
        self.drift_range = r.randrange(MAX_DRIFT_RANGE * 2)
        self.speed = r.uniform(MIN_SPEED, MAX_SPEED * 1.5)
                
        self.radius = r.randint(MAX_RADIUS - RADIUS_VARIATION, MAX_RADIUS + RADIUS_VARIATION)
        
        self.pulse = r.uniform(PULSE_MEDIAN - .2, PULSE_MEDIAN + .2)
        self.pulse_speed = self.pulse * r.randint(20, 50)
        self.pulse_count = 0
        
        self.red = r.randint(15, 20)
        self.green = r.randint(100, 250)
        self.blue = r.randint(50, 100)
        self.color_change = COLOR_CHANGE / 3
        
        self.alive = True
        self.child = child
    
    def update(self, flag):
        # move and drift
        self.x += math.cos(self.direction * (math.pi / 180)) * self.speed
        self.y += math.sin(self.direction * (math.pi / 180)) * self.speed
        self.direction += r.randint(-self.drift_range, self.drift_range)
        
        # wrap around smoothly
        if self.x < 0 - self.radius:
            self.x = SCR_WIDTH + self.radius
        elif self.x > SCR_WIDTH + self.radius:
            self.x = 0 - self.radius
        if self.y < 0 - self.radius:
            self.y = SCR_HEIGHT + self.radius
        elif self.y > SCR_HEIGHT + self.radius:
            self.y = 0 - self.radius
        
        # if flag set, shrink radius and fade colors until death
        if flag:
            self.radius = max(self.radius - SHRINK_RATE, 2)
            
            # fade colors
            self.red = max(self.red - self.color_change, 0)
            self.green = max(self.green - self.color_change, 0)
            self.blue = max(self.blue - self.color_change, 0)
            
            # kill if black and tiny and make children if not a child itself
            if self.red + self.green + self.blue == 0 and self.radius == 2:
                self.alive = False
                if not self.child:
                    new_circles = []
                    for i in range(r.randint(2, MAX_CHILDREN)):
                        x = self.x + r.randint(int(-self.radius), int(self.radius))
                        y = self.y + r.randint(int(-self.radius), int(self.radius))
                        if i == 0:
                            child = False # one will be a parent for next burst
                        else:
                            child = True
                        new_circles.append(Circle((x, y), child))
                    return new_circles
        # else just pulsate a bit:
        else:
            self.radius = max(self.radius + self.pulse, 2)
            self.pulse_count += 1
            if self.pulse_count >= self.pulse_speed:
                self.pulse = -self.pulse
                self.pulse_count = 0
            
        return []
    
    def draw(self, surface):
        pygame.draw.circle(surface, (int(self.red), int(self.green), int(self.blue)), (int(self.x), int(self.y)), int(self.radius))
    
    def draw_shadow(self, surface):
        pygame.draw.circle(surface, SHADOW_COLOR, (int(self.x + SHADOW_OFFSET_X), int(self.y + SHADOW_OFFSET_Y)), int(self.radius))
        

def run():
    # Initialize game and create screen object.
    pygame.init()
    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    pygame.display.set_caption('random stuff')
    
    running = True
    
    # determines if screen is filled w/ background color between flips
    fill_flag = True
    # determines if shadows should be drawn
    shadow_flag = False
    # determines if square1 just floats around, or changes size and direction
    change_flag = False
    
    
    objects = []
    
    # Start the main loop for the game.
    while running:
        
        if fill_flag:
            screen.fill(BG_COLOR)
    
        if shadow_flag:
            for obj in objects:
                obj.draw_shadow(screen)
        
        # seperate from above to make sure all objects are draw above all shadows
        for obj in objects:
            obj.draw(screen)
            objects.extend(obj.update(change_flag))
        
        # update objects list
        objects = [obj for obj in objects if obj.alive]
            
        # Watch for keyboard and mouse events.
        # Enter: turn on/off bg fill (visually: animation vs drawing)
        # Space: change behavior of objects
        # Esc: clear ALL objects
        # S: shadows on/off
        # Left mouse button: create object 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                objects.append(Square())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                objects.append(Circle(pygame.mouse.get_pos()))
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                change_flag = not change_flag
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                fill_flag = not fill_flag
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                shadow_flag = not shadow_flag
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                objects = []
                
                    
        # Make the most recently drawn screen visible
        pygame.display.flip()

run()

