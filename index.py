import pygame
import pygame_gui
import sys

from stars.pulsating_star import PulsatingStar
from stars.orbiting_star import OrbitingStar
from stars.orbit_calculation import update_planet_position

from ui.slider import Slider

pygame.init()
info = pygame.display.Info()

#Resolution
resolution_factor = 2

#Screen Dimensions
width, height = info.current_w, info.current_h
center_pos = [width // 2, height // 2]
screen = pygame.display.set_mode((width, height))

manager = pygame_gui.UIManager((width, height))

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

orbiting_planets = []
        
def main():
    global orbiting_planets
    
    clock = pygame.time.Clock()
    running = True
    
    high_res_surface = pygame.Surface((width * resolution_factor, height * resolution_factor))
    
    pulsating_star = PulsatingStar(
        location=center_pos,
        mass=1000,
        resolution_factor=resolution_factor,
        min_radius=min_radius,
        max_radius = max_radius,
        pulse_speed=pulse_speed,
        color_inner=RED,
        color_outer=YELLOW,
        gradient_factor=gradient_factor,
        gradient_stretch=gradient_stretch
    )
    
    orbiting_planet = OrbitingStar(
        location=[width // 2 + 300, height // 2],
        velocity=[0, -2 / resolution_factor],
        mass=1,
        speed_factor=8.0,
        resolution_factor=resolution_factor,
        min_radius=min_radius,
        max_radius = max_radius,
        pulse_speed=pulse_speed,
        color_inner=RED,
        color_outer=YELLOW,
        gradient_factor=gradient_factor,
        gradient_stretch=gradient_stretch
    )
    
    orbiting_planets.append(orbiting_planet)
    
    #Sliders
    mass_slider = Slider(
        manager=manager,
        other_instance=orbiting_planet,
        update_value='mass',
        window_size=(width, height),
        resolution_factor=resolution_factor,
        line_width=4,
        line_length=200,
        x_margin=20,
        y_margin=20,
        dot_radius=10,
        slider_color=(255, 255, 255),
        dot_color=(255, 0, 0)
    )
    
    speed_slider = Slider(
        manager=manager,
        other_instance=orbiting_planet,
        update_value='speed_factor',
        window_size=(width, height),
        resolution_factor=resolution_factor,
        line_width=4,
        line_length=200,
        x_margin=20,
        y_margin=60,
        dot_radius=10,
        slider_color=(255, 255, 255),
        dot_color=(255, 0, 0)
    )
    
    mass_slider.create_slider("Mass of Planet 1: SLIDER_VALUE", pygame.font.SysFont(None, 36), 1, 100000, 1)
    speed_slider.create_slider("Speed of Planet 1: SLIDER_VALUE", pygame.font.SysFont(None, 36), 1.0, 20.0, 8.0)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            mass_slider.slider_events(event)
            speed_slider.slider_events(event)
        
        #Twinkling
        high_res_surface.fill(BLACK)
        
        orbiting_planet.location, orbiting_planet.velocity = update_planet_position(orbiting_planet.location, orbiting_planet.velocity, orbiting_planet.mass, pulsating_star.location, pulsating_star.mass, orbiting_planet.speed_factor)
        
        pulsating_star.update()
        pulsating_star.draw(surface=high_res_surface, resolution_factor=resolution_factor)
        
        orbiting_planet.update()
        orbiting_planet.draw(surface=high_res_surface, resolution_factor=resolution_factor)
        
        #Sliders
        mass_slider.draw(high_res_surface)
        speed_slider.draw(high_res_surface)
        
        scaled_surface = pygame.transform.smoothscale(high_res_surface, (width, height))
        screen.blit(scaled_surface, (0, 0))
               
        pygame.display.flip()
        
        pygame.display.update()
        
        clock.tick(60)
        
    pygame.quit()
    sys.exit()
    
if __name__ == '__main__':
    main()