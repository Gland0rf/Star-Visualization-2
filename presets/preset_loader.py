import json
import math
from stars.pulsating_star import PulsatingStar
from stars.orbiting_planet import OrbitingStar
from stars.spaceStation.space_station import SpaceStation
from stars.blackHole import BlackHole

def load_preset(game, filename):
    with open(filename, "r") as f:
        data = json.load(f)

    game.orbiting_planets.clear()
    game.stars.clear()
    game.black_holes.clear()

    for s in data.get("stars", []):
        star = PulsatingStar(
            location=s.get("location", [0.0, 0.0]),
            mass=s["mass"],
            min_radius=game.min_radius,
            max_radius=game.max_radius,
            pulse_speed=game.pulse_speed,
            color_inner=tuple(s.get("color_inner", (255, 255, 200))),
            color_outer=tuple(s.get("color_outer", (255, 200, 100))),
            gradient_factor=game.gradient_factor,
            gradient_stretch=game.gradient_stretch,
            screen_center=game.center_pos,
            scale=game.scale,
            game=game
        )

        star.name = s.get("name", "Unnamed Star")
        game.stars.append(star)

    for p in data.get("planets", []):
        parent_name = p.get("parent")
        parent_star = next((s for s in game.stars if getattr(s, "name", None) == parent_name), None)

        planet = OrbitingStar(
            location=p["location"],
            velocity=p.get("velocity", [0.0, 0.0]),
            mass=p["mass"],
            speed_factor=60*60*24,
            parent_star=parent_star,
            min_radius=game.min_radius,
            max_radius=game.max_radius,
            pulse_speed=game.pulse_speed,
            color_inner=tuple(p.get("color_inner", (255, 255, 255))),
            color_outer=tuple(p.get("color_outer", (180, 180, 180))),
            gradient_factor=game.gradient_factor,
            gradient_stretch=game.gradient_stretch,
            screen_center=game.center_pos,
            scale=game.scale,
            game=game
        )
        planet.name = p.get("name", "Unnamed Planet")
        game.orbiting_planets.append(planet)

    # --- Create Stations ---
    for s in data.get("stations", []):
        parent_planet = next((p for p in game.orbiting_planets if getattr(p, "name", None) == s.get("parent")), None)
        station = SpaceStation(
            location=s["location"],
            velocity=s.get("velocity", [0.0, 0.0]),
            mass=s["mass"],
            speed_factor=60*60*24,
            screen_center=game.center_pos,
            scale=game.scale,
            game=game,
            name=s.get("name", "Unnamed Station")
        )
        station.parent_planet = parent_planet
        game.stations.append(station)

    # --- Create Black Holes ---
    for b in data.get("black_holes", []):
        bh = BlackHole(
            location=b["location"],
            mass=b["mass"],
            game=game,
            disk_outer_factor=b.get("disk_outer_factor", 50),
            inclination=b.get("inclination", 0.0),
            rotation_speed_deg=b.get("rotation_speed_deg", 0.35),
            disk_quality=b.get("disk_quality", 0.8)
        )
        bh.name = b.get("name", "Unnamed Black Hole")
        game.black_holes.append(bh)