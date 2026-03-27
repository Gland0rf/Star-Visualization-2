import pygame
import math

class PlanetDetails:
    def __init__(self, screen, planet, star, game):
        self.screen = screen
        self.planet = planet
        self.star = star
        self.game = game

        self.white = (255, 255, 255)

    def calculate_a(self):
        # 1 / ((2/r)-(v2/mu))
        planet_loc = self.planet.location
        star_loc = self.star.location
        dx = planet_loc[0] - star_loc[0]
        dy = planet_loc[1] - star_loc[1]
        r = math.sqrt(dx*dx + dy*dy)

        planet_vel = self.planet.velocity
        dvx = planet_vel[0]
        dvy = planet_vel[1]
        v = math.sqrt(dvx*dvx + dvy*dvy)

        mu = self.game.gravitational_constant * self.star.mass

        a = 1.0 / (2.0/r - (v*v)/mu)

        return a
    
    def calculate_e(self):
        dx = self.planet.location[0] - self.star.location[0]
        dy = self.planet.location[1] - self.star.location[1]
        vx, vy = self.planet.velocity
        r_vec = [dx, dy]
        v_vec = [vx, vy]

        r = math.sqrt(dx*dx + dy*dy)
        v = math.sqrt(vx*vx + vy*vy)

        mu = self.game.gravitational_constant * self.star.mass

        h = dx*vy - dy*vx

        ex = ( (vy*h)/mu ) - (dx/r)
        ey = ( -(vx*h)/mu ) - (dy/r)

        e = math.sqrt(ex*ex + ey*ey)

        
        #print(self.planet.location, self.planet.velocity, self.star.mass, self.game.gravitational_constant, r, v, mu, h, e)
        return e, ex, ey
    
    def calculate_anomaly(self):
        e, ex, ey = self.calculate_e()

        dx = self.planet.location[0] - self.star.location[0]
        dy = self.planet.location[1] - self.star.location[1]
        vx, vy = self.planet.velocity
        r = math.sqrt(dx*dx + dy*dy)

        if e > 0.02:
            dot = ex*dx + ey*dy
            cross = ex*dy - ey*dx
            nu = math.atan2(cross, dot)

            if nu < 0:
                nu += 2*math.pi
        else:
            nu = math.atan2(dy, dx)
            if nu < 0:
                nu += 2*math.pi

        return math.degrees(nu)

    def draw(self):
        a = self.calculate_a()
        e, _, _ = self.calculate_e()
        nu = self.calculate_anomaly()

        a = round(a / 1000, 3)
        e = round(e, 3)
        nu = round(nu, 3)

        label = f"Semi-Major Axis (a): {a} km\nEccentricity (e): {e}\nTrue anomaly (nu): {nu} deg"
        font_size = max(10, 36)
        font = pygame.font.SysFont(None, font_size)
        self.screen.blit(font.render(label, False, self.white), (20, self.game.height - 100))

        name_text = font.render(self.planet.name or "Unnamed Planet", False, self.white)
        name_text_rect = name_text.get_rect(center=(self.game.width // 2, 20))
        self.screen.blit(name_text, name_text_rect)