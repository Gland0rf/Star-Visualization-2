import pygame
import math
import copy
import ui.lagrange.math as l_math
from stars.orbit_calculation import Orbit_Calc


class Lagrange_Points:
    def __init__(self, star, resolution_factor, scale, screen_center):
        self.star = star
        self.resolution_factor = resolution_factor
        self.scale = scale
        self.screen_center = screen_center

        # Cache orbit once (physics + pixels)
        self.cached_orbit_real = None
        self.cached_orbit_px = None
        self.current_planet = None

        self.iteration = 0

    def to_px(self, pos):
        """Convert physics coordinates (meters) to screen pixels."""
        return (
            pos[0] / self.scale + self.screen_center[0],
            pos[1] / self.scale + self.screen_center[1]
        )

    def compute_orbit(self, G, max_steps=1000):
        """Simulate orbit in physics space and cache both real + pixel paths."""
        orbit_calculation = Orbit_Calc(G)
        r = math.dist(self.current_planet.location, self.star.location)
        period = 2 * math.pi * math.sqrt(r**3 / (G * self.star.mass))
        dt = period / 1000 # 2000 steps per orbit
        total_time = period
        orbit_path = orbit_calculation.simulate_orbit(
            copy.deepcopy(self.current_planet.location),
            copy.deepcopy(self.current_planet.velocity),
            self.current_planet.mass,
            self.star.location,
            self.star.mass,
            dt, total_time=total_time
        )
        self.cached_orbit_real = orbit_path
        self.cached_orbit_px = [self.to_px(p) for p in orbit_path]

    def draw_dotted_line(self, surface, color, start_pos, end_pos,
                         width=1, segment_length=10, gap_length=5):
        total_length = math.dist(start_pos, end_pos)
        direction_vector = (
            (end_pos[0] - start_pos[0]) / total_length,
            (end_pos[1] - start_pos[1]) / total_length,
        )
        current_pos = start_pos
        drawing = True
        while total_length > 0:
            if drawing:
                segment_end_pos = (
                    current_pos[0] + direction_vector[0] * min(segment_length, total_length),
                    current_pos[1] + direction_vector[1] * min(segment_length, total_length),
                )
                pygame.draw.line(surface, color, current_pos, segment_end_pos, width)
                current_pos = segment_end_pos
                total_length -= segment_length
            else:
                current_pos = (
                    current_pos[0] + direction_vector[0] * min(gap_length, total_length),
                    current_pos[1] + direction_vector[1] * min(gap_length, total_length),
                )
                total_length -= gap_length
            drawing = not drawing

    def draw_lagrange_points(self, planet, surface, G):
        white, red = (255, 255, 255), (255, 0, 0)

        if (self.current_planet != planet or self.iteration >= 5):
            self.current_planet_px = None
            self.cached_orbit_real = None
            self.cached_orbit_px = None
            self.iteration = 0
        self.current_planet = planet

        # --- Orbit preview ---
        if self.cached_orbit_px is None or self.cached_orbit_real is None:
            self.compute_orbit(G, max_steps=1000)
        if len(self.cached_orbit_px) > 1:
            pts = self.cached_orbit_px[::8]
            if len(pts) > 1:
                pygame.draw.aalines(surface, red, False, pts)

        # L points
        l1, l2, l3, l4, l5 = l_math._compute_lagrange_points_phys(self.star, self.current_planet)
        
        # Draw helpers
        font = pygame.font.SysFont(None, 36)
        def dot_and_label(p, label):
            q = self.to_px(p)
            pygame.draw.circle(surface, white, q, 10)
            surface.blit(font.render(label, False, white), (q[0] + 12, q[1] - 12))
            return q
        
        p_px  = self.to_px(self.current_planet.location)
        s_px  = self.to_px(self.star.location)
        l1_px = dot_and_label(l1, "L1")
        l2_px = dot_and_label(l2, "L2")
        l3_px = dot_and_label(l3, "L3")
        l4_px = dot_and_label(l4, "L4")
        l5_px = dot_and_label(l5, "L5")

        # ---- Lines (pixel coords) ----
        self.draw_dotted_line(surface, white, p_px, s_px, width=2)
        self.draw_dotted_line(surface, white, s_px, l3_px, width=2)
        self.draw_dotted_line(surface, white, p_px, l4_px, width=2)
        self.draw_dotted_line(surface, white, p_px, l5_px, width=2)

        self.iteration += 1

    