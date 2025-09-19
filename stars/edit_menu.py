import pygame
import math
from ui.sliders.slider import Slider

class Edit_Menu:
    
    def __init__(self, surface, scale, screen_center):
        self.surface = surface
        self.scale = scale
        self.screen_center = screen_center
    
    def check_events(self, event):
        if(hasattr(self, 'planet_gc_slider')):
            self.planet_gc_slider.slider_events(event)
        if(hasattr(self, 'planet_vx_slider')):
            self.planet_vx_slider.slider_events(event)
        if(hasattr(self, 'planet_vy_slider')):
            self.planet_vy_slider.slider_events(event)
        if(hasattr(self, 'planet_speed_slider')):
            self.planet_speed_slider.slider_events(event)
        if(hasattr(self, 'mass_star_slider')):
            self.mass_star_slider.slider_events(event)
    
    def check_for_click(self, event, orbiting_planets, resolution_factor):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            for i, planet in enumerate(orbiting_planets):
                cx = int(planet.location[0] / self.scale + self.screen_center[0])
                cy = int(planet.location[1] / self.scale + self.screen_center[1])
                
                radius = planet.radius
                distance = math.sqrt((mouse_pos[0] - cx) ** 2 +
                                 (mouse_pos[1] - cy) ** 2)
                
                if distance <= radius:
                    return planet
            return "MISSED"
        return None
    
    def create_sliders_planet(self, planet, window_size, resolution_factor):
        self.planet_gc_slider = Slider(
            other_instance=planet,
            update_value='mass',
            index=None,
            window_size=window_size,
            resolution_factor=resolution_factor,
            line_width=4,
            line_length=200,
            x_margin=20,
            y_margin=20,
            dot_radius=10,
            slider_color=(255, 255, 255),
            dot_color=(255, 0, 0)
        )
        
        self.planet_speed_slider = Slider(
            other_instance=planet,
            update_value='speed_factor',
            index=None,
            window_size=window_size,
            resolution_factor=resolution_factor,
            line_width=4,
            line_length=200,
            x_margin=20,
            y_margin=60,
            dot_radius=10,
            slider_color=(255, 255, 255),
            dot_color=(255, 0, 0)
        )
        
        self.planet_vx_slider = Slider(
            other_instance=planet,
            update_value='velocity',
            index=0,
            window_size=window_size,
            resolution_factor=resolution_factor,
            line_width=4,
            line_length=200,
            x_margin=20,
            y_margin=100,
            dot_radius=10,
            slider_color=(255, 255, 255),
            dot_color=(255, 0, 0)
        )
        
        self.planet_vy_slider = Slider(
            other_instance=planet,
            update_value='velocity',
            index=1,
            window_size=window_size,
            resolution_factor=resolution_factor,
            line_width=4,
            line_length=200,
            x_margin=20,
            y_margin=140,
            dot_radius=10,
            slider_color=(255, 255, 255),
            dot_color=(255, 0, 0)
        )
        
        self.planet_gc_slider.create_slider("Mass of Planet: SLIDER_VALUE", pygame.font.SysFont(None, 24), 5.972e1, 1.0e25, 5.972e24)
        self.planet_speed_slider.create_slider("Speed of Planet: SLIDER_VALUE", pygame.font.SysFont(None, 24), 60*60, 60*60*120, 60*60*24)
        self.planet_vx_slider.create_slider("Planet velocity x: SLIDER_VALUE", pygame.font.SysFont(None, 24), -4, 4, 0)
        self.planet_vy_slider.create_slider("Planet velocity y: SLIDER_VALUE", pygame.font.SysFont(None, 24), -4, 4, -2)
        
    def create_sliders_star(self, star, window_size, resolution_factor):
        self.mass_star_slider = Slider(
            other_instance=star,
            update_value='mass',
            index=None,
            window_size=window_size,
            resolution_factor=resolution_factor,
            line_width=4,
            line_length=200,
            x_margin=20,
            y_margin=20,
            dot_radius=10,
            slider_color=(255, 255, 255),
            dot_color=(255, 0, 0)
        )
        
        self.mass_star_slider.create_slider("Mass of Star: SLIDER_VALUE", pygame.font.SysFont(None, 24), 1.989e10, 1.000e31, 1.989e30)

    def open_planet_menu(self):
        self.planet_gc_slider.draw(self.surface)
        self.planet_speed_slider.draw(self.surface)
        self.planet_vx_slider.draw(self.surface)
        self.planet_vy_slider.draw(self.surface)
        
        return self.planet_gc_slider
    
    def open_star_menu(self):
        self.mass_star_slider.draw(self.surface)