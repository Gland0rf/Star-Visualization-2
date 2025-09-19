import math
import numpy as np

class Orbit_Calc:
    def __init__(self, G):
        #Gravitational force (non-accurate)
        self.G = G
    
    def calculate_gravitational_force(self, star_pos, star_mass, planet_pos, planet_mass):
        #Vector from the planet to the star
        distance_vector = [star_pos[0] - planet_pos[0], star_pos[1] - planet_pos[1]]
        distance = math.sqrt(distance_vector[0]**2 + distance_vector[1]**2)
        
        if distance == 0:
            return [0, 0]
        
        #Gravitational force magnitude
        force_magnitude = self.G * star_mass * planet_mass / distance**2
        
        #Normalize the distance vector
        force_direction = [distance_vector[0] / distance, distance_vector[1] / distance]
        
        #Force vector
        force_vector = [force_magnitude * force_direction[0], force_magnitude * force_direction[1]]
        
        return force_vector

    def update_planet_position(self, planet_pos, planet_vel, planet_mass, star_pos, star_mass, time_step):
        """#Gravitational force
        force = self.calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass)
        acceleration = [force[0] / planet_mass, force[1] / planet_mass]
        
        planet_vel[0] += 0.5 * acceleration[0] * time_step
        planet_vel[1] += 0.5 * acceleration[1] * time_step
        
        #Update position
        planet_pos[0] += planet_vel[0] * time_step
        planet_pos[1] += planet_vel[1] * time_step
        
        new_force = self.calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass)
        new_acceleration = [new_force[0] / planet_mass, new_force[1] / planet_mass]
        
        #Update velocity
        planet_vel[0] += 0.5 * new_acceleration[0] * time_step
        planet_vel[1] += 0.5 * new_acceleration[1] * time_step
        
        return planet_pos, planet_vel"""
        
        # Update velocity (half step)
        """Leapfrog integration step for position and velocity update."""

        #print("pos start ", planet_pos)
        # Calculate acceleration due to gravity at the current position
        force = self.calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass)
        acceleration = [force[0] / planet_mass, force[1] / planet_mass]
        
        # Update velocity (half step)
        planet_vel[0] += 0.5 * acceleration[0] * time_step
        planet_vel[1] += 0.5 * acceleration[1] * time_step
        
        # Update position (full step)
        planet_pos[0] += planet_vel[0] * time_step
        planet_pos[1] += planet_vel[1] * time_step
        
        # Recalculate acceleration after position update
        force = self.calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass)
        acceleration = [force[0] / planet_mass, force[1] / planet_mass]
        
        # Update velocity (half step)
        planet_vel[0] += 0.5 * acceleration[0] * time_step
        planet_vel[1] += 0.5 * acceleration[1] * time_step
        
        #print("pos end ", planet_pos)
        return planet_pos, planet_vel
    
    def simulate_orbit(self, planet_pos, planet_vel, planet_mass, star_pos, star_mass, dt, total_time):
        orbit_path = []
        steps = int(total_time / dt * 4)

        for _ in range(steps):
            planet_pos, planet_vel = self.update_planet_position(
                planet_pos, planet_vel, planet_mass, star_pos, star_mass, dt
            )
            orbit_path.append((planet_pos[0], planet_pos[1]))

        return orbit_path
    
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