import math

G = 1

def calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass):
    # Calculate the vector from the planet to the star
    distance_vector = [star_pos[0] - planet_pos[0], star_pos[1] - planet_pos[1]]
    distance = math.sqrt(distance_vector[0]**2 + distance_vector[1]**2)
    
    # Avoid division by zero
    if distance == 0:
        return [0, 0]
    
    # Calculate gravitational force magnitude
    force_magnitude = G * star_mass * planet_mass / distance**2
    
    # Normalize the distance vector to get the direction
    force_direction = [distance_vector[0] / distance, distance_vector[1] / distance]
    
    # Calculate the force vector
    force_vector = [force_magnitude * force_direction[0], force_magnitude * force_direction[1]]
    
    return force_vector

def update_planet_position(planet_pos, planet_vel, planet_mass, star_pos, star_mass, speed_factor):
    # Calculate the gravitational force
    force = calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass)
    
    # Update velocity: F = ma -> a = F/m -> dv = a*dt (assuming dt = 1 for simplicity)
    acceleration = [force[0] / planet_mass, force[1] / planet_mass]
    planet_vel[0] += acceleration[0] * speed_factor
    planet_vel[1] += acceleration[1] * speed_factor
    
    # Update position: dr = v*dt (assuming dt = 1 for simplicity)
    planet_pos[0] += planet_vel[0] * speed_factor
    planet_pos[1] += planet_vel[1] * speed_factor
    
    return planet_pos, planet_vel