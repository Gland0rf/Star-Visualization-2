import pygame
import pygame_gui
import sys
from stars.edit_menu import Edit_Menu

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
stars = []
        
def main():
    global orbiting_planets, stars
    
    CURRENT_STATE = 1
    ACTIVE_STATE = 1
    PAUSE_STATE = 2
    
    CURRENT_EDIT_MENU = None
    
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
    
    orbiting_planet_2 = OrbitingStar(
        location=[width // 2 - 300, height // 2 - 100],
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
    orbiting_planets.append(orbiting_planet_2)
    
    stars.append(pulsating_star)
    
    edit_menu = Edit_Menu(surface=high_res_surface)
    
    while running:
        high_res_surface.fill(BLACK)
        
        for event in pygame.event.get():
            edit_menu.check_events(event)
            
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if CURRENT_STATE == ACTIVE_STATE:
                        CURRENT_STATE = PAUSE_STATE
                    else:
                        CURRENT_STATE = ACTIVE_STATE
                        CURRENT_EDIT_MENU = None
                        
            result_planet = edit_menu.check_for_click(event, orbiting_planets, resolution_factor)
            result_star = edit_menu.check_for_click(event, stars, resolution_factor)
            
            if result_planet == "MISSED" and result_star == "MISSED":
                mouse_pos = pygame.mouse.get_pos()
                if(hasattr(edit_menu, 'planet_gc_slider')):
                    if(mouse_pos[0] * resolution_factor < edit_menu.planet_gc_slider.line_start[0] - 50):
                        CURRENT_EDIT_MENU = None
                elif(hasattr(edit_menu, 'mass_star_slider')):
                    if(mouse_pos[0] * resolution_factor < edit_menu.mass_star_slider.line_start[0] - 50):
                        CURRENT_EDIT_MENU = None
                        
            elif result_planet is not None and result_planet != "MISSED":
                CURRENT_EDIT_MENU = result_planet
                edit_menu.create_sliders_planet(result_planet, (width, height), resolution_factor)
            elif result_star is not None and result_star != "MISSED":
                CURRENT_EDIT_MENU = result_star
                edit_menu.create_sliders_star(result_star, (width, height), resolution_factor)
            
        if(CURRENT_EDIT_MENU in orbiting_planets):
            edit_menu.open_planet_menu()
        elif(CURRENT_EDIT_MENU in stars):
            edit_menu.open_star_menu()
        
        #Twinkling
        if(CURRENT_STATE == ACTIVE_STATE):
            orbiting_planet.location, orbiting_planet.velocity = orbit_calculation.update_planet_position(
                orbiting_planet.location, orbiting_planet.velocity, orbiting_planet.mass,pulsating_star.location,
                pulsating_star.mass, orbiting_planet.speed_factor
            )
            
            orbiting_planet_2.location, orbiting_planet_2.velocity = orbit_calculation.update_planet_position(
                orbiting_planet_2.location, orbiting_planet_2.velocity, orbiting_planet_2.mass,pulsating_star.location,
                pulsating_star.mass, orbiting_planet_2.speed_factor
            )
        
        pulsating_star.update()
        pulsating_star.draw(surface=high_res_surface, resolution_factor=resolution_factor)
        
        orbiting_planet.update()
        orbiting_planet.draw(surface=high_res_surface, resolution_factor=resolution_factor)
        
        orbiting_planet_2.update()
        orbiting_planet_2.draw(surface=high_res_surface, resolution_factor=resolution_factor)
        
        #Sliders
        #mass_star_slider.draw(high_res_surface)
        
        scaled_surface = pygame.transform.smoothscale(high_res_surface, (width, height))
        screen.blit(scaled_surface, (0, 0))
               
        pygame.display.flip()
        
        pygame.display.update()
        
        clock.tick(60)
        
    pygame.quit()
    sys.exit()
    
if __name__ == '__main__':
    main()