import random
import pygame

class PulsatingStar:
    def lerp(self, color1, color2, t):
        """Linearly interpolate between two colors."""
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

    def adjust_brightness(self, color, factor):
        return tuple(int(c + (255 - c) * factor) for c in color)

    def draw_pulsating_star(self, surface, location, radius, color_inner, color_outer, gradient_factor, gradient_stretch, pulse_brightness):
        
        color_inner = self.adjust_brightness(color_inner, pulse_brightness)
        color_outer = self.adjust_brightness(color_outer, pulse_brightness)
        
        gradient_start = (1.0 - gradient_stretch) * gradient_factor
        gradient_end = gradient_start + gradient_stretch
        
        for r in range(radius, 0, -1):
            t = r / radius
            
            if t > gradient_start:  # Apply gradient
                if t < gradient_end:
                    gradient_t = (t - gradient_start) / gradient_stretch
                    color = self.lerp(color_inner, color_outer, gradient_t)
                else:
                    color = color_outer
            else:
                color = color_inner
                
            pygame.draw.circle(surface, color, location, r)
    
    def __init__(self, location, mass, resolution_factor, min_radius, max_radius, pulse_speed, color_inner, color_outer, gradient_factor, gradient_stretch):
        self.location = [c * resolution_factor for c in location]
        self.mass = mass
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.pulse_speed = pulse_speed
        self.color_inner = color_inner
        self.color_outer = color_outer
        self.gradient_factor = gradient_factor
        self.gradient_stretch = gradient_stretch

        self.radius = min_radius
        self.grow = True
        self.allowed_grow = False

        self.initial_brightness = 0.0
        self.current_brightness = self.initial_brightness
        self.target_brightness = random.uniform(0.2, 1.0)
        self.brightness_direction = 1
        
    def update(self):
        rand = random.randint(0, 50)
        if rand == 13:
            self.allowed_grow = True
            self.target_brightness = random.uniform(0.2, 1.0)

        if self.allowed_grow:
            if self.grow:
                self.radius += self.pulse_speed * self.max_radius
                if self.radius >= self.max_radius:
                    self.grow = False
                    self.brightness_direction = -1
            else:
                self.radius -= self.pulse_speed * self.max_radius
                if self.radius <= self.min_radius:
                    self.grow = True
                    self.brightness_direction = 1
                    self.allowed_grow = False

            if self.brightness_direction == 1:
                self.current_brightness = self.initial_brightness + (self.target_brightness - self.initial_brightness) * (self.radius - self.min_radius) / (self.max_radius - self.min_radius)
            else:
                self.current_brightness = self.target_brightness - (self.target_brightness - self.initial_brightness) * (self.max_radius - self.radius) / (self.max_radius - self.min_radius)
                
    def draw(self, surface, resolution_factor):
        radius_scaled = int(self.radius * resolution_factor)
        color_inner = self.adjust_brightness(self.color_inner, self.current_brightness)
        color_outer = self.adjust_brightness(self.color_outer, self.current_brightness)

        gradient_start = (1.0 - self.gradient_stretch) * self.gradient_factor
        gradient_end = gradient_start + self.gradient_stretch

        for r in range(radius_scaled, 0, -1):
            t = r / radius_scaled

            if t > gradient_start:
                if t < gradient_end:
                    gradient_t = (t - gradient_start) / self.gradient_stretch
                    color = self.lerp(color_inner, color_outer, gradient_t)
                else:
                    color = color_outer
            else:
                color = color_inner

            color = [min(i, 255) for i in color]
            pygame.draw.circle(surface, color, self.location, r)