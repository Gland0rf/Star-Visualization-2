import math
import numpy as np

class Orbit_Calc:
    def __init__(self, G):
        # Gravitational constant
        self.G = G
    
    def calculate_total_gravitational_acceleration(self, planet_pos, bodies):
        total_acc = [0.0, 0.0]
        for body in bodies:
            dx = body.location[0] - planet_pos[0]
            dy = body.location[1] - planet_pos[1]
            r2 = dx*dx + dy*dy
            if r2 == 0:
                continue
            r = math.sqrt(r2)
            F_over_m = self.G * body.mass / r2   # acceleration = GM/r²
            total_acc[0] += F_over_m * dx / r
            total_acc[1] += F_over_m * dy / r
        return total_acc

    def update_planet_position(self, planet_pos, planet_vel, planet_mass, stars, time_step, method="Euler"):
        if method == "Runge-Kutta-4":
            def accel(pos):
                ax, ay = self.calculate_total_gravitational_acceleration(pos, stars)
                return ax, ay
            
            # k1
            ax1, ay1 = accel(planet_pos)
            k1_vx = ax1 * time_step
            k1_vy = ay1 * time_step
            k1_x = planet_vel[0] * time_step
            k1_y = planet_vel[1] * time_step

            # k2
            mid1_pos = (planet_pos[0] + 0.5 * k1_x,
                        planet_pos[1] + 0.5 * k1_y)
            mid1_vel = (planet_vel[0] + 0.5 * k1_vx,
                        planet_vel[1] + 0.5 * k1_vy)
            
            ax2, ay2 = accel(mid1_pos)
            k2_vx = ax2 * time_step
            k2_vy = ay2 * time_step
            k2_x = mid1_vel[0] * time_step
            k2_y = mid1_vel[1] * time_step

            # k3
            mid2_pos = (planet_pos[0] + 0.5 * k2_x,
                        planet_pos[1] + 0.5 * k2_y)
            mid2_vel = (planet_vel[0] + 0.5 * k2_vx,
                        planet_vel[1] + 0.5 * k2_vy)
            
            ax3, ay3 = accel(mid2_pos)
            k3_vx = ax3 * time_step
            k3_vy = ay3 * time_step
            k3_x = mid2_vel[0] * time_step
            k3_y = mid2_vel[1] * time_step

            # k4
            end_pos = (planet_pos[0] + k3_x,
                       planet_pos[1] + k3_y)
            end_vel = (planet_vel[0] + k3_vx,
                       planet_vel[1] + k3_vy)
            
            ax4, ay4 = accel(end_pos)
            k4_vx = ax4 * time_step
            k4_vy = ay4 * time_step
            k4_x = end_vel[0] * time_step
            k4_y = end_vel[1] * time_step

            new_x = planet_pos[0] + (k1_x + 2*k2_x + 2*k3_x + k4_x) / 6
            new_y = planet_pos[1] + (k1_y + 2*k2_y + 2*k3_y + k4_y) / 6
            new_vx = planet_vel[0] + (k1_vx + 2*k2_vx + 2*k3_vx + k4_vx) / 6
            new_vy = planet_vel[1] + (k1_vy + 2*k2_vy + 2*k3_vy + k4_vy) / 6

            return [new_x, new_y], [new_vx, new_vy]

        elif method == "Leapfrog":
            ax1, ay1 = self.calculate_total_gravitational_acceleration(planet_pos, stars)

            vx_half = planet_vel[0] + ax1 * (time_step * 0.5)
            vy_half = planet_vel[1] + ay1 * (time_step * 0.5)

            new_x = planet_pos[0] + vx_half * time_step
            new_y = planet_pos[1] + vy_half * time_step

            ax2, ay2 = self.calculate_total_gravitational_acceleration((new_x, new_y), stars)

            new_vx = vx_half + ax2 * (time_step * 0.5)
            new_vy = vy_half + ay2 * (time_step * 0.5)

            return [new_x, new_y], [new_vx, new_vy]
        elif method == "Euler":
            # Compute acceleration due to stars
            acc = self.calculate_total_gravitational_acceleration(planet_pos, stars)

            # Update velocity
            planet_vel[0] += acc[0] * time_step
            planet_vel[1] += acc[1] * time_step

            # Update position
            planet_pos[0] += planet_vel[0] * time_step
            planet_pos[1] += planet_vel[1] * time_step

            return planet_pos, planet_vel

    def simulate_orbit(self, planet_pos, planet_vel, planet_mass, stars, dt, total_time):
        orbit_path = []
        steps = int(total_time / dt)

        for _ in range(steps):
            planet_pos, planet_vel = self.update_planet_position(
                planet_pos, planet_vel, planet_mass, stars, dt
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
