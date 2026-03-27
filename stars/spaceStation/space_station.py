# stars/space_station.py
import math
import pygame

class SpaceStation:
    """
    Player-spawnable body obeying gravity like planets.
    Separate class (not subclassing OrbitingStar) to avoid coupling.
    """
    def __init__(self,
                 location,
                 velocity,
                 mass,
                 speed_factor,
                 screen_center,
                 scale,
                 game,
                 name="Station-1",
                 color_body=(180, 220, 255),
                 color_outline=(80, 140, 255),
                 thrust_power=5.0,
                 fuel=1000.0):
        self.location = list(location)
        self.velocity = list(velocity)
        self.mass = float(mass)
        self.speed_factor = float(speed_factor)

        self.screen_center = screen_center
        self.scale = scale
        self.game = game

        self.name = name
        self.color_body = color_body
        self.color_outline = color_outline

        # visuals
        self.base_size_px = 6  # UI symbol size baseline
        self.label_color = (200, 220, 255)

        self.direction = 0.0        # radians, 0 = +x
        self.rotation_speed = math.radians(90)  # deg/sec -> rad/sec
        self.thrust_power = thrust_power        # m/s² per full burn
        self.fuel = fuel
        self.is_thrusting = False
        self.auto_reboost = False

    def get_click_radius(self, padding: int = 20):
        """
        Return the clickable radius in pixel space.
        Stations are small, so use a fixed visible radius scaled by zoom.
        """
        zoom_factor = self.game.base_scale / self.game.scale
        visual_radius = int(self.base_size_px * zoom_factor)
        return max(10, visual_radius + padding)

    def update(self):
        """Hook for future (thrust, RCS, autopilot)."""
        pass

    def draw(self, surface, scale, base_scale):
        # Stable symbol size across zoom
        zoom = base_scale / max(scale, 1e-12)
        px_size = max(3, int(self.base_size_px * (0.6 + 0.4 * zoom)))

        x_px, y_px = self.game.to_pixels(self.location)
        cx, cy = int(x_px), int(y_px)

        # body (square) + antenna
        body = pygame.Rect(cx - px_size, cy - px_size, 2 * px_size, 2 * px_size)
        pygame.draw.rect(surface, self.color_body, body)
        pygame.draw.rect(surface, self.color_outline, body, 1)

        arm_len = int(px_size * 1.5)
        arm_len = int(px_size * 1.5)
        tip_x = cx + math.cos(self.direction) * arm_len
        tip_y = cy + math.sin(self.direction) * arm_len
        pygame.draw.line(surface, self.color_outline, (cx, cy), (tip_x, tip_y), 1)
        pygame.draw.circle(surface, self.color_outline, (int(tip_x), int(tip_y)), 1)

        # label (tiny)
        if hasattr(self.game, "font_small") and self.game.font_small:
            lbl = self.game.font_small.render(self.name, True, self.label_color)
            surface.blit(lbl, (cx + 6, cy - 6))

        if self.is_thrusting:
            flame_len = 12
            end_x = cx - math.cos(self.direction) * flame_len
            end_y = cy - math.sin(self.direction) * flame_len
            pygame.draw.line(surface, (255, 180, 60), (cx, cy), (end_x, end_y), 2)

        if self.game.CURRENT_EDIT_MENU is self:
            pygame.draw.circle(surface, (255, 255, 0), (cx, cy), px_size + 4, 1)

    # ------------------------------------------------------------------
    # CONTROL INPUTS
    # ------------------------------------------------------------------
    def apply_controls(self, keys, dt):
        """Handle rotation and thrust input — only moves if selected."""
        self.is_thrusting = False
        if self.fuel <= 0:
            return

        # Rotate (A/D)
        if keys[pygame.K_a]:
            self.direction -= self.rotation_speed * dt
        if keys[pygame.K_d]:
            self.direction += self.rotation_speed * dt

        # Forward/back thrust (W/S)
        if keys[pygame.K_w]:
            self.fire_thrusters(1.0, dt)
        elif keys[pygame.K_s]:
            self.fire_thrusters(-0.5, dt)

        # Lateral RCS (Q/E)
        if keys[pygame.K_q]:
            self.fire_rcs(-1.0, dt)
        if keys[pygame.K_e]:
            self.fire_rcs(1.0, dt)

    def fire_thrusters(self, power_scale, dt):
        """Main engine thrust along facing direction."""
        if self.fuel <= 0:
            return

        self.is_thrusting = True
        thrust_accel = self.thrust_power * power_scale  # m/s²
        fx = math.cos(self.direction) * thrust_accel
        fy = math.sin(self.direction) * thrust_accel

        # ✅ Apply Δv directly in real seconds (NO speed_factor)
        self.velocity[0] += fx * dt
        self.velocity[1] += fy * dt

        # Consume fuel
        burn = abs(thrust_accel) * dt * 0.5
        self.fuel = max(0.0, self.fuel - burn)

    def fire_rcs(self, side_scale, dt):
        """Small side thrusters for strafing."""
        if self.fuel <= 0:
            return

        self.is_thrusting = True
        side_accel = self.thrust_power * 0.3 * side_scale
        fx = -math.sin(self.direction) * side_accel
        fy = math.cos(self.direction) * side_accel

        # ✅ Same: apply Δv directly
        self.velocity[0] += fx * dt
        self.velocity[1] += fy * dt

        self.fuel = max(0.0, self.fuel - abs(side_accel) * dt * 0.25)