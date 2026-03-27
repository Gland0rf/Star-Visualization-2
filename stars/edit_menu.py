import pygame
import math
from ui.sliders.slider import Slider

class Edit_Menu:
    
    def __init__(self, surface, game, inclination=74.25):
        self.surface = surface
        self.game = game
        self.selected_object = None
        self.inclination = math.radians(inclination)

        self.font_small = pygame.font.SysFont(None, 24)

        self.time_scale_exp = 0 if game.time_scale <= 1 else math.log10(game.time_scale)
    
    def check_events(self, event):
        # Planet sliders
        if hasattr(self, 'planet_gc_slider'):
            self.planet_gc_slider.slider_events(event)
        if hasattr(self, 'planet_vx_slider'):
            self.planet_vx_slider.slider_events(event)
        if hasattr(self, 'planet_vy_slider'):
            self.planet_vy_slider.slider_events(event)
        if hasattr(self, 'planet_speed_slider'):
            self.planet_speed_slider.slider_events(event)

        # Star slider(s)
        if hasattr(self, 'mass_star_slider'):
            self.mass_star_slider.slider_events(event)

        # Black hole sliders
        if hasattr(self, 'bh_mass_slider'):
            self.bh_mass_slider.slider_events(event)
        if hasattr(self, 'bh_disk_slider'):
            self.bh_disk_slider.slider_events(event)
        if hasattr(self, 'bh_inclination_slider'):
            self.bh_inclination_slider.slider_events(event)

    def check_for_click(self, event, objects, resolution_factor):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            mouse_pos = pygame.mouse.get_pos()
            for flyingObject in objects:
                cx, cy = self.game.to_pixels(flyingObject.location)
                radius = flyingObject.get_click_radius()
                distance = math.dist(mouse_pos, (cx, cy))
                if distance <= radius:
                    return flyingObject
            return "MISSED"
        return None
    
    # -------------------------------------------------
    # Planet sliders
    # -------------------------------------------------
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
        
        self.planet_gc_slider.create_slider("Mass of Planet: SLIDER_VALUE kg", self.font_small, 5.972e1, 1.0e25, planet.mass)
        self.planet_speed_slider.create_slider("Speed of Planet: SLIDER_VALUE sec", self.font_small, 1, 60*60*24*365, planet.speed_factor)
        
    # -------------------------------------------------
    # Star sliders
    # -------------------------------------------------
    def create_sliders_star(self, star, window_size, resolution_factor):
        # Mass slider
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
        self.mass_star_slider.create_slider(
            "Mass of Star: SLIDER_VALUE", self.font_small,
            1.989e10, 1.000e35, star.mass, log_scale=True
        )

        self.create_time_scale_slider(window_size, resolution_factor)

    def create_time_scale_slider(self, window_size, resolution_factor):
        """Logarithmic time-scale slider (10^x)."""
        # keep exponent in sync when (re)creating the slider
        self.time_scale_exp = 0 if self.game.time_scale <= 1 else math.log10(self.game.time_scale)

        self.time_scale_slider = Slider(
            # bind to *this* menu object's exponent, not game.time_scale
            other_instance=self,
            update_value='time_scale_exp',
            index=None,
            window_size=window_size,
            resolution_factor=resolution_factor,
            line_width=4,
            line_length=200,
            x_margin=20,
            y_margin=70,  # below star mass slider
            dot_radius=10,
            slider_color=(255, 255, 255),
            dot_color=(0, 200, 255)
        )

        self.time_scale_slider.create_slider(
            "Time Scale: 10^SLIDER_VALUE×", self.font_small,
            0, 20, self.time_scale_exp
        )

    # -------------------------------------------------
    # Black hole sliders
    # -------------------------------------------------
    def create_sliders_blackhole(self, blackhole, window_size, resolution_factor):
        mass_min = 1e20
        mass_max = max(1e32, blackhole.mass)
        disk_min = blackhole.r_s * 2
        disk_max = max(blackhole.r_s * 20, blackhole.disk_outer_m)

        self.bh_mass_slider = Slider(
            other_instance=blackhole, update_value='mass', index=None,
            window_size=window_size, resolution_factor=resolution_factor,
            line_width=4, line_length=200, x_margin=20, y_margin=20,
            dot_radius=10, slider_color=(255, 255, 255), dot_color=(255, 0, 0)
        )
        self.bh_mass_slider.create_slider(
            "Mass of Black Hole: SLIDER_VALUE kg", self.font_small,
            mass_min, mass_max, blackhole.mass
        )

        self.bh_disk_slider = Slider(
            other_instance=blackhole, update_value='disk_outer_m', index=None,
            window_size=window_size, resolution_factor=resolution_factor,
            line_width=4, line_length=200, x_margin=20, y_margin=60,
            dot_radius=10, slider_color=(255, 255, 255), dot_color=(255, 0, 0)
        )
        self.bh_disk_slider.create_slider(
            "Disk Outer Radius: SLIDER_VALUE m", self.font_small,
            disk_min, disk_max, blackhole.disk_outer_m
        )

    # -------------------------------------------------
    # Draw menus
    # -------------------------------------------------
    def open_planet_menu(self):
        self.planet_gc_slider.draw(self.surface)
        self.planet_speed_slider.draw(self.surface)
        return self.planet_gc_slider
    
    def open_star_menu(self):
        self.mass_star_slider.draw(self.surface)
        if hasattr(self, "time_scale_slider"):
            self.time_scale_slider.draw(self.surface)
            scale_text = self.font_small.render(
                f"Current: {self.game.time_scale:.2e}×", True, (200, 255, 255)
            )
            self.surface.blit(scale_text, (250, 90))

    def open_blackhole_menu(self):
        self.bh_mass_slider.draw(self.surface)
        self.bh_disk_slider.draw(self.surface)
        return self.bh_mass_slider
