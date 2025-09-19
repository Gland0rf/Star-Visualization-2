import pygame
import math
import numpy as np
import time
from ui.text.TextRenderer import TextRenderer
from itertools import product

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
            "Kepler's Third Law states that the square of a planet's orbital period (T²) is directly proportional to the cube of its semi-major axis (a³)",
            "Proportional means, that if one side dobles, the other does too.",
            "The orbital period is the time the planet needs to fulfill one rotation around the star it's orbiting.",
            "In our case we will measure the time in seconds.",
            "... MEASURE_TIME_FOR_HALF_T",
            "In our case, the planet took ~PLANET_ROT_TIMEs to orbit around the star.",
            "This squared is ~SQUARE_ROT_TIME seconds.",
            "Knowing that, we can calculate a (the semi major axis) by just using the formula T² perp a³",
            "In this simulation, a is ~CALCULATE_A AU (astronomical units) or CONVERT_TO_KM kilometers.",
            "Lets say the planet required DOUBLE_AMOUNT_TIME seconds now (double the time it used before), we can calculate a again.",
            "We can expect that a will be x1.59 times bigger, since keplers law states that a² perp T³  OR  a perp T²⁄³",
            "With DOUBLE_AMOUNT_TIME seconds, a would be CALCULATE_DOUBLE_A kilometers. This is around the x1.59 of our old value (CONVERT_TO_KM km)",
            "Please note that slight rounding inaccuracies can occur here."
        ]
        
        self.text_renderer = TextRenderer(font_name, base_font_size * resolution_factor, resolution_factor, color, position, char_delay=0.001)
    
    def add_text(self, text, state):
        if ("MEASURE_TIME_FOR_HALF_T" in text):
            text = text.replace(" MEASURE_TIME_FOR_HALF_T", "")
            if self.current_planet_iteration == 1:
                self.draw_hitpoints(self.hit_points1, self.COLOR_RED)
                self.draw_data(True, 1, color=(0, 0, 255))
            else:
                self.draw_data(True, 0)

            self.allowed_draw_hitpoints1 = True
        if ("PLANET_ROT_TIME" in text):
            text = text.replace("PLANET_ROT_TIME", f"{self.passedTime}")
        if ("SQUARE_ROT_TIME" in text):
            text = text.replace("SQUARE_ROT_TIME", f"{round(self.passedTime ** 2, 2)}")
        if ("CALCULATE_A" in text):
            calculated_T = self.passedTime / 31_556_952 # seconds in a year
            calculated_a = (calculated_T ** 2)**(1./3.)
            text = text.replace("CALCULATE_A", f"{round(calculated_a, 10)}")
        if ("CONVERT_TO_KM" in text):
            passed_time = self.passedTime

            calculated_T = passed_time / 31_556_952 # seconds in a year
            calculated_a = (calculated_T ** 2)**(1./3.)

            converted_km = (calculated_a * 1.496 * 10**11) / 1000
            text = text.replace("CONVERT_TO_KM_D", f"{round(converted_km, 2)}")
            text = text.replace("CONVERT_TO_KM", f"{round(converted_km, 2)}")
        if ("DOUBLE_AMOUNT_TIME" in text):
            text = text.replace("DOUBLE_AMOUNT_TIME", f"{round(self.passedTime * 2, 2)}")
        if ("CALCULATE_DOUBLE_A" in text):
            calculated_T = self.passedTime * 2 / 31_556_952 # seconds in a year
            calculated_a = (calculated_T ** 2)**(1./3.)

            converted_km = (calculated_a * 1.496 * 10**11) / 1000
            text = text.replace("CALCULATE_DOUBLE_A", f"{round(converted_km, 2)}")

        self.text_renderer.add_text(text)
        self.text_renderer.render(self.screen)

    def draw_data(self, show_area_covered, hit_point, color=(255, 0, 0)):
        if show_area_covered:
            self.main_instance.current_state = self.main_instance.MOVE_ONLY_STATE
            
            # Track the start time of this section
            if not hasattr(self, 'start_time') or self.start_time is None:
                self.start_time = time.time()

            if hit_point == 0:
                location = tuple(self.main_instance.orbiting_planets[0].location)

                if any(self.within_tolerance(location, hp) for hp in self.hit_points1):
                    self.passedTime = round(time.time() - self.start_time, 2)

                    self.start_time = None
                    self.main_instance.current_state = self.main_instance.GUIDE_STATE
                    
                    self.clear_text()
                    self.main_instance.guide_iteration += 1

                self.hit_points1.append(location)
                self.draw_hitpoints(self.hit_points1, color)

    def within_tolerance(self, a, b, tol=3):
        if not isinstance(a, (tuple, list)):
            a = (a,)
        if not isinstance(b, (tuple, list)):
            b = (b,)
        return all(abs(x - y) <= tol for x, y in zip(a, b))

    def draw_hitpoints(self, hit_points, color, dot_radius=5):
        for point in hit_points:
            pygame.draw.circle(self.screen, color, point, dot_radius)

    def call_state(self, state):
        #Display text
        self.add_text(self.iterationQueue[state], state)

    def clear_text(self):
        self.text_renderer.clear_text()

    def get_iteration_count(self):
        return len(self.iterationQueue)