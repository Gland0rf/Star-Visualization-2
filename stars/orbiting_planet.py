import random
import pygame

class OrbitingStar:
    def lerp(self, color1, color2, t):
        """Linearly interpolate between two colors."""
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

    def adjust_brightness(self, color, factor):
        return tuple(int(c + (255 - c) * factor) for c in color)
    
    def __init__(self, location, velocity, mass, speed_factor, min_radius, max_radius, pulse_speed, color_inner, color_outer, gradient_factor, gradient_stretch, screen_center, scale):
        self.location = location
        self.velocity = velocity
        self.mass = mass
        self.speed_factor = speed_factor
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.pulse_speed = pulse_speed
        self.color_inner = color_inner
        self.color_outer = color_outer
        self.gradient_factor = gradient_factor
        self.gradient_stretch = gradient_stretch
        self.screen_center = screen_center
        self.scale = scale

        self.radius = min_radius
        
    def update(self):
        pass
                
    def draw(self, surface):
        x_px = int(self.location[0] / self.scale + self.screen_center[0])
        y_px = int(self.location[1] / self.scale + self.screen_center[1])
        location_px = (x_px, y_px)

        radius_scaled = int(self.radius / 2)

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