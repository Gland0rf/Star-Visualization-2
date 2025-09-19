import pygame
import pygame_gui
import sys
from stars.edit_menu import Edit_Menu

from stars.pulsating_star import PulsatingStar
from stars.orbiting_planet import OrbitingStar
from stars.orbit_calculation import Orbit_Calc

from ui.kepler.menu import MenuButton, Menu
from ui.kepler.kepler_guides_sun_focus import Kepler_Guide_Sun_Focus
from ui.kepler.kepler_guides_equal import Kepler_Guide_Equal
from ui.kepler.kepler_guides_three import Kepler_Guide_Three

from ui.lagrange.draw import Lagrange_Points

class Game:
    pygame.init()
    
    def __init__(self, width, height, center_pos, resolution_factor, gravitational_constant, scale):
        #Screen dim
        self.width = width
        self.height = height
        self.center_pos = center_pos
        
        #Pygame
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.manager = pygame_gui.UIManager((self.width, self.height))
        
        #Resolution
        self.resolution_factor = resolution_factor
        
        self.orbiting_planets = []
        self.stars = []
        
        #Constant
        self.gravitational_constant = gravitational_constant
        self.scale = scale
        
        #States
        self.current_state = 1
        self.ACTIVE_STATE = 1
        self.PAUSE_STATE = 2
        self.GUIDE_STATE = 3
        self.MOVE_ONLY_STATE = 4
        self.guide_iteration = 0
        
        self.current_guide_active = -1

        
    def load_star(self, min_radius, max_radius, pulse_speed, gradient_factor, gradient_stretch):
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.pulse_speed = pulse_speed
        self.gradient_factor = gradient_factor
        self.gradient_stretch = gradient_stretch
    
    def change_state(self, state):
        self.current_state = state
    
    def to_pixels(self, real_pos, scale, screen_center):
        x_px = int(real_pos[0] / scale + screen_center[0])
        y_px = int(real_pos[1] / scale + screen_center[1])
        return [x_px, y_px]
            
    def main(self):
        #Colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        YELLOW = (255, 255, 0)
        RED = (255, 0, 0)
        
        width = self.width
        height = self.height
        resolution_factor = self.resolution_factor
        GRAVITATIONAL_CONSTANT = self.gravitational_constant
        center_pos = self.center_pos
        min_radius = self.min_radius
        max_radius = self.max_radius
        pulse_speed = self.pulse_speed
        gradient_factor = self.gradient_factor
        gradient_stretch = self.gradient_stretch
        screen_center = (width // 2, height // 2)
        
        CURRENT_EDIT_MENU = None
        
        clock = pygame.time.Clock()
        running = True
        
        self.high_res_surface = pygame.Surface((width * resolution_factor, height * resolution_factor))
        
        orbit_calculation = Orbit_Calc(G=GRAVITATIONAL_CONSTANT)
        
        pulsating_star = PulsatingStar(
            location=[0.0, 0.0],
            mass=1.989e30,
            min_radius=min_radius,
            max_radius = max_radius,
            pulse_speed=pulse_speed,
            color_inner=RED,
            color_outer=YELLOW,
            gradient_factor=gradient_factor,
            gradient_stretch=gradient_stretch,
            screen_center=screen_center,
            scale=self.scale
        )
        
        orbiting_planet = OrbitingStar(
            location=[1.996e11, 0.0],
            velocity=[0.0, 21_000.0],
            mass=5.972e24,
            speed_factor=60*60*24,
            min_radius=min_radius,
            max_radius = max_radius,
            pulse_speed=pulse_speed,
            color_inner=RED,
            color_outer=YELLOW,
            gradient_factor=gradient_factor,
            gradient_stretch=gradient_stretch,
            screen_center=screen_center,
            scale=self.scale
        )
        
        orbiting_planet_2 = OrbitingStar(
            location=[-1.496e11, 0.0],
            velocity=[0.0, -29_800.0],
            mass=5.972e24,
            speed_factor=60*60*24,
            min_radius=min_radius,
            max_radius = max_radius,
            pulse_speed=pulse_speed,
            color_inner=RED,
            color_outer=YELLOW,
            gradient_factor=gradient_factor,
            gradient_stretch=gradient_stretch,
            screen_center=screen_center,
            scale=self.scale
        )
        
        self.orbiting_planets.append(orbiting_planet)
        self.orbiting_planets.append(orbiting_planet_2)
        
        self.stars.append(pulsating_star)
        
        edit_menu = Edit_Menu(surface=self.high_res_surface, scale=self.scale, screen_center=screen_center)
        
        kepler_menu = Menu(resolution_factor, 0, 0, 300, 300, self)
        kepler_menu.add_button('Sun Focus', 50, 50, 200, 50, action=lambda: kepler_menu.button_action('Sun Focus'))
        kepler_menu.add_button('Equal areas in equal times', 50, 120, 200, 50, action=lambda: kepler_menu.button_action('Equal areas in equal times'))
        kepler_menu.add_button('Third Law', 50, 190, 200, 50, action=lambda: kepler_menu.button_action('Third Law'))
        
        kepler_menu_button = MenuButton(resolution_factor, 100, 100, 200, 50, 'Open Menu', kepler_menu)

        kepler_sun_focus_guide = Kepler_Guide_Sun_Focus(self.high_res_surface, self.orbiting_planets[0], self.stars[0], 13, (255, 255, 255), (self.width / 2, 100), GRAVITATIONAL_CONSTANT, resolution_factor)
        kepler_equal_guide = Kepler_Guide_Equal(self, self.high_res_surface, self.orbiting_planets[0], self.stars[0], 13, (255, 255, 255), (self.width / 2, 100), GRAVITATIONAL_CONSTANT, resolution_factor)
        kepler_guide_three = Kepler_Guide_Three(self, self.high_res_surface, self.orbiting_planets[0], self.stars[0], 13, (255, 255, 255), (self.width / 2, 100), GRAVITATIONAL_CONSTANT, resolution_factor)
        
        lagrange = Lagrange_Points(pulsating_star, resolution_factor, self.scale, screen_center)

        while running:
            self.high_res_surface.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.current_state == self.GUIDE_STATE:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.current_guide_active == 1:
                            if self.guide_iteration == kepler_sun_focus_guide.get_iteration_count() - 1:
                                self.current_state = self.ACTIVE_STATE
                                self.guide_iteration = -1
                            kepler_sun_focus_guide.clear_text()
                            self.guide_iteration += 1
                        elif self.current_guide_active == 2:
                            if self.guide_iteration == kepler_equal_guide.get_iteration_count() - 1:
                                self.current_state = self.ACTIVE_STATE
                                self.guide_iteration = -1
                                kepler_equal_guide.reset_values()
                            kepler_equal_guide.clear_text()
                            self.guide_iteration += 1
                        elif self.current_guide_active == 3:
                            if self.guide_iteration == kepler_guide_three.get_iteration_count() - 1:
                                self.current_state = self.ACTIVE_STATE
                                self.guide_iteration = -1
                                kepler_guide_three.reset_values()
                            kepler_guide_three.clear_text()
                            self.guide_iteration += 1
                elif self.current_state != self.MOVE_ONLY_STATE:
                    edit_menu.check_events(event)
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if self.current_state == self.ACTIVE_STATE:
                                self.current_state = self.PAUSE_STATE
                            elif self.current_state == self.PAUSE_STATE:
                                self.current_state = self.ACTIVE_STATE
                                
                    result_planet = edit_menu.check_for_click(event, self.orbiting_planets, resolution_factor)
                    result_star = edit_menu.check_for_click(event, self.stars, resolution_factor)
                    
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
                        
                    #Kepler Menu
                    if kepler_menu.is_visible:
                        kepler_menu.handle_event(event)
                    elif(self.current_state != self.GUIDE_STATE):
                        kepler_menu_button.handle_event(event)

                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.scale *= 0.9
                    elif event.y < 0:
                        self.scale *= 1.1
                
            if(CURRENT_EDIT_MENU in self.orbiting_planets):
                edit_menu.open_planet_menu()
                lagrange.draw_lagrange_points(CURRENT_EDIT_MENU, self.high_res_surface, GRAVITATIONAL_CONSTANT)
            elif(CURRENT_EDIT_MENU in self.stars):
                edit_menu.open_star_menu()
                
            #Guides
            if self.current_state == self.GUIDE_STATE or self.current_state == self.MOVE_ONLY_STATE:
                if self.current_guide_active == 1:
                    #Kepler law 1
                    kepler_sun_focus_guide.call_state(self.guide_iteration)
                elif self.current_guide_active == 2:
                    #Kepler law 2
                    kepler_equal_guide.call_state(self.guide_iteration)
                elif self.current_guide_active == 3:
                    #Kepler law 3
                    kepler_guide_three.call_state(self.guide_iteration)
            
            #Twinkling
            if(self.current_state == self.ACTIVE_STATE or self.current_state == self.MOVE_ONLY_STATE):
                orbiting_planet.location, orbiting_planet.velocity = orbit_calculation.update_planet_position(
                    orbiting_planet.location, orbiting_planet.velocity, orbiting_planet.mass,pulsating_star.location,
                    pulsating_star.mass, orbiting_planet.speed_factor
                )
                
                orbiting_planet_2.location, orbiting_planet_2.velocity = orbit_calculation.update_planet_position(
                    orbiting_planet_2.location, orbiting_planet_2.velocity, orbiting_planet_2.mass,pulsating_star.location,
                    pulsating_star.mass, orbiting_planet_2.speed_factor
                )
            
            pulsating_star.update()
            pulsating_star.draw(surface=self.high_res_surface)
            
            orbiting_planet.update()
            orbiting_planet.draw(surface=self.high_res_surface)
            
            orbiting_planet_2.update()
            orbiting_planet_2.draw(surface=self.high_res_surface)
            
            #Kepler Menu
            if self.current_state != self.GUIDE_STATE and self.current_state != self.MOVE_ONLY_STATE:
                kepler_menu_button.draw(self.high_res_surface)
            if kepler_menu.is_visible:
                kepler_menu.draw(self.high_res_surface)
            
            #Sliders
            #mass_star_slider.draw(self.high_res_surface)
                    
            scaled_surface = pygame.transform.smoothscale(self.high_res_surface, (width, height))
            self.screen.blit(scaled_surface, (0, 0))
                
            pygame.display.flip()
            
            pygame.display.update()
                    
            clock.tick(60)
            
        pygame.quit()
        sys.exit()
        
    if __name__ == '__main__':
        main()