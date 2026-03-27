import pygame
import math
import copy
import ui.lagrange.math as l_math
from stars.orbit_calculation import Orbit_Calc
from stars.details.planetDetails import PlanetDetails

class Lagrange_Points:
    def __init__(self, resolution_factor, scale, screen_center, game):
        self.resolution_factor = resolution_factor
        self.scale = scale
        self.screen_center = screen_center
        self.game = game

        # Cache orbit once (physics + pixels)
        self.cached_orbit_real = None
        self.cached_orbit_px = None
        self.cached_star_mass = None
        self.current_planet = None

        self.iteration = 0

    def to_px(self, pos):
        return self.game.to_pixels(pos)

    def compute_orbit(self, planet, G, max_steps=3650):  # ~10 years at 1-day steps
        orbit_calculation = Orbit_Calc(G)

        dt = 60 * 60 * 24      # 1 day in seconds
        total_time = dt * max_steps

        orbit_path = orbit_calculation.simulate_orbit(
            copy.deepcopy(planet.location),
            copy.deepcopy(planet.velocity),
            planet.mass,
            self.game.stars,   # ✅ all stars
            dt,
            total_time=total_time
        )
        self.cached_orbit_real = orbit_path

    def draw_dotted_line(self, surface, color, start_pos, end_pos,
                     width=1, segment_length=10, gap_length=5):
        zoom_factor = self.game.base_scale / self.game.scale

        # Width must stay visible
        width = max(1, int(width * zoom_factor))

        # Clamp segment & gap so they never hit 0 at extreme zooms
        seg_px = max(2, int(segment_length * zoom_factor))
        gap_px = max(2, int(gap_length * zoom_factor))

        if seg_px < 2 and gap_px < 2:
            return

        # If the points are (nearly) identical, don’t draw (avoid div by zero)
        total_length = math.dist(start_pos, end_pos)
        if total_length < 1e-6:
            return

        dx = (end_pos[0] - start_pos[0]) / total_length
        dy = (end_pos[1] - start_pos[1]) / total_length

        x, y = start_pos
        remain = total_length
        draw_phase = True

        while remain > 0:
            step = seg_px if draw_phase else gap_px
            step = min(step, remain)           # last partial segment
            nx = x + dx * step
            ny = y + dy * step

            if draw_phase:
                pygame.draw.line(surface, color, (x, y), (nx, ny), width)

            x, y = nx, ny
            remain -= step
            draw_phase = not draw_phase

    def draw_planet_details(self, screen, planet, star, game):
        planetDetails = PlanetDetails(screen, planet, star, game)
        planetDetails.draw()

    def draw_lagrange_points(self, planet, star, surface, G):
        white, red = (255, 255, 255), (255, 0, 0)

        if (
            self.current_planet is None
            or self.current_planet.mass != planet.mass
            or self.current_planet.speed_factor != planet.speed_factor
            or self.iteration >= 2
            or self.cached_star_mass is None
            or star.mass != self.cached_star_mass
        ):    
            self.compute_orbit(planet, G)
            self.current_planet = planet
            self.cached_star_mass = star.mass
            self.iteration = 0

        if self.cached_orbit_real and len(self.cached_orbit_real) > 1:
            pts = [self.to_px(p) for p in self.cached_orbit_real[::8]]
            if len(pts) > 1:
                pygame.draw.aalines(surface, red, False, pts)

        # L points
        l1, l2, l3, l4, l5 = l_math._compute_lagrange_points_phys(planet.parent_star, self.current_planet)
        
        zoom_factor = self.game.base_scale / self.game.scale
        font_size = max(10, int(36 * zoom_factor))
        font = pygame.font.SysFont(None, font_size)
        # Draw helpers
        def dot_and_label(p, label):
            dot_radius = max(2, int(10 * zoom_factor))

            q = self.to_px(p)
            pygame.draw.circle(surface, white, q, dot_radius)
            surface.blit(font.render(label, False, white), (q[0] + dot_radius + 4, q[1] - font_size // 2))
            return q
        
        p_px  = self.to_px(planet.location)
        s_px  = self.to_px(star.location)
        l1_px = dot_and_label(l1, "L1")
        l2_px = dot_and_label(l2, "L2")
        l3_px = dot_and_label(l3, "L3")
        l4_px = dot_and_label(l4, "L4")
        l5_px = dot_and_label(l5, "L5")

        # ---- Lines (pixel coords) ----
        self.draw_dotted_line(surface, white, p_px, s_px, width=int(2 * (self.game.base_scale / self.game.scale)))
        self.draw_dotted_line(surface, white, s_px, l3_px, width=int(2 * (self.game.base_scale / self.game.scale)))
        self.draw_dotted_line(surface, white, p_px, l4_px, width=int(2 * (self.game.base_scale / self.game.scale)))
        self.draw_dotted_line(surface, white, p_px, l5_px, width=int(2 * (self.game.base_scale / self.game.scale)))

        self.iteration += 1

        # Draw Planet Details
        self.draw_planet_details(surface, planet, star, self.game)