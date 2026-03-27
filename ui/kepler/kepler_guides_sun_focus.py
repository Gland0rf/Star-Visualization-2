import pygame
import math
import copy
import numpy as np
from stars.orbit_calculation import Orbit_Calc
from ui.text.TextRenderer import TextRenderer

class Kepler_Guide_Sun_Focus():
    def __init__(self, screen, planet, star, base_font_size, color, position, G, game, resolution_factor=1.0, font_name=None):
        self.screen = screen
        self.resolution_factor = resolution_factor
        self.G = G
        self.planet = planet
        self.star = star
        self.game = game
        
        self.iterationQueue = [
            "Keplers first law states that the orbit of every planet is an ellipse, with the sun at one of the two foci.",
            "This right here is the orbit path of our planet. DRAW_ELLIPSE",
            "Foci one is the red dot here. DRAW_RED_DOT",
            "Calculated foci two is on the exact spot where the star is. DRAW_BLUE_DOT",
            "This means, that the sun is always at one of the two foci of the ellipse. DRAW_ALL"
        ]
        
        self.text_renderer = TextRenderer(font_name, int(base_font_size * resolution_factor * 1.8), resolution_factor, color, position, char_delay=0.001)
    
    def call_state(self, state):
        #Display text
        self.add_text(self.iterationQueue[state])
        
    def clear_text(self):
        self.text_renderer.clear_text()
    
    def add_text(self, text):
        if "DRAW_ELLIPSE" in text:
            text = text.replace(" DRAW_ELLIPSE", "")
            self.draw_data(True, False, False)
        elif "DRAW_RED_DOT" in text:
            text = text.replace(" DRAW_RED_DOT", "")
            self.draw_data(True, True, False)
        elif "DRAW_BLUE_DOT" in text or "DRAW_ALL" in text:
            text = text.replace(" DRAW_BLUE_DOT", "")
            text = text.replace(" DRAW_ALL", "")
            self.draw_data(True, True, True)
            
        self.text_renderer.add_text(text)
        self.text_renderer.render(self.screen)
        
    def draw_data(self, draw_ellipse, draw_foci, draw_foci_two):
        if not hasattr(self, "cached_orbit_px"):
            self._precompute_orbit_and_foci()

        if len(self.cached_orbit_px) > 2 and draw_ellipse:
            pygame.draw.aalines(self.screen, (255, 0, 0), False, self.cached_orbit_px, blend=3)

        if draw_foci:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(self.f2_px[0]), int(self.f2_px[1])), 30)
            
        if draw_foci_two:
            pygame.draw.circle(self.screen, (0, 0, 255), (int(self.star_px[0]), int(self.star_px[1])), 30)
            
    def subdivide_points(self, points, points_between=4):
        new_points = []
        
        for i in range(len(points) - 1):
            p1 = np.array(points[i])
            p2 = np.array(points[i + 1])
            
            new_points.append(p1)
            
            for j in range(1, points_between + 1):
                t = j / (points_between + 1)
                interpolated_point = (1 - t) * p1 + t * p2
                new_points.append(interpolated_point)
                
        new_points.append(points[-1])
        
        return np.array(new_points)
            
    def find_closest_point(self, points, other_point):
        closest_distance = -1
        closest_point = -1
        for point in points:
            distance = math.sqrt((other_point[0] - point[0]) ** 2 + (other_point[1] - point[1]) ** 2)
            if distance < closest_distance or closest_distance == -1:
                closest_distance = distance
                closest_point = point
                
        return closest_point
    
    def find_farthest_point(self, points, other_point):
        closest_distance = -1
        closest_point = -1
        for point in points:
            distance = math.sqrt((other_point[0] - point[0]) ** 2 + (other_point[1] - point[1]) ** 2)
            if distance > closest_distance or closest_distance == -1:
                closest_distance = distance
                closest_point = point
                
        return closest_point
    
    def draw_dotted_line(self, surface, color, start_pos, end_pos, width=1, segment_length=10, gap_length=5):
        #Total length of line
        total_length = math.dist(start_pos, end_pos)
        
        #Direction vector
        direction_vector = (
            (end_pos[0] - start_pos[0]) / total_length,
            (end_pos[1] - start_pos[1]) / total_length,
        )
        
        #Variables
        current_pos = start_pos
        drawing = True
        
        while total_length > 0:
            if drawing:
                #Calculate segment pos
                segment_end_pos = (
                    current_pos[0] + direction_vector[0] * min(segment_length, total_length),
                    current_pos[1] + direction_vector[1] * min(segment_length, total_length),
                )
                
                #Draw segment
                pygame.draw.line(surface, color, current_pos, segment_end_pos, width)
                
                #Update pos
                current_pos = segment_end_pos
                total_length -= segment_length
            else:
                #Move current pos by gap
                current_pos = (
                    current_pos[0] + direction_vector[0] * min(gap_length, total_length),
                    current_pos[1] + direction_vector[1] * min(gap_length, total_length),
                )
                total_length -= gap_length
            
            #Toggle    
            drawing = not drawing
            
    def get_iteration_count(self):
        return len(self.iterationQueue)
    
    def _precompute_orbit_and_foci(self):
        orbit_calc = Orbit_Calc(self.G)
        
        r = math.dist(self.planet.location, self.star.location)
        period = 2 * math.pi * math.sqrt(r**3 / (self.G * self.star.mass))
        dt = period / 1000 # 2000 steps per orbit
        total_time = period

        raw_path_world = orbit_calc.simulate_orbit(
            copy.deepcopy(self.planet.location),
            copy.deepcopy(self.planet.velocity),
            self.planet.mass,
            self.game.stars,
            dt,
            total_time
        )
        
        to_px = self.planet.game.to_pixels
        step = max(1, len(raw_path_world) // 1200)
        pixel_path = [to_px(p) for p in raw_path_world[::step]]
        self.cached_orbit_px = self.subdivide_points(pixel_path, points_between=10)
    
        peri = self.find_closest_point(raw_path_world, self.star.location)
        apo = self.find_farthest_point(raw_path_world, self.star.location)
        cx, cy = (0.5 * (peri[0] + apo[0]), 0.5 * (peri[1] + apo[1]))

        sx, sy = self.star.location
        f2_world = (2 * cx - sx, 2 * cy - sy)

        self.star_px = to_px(self.star.location)
        self.f2_px = to_px(f2_world)