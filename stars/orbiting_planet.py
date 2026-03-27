import random
import math
import pygame

class OrbitingStar:
    def lerp(self, color1, color2, t):
        """Linearly interpolate between two colors."""
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

    def adjust_brightness(self, color, factor):
        return tuple(int(c + (255 - c) * factor) for c in color)
    
    def compute_radius(self, mass, density=5500):
        return ((3 * mass) / (4 * math.pi * density)) ** (1/3)
    
    def get_click_radius(self, padding: int = 20):
        """Return the clickable radius in pixel space, matching draw size."""
        zoom_factor = self.game.base_scale / self.game.scale
        visual_radius = int(self.radius / 2 * zoom_factor)
        return max(5, visual_radius + padding)
    
    def __init__(self, location, velocity, mass, speed_factor, parent_star, min_radius, max_radius, pulse_speed, color_inner, color_outer, gradient_factor, gradient_stretch, screen_center, scale, game):
        self.location = location
        self.velocity = velocity
        self.mass = mass
        self.speed_factor = speed_factor
        self.parent_star = parent_star
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.pulse_speed = pulse_speed
        self.color_inner = color_inner
        self.color_outer = color_outer
        self.gradient_factor = gradient_factor
        self.gradient_stretch = gradient_stretch
        self.screen_center = screen_center
        self.scale = scale
        self.game = game

        self.name = "Unnamed Planet"

        self.density = 5500
        self.physical_radius = self.compute_radius(self.mass, self.density)

        self.radius = self.min_radius
        
    def update(self):
        pass
                
    def draw(self, surface, scale, base_scale):
        zoom_factor = base_scale / scale
        radius_scaled = max(1, int(self.radius / 2 * zoom_factor))

        from game import Game
        x_px, y_px = self.game.to_pixels(self.location)
        location_px = (int(x_px), int(y_px))


        gradient_start = (1.0 - self.gradient_stretch) * self.gradient_factor
        gradient_end = gradient_start + self.gradient_stretch

        for r in range(radius_scaled, 0, -1):
            t = r / radius_scaled

            if t > gradient_start:
                if t < gradient_end:
                    gradient_t = (t - gradient_start) / self.gradient_stretch
                    color = self.lerp(self.color_inner, self.color_outer, gradient_t)
                else:
                    color = self.color_outer
            else:
                color = self.color_inner

            pygame.draw.circle(surface, color, location_px, r)