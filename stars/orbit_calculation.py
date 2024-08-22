import math

#Gravitational force (non-accurate)
G = 1

def calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass):
    #Vector from the planet to the star
    distance_vector = [star_pos[0] - planet_pos[0], star_pos[1] - planet_pos[1]]
    distance = math.sqrt(distance_vector[0]**2 + distance_vector[1]**2)
    
    if distance == 0:
        return [0, 0]
    
    #Gravitational force magnitude
    force_magnitude = G * star_mass * planet_mass / distance**2
    
    #Normalize the distance vector
    force_direction = [distance_vector[0] / distance, distance_vector[1] / distance]
    
    #Force vector
    force_vector = [force_magnitude * force_direction[0], force_magnitude * force_direction[1]]
    
    return force_vector

def update_planet_position(planet_pos, planet_vel, planet_mass, star_pos, star_mass, speed_factor):
    #Gravitational force
    force = calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass)
    
    #Update velocity
    acceleration = [force[0] / planet_mass, force[1] / planet_mass]
    planet_vel[0] += acceleration[0] * speed_factor
    planet_vel[1] += acceleration[1] * speed_factor
    
    #Update position
    planet_pos[0] += planet_vel[0] * speed_factor
    planet_pos[1] += planet_vel[1] * speed_factor
    
    return planet_pos, planet_vel