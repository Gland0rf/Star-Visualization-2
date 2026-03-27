from game import Game
import pygame

info = pygame.display.Info()

#Resolution
resolution_factor = 1

#Screen Dimensions
width, height = info.current_w, info.current_h
print(width, height)
center_pos = [width // 2, height // 2]

#Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

#Star properties
max_radius = 70
min_radius = 60
pulse_speed = 0.008

#Gradient
gradient_factor = 0.93
gradient_stretch = 0.5

# Scale
AU = 1.496e11
scale = AU / 1000

GRAVITATIONAL_CONSTANT = 6.674 * (10 ** -11)
SPEED_OF_LIGHT = 299_792_458.0

game = Game(width, height, center_pos, resolution_factor, GRAVITATIONAL_CONSTANT, SPEED_OF_LIGHT, scale)
game.load_star(min_radius, max_radius, pulse_speed, gradient_factor, gradient_stretch)
game.main()