
''' random shit to try:
-screenwrap/torus

-middle click for a line(s) that....? alternate which point rotates 

use background color in new surface and alpha values to fade things?
'''


import pygame
import math
import random as r


SCR_WIDTH = 1200
SCR_HEIGHT = 800
CENTER = SCR_WIDTH // 2, SCR_HEIGHT // 2

BG_COLORS = ((200, 200, 200), (100, 100, 100))

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

# for lines
MAX_LENGTH = 200
MEDIAN_WIDTH = 4

# for all objects
MAX_DRIFT_RANGE = 10
MAX_SPEED = 1.5
MIN_SPEED = 0.5
COLOR_CHANGE = 1
SHADOW_COLOR = (150, 150, 150)
SHADOW_OFFSET = 15


'''------------------------'''

def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    

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
                  
    def draw(self, surface, flag):
        # x y is center of rect in this object so...
        x = self.x - self.size // 2
        y = self.y - self.size // 2
        pygame.draw.rect(surface, (self.red, self.green, 255 - self.red), (x, y, self.size, self.size))
        
        if flag:
            pygame.draw.rect(surface, (255 - self.red, self.green, self.red), (x + self.size, y + self.size, self.size, self.size))
        
            
    
    # draw shadows seperately so shadows aren't drawn on other objects
    def draw_shadow(self, surface, flag):
        # x y is center of rect in this object so...
        x = self.x - self.size // 2
        y = self.y - self.size // 2
        pygame.draw.rect(surface, SHADOW_COLOR, (x + SHADOW_OFFSET, y + SHADOW_OFFSET, self.size, self.size))
        
        if flag:
            pygame.draw.rect(surface, SHADOW_COLOR, (x + self.size + SHADOW_OFFSET, 
                y + self.size + SHADOW_OFFSET, self.size, self.size))
        

'''------------------------'''

class Circle:
    
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
    
    def draw(self, surface, flag):
        pygame.draw.circle(surface, (int(self.red), int(self.green), int(self.blue)),
            (int(self.x), int(self.y)), int(self.radius))
    
    def draw_shadow(self, surface, flag):
        pygame.draw.circle(surface, SHADOW_COLOR, (int(self.x + SHADOW_OFFSET),
            int(self.y + SHADOW_OFFSET)), int(self.radius))

'''------------------------'''

class Line:
    
    def __init__(self, xy_pos):
        self.x1, self.y1 = xy_pos
        self.x2, self.y2 = xy_pos
        self.length = r.randint(MAX_LENGTH // 2, MAX_LENGTH)
        self.width = r.randint(MEDIAN_WIDTH // 2, MEDIAN_WIDTH * 2)
        
        self.direction1 = r.randrange(360)
        self.direction2 = r.randrange(360)
        self.drift_range1 = r.randrange(MAX_DRIFT_RANGE)
        self.drift_range2 = r.randrange(MAX_DRIFT_RANGE // 2)
        self.speed = r.uniform(0.5, 1)
                        
        self.red = r.randint(200, 250)
        self.green = r.randint(200, 250)
        self.blue = r.randint(0, 100)
                
        self.alive = True
    
    def update(self, flag):
        
        # move and drift for both points 
        self.x1 += math.cos(self.direction1 * (math.pi / 180)) * self.speed
        self.y1 += math.sin(self.direction1 * (math.pi / 180)) * self.speed
        self.direction1 += r.randint(-self.drift_range1, self.drift_range1)    
        
        # point 2 stops if flag is on
        if not flag:
            self.x2 += math.cos(self.direction2 * (math.pi / 180)) * self.speed
            self.y2 += math.sin(self.direction2 * (math.pi / 180)) * self.speed
            self.direction2 += r.randint(-self.drift_range2, self.drift_range2)
        
        # keep them within 'length' of each other
        if distance(self.x1, self.y1, self.x2, self.y2) >= self.length:
            self.direction1 = math.atan2(self.y2 - self.y1, self.x2 - self.x1) * (180 / math.pi)
            
        # bounce off walls
        if self.x1 <= 0 or self.x1 >= SCR_WIDTH - 1 or self.y1 < 0 or self.y1 >= SCR_HEIGHT - 1:
            self.direction1 = self.direction1 - 180
        if self.x2 <= 0 or self.x2 >= SCR_WIDTH - 1 or self.y2 < 0 or self.y2 >= SCR_HEIGHT - 1:
            self.direction2 = self.direction2 - 180
        
        # fix position so it doesn't get stuck
        if self.x1 <= 0:
            self.x1 = 1
        elif self.x1 >= SCR_WIDTH - 1:
            self.x1 = SCR_WIDTH - 2
        if self.y1 <= 0:
            self.y1 = 1
        elif self.y1 >= SCR_HEIGHT - 1:
            self.y1 = SCR_HEIGHT - 2
        if self.x2 <= 0:
            self.x2 = 1
        elif self.x2 >= SCR_WIDTH - 1:
            self.x2 = SCR_WIDTH - 2
        if self.y2 <= 0:
            self.y2 = 1
        elif self.y2 >= SCR_HEIGHT - 1:
            self.y2 = SCR_HEIGHT - 2
        
        return []
    
    def draw(self, surface, flag):
        offset = 0
        if flag:
            offset = SHADOW_OFFSET # change pos to make it look stuck to surface
        pygame.draw.line(surface, (int(self.red), int(self.green), int(self.blue)), 
            (int(self.x1), int(self.y1)), (int(self.x2) + offset, int(self.y2) + offset), self.width)
    
    def draw_shadow(self, surface, flag):
        pygame.draw.line(surface, SHADOW_COLOR, (int(self.x1 + SHADOW_OFFSET), 
            int(self.y1 + SHADOW_OFFSET)), (int(self.x2 + SHADOW_OFFSET), 
            int(self.y2 + SHADOW_OFFSET)), self.width)
        
'''------------------------'''

def run():
    # Initialize game and create screen object.
    pygame.init()
    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    pygame.display.set_caption('random stuff')
    
    running = True
    bg_index = False
    
    # determines if screen is filled w/ background color between flips
    fill_flag = True
    # determines if shadows should be drawn
    shadow_flag = True
    # determines alternate actions of squares/circles/lines
    change_flag = False
    
    
    objects = []
    
    # Start the main loop for the game.
    while running:
        
        if fill_flag:
            screen.fill(BG_COLORS[bg_index])
    
        if shadow_flag:
            for obj in objects:
                obj.draw_shadow(screen, change_flag)
        
        # seperate from above to make sure all objects are draw above all shadows
        for obj in objects:
            obj.draw(screen, change_flag)
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
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                objects.append(Line(pygame.mouse.get_pos()))            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                change_flag = not change_flag
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                fill_flag = not fill_flag
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                shadow_flag = not shadow_flag
                bg_index = not bg_index # switches index between True and False (1 and 0 for index)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                objects = []
                
                    
        # Make the most recently drawn screen visible
        pygame.display.flip()

run()

