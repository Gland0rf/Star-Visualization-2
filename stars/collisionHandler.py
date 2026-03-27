import math
import random
import pygame
from stars.orbiting_planet import OrbitingStar

class CollisionHandler:
    def __init__(self, game):
        self.game = game
        self.explosions = []

    def handle_merge(self, p1, p2):
        total_mass = p1.mass + p2.mass
        new_vx = (p1.velocity[0]*p1.mass + p2.velocity[0]*p2.mass) / total_mass
        new_vy = (p1.velocity[1]*p1.mass + p2.velocity[1]*p2.mass) / total_mass
        new_x  = (p1.location[0]*p1.mass + p2.location[0]*p2.mass) / total_mass
        new_y  = (p2.location[1]*p1.mass + p2.location[1]*p2.mass) / total_mass
        new_radius = int((p1.min_radius**3 + p2.min_radius**3) ** (1/3))

        merged = OrbitingStar(
            location=[new_x, new_y],
            velocity=[new_vx, new_vy],
            mass=total_mass,
            speed_factor=p1.speed_factor,
            min_radius=new_radius,
            max_radius=new_radius,
            color_inner=self.game.RED,
            color_outer=self.game.YELLOW,
            gradient_factor=self.game.gradient_factor,
            gradient_stretch=self.game.gradient_stretch,
            screen_center=self.game.center_pos,
            scale=self.game.scale,
            pulse_speed=self.game.pulse_speed,
            game=self.game
        )

        if p1 in self.game.orbiting_planets: self.game.orbiting_planets.remove(p1)
        if p2 in self.game.orbiting_planets: self.game.orbiting_planets.remove(p2)
        self.game.orbiting_planets.append(merged)

    def handle_explosion(self, p1, p2):
        x = (p1.location[0] + p2.location[0]) / 2
        y = (p1.location[1] + p2.location[1]) / 2
        total_mass = p1.mass + p2.mass

        for _ in range(15):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(500, 2000)
            vx = math.cos(angle) * speed,
            vy = math.sin(angle) * speed
            fragment_mass = total_mass / 200

            frag = OrbitingStar(
                location=[x, y],
                velocity=[vx, vy],
                mass=total_mass,
                speed_factor=p1.speed_factor,
                min_radius=60,
                max_radius=70,
                color_inner=self.game.RED,
                color_outer=self.game.YELLOW,
                gradient_factor=self.game.gradient_factor,
                gradient_stretch=self.game.gradient_stretch,
                screen_center=self.game.center_pos,
                scale=self.game.scale,
                game=self.game
            )
            self.game.orbiting_planets.append(frag)
        
        self.explosions.append({
            "pos": [x, y],
            "radius": max(p1.min_radius, p2.min_radius) * 3,
            "life": 40
        })

        if p1 in self.game.orbiting_planets: self.game.orbiting_planets.remove(p1)
        if p2 in self.game.orbiting_planets: self.game.orbiting_planets.remove(p2)

    def handle_collision(self, p1, p2):
        dvx = p1.velocity[0] - p2.velocity[0]
        dvy = p1.velocity[1] - p2.velocity[1]
        rel_speed = (dvx*dvx + dvy*dvy) ** 0.5

        vesc = math.sqrt(
            2 * self.game.gravitational_constant * (p1.mass + p2.mass) / (p1.min_radius + p2.min_radius)
        )

        if rel_speed < vesc:
            self.handle_merge(p1, p2)
        else:
            self.handle_explosion(p1, p2)

    def update_explosions(self, surface):
        for exp in self.explosions[:]:
            pos_px = self.game.to_pixels(exp["pos"])
            radius = int(exp["radius"] * (1.2 - exp["life"]/40))
            alpha = int(255 * (exp["life"]/40))

            surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 100, 0, alpha), (radius, radius), radius)
            surface.blit(surf, (pos_px[0]-radius, pos_px[1]-radius))

            exp["life"] -= 1
            if exp["life"] <= 0:
                self.explosions.remove(exp)