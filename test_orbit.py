import pygame
import math

pygame.init()

#Constants
WIDTH, HEIGHT = 1600, 1200
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Orbiting Star")

#Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#Gravitational constant (arbitrary units)
G = 1

#Star properties
star_mass = 1000
star_pos = [WIDTH // 2, HEIGHT // 2]

#Planet properties
planet_mass = 1
planet_pos = [WIDTH // 2 + 300, HEIGHT // 2]
planet_vel = [0, -2]

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
    
    #Calculate the force vector
    force_vector = [force_magnitude * force_direction[0], force_magnitude * force_direction[1]]
    
    return force_vector

def update_planet_position(planet_pos, planet_vel, planet_mass, star_pos, star_mass):
    force = calculate_gravitational_force(star_pos, star_mass, planet_pos, planet_mass)
    
    # Update velocity:
    acceleration = [force[0] / planet_mass, force[1] / planet_mass]
    planet_vel[0] += acceleration[0]
    planet_vel[1] += acceleration[1]
    
    # Update position:
    planet_pos[0] += planet_vel[0]
    planet_pos[1] += planet_vel[1]
    
    return planet_pos, planet_vel

def simulate_orbit(planet_pos, planet_vel, planet_mass, star_pos, star_mass, steps):
    orbit_path = []
    for _ in range(steps):
        orbit_path.append((int(planet_pos[0]), int(planet_pos[1])))
        planet_pos, planet_vel = update_planet_position(planet_pos, planet_vel, planet_mass, star_pos, star_mass)
    return orbit_path

def main():
    global planet_pos, planet_vel
    clock = pygame.time.Clock()
    run = True
    
    orbit_path = simulate_orbit(planet_pos[:], planet_vel[:], planet_mass, star_pos, star_mass, steps=5000)
    
    while run:
        clock.tick(60)
        WIN.fill(BLACK)
        
        if len(orbit_path) > 1:
            pygame.draw.lines(WIN, WHITE, False, orbit_path, 1)
        
        #Star
        pygame.draw.circle(WIN, WHITE, (int(star_pos[0]), int(star_pos[1])), 10)
        
        #Planet
        pygame.draw.circle(WIN, WHITE, (int(planet_pos[0]), int(planet_pos[1])), 5)
        
        #Planet position
        planet_pos, planet_vel = update_planet_position(planet_pos, planet_vel, planet_mass, star_pos, star_mass)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
    pygame.quit()

if __name__ == "__main__":
    main()