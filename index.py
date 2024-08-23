import pygame
import pygame_gui
import sys

from stars.pulsating_star import PulsatingStar
from stars.orbiting_planet import OrbitingStar
from stars.orbit_calculation import Orbit_Calc

from ui.sliders.slider import Slider

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
    
    CURRENT_STATE = 1
    ACTIVE_STATE = 1
    PAUSE_STATE = 2
    
    clock = pygame.time.Clock()
    running = True
    
    high_res_surface = pygame.Surface((width * resolution_factor, height * resolution_factor))
    
    orbit_calculation = Orbit_Calc(G=1)
    
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
        location=[width // 2 + 300, height // 2 + 100],
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
    mass_planet_slider = Slider(
        other_instance=orbiting_planet,
        update_value='mass',
        index=None,
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
    
    mass_star_slider = Slider(
        other_instance=pulsating_star,
        update_value='mass',
        index=None,
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
    
    speed_slider = Slider(
        other_instance=orbiting_planet,
        update_value='speed_factor',
        index=None,
        window_size=(width, height),
        resolution_factor=resolution_factor,
        line_width=4,
        line_length=200,
        x_margin=20,
        y_margin=100,
        dot_radius=10,
        slider_color=(255, 255, 255),
        dot_color=(255, 0, 0)
    )
    
    gc_slider = Slider(
        other_instance=orbit_calculation,
        update_value='G',
        index=None,
        window_size=(width, height),
        resolution_factor=resolution_factor,
        line_width=4,
        line_length=200,
        x_margin=20,
        y_margin=140,
        dot_radius=10,
        slider_color=(255, 255, 255),
        dot_color=(255, 0, 0)
    )
    
    planet_vx_slider = Slider(
        other_instance=orbiting_planet,
        update_value='velocity',
        index=0,
        window_size=(width, height),
        resolution_factor=resolution_factor,
        line_width=4,
        line_length=200,
        x_margin=20,
        y_margin=180,
        dot_radius=10,
        slider_color=(255, 255, 255),
        dot_color=(255, 0, 0)
    )
    
    planet_vy_slider = Slider(
        other_instance=orbiting_planet,
        update_value='velocity',
        index=1,
        window_size=(width, height),
        resolution_factor=resolution_factor,
        line_width=4,
        line_length=200,
        x_margin=20,
        y_margin=220,
        dot_radius=10,
        slider_color=(255, 255, 255),
        dot_color=(255, 0, 0)
    )
    
    mass_planet_slider.create_slider("Mass of Planet 1: SLIDER_VALUE", pygame.font.SysFont(None, 36), 1, 100000, 1)
    mass_star_slider.create_slider("Mass of Star: SLIDER_VALUE", pygame.font.SysFont(None, 36), 1, 10000, 1000)
    speed_slider.create_slider("Speed of Planet 1: SLIDER_VALUE", pygame.font.SysFont(None, 36), 1, 80, 8)
    gc_slider.create_slider("Gravitational Constant: SLIDER_VALUE", pygame.font.SysFont(None, 36), 1, 5, 1)
    
    planet_vx_slider.create_slider("Planet 1 velocity x: SLIDER_VALUE", pygame.font.SysFont(None, 36), -4, 4, 0)
    planet_vy_slider.create_slider("Planet 1 velocity y: SLIDER_VALUE", pygame.font.SysFont(None, 36), -4, 4, -2)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if CURRENT_STATE == ACTIVE_STATE:
                        CURRENT_STATE = PAUSE_STATE
                    else:
                        CURRENT_STATE = ACTIVE_STATE
                
            mass_planet_slider.slider_events(event)
            mass_star_slider.slider_events(event)
            speed_slider.slider_events(event)
            gc_slider.slider_events(event)
            
            planet_vx_slider.slider_events(event)
            planet_vy_slider.slider_events(event)
        
        #Twinkling
        high_res_surface.fill(BLACK)
        
        if(CURRENT_STATE == ACTIVE_STATE):
            orbiting_planet.location, orbiting_planet.velocity = orbit_calculation.update_planet_position(
                orbiting_planet.location, orbiting_planet.velocity, orbiting_planet.mass,pulsating_star.location,
                pulsating_star.mass, orbiting_planet.speed_factor
            )
        
        pulsating_star.update()
        pulsating_star.draw(surface=high_res_surface, resolution_factor=resolution_factor)
        
        orbiting_planet.update()
        orbiting_planet.draw(surface=high_res_surface, resolution_factor=resolution_factor)
        
        #Sliders
        mass_planet_slider.draw(high_res_surface)
        mass_star_slider.draw(high_res_surface)
        speed_slider.draw(high_res_surface)
        gc_slider.draw(high_res_surface)
        planet_vx_slider.draw(high_res_surface)
        planet_vy_slider.draw(high_res_surface)
        
        scaled_surface = pygame.transform.smoothscale(high_res_surface, (width, height))
        screen.blit(scaled_surface, (0, 0))
               
        pygame.display.flip()
        
        pygame.display.update()
        
        clock.tick(60)
        
    pygame.quit()
    sys.exit()
    
if __name__ == '__main__':
    main()