import pygame
import math
import numpy as np
import time
from ui.text.TextRenderer import TextRenderer

class Kepler_Guide_Three():
    def __init__(self, main_instance, screen, planet, star, base_font_size, color, position, G, resolution_factor=1.0, font_name=None):
        self.screen = screen
        self.resolution_factor = resolution_factor
        self.G = G
        self.planet = planet
        self.star = star
        self.main_instance = main_instance

        self.hit_points1 = []
        self.allowed_draw_hitpoints1 = False
        self.current_planet_iteration = 0
        self.passedTime = None

        self.iterationQueue = [
            "Kepler's Third Law states that the square of a planet's orbital period (T²) is directly proportional to the cube of its semi-major axis (a³).",
            "Proportional means that if one side doubles, the other grows accordingly.",
            "The orbital period is the time the planet needs to complete one orbit around its star.",
            "In our case we will measure the time in seconds.",
            "... MEASURE_TIME_FOR_HALF_T",
            "In our case, the planet took ~PLANET_ROT_TIME seconds to orbit around the star.",
            "This squared is ~SQUARE_ROT_TIME seconds.",
            "Knowing that, we can calculate a (the semi-major axis) using T² perp a³.",
            "In this simulation, a is ~CALCULATE_A AU (astronomical units), or ~CONVERT_TO_KM km.",
            "Now, let’s imagine the planet required DOUBLE_AMOUNT_TIME seconds instead — double the time.",
            "We can expect a will scale with T^(2/3).",
            "With DOUBLE_AMOUNT_TIME seconds, a would be ~CALCULATE_DOUBLE_A km. That’s ~1.59× our old value (~CONVERT_TO_KM km).",
            "Please note that slight rounding inaccuracies can occur here."
        ]
        
        self.text_renderer = TextRenderer(
            font_name,
            int(base_font_size * resolution_factor * 1.8),
            resolution_factor,
            color,
            position,
            char_delay=0.001
        )
    
    def add_text(self, text, state):
        if "MEASURE_TIME_FOR_HALF_T" in text:
            text = text.replace(" MEASURE_TIME_FOR_HALF_T", "")
            self.draw_data(True)

        if "PLANET_ROT_TIME" in text and self.passedTime:
            text = text.replace("PLANET_ROT_TIME", f"{self.passedTime:.2f}")

        if "SQUARE_ROT_TIME" in text and self.passedTime:
            text = text.replace("SQUARE_ROT_TIME", f"{self.passedTime ** 2:.2f}")

        if "CALCULATE_A" in text and self.passedTime:
            T_years = self.passedTime / 31_556_952  # seconds → years
            a_AU = (T_years ** (2/3))
            text = text.replace("CALCULATE_A", f"{a_AU:.6f}")

        if "CONVERT_TO_KM" in text and self.passedTime:
            T_years = self.passedTime / 31_556_952
            a_AU = (T_years ** (2/3))
            converted_km = a_AU * 1.496e8  # 1 AU = 1.496e8 km
            text = text.replace("CONVERT_TO_KM", f"{converted_km:.2f}")

        if "DOUBLE_AMOUNT_TIME" in text and self.passedTime:
            text = text.replace("DOUBLE_AMOUNT_TIME", f"{self.passedTime * 2:.2f}")

        if "CALCULATE_DOUBLE_A" in text and self.passedTime:
            T_years = (self.passedTime * 2) / 31_556_952
            a_AU = (T_years ** (2/3))
            converted_km = a_AU * 1.496e8
            text = text.replace("CALCULATE_DOUBLE_A", f"{converted_km:.2f}")

        self.text_renderer.add_text(text)
        self.text_renderer.render(self.screen)

    def draw_data(self, active, color=(255, 0, 0)):
        if active:
            self.main_instance.current_state = self.main_instance.MOVE_ONLY_STATE

            # First activation → record starting point
            if not hasattr(self, "start_time") or self.start_time is None:
                self.start_time = time.time()
                self.start_px = tuple(self.main_instance.to_pixels(
                    self.main_instance.orbiting_planets[0].location
                ))
                self.hit_points1 = [self.start_px]
                self.orbit_complete = False  # ✅ reset flag

            if self.orbit_complete:
                # ✅ do nothing once the orbit is already measured
                self.draw_hitpoints(self.hit_points1, color)
                return

            planet_px = tuple(self.main_instance.to_pixels(
                self.main_instance.orbiting_planets[0].location
            ))
            self.hit_points1.append(planet_px)

            # Draw trace
            self.draw_hitpoints(self.hit_points1, color)

            # Detect return to start
            if (
                len(self.hit_points1) > 50
                and self.within_tolerance(planet_px, self.start_px, tol=5)
            ):
                self.passedTime = round(time.time() - self.start_time, 2)
                self.start_time = None
                self.orbit_complete = True   # ✅ freeze measurement

                # Switch back to guide state
                self.main_instance.current_state = self.main_instance.GUIDE_STATE
                self.clear_text()
                self.main_instance.guide_iteration += 1

    def within_tolerance(self, a, b, tol=3):
        return math.dist(a, b) <= tol

    def draw_hitpoints(self, hit_points, color, dot_radius=3):
        if len(hit_points) > 1:
            pygame.draw.aalines(self.screen, color, False, hit_points)
        for p in hit_points:
            pygame.draw.circle(self.screen, color, p, dot_radius)

    def call_state(self, state):
        self.add_text(self.iterationQueue[state], state)

    def clear_text(self):
        self.text_renderer.clear_text()

    def get_iteration_count(self):
        return len(self.iterationQueue)

    def reset_values(self):
        """Reset guide state so it can be run again cleanly."""
        self.hit_points1 = []
        self.allowed_draw_hitpoints1 = False
        self.current_planet_iteration = 0
        self.passedTime = None
        self.start_time = None
        self.start_px = None
        self.orbit_complete = False