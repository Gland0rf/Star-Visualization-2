import pygame
import pygame_gui
import sys

from stars.edit_menu import Edit_Menu
from stars.createPlanetMenu import CreatePlanetMenu
from stars.collisionHandler import CollisionHandler
from stars.blackHole import BlackHole

from stars.pulsating_star import PulsatingStar
from stars.orbiting_planet import OrbitingStar
from stars.orbit_calculation import Orbit_Calc

from stars.spaceStation.space_station import SpaceStation
from stars.spaceStation.createStationMenu import CreateStationMenu

from ui.kepler.menu import MenuButton, Menu
from ui.kepler.kepler_guides_sun_focus import Kepler_Guide_Sun_Focus
from ui.kepler.kepler_guides_equal import Kepler_Guide_Equal
from ui.kepler.kepler_guides_three import Kepler_Guide_Three

from ui.lagrange.draw import Lagrange_Points
from stars.details.starDetails import StarDetails

from ui.advanced.advanced_menu import AdvancedMenu

class Game:
    pygame.init()
    
    def __init__(self, width, height, center_pos, resolution_factor, gravitational_constant, light_speed, scale):
        #Screen dim
        self.width = width
        self.height = height
        self.center_pos = center_pos
        
        # Classes
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.manager = pygame_gui.UIManager((self.width, self.height))
        self.collision_handler = CollisionHandler(self)
        
        # Resolution
        self.resolution_factor = resolution_factor
        
        self.orbiting_planets = []
        self.stars = []
        self.black_holes = []
        self.stations = []
        
        # Constant
        self.gravitational_constant = gravitational_constant
        self.light_speed = light_speed
        self.scale = scale
        self.base_scale = scale
        self.time_scale = 1.0

        # Camera
        self.camera_offset = [0, 0]

        # Panning
        self.is_panning = False
        self.last_mouse_pos = None
        self.mouse_down_pos = None
        self.drag_threshold = 5
        
        # States
        self.current_state = 1
        self.ACTIVE_STATE = 1
        self.PAUSE_STATE = 2
        self.GUIDE_STATE = 3
        self.MOVE_ONLY_STATE = 4
        self.guide_iteration = 0
        
        self.current_guide_active = -1
        
    def load_star(self, min_radius, max_radius, pulse_speed, gradient_factor, gradient_stretch):    
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.pulse_speed = pulse_speed
        self.gradient_factor = gradient_factor
        self.gradient_stretch = gradient_stretch
    
    def change_state(self, state):
        self.current_state = state
    
    def to_pixels(self, real_pos):
        x_px = real_pos[0] / self.scale + self.center_pos[0] + self.camera_offset[0]
        y_px = real_pos[1] / self.scale + self.center_pos[1] + self.camera_offset[1]
        return [round(x_px), round(y_px)]
    
    def to_world(self, screen_pos):
        x_world = (screen_pos[0] - self.center_pos[0] - self.camera_offset[0]) * self.scale
        y_world = (screen_pos[1] - self.center_pos[1] - self.camera_offset[1]) * self.scale
        return [x_world, y_world]
    
    def _over_advanced_menu(self, adv_menu, pos):
        """True if mouse is over the Advanced button, its tabs, the panel, or the small hover gap."""
        if adv_menu is None:
            return False

        # Button
        if getattr(adv_menu.button, "visible", True):
            brect = adv_menu.button.get_abs_rect()
            if brect.collidepoint(pos):
                return True
            # small hover gap (mirrors AdvancedMenu.handle_event)
            gap_rect = pygame.Rect(brect.left, brect.bottom, brect.width, 6)
            if gap_rect.collidepoint(pos):
                return True

        # Panel
        if getattr(adv_menu.panel, "visible", False):
            prect = adv_menu.panel.get_abs_rect()
            if prect.collidepoint(pos):
                return True
            # Tabs (Time / Interaction / View)
            for btn in getattr(adv_menu, "sub_tabs", {}).values():
                if getattr(btn, "visible", True) and btn.get_abs_rect().collidepoint(pos):
                    return True

        return False
    
    def _over_ui(self, pos, *ui_elements):
        for ui in ui_elements:
            if ui is None:
                continue
            if hasattr(ui, "panel") and ui.panel.visible:
                if ui.panel.get_abs_rect().collidepoint(pos):
                    return True
        return False
            
    def main(self):
        #Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)

        self.FRAMES_PER_SECOND = 60
        
        width = self.width
        height = self.height
        resolution_factor = self.resolution_factor
        GRAVITATIONAL_CONSTANT = self.gravitational_constant
        center_pos = self.center_pos
        min_radius = self.min_radius
        max_radius = self.max_radius
        pulse_speed = self.pulse_speed
        gradient_factor = self.gradient_factor
        gradient_stretch = self.gradient_stretch
        screen_center = (width // 2, height // 2)
        
        self.CURRENT_EDIT_MENU = None
        
        clock = pygame.time.Clock()
        running = True
        
        self.high_res_surface = pygame.Surface((width * resolution_factor, height * resolution_factor))
        
        self.orbit_calc = Orbit_Calc(G=GRAVITATIONAL_CONSTANT)

        # Location in meters!
        # Velocity in m/s!
        # Mass in kg!
        
        pulsating_star = PulsatingStar(
            location=[0.0, 0.0],
            mass=1.989e30,
            min_radius=min_radius,
            max_radius = max_radius,
            pulse_speed=pulse_speed,
            color_inner=self.RED,
            color_outer=self.YELLOW,
            gradient_factor=gradient_factor,
            gradient_stretch=gradient_stretch,
            screen_center=screen_center,
            scale=self.scale,
            game=self,
        )

        pulsating_star_2 = PulsatingStar(
            location=[5000.996e11, 0.0],
            mass=1.989e30,
            min_radius=min_radius,
            max_radius = max_radius,
            pulse_speed=pulse_speed,
            color_inner=self.RED,
            color_outer=self.YELLOW,
            gradient_factor=gradient_factor,
            gradient_stretch=gradient_stretch,
            screen_center=screen_center,
            scale=self.scale,
            game=self,
        )
        
        orbiting_planet = OrbitingStar(
            location=[1.996e11, 0.0],
            velocity=[0.0, 21_000.0],
            mass=5.972e24,
            speed_factor=60*60*24,
            parent_star=pulsating_star,
            min_radius=min_radius,
            max_radius = max_radius,
            pulse_speed=pulse_speed,
            color_inner=self.RED,
            color_outer=self.YELLOW,
            gradient_factor=gradient_factor,
            gradient_stretch=gradient_stretch,
            screen_center=screen_center,
            scale=self.scale,
            game=self,
        )
        
        orbiting_planet_2 = OrbitingStar(
            location=[-1.496e11, 0.0],
            velocity=[0.0, -29_800.0],
            mass=5.972e24,
            speed_factor=60*60*24,
            parent_star=pulsating_star,
            min_radius=min_radius,
            max_radius = max_radius,
            pulse_speed=pulse_speed,
            color_inner=self.RED,
            color_outer=self.YELLOW,
            gradient_factor=gradient_factor,
            gradient_stretch=gradient_stretch,
            screen_center=screen_center,
            scale=self.scale,
            game=self,
        )
        
        self.orbiting_planets.append(orbiting_planet)
        self.orbiting_planets.append(orbiting_planet_2)
        
        self.stars.append(pulsating_star)
        #self.stars.append(pulsating_star_2)

        black_hole = BlackHole(location=[30e14, 1e11], mass=8e37, game=self,
                               disk_outer_factor=5,
                               inclination=0.0,
                               rotation_speed_deg=0.35,
                               disk_quality=0.8)
        self.black_holes.append(black_hole)

        edit_menu = Edit_Menu(surface=self.high_res_surface, game=self)

        create_station_menu = CreateStationMenu(self.resolution_factor, self.width - 600, 0, 260, 230, self)

        kepler_menu = Menu(resolution_factor, 0, 0, 300, 300, self)
        kepler_menu.add_button('Sun Focus', 50, 50, 200, 50, action=lambda: kepler_menu.button_action('Sun Focus'))
        kepler_menu.add_button('Equal areas in equal times', 50, 120, 200, 50, action=lambda: kepler_menu.button_action('Equal areas in equal times'))
        kepler_menu.add_button('Third Law', 50, 190, 200, 50, action=lambda: kepler_menu.button_action('Third Law'))
        
        kepler_menu_button = MenuButton(resolution_factor, 100, 100, 200, 50, 'Open Menu', kepler_menu)

        kepler_sun_focus_guide = Kepler_Guide_Sun_Focus(self.high_res_surface, self.orbiting_planets[0], self.stars[0], 13, (255, 255, 255), (self.width / 2, 100), GRAVITATIONAL_CONSTANT, self, resolution_factor)
        kepler_equal_guide = Kepler_Guide_Equal(self, self.high_res_surface, self.orbiting_planets[0], self.stars[0], 13, (255, 255, 255), (self.width / 2, 100), GRAVITATIONAL_CONSTANT, resolution_factor)
        kepler_guide_three = Kepler_Guide_Three(self, self.high_res_surface, self.orbiting_planets[0], self.stars[0], 13, (255, 255, 255), (self.width / 2, 100), GRAVITATIONAL_CONSTANT, resolution_factor)
        
        lagrange = Lagrange_Points(resolution_factor, self.scale, screen_center, self)

        menu_width = 300
        menu_height = 300
        create_menu = CreatePlanetMenu(pygame.Rect(self.width - menu_width, 0, menu_width, menu_height), self.manager, self)

        advanced_menu = AdvancedMenu(
            resolution_factor,
            x=self.width - 400,
            y=350,
            width=400,
            height=300,
            game=self
        )

        FIXED_DT = 1.0 / self.FRAMES_PER_SECOND
        accumulator = 0.0
        previous_time = pygame.time.get_ticks() / 1000.0

        while running:
            current_time = pygame.time.get_ticks() / 1000.0
            frame_time = current_time - previous_time
            previous_time = current_time

            if frame_time > 0.25:
                frame_time = 0.25
            accumulator += frame_time

            keys = pygame.key.get_pressed()
            pan_speed = 10  # adjust as needed

            if self.current_state not in (self.GUIDE_STATE, self.MOVE_ONLY_STATE):
                if keys[pygame.K_LEFT]:
                    self.camera_offset[0] += pan_speed
                if keys[pygame.K_RIGHT]:
                    self.camera_offset[0] -= pan_speed
                if keys[pygame.K_UP]:
                    self.camera_offset[1] += pan_speed
                if keys[pygame.K_DOWN]:
                    self.camera_offset[1] -= pan_speed
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                self.manager.process_events(event)
                
                if self.current_state == self.GUIDE_STATE:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.current_guide_active == 1:
                            if self.guide_iteration == kepler_sun_focus_guide.get_iteration_count() - 1:
                                self.current_state = self.ACTIVE_STATE
                                self.guide_iteration = -1
                            kepler_sun_focus_guide.clear_text()
                            self.guide_iteration += 1
                        elif self.current_guide_active == 2:
                            if self.guide_iteration == kepler_equal_guide.get_iteration_count() - 1:
                                self.current_state = self.ACTIVE_STATE
                                self.guide_iteration = -1
                                kepler_equal_guide.reset_values()
                            kepler_equal_guide.clear_text()
                            self.guide_iteration += 1
                        elif self.current_guide_active == 3:
                            if self.guide_iteration == kepler_guide_three.get_iteration_count() - 1:
                                self.current_state = self.ACTIVE_STATE
                                self.guide_iteration = -1
                                kepler_guide_three.reset_values()
                            kepler_guide_three.clear_text()
                            self.guide_iteration += 1

                elif self.current_state != self.MOVE_ONLY_STATE:
                    edit_menu.check_events(event)
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if self.current_state == self.ACTIVE_STATE:
                                self.current_state = self.PAUSE_STATE
                            elif self.current_state == self.PAUSE_STATE:
                                self.current_state = self.ACTIVE_STATE

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self._over_advanced_menu(advanced_menu, event.pos) or self._over_ui(event.pos, create_menu):
                            self.is_panning = False
                            self.last_mouse_pos = None
                            continue

                        if event.button in (4, 5):
                            continue    

                        self.mouse_down_pos = pygame.mouse.get_pos()

                        result_planet = edit_menu.check_for_click(event, self.orbiting_planets, resolution_factor)
                        result_star = edit_menu.check_for_click(event, self.stars, resolution_factor)
                        result_blackhole = edit_menu.check_for_click(event, self.black_holes, resolution_factor)
                        result_station = edit_menu.check_for_click(event, self.stations, resolution_factor)

                        clicked_object = False
                                    
                        if result_planet is not None and result_planet != "MISSED":
                            self.CURRENT_EDIT_MENU = result_planet
                            edit_menu.create_sliders_planet(result_planet, (width, height), resolution_factor)
                            clicked_object = True
                        elif result_star is not None and result_star != "MISSED":
                            self.CURRENT_EDIT_MENU = result_star
                            edit_menu.create_sliders_star(result_star, (width, height), resolution_factor)
                            clicked_object = True
                        elif result_blackhole is not None and result_blackhole != "MISSED":
                            self.CURRENT_EDIT_MENU = result_blackhole
                            edit_menu.create_sliders_blackhole(result_blackhole, (width, height), resolution_factor)
                            clicked_object = True
                        elif result_station is not None and result_station != "MISSED":
                            self.CURRENT_EDIT_MENU = result_station
                            clicked_object = True

                        in_slider_zone = False
                        mouse_pos = pygame.mouse.get_pos()
                        if hasattr(edit_menu, 'planet_gc_slider'):
                            if mouse_pos[0] * resolution_factor > edit_menu.planet_gc_slider.line_start[0] - 50:
                                in_slider_zone = True
                        if hasattr(edit_menu, 'mass_star_slider'):
                            if mouse_pos[0] * resolution_factor > edit_menu.mass_star_slider.line_start[0] - 50:
                                in_slider_zone = True
                        if hasattr(edit_menu, 'bh_mass_slider'):
                            if mouse_pos[0] * resolution_factor > edit_menu.bh_mass_slider.line_start[0] - 50:
                                in_slider_zone = True
                        if hasattr(edit_menu, 'bh_disk_slider'):
                            if mouse_pos[0] * resolution_factor > edit_menu.bh_disk_slider.line_start[0] - 50:
                                in_slider_zone = True
                        if hasattr(edit_menu, 'bh_inclination_slider'):
                            if mouse_pos[0] * resolution_factor > edit_menu.bh_inclination_slider.line_start[0] - 50:
                                in_slider_zone = True

                        if not clicked_object and not in_slider_zone:
                            self.is_panning = True
                            self.last_mouse_pos = pygame.mouse.get_pos()

                    create_menu.handle_event(event)
                    advanced_menu.handle_event(event)

                    if create_menu.placing_planet and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self._over_ui(event.pos, create_menu):
                            continue

                        scaled_pos = (event.pos[0] * resolution_factor,
                                        event.pos[1] * resolution_factor)
                        world_x, world_y = self.to_world(scaled_pos)
                        mass, speed, velocity, orbit_flag, ecc = create_menu.pending_data

                        closest_star = min(
                            self.stars,
                            key=lambda s: (s.location[0]-world_x)**2 + (s.location[1]-world_y)**2
                        )

                        if orbit_flag:
                            ecc = max(0.0, min(0.9, float(ecc)))

                            dx = world_x - closest_star.location[0]
                            dy = world_y - closest_star.location[1]
                            r = (dx**2 + dy**2) ** 0.5

                            if r < 1e-06:
                                r = 1e-06

                            a = r / (1.0 - ecc)

                            term = (2.0 / r) - (1.0 / a)
                            if term < 0:
                                if term > -1e-12:
                                    term = 0.0
                                else:
                                    print("⚠️ Invalid orbit parameters: produced negative vis-viva term")
                                    term = 0.0
                            v = (self.gravitational_constant * closest_star.mass * term) ** 0.5

                            import math
                            ux, uy = -dy / r, dx / r
                            norm = math.sqrt(ux*ux + uy*uy)
                            ux, uy = ux / norm, uy / norm
                            velocity = [ux * v, uy * v]

                            print(f"New planet v={v}, r={r}, a={a}, ecc={ecc}")

                        new_planet = OrbitingStar(
                            location=[world_x, world_y],
                            velocity=velocity,
                            mass=mass,
                            speed_factor=speed,
                            parent_star=closest_star,
                            min_radius=self.min_radius,
                            max_radius=self.max_radius,
                            pulse_speed=self.pulse_speed,
                            color_inner=self.RED,
                            color_outer=self.YELLOW,
                            gradient_factor=self.gradient_factor,
                            gradient_stretch=self.gradient_stretch,
                            screen_center=self.center_pos,
                            scale=self.scale,
                            game=self,
                        )
                        self.orbiting_planets.append(new_planet)
                        self.CURRENT_EDIT_MENU = new_planet

                        edit_menu.create_sliders_planet(new_planet, (width, height), resolution_factor)
                        
                        create_menu.placing_planet = False
                        create_menu.pending_data = None

                    create_station_menu.handle_event(event)

                    if create_station_menu.placing_station and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self._over_ui(event.pos, create_menu):
                            continue

                        scaled_pos = (event.pos[0] * self.resolution_factor, event.pos[1] * self.resolution_factor)
                        world_x, world_y = self.to_world(scaled_pos)
                        name, mass, speed, velocity, orbit_flag, ecc = create_station_menu.pending_data

                        # nearest star for orbit seeding if requested
                        closest_star = min(
                            self.stars,
                            key=lambda s: (s.location[0]-world_x)**2 + (s.location[1]-world_y)**2
                        ) if self.stars else None

                        if orbit_flag and closest_star is not None:
                            ecc = max(0.0, min(0.9, float(ecc)))
                            dx = world_x - closest_star.location[0]
                            dy = world_y - closest_star.location[1]
                            r = (dx*dx + dy*dy) ** 0.5
                            if r < 1e-06:
                                r = 1e-06
                            a = r / (1.0 - ecc)
                            term = (2.0 / r) - (1.0 / a)
                            if term < 0:
                                if term > -1e-12:
                                    term = 0.0
                                else:
                                    print("⚠️ Invalid orbit parameters for station: negative vis-viva term")
                                    term = 0.0
                            v = (self.gravitational_constant * closest_star.mass * term) ** 0.5

                            import math
                            ux, uy = -dy / r, dx / r
                            norm = math.sqrt(ux*ux + uy*uy)
                            ux, uy = ux / norm, uy / norm
                            velocity = [ux * v, uy * v]

                        station = SpaceStation(
                            location=[world_x, world_y],
                            velocity=velocity,
                            mass=mass,
                            speed_factor=speed,
                            screen_center=self.center_pos,
                            scale=self.scale,
                            game=self,
                            name=name,
                            thrust_power=1000,
                        )
                        self.stations.append(station)
                        create_station_menu.placing_station = False
                        create_station_menu.pending_data = None

                        self.change_state(self.PAUSE_STATE)
                            
                        #Kepler Menu
                        if kepler_menu.is_visible:
                            kepler_menu.handle_event(event)
                        elif(self.current_state != self.GUIDE_STATE):
                            kepler_menu_button.handle_event(event)

                if self.current_state not in (self.GUIDE_STATE, self.MOVE_ONLY_STATE):
                    if event.type == pygame.MOUSEWHEEL:
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        world_x = (mouse_x - self.center_pos[0] - self.camera_offset[0]) * self.scale
                        world_y = (mouse_y - self.center_pos[1] - self.camera_offset[1]) * self.scale
                        
                        zoom_factor = 0.9 if event.y > 0 else 1.1
                        self.scale *= zoom_factor
                        
                        self.camera_offset[0] = mouse_x - self.center_pos[0] - (world_x / self.scale)
                        self.camera_offset[1] = mouse_y - self.center_pos[1] - (world_y / self.scale)

                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.is_panning = False
                            self.last_mouse_pos = None

                            if self.mouse_down_pos:
                                mx, my = event.pos
                                dx = mx - self.mouse_down_pos[0]
                                dy = my - self.mouse_down_pos[1]
                                dist = (dx*dx + dy*dy) ** 0.5

                                if dist < 5:
                                    result_planet = edit_menu.check_for_click(event, self.orbiting_planets, resolution_factor)
                                    result_star = edit_menu.check_for_click(event, self.stars, resolution_factor)
                                    result_blackhole = edit_menu.check_for_click(event, self.black_holes, resolution_factor)
                                    result_station = edit_menu.check_for_click(event, self.stations, resolution_factor)
                                    
                                    selected_obj = None
                                    if result_planet not in (None, "MISSED"):
                                        selected_obj = result_planet
                                    elif result_star not in (None, "MISSED"):
                                        selected_obj = result_star
                                    elif result_blackhole not in (None, "MISSED"):
                                        selected_obj = result_blackhole
                                    elif result_station not in (None, "MISSED"):
                                        selected_obj = result_station

                                    mouse_pos = pygame.mouse.get_pos()
                                    in_slider_zone = False
                                    # --- keep your slider exclusion logic ---
                                    if hasattr(edit_menu, 'planet_gc_slider'):
                                        if mouse_pos[0] * resolution_factor > edit_menu.planet_gc_slider.line_start[0] - 50:
                                            in_slider_zone = True
                                    if hasattr(edit_menu, 'mass_star_slider'):
                                        if mouse_pos[0] * resolution_factor > edit_menu.mass_star_slider.line_start[0] - 50:
                                            in_slider_zone = True
                                    if hasattr(edit_menu, 'bh_mass_slider'):
                                        if mouse_pos[0] * resolution_factor > edit_menu.bh_mass_slider.line_start[0] - 50:
                                            in_slider_zone = True
                                    if hasattr(edit_menu, 'bh_disk_slider'):
                                        if mouse_pos[0] * resolution_factor > edit_menu.bh_disk_slider.line_start[0] - 50:
                                            in_slider_zone = True
                                    if hasattr(edit_menu, 'bh_inclination_slider'):
                                        if mouse_pos[0] * resolution_factor > edit_menu.bh_inclination_slider.line_start[0] - 50:
                                            in_slider_zone = True

                                    # --- apply toggle logic safely ---
                                    if not in_slider_zone:
                                        if selected_obj is not None:
                                            if self.CURRENT_EDIT_MENU is not selected_obj:
                                                self.CURRENT_EDIT_MENU = selected_obj
                                        else:
                                            # clicked empty space — deselect
                                            self.CURRENT_EDIT_MENU = None
                            
                                self.mouse_down_pos = None
                            
                    if event.type == pygame.MOUSEMOTION:
                        if self._over_advanced_menu(advanced_menu, event.pos):
                            self.is_panning = False
                            self.last_mouse_pos = None
                        elif self.is_panning and self.last_mouse_pos:
                            mouse_x, mouse_y = event.pos
                            dx = mouse_x - self.last_mouse_pos[0]
                            dy = mouse_y - self.last_mouse_pos[1]
                            self.camera_offset[0] += dx
                            self.camera_offset[1] += dy
                            self.last_mouse_pos = (mouse_x, mouse_y)

            while accumulator >= FIXED_DT:
                self.high_res_surface.fill(self.BLACK)
                self.delta_time = FIXED_DT

                advanced_menu.draw(self.high_res_surface)
                create_station_menu.draw(self.high_res_surface)
                    
                if(self.CURRENT_EDIT_MENU in self.orbiting_planets):
                    edit_menu.open_planet_menu()
                    lagrange.draw_lagrange_points(self.CURRENT_EDIT_MENU, self.CURRENT_EDIT_MENU.parent_star, self.high_res_surface, GRAVITATIONAL_CONSTANT)
                elif(self.CURRENT_EDIT_MENU in self.stars):
                    edit_menu.open_star_menu()
                    StarDetails(self.high_res_surface, self.CURRENT_EDIT_MENU, self).draw()
                elif(self.CURRENT_EDIT_MENU in self.black_holes):
                    edit_menu.open_blackhole_menu()
                    
                #Guides
                if self.current_state == self.GUIDE_STATE or self.current_state == self.MOVE_ONLY_STATE:
                    if self.current_guide_active == 1:
                        #Kepler law 1
                        kepler_sun_focus_guide.call_state(self.guide_iteration)
                    elif self.current_guide_active == 2:
                        #Kepler law 2
                        kepler_equal_guide.call_state(self.guide_iteration)
                    elif self.current_guide_active == 3:
                        #Kepler law 3
                        kepler_guide_three.call_state(self.guide_iteration)
                
                for star in self.stars:
                    star.update()
                    star.draw(self.high_res_surface, self.scale, self.base_scale)
                
                for planet in self.orbiting_planets:
                    if self.current_state in (self.ACTIVE_STATE, self.MOVE_ONLY_STATE):
                        if advanced_menu.disable_blackholes:
                            influencing_bodies = self.stars
                        else:
                            influencing_bodies = self.stars + self.black_holes
                            print(planet.name)

                        planet.location, planet.velocity = self.orbit_calc.update_planet_position(
                            planet.location,
                            planet.velocity,
                            planet.mass,                                                     # not used in accel calc but kept
                            influencing_bodies,                                              # stars stay constant reference points
                            FIXED_DT * planet.speed_factor * advanced_menu.planet_speed_multiplier,
                            method=advanced_menu.integration_method
                        )

                    planet.update()
                    planet.draw(self.high_res_surface, self.scale, self.base_scale)

                for black_hole in self.black_holes:
                    black_hole.update()
                    black_hole.draw(self.high_res_surface, self.scale, self.base_scale)

                for station in self.stations:
                    # only allow control input for the currently selected station
                    if self.CURRENT_EDIT_MENU is station:
                        keys = pygame.key.get_pressed()
                        station.apply_controls(keys, self.delta_time)

                    if self.current_state in (self.ACTIVE_STATE, self.MOVE_ONLY_STATE):
                        influencing_bodies = [station.parent_planet] if hasattr(station, "parent_planet") else self.stars
                        station.location, station.velocity = self.orbit_calc.update_planet_position(
                            station.location,
                            station.velocity,
                            station.mass,
                            influencing_bodies,
                            station.speed_factor
                        )

                    station.update()
                    station.draw(self.high_res_surface, self.scale, self.base_scale)

                # Collision detection
                """for i in range(len(self.orbiting_planets)):
                    for j in range(i+1, len(self.orbiting_planets)):
                        if i >= len(self.orbiting_planets) or j >= len(self.orbiting_planets):
                            continue
                        p1 = self.orbiting_planets[i]
                        p2 = self.orbiting_planets[j]

                        dx = p1.location[0] - p2.location[0]
                        dy = p1.location[1] - p2.location[1]
                        dist = (dx*dx + dy*dy) ** 0.5

                        print(dist)
                        if dist < p1.physical_radius + p2.physical_radius:
                            self.collision_handler.handle_collision(p1, p2)
                            break"""

                self.collision_handler.update_explosions(self.high_res_surface)
                
                #Kepler Menu
                if self.current_state != self.GUIDE_STATE and self.current_state != self.MOVE_ONLY_STATE:
                    kepler_menu_button.draw(self.high_res_surface)
                if kepler_menu.is_visible:
                    kepler_menu.draw(self.high_res_surface)

                accumulator -= FIXED_DT
            
            #Sliders
            #mass_star_slider.draw(self.high_res_surface)

            self.manager.update(frame_time)
                    
            scaled_surface = pygame.transform.smoothscale(self.high_res_surface, (width, height))
            self.screen.blit(scaled_surface, (0, 0))

            self.manager.draw_ui(self.screen)
                
            pygame.display.flip()
            
            pygame.display.update()
                    
            clock.tick(self.FRAMES_PER_SECOND)
            
        pygame.quit()
        sys.exit()
        
    if __name__ == '__main__':
        main()