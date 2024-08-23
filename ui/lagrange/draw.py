import pygame
import math
import ui.lagrange.math as l_math

from stars.orbit_calculation import Orbit_Calc

class Lagrange_Points():
    def __init__(self, planet, star, resolution_factor):
        self.planet = planet
        self.star = star
        self.resolution_factor = resolution_factor
        
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
        
    def draw_lagrange_points(self, surface, G):
        #L1 and L2
        planet = self.planet
        star = self.star
        
        white = (255, 255, 255)
        red = (255, 0, 0)
        
        planet_loc = planet.location
        star_loc = star.location
        self.draw_dotted_line(surface, white, planet_loc, star_loc, width=5, segment_length=20, gap_length=10)
        
        orbit_calculation = Orbit_Calc(G)
        orbit_path = orbit_calculation.simulate_orbit(planet_loc[:], planet.velocity[:], planet.mass, star_loc, star.mass, 8, tolerance=100)
        
        if len(orbit_path) > 1:
            pygame.draw.aalines(surface, red, True, orbit_path, blend=3)
            
        #L3
        dx = planet_loc[0] - star_loc[0]
        dy = planet_loc[1] - star_loc[1]
        length = math.sqrt(dx**2 + dy**2)
        
        if length != 0:
            dx /= length
            dy /= length
        
        opposite_length = 1000
        opposite_point = (
            star_loc[0] - dx * opposite_length,
            star_loc[1] - dy * opposite_length,
        )
        
        intersection_point = l_math.find_collision_point(orbit_path, star_loc, opposite_point)
        if intersection_point is None:
            intersection_point = opposite_point
        
        self.draw_dotted_line(surface, white, star_loc, intersection_point, width=5, segment_length=20, gap_length=10)
        
        #L4
        rotated_x, rotated_y = l_math.rotate_vector(dx, dy, 120) #L4 is 60 degrees off
        
        max_length = 1000
        max_point = (
            star_loc[0] - rotated_x * max_length,
            star_loc[1] - rotated_y * max_length,
        )
        
        intersection_point = l_math.find_collision_point(orbit_path, star_loc, max_point)
        if intersection_point is None:
            intersection_point = max_point
            
        self.draw_dotted_line(surface, white, star_loc, intersection_point, width=5, segment_length=20, gap_length=10)
        
        #L5
        rotated_x, rotated_y = l_math.rotate_vector(dx, dy, -120) #L5 is 60 degrees off into the other direction
        
        max_length = 1000
        max_point = (
            star_loc[0] - rotated_x * max_length,
            star_loc[1] - rotated_y * max_length,
        )
        
        intersection_point = l_math.find_collision_point(orbit_path, star_loc, max_point)
        if intersection_point is None:
            intersection_point = max_point
            
        self.draw_dotted_line(surface, white, star_loc, intersection_point, width=5, segment_length=20, gap_length=10)