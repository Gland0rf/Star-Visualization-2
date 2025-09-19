import pygame
import math
import numpy as np
import time
from ui.text.TextRenderer import TextRenderer

class Kepler_Guide_Equal():
    def __init__(self, main_instance, screen, planet, star, base_font_size, color, position, G, resolution_factor=1.0, font_name=None):
        self.screen = screen
        self.resolution_factor = resolution_factor
        self.G = G
        self.planet = planet
        self.star = star
        self.main_instance = main_instance

        self.hit_points1 = []
        self.hit_points2 = []
        self.COLOR_RED = (255, 0, 0)

        self.allowed_draw_hitpoints1 = False
        self.allowed_connect1 = False
        self.allowed_fill1 = False
        self.allowed_connect2 = False
        self.allowed_fill2 = False
        self.current_planet_iteration = 0
        
        self.iterationQueue = [
            "Keplers second law states that a planet sweeps out equal areas in eqal time intervals as it orbits a star.",
            "Lets let the planet orbit for one second and take a look at what area if covers.",
            "... MOVE_PLANET",
            "Let's connect the lines to make a triangle. CONNECT",
            "Now we can calculate the area of the orbit. FILL_AREA_WITH_COLOR",
            "CALC_AREA Here, the area would be ~REPLACE_WITH_AREA units.",
            "Now, let's do the same thing again. CHANGE_ITERATION",
            "... MOVE_PLANET",
            "We can connect them again. CONNECT FILL_AREA_WITH_COLOR",
            "CALC_AREA Here, the area would be ~REPLACE_WITH_AREA units. The green area was REPLACE_WITH_OLD_AREA units, which is (almost) the same.",
            "Note that the planet has to be in an stable orbit for this to work. If the area isn't equal, then the planet might not be in a stable orbit.",
            "Slight inaccuracies can occur in this simulation since it's calculated by pixels."
        ]
        
        self.text_renderer = TextRenderer(font_name, base_font_size * resolution_factor, resolution_factor, color, position, char_delay=0.001)
    
    def call_state(self, state):
        #Display text
        self.add_text(self.iterationQueue[state], state)
        
    def clear_text(self):
        self.text_renderer.clear_text()
    
    def add_text(self, text, state):
        if "MOVE_PLANET" in text:
            text = text.replace(" MOVE_PLANET", "")
            if self.current_planet_iteration == 1:
                self.draw_hitpoints(self.hit_points1, self.COLOR_RED)
                self.draw_data(True, 1, color=(0, 0, 255))
            else:
                self.draw_data(True, 0)

            self.allowed_draw_hitpoints1 = True
        
        if "CONNECT" in text or self.allowed_connect1:
            replaced = False
            if "CONNECT" in text:
                text = text.replace(" CONNECT", "")
                replaced = True
            self.draw_triangle(self.hit_points1)
            if (self.current_planet_iteration == 1 and replaced) or self.allowed_connect2:
                self.draw_triangle(self.hit_points2, (0, 0, 255))
                self.allowed_connect2 = True
            self.allowed_connect1 = True

        if "FILL_AREA_WITH_COLOR" in text or self.allowed_fill1:
            replaced = False
            if "FILL_AREA_WITH_COLOR" in text:
                text = text.replace("FILL_AREA_WITH_COLOR", "")
                replaced = True
            self.fill_area(self.hit_points1)
            if (self.current_planet_iteration == 1 and replaced) or self.allowed_fill2:
                self.fill_area(self.hit_points2, (255, 255, 0))
                self.allowed_fill2 = True
            self.allowed_fill1 = True

        if "CALC_AREA" in text:
            text = text.replace("CALC_AREA ", "")
            area = self.calc_area(self.hit_points1)
            self.old_area = int(area)
            if self.current_planet_iteration == 1:
                area = self.calc_area(self.hit_points2)
            text = text.replace("REPLACE_WITH_AREA", str(int(area)))
            if "REPLACE_WITH_OLD_AREA" in text:
                text = text.replace("REPLACE_WITH_OLD_AREA", str(int(self.old_area)))

        if "CHANGE_ITERATION" in text:
            text = text.replace(" CHANGE_ITERATION", "")
            self.current_planet_iteration = 1

        if self.allowed_draw_hitpoints1:
            self.draw_hitpoints(self.hit_points1, self.COLOR_RED)

        self.text_renderer.add_text(text)
        self.text_renderer.render(self.screen)
        
    def draw_data(self, show_area_covered, hit_point, color=(255, 0, 0)):
        if show_area_covered:
            self.main_instance.current_state = self.main_instance.MOVE_ONLY_STATE
            
            # Track the start time of this section
            if not hasattr(self, 'start_time') or self.start_time is None:
                self.start_time = time.time()

            # Perferm the operations while within once second
            if time.time() - self.start_time < 1.0:
                if hit_point == 0:
                    self.hit_points1.append(tuple(i for i in self.main_instance.orbiting_planets[0].location))
                    self.draw_hitpoints(self.hit_points1, color)
                else:
                    self.hit_points2.append(tuple(i for i in self.main_instance.orbiting_planets[0].location))
                    self.draw_hitpoints(self.hit_points2, color)
            else:
                self.start_time = None
                self.main_instance.current_state = self.main_instance.GUIDE_STATE
                
                self.clear_text()
                self.main_instance.guide_iteration += 1
                

    def draw_triangle(self, hit_points, color=(255, 0, 0)):
        star_loc = self.main_instance.stars[0].location
        pygame.draw.line(self.screen, color, hit_points[0], star_loc, 5)
        pygame.draw.line(self.screen, color, hit_points[-1], star_loc, 5)
            
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
    
    def draw_hitpoints(self, hit_points, color, dot_radius=5):
        for point in hit_points:
            pygame.draw.circle(self.screen, color, point, dot_radius)

    def get_polygon_points(self, hit_points):
        star_loc = self.main_instance.stars[0].location
        baseline1_start = hit_points[0]
        baseline1_end = tuple(i for i in star_loc)
        baseline2_end = baseline1_end

        baseline_x = [baseline1_start[0], baseline1_end[0], baseline2_end[0]]
        baseline_y = [baseline1_start[1], baseline1_end[1], baseline2_end[1]]

        circle_points = hit_points
        curve_x, curve_y = zip(*circle_points)

        polygon_x = np.concatenate((baseline_x, curve_x[::-1]))
        polygon_y = np.concatenate((baseline_y, curve_y[::-1]))

        return polygon_x, polygon_y

    def fill_area(self, hit_points, color=(10, 255, 10)):
        polygon_x, polygon_y = self.get_polygon_points(hit_points)

        polygon_points = list(zip(polygon_x, polygon_y))

        pygame.draw.polygon(self.screen, color, polygon_points)

    def calc_area(self, hit_points):
        polygon_x, polygon_y = self.get_polygon_points(hit_points)

        area = 0.5 * np.abs(np.dot(polygon_x, np.roll(polygon_y, 1)) - np.dot(polygon_y, np.roll(polygon_x, 1)))
        return area
    
    def reset_values(self):
        self.allowed_draw_hitpoints1 = False
        self.allowed_connect1 = False
        self.allowed_fill1 = False
        self.allowed_connect2 = False
        self.allowed_fill2 = False
        self.current_planet_iteration = 0

        self.hit_points1 = []
        self.hit_points2 = []