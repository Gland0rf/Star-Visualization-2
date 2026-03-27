import random
import pygame
from stars.blackHole import BlackHole

M_SUN = 1.98847e30

class PulsatingStar:
    def lerp(self, color1, color2, t):
        """Linearly interpolate between two colors."""
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

    def adjust_brightness(self, color, factor):
        return tuple(int(c + (255 - c) * factor) for c in color)
    
    def get_click_radius(self, padding: int = 6):
        """Return the clickable radius in pixel space, matching draw size."""
        zoom_factor = self.game.base_scale / self.game.scale
        visual_radius = int(self.radius / 2 * zoom_factor)
        return max(5, visual_radius + padding)

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
    
    def __init__(self, location, mass, min_radius, max_radius, pulse_speed, color_inner, color_outer, gradient_factor, gradient_stretch, screen_center, scale, game):
        self.location = location
        self.mass = mass
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

        self.name = "Unnamed Star"

        self.radius = min_radius
        self.grow = True
        self.allowed_grow = False
        self.initial_brightness = 0.0
        self.current_brightness = self.initial_brightness
        self.target_brightness = random.uniform(0.2, 1.0)
        self.brightness_direction = 1

        self.age = 0.0
        self.stage = "main_sequence"
        self.lifetime = self.calculate_lifetime() * 31_557_600
        self.state_limits = self.define_stage_fractions()

    def calculate_lifetime(self):
        m = self.mass / M_SUN
        if m < 0.43:
            return 100e9 * (m ** -2.3)
        elif m < 2:
            return 10e9 * (m ** -3.5)
        elif m < 20:
            return 10e9 * (m ** -2.5)
        else:
            return 3e9 * (m ** -1.0)
        
    def define_stage_fractions(self):
        return {"main_sequence": 0.0, "subgiant": 0.85, "giant": 0.95, "final": 1.0}
    
    def update_stellar_evolution(self, dt):
        self.age += dt * self.game.time_scale

        frac = self.age / self.lifetime
        if self.stage == "main_sequence" and frac >= self.state_limits["subgiant"]:
            self.stage = "subgiant"
        if self.stage == "subgiant" and frac >= self.state_limits["giant"]:
            self.stage = "giant"
        if self.stage == "giant" and frac >= self.state_limits["final"]:
            self.trigger_death()

        if self.stage == "main_sequence":
            self.color_inner = (255, 230, 160)
            self.color_outer = (255, 170, 80)
        elif self.stage == "subgiant":
            self.color_inner = (255, 210, 120)
            self.color_outer = (255, 120, 50)
        elif self.stage == "giant":
            self.color_inner = (255, 130, 80)
            self.color_outer = (255, 60, 30)
            self.max_radius *= 1.005

    def trigger_death(self):
        """Transition the star to its final evolutionary stage."""
        m = self.mass / M_SUN

        # --- White Dwarf (low mass < 8 solar masses) ---
        if m < 8:
            self.stage = "white_dwarf"
            self.mass *= 0.5  # loses about half its mass
            self.radius = self.max_radius * 0.05
            self.max_radius = self.radius
            self.color_inner = (220, 230, 255)
            self.color_outer = (160, 190, 255)
            self.allowed_grow = False
            self.cool_rate = 0.9999  # gradual fading
            self.current_brightness = 0.8

        # --- Neutron Star (medium mass < 25 solar masses) ---
        elif m < 25:
            self.stage = "neutron_star"
            self.mass *= 0.2  # most mass lost
            self.radius = 4  # small but visible pulsar
            self.max_radius = 4
            self.min_radius = 3
            self.color_inner = (140, 170, 255)
            self.color_outer = (80, 120, 255)
            self.allowed_grow = True
            self.pulse_speed *= 2.5  # pulsar-like
            self.current_brightness = 1.0

        # --- Black Hole (high mass ≥ 25 solar masses) ---
        else:
            self.stage = "black_hole"
            bh = BlackHole(
                location=self.location[:],
                mass=self.mass * 0.4,
                game=self.game,
                disk_outer_factor=50,
                inclination=0.0,
                rotation_speed_deg=0.35,
                disk_quality=0.8
            )

            bh.r_s *= 1e2
            bh.disk_outer_m = bh.r_s * 50
            bh.refresh_disk()

            self.game.black_holes.append(bh)
            if self in self.game.stars:
                self.game.stars.remove(self)
            return  # stop simulating this star

    def update(self):
        """Update brightness pulse + aging."""
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
                self.current_brightness = self.initial_brightness + (
                    (self.target_brightness - self.initial_brightness)
                    * (self.radius - self.min_radius)
                    / (self.max_radius - self.min_radius)
                )
            else:
                self.current_brightness = self.target_brightness - (
                    (self.target_brightness - self.initial_brightness)
                    * (self.max_radius - self.radius)
                    / (self.max_radius - self.min_radius)
                )

        # --- evolve with global time scale ---
        self.update_stellar_evolution(self.game.delta_time)

    def draw(self, surface, scale, base_scale):
        zoom_factor = base_scale / scale
        radius_scaled = max(1, int(self.radius * zoom_factor))
        x_px, y_px = self.game.to_pixels(self.location)
        pos = (x_px, y_px)

        if self.stage == "black_hole":
            pygame.draw.circle(surface, (0, 0, 0), pos, radius_scaled)
            pygame.draw.circle(surface, (80, 80, 80), pos, radius_scaled + 4, 2)
            return
        elif self.stage == "white_dwarf":
            r, g, b = self.color_inner
            r = max(int(r - 0.05), 100)
            g = max(int(g - 0.05), 100)
            b = max(int(b - 0.05), 100)
            self.color_inner = (r, g, b)

            r2, g2, b2 = self.color_outer
            r2 = max(int(r2 - 0.1), 80)
            g2 = max(int(g2 - 0.1), 80)
            b2 = max(int(b2 - 0.1), 80)
            self.color_outer = (r2, g2, b2)

            self.current_brightness *= self.cool_rate

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
            pygame.draw.circle(surface, color, pos, r)