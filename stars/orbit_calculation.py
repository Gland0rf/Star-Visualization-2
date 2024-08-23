import math

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

    def update_planet_position(self, planet_pos, planet_vel, planet_mass, star_pos, star_mass, speed_factor):
        #Gravitational force
        force = self.calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass)
        
        #Update velocity
        acceleration = [force[0] / planet_mass, force[1] / planet_mass]
        planet_vel[0] += acceleration[0] * speed_factor
        planet_vel[1] += acceleration[1] * speed_factor
        
        #Update position
        planet_pos[0] += planet_vel[0] * speed_factor
        planet_pos[1] += planet_vel[1] * speed_factor
        
        return planet_pos, planet_vel
    
    def simulate_orbit(self, planet_pos, planet_vel, planet_mass, star_pos, star_mass, speed_factor, tolerance=5, max_steps=1000):
        orbit_path = []
        initial_pos = planet_pos.copy()
        close_to_start = False

        steps = 0
        while not close_to_start and steps < max_steps:
            # Update planet position and velocity
            planet_pos, planet_vel = self.update_planet_position(planet_pos, planet_vel, planet_mass, star_pos, star_mass, speed_factor)
            orbit_path.append((int(planet_pos[0]), int(planet_pos[1])))

            # Check if the planet has returned to a position close to the starting point
            distance_to_start = math.sqrt((planet_pos[0] - initial_pos[0])**2 + (planet_pos[1] - initial_pos[1])**2)
            if distance_to_start < tolerance and len(orbit_path) > 100:
                close_to_start = True
                
            steps += 1

        return orbit_path