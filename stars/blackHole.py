import math
import random
import pygame
from pygame import gfxdraw

# -------- utility: simple color lerp --------
def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )

class BlackHole:
    """
    Stylized black hole:
      • Smooth glowing disk (yellow→orange→red).
      • Stable white rim.
      • Pulsating black event horizon.
      • Scales with zoom.
      • Freezes when paused.
    """

    def __init__(
        self,
        location,
        mass,
        game,
        *,
        disk_outer_factor=3.0,
        inclination=0.0,
        rotation_speed_deg=0.35,
        pulse_speed_hz=0.01,
        disk_quality=1.0,
        seed=7
    ):
        self.location = list(location)
        self.mass = float(mass)
        self.game = game

        # constants
        self.G = game.gravitational_constant
        self.c = game.light_speed

        # physical radii
        self.r_s = (2 * self.G * self.mass) / (self.c**2)
        self.r_photon = 1.5 * self.r_s
        self.r_isco = 3.0 * self.r_s
        self.disk_inner_m = self.r_isco
        self.disk_outer_m = self.r_s * disk_outer_factor

        # For compatibility
        self.physical_radius = self.r_s

        # visual params
        self.inclination = 74.25
        self.rotation_speed = math.radians(rotation_speed_deg)
        self.pulse_speed_hz = float(pulse_speed_hz)
        self.disk_quality = disk_quality

        # prerender base size
        self.base_px = 420

        # palette (warm gradient)
        self.palette = [
            (255, 200, 60),
            (255, 140, 40),
            (230, 70, 30),
            (120, 20, 20),
        ]

        self.horizon_tilt = True

        # runtime
        self.theta = 0.0
        self._pulse_phase = 0.0
        random.seed(seed)

        # prerender
        self.disk_tex = self._make_disk_texture(self.base_px, quality=self.disk_quality)

    # ----------------- public API -----------------

    def update(self, dt: float = 1.0):
        if getattr(self.game, "current_state", None) == getattr(self.game, "PAUSE_STATE", -999):
            return

        self.theta = (self.theta + self.rotation_speed * dt) % math.tau
        self._pulse_phase = (self._pulse_phase + (math.tau * self.pulse_speed_hz) * dt) % math.tau

    def draw(self, surface, scale, base_scale):
        px_x, px_y = self.game.to_pixels(self.location)
        screen_w, screen_h = self.game.width, self.game.height

        # Skip if far outside view (+ margin)
        margin = 500
        if not (-margin < px_x < screen_w + margin and -margin < px_y < screen_h + margin):
            return

        # Compute disk size in pixel space — correctly scales with zoom
        disk_outer_px = self.disk_outer_m / self.game.scale

        # If the disk is tiny, skip rendering entirely (perf optimization)
        if disk_outer_px < 2:
            return

        # Clamp to avoid insane texture sizes when zoomed in
        disk_outer_px = min(disk_outer_px, 1200)

        # Compute scale factor for pre-rendered texture
        scale_factor = disk_outer_px / (self.base_px / 2)

        # Rotate + scale the disk texture
        rotated_disk = pygame.transform.rotozoom(
            self.disk_tex, -math.degrees(self.theta), scale_factor
        )

        # Apply inclination squash
        if self.inclination != 0.0:
            squash = max(0.15, math.cos(self.inclination))
            w, h = rotated_disk.get_size()
            rotated_disk = pygame.transform.smoothscale(
                rotated_disk, (w, max(1, int(h * squash)))
            )

        rect = rotated_disk.get_rect(center=(
            int(px_x / self.game.resolution_factor),
            int(px_y / self.game.resolution_factor)
        ))

        w, h = rotated_disk.get_size()
        back_half = rotated_disk.subsurface((0, 0, w, h // 2))
        front_half = rotated_disk.subsurface((0, h // 2, w, h - h // 2))

        # Draw back half first
        surface.blit(back_half, rect.topleft)

        # Draw pulsating black core (event horizon)
        self._draw_core(surface, rect.center)

        # Then front half (for depth illusion)
        surface.blit(front_half, (rect.left, rect.top + h // 2))

    def get_click_radius(self, padding: int = 20):
        """Return the clickable radius in pixels, around the event horizon."""
        zoom_factor = self.game.base_scale / self.game.scale
        horizon_px = int((self.r_s / self.game.scale) * zoom_factor)
        return max(5, horizon_px + padding)

    def update_physics(self):
        # recompute radii
        self.r_s = (2 * self.G * self.mass) / (self.c**2)
        self.r_photon = 1.5 * self.r_s
        self.r_isco = 3.0 * self.r_s
        self.disk_inner_m = self.r_isco

    def refresh_disk(self):
        self.disk_tex = self._make_disk_texture(self.base_px, quality=self.disk_quality)

    def __setattr__(self, name, value):
        if name == "inclination":
            super().__setattr__(name, math.radians(value))  # convert degrees → radians
            return
        
        super().__setattr__(name, value)

        if name == "mass" and hasattr(self, "G") and hasattr(self, "c"):
            self.update_physics()
            self.refresh_disk()

        if name == "disk_outer_m" and hasattr(self, "base_px"):
            self.refresh_disk()

    # ----------------- internals -----------------

    def _make_disk_texture(self, size, quality=1.0):
        """Smooth gradient disk (no streaks)."""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        outer_px = int(0.48 * size)
        inner_px = int(outer_px * (self.disk_inner_m / self.disk_outer_m))

        step = max(1, int(1 / quality))
        # fill with concentric circles
        for r in range(outer_px, inner_px, -step):
            t = (r - inner_px) / max(1, outer_px - inner_px)
            col = lerp_color(self.palette[0], self.palette[-1], 1 - t)
            alpha = int(lerp(255, 40, t))
            gfxdraw.aacircle(surf, cx, cy, r, (*col, alpha))
            gfxdraw.filled_circle(surf, cx, cy, r, (*col, alpha))

        return surf

    def _draw_core(self, surface, center):
        """Draw slow pulsating event horizon (top half only) with glowing rim."""
        core_px_world = self.r_s / self.game.scale
        base_px = max(1, int(core_px_world))

        # Gentle breathing (±2% radius)
        pulse = 1.0 + 0.02 * math.sin(self._pulse_phase)
        core_px = max(1, int(base_px * pulse))

        # Stronger brightness modulation (100–255)
        brightness = 100 + int(155 * (0.5 + 0.5 * math.sin(self._pulse_phase)))
        rim_color = (brightness, brightness, brightness)

        # Horizon surface
        horizon_surf = pygame.Surface((core_px * 4, core_px * 4), pygame.SRCALPHA)
        cx, cy = horizon_surf.get_width() // 2, horizon_surf.get_height() // 2

        # Black event horizon
        pygame.draw.circle(horizon_surf, (0, 0, 0), (cx, cy), core_px)

        # White rim (solid)
        pygame.draw.circle(horizon_surf, rim_color, (cx, cy), core_px, 2)
        gfxdraw.aacircle(horizon_surf, cx, cy, core_px, rim_color)

        # Soft glow halo (fade outward)
        for i in range(6):
            alpha = max(0, 80 - i * 12)
            radius = core_px + i + 1
            glow_color = (brightness, brightness, brightness, alpha)
            gfxdraw.aacircle(horizon_surf, cx, cy, radius, glow_color)

        # Mask bottom half
        pygame.draw.rect(horizon_surf, (0, 0, 0, 0), (0, cy, horizon_surf.get_width(), cy))

        # Blit centered
        rect = horizon_surf.get_rect(center=center)
        surface.blit(horizon_surf, rect)