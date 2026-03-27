# stars/createStationMenu.py
import pygame

class CreateStationMenu:
    def __init__(self, resolution_factor, x, y, width, height, game):
        self.resolution_factor = resolution_factor
        self.rect = pygame.Rect(x * resolution_factor, y * resolution_factor,
                                width * resolution_factor, height * resolution_factor) 
        self.is_visible = True
        self.font = pygame.font.SysFont(None, int(18 * resolution_factor))
        self.game = game

        # Defaults
        self.name = "Station-1"
        self.mass = 2.0e6
        self.speed_factor = 60 * 60 * 24
        self.velocity = [0.0, 0.0]
        self.eccentricity = 0.0

        # Input state
        self.active_input = None
        self.input_texts = {
            "name": self.name,
            "mass": str(self.mass),
            "speed": str(self.speed_factor),
            "velocity": "0,0",
            "eccentricity": str(self.eccentricity),
        }

        # Buttons
        self.create_btn = pygame.Rect((x + 20) * resolution_factor, (y + 200) * resolution_factor,
                                      100 * resolution_factor, 30 * resolution_factor)

        # Orbit checkbox (auto-velocity via vis-viva)
        self.orbit_checkbox = pygame.Rect((x + 20) * resolution_factor, (y + 140) * resolution_factor,
                                          20 * resolution_factor, 20 * resolution_factor)
        self.orbit_mode = False

        # Placement flags
        self.placing_station = False
        self.pending_data = None
        self.awaiting_click = False

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    def draw(self, screen):
        if not self.is_visible:
            return

        # Re-Add later
        """
        pygame.draw.rect(screen, (25, 28, 35), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        labels = [
            ("Name:", "name", 20),
            ("Mass:", "mass", 50),
            ("Speed:", "speed", 80),
            ("Velocity (x,y):", "velocity", 110),
        ]

        # Orbit checkbox
        pygame.draw.rect(screen, (200, 200, 200), self.orbit_checkbox, 2)
        if self.orbit_mode:
            pygame.draw.line(screen, (0, 200, 0), self.orbit_checkbox.topleft, self.orbit_checkbox.bottomright, 2)
            pygame.draw.line(screen, (0, 200, 0), self.orbit_checkbox.topright, self.orbit_checkbox.bottomleft, 2)
        txt = self.font.render("Orbit Nearest Star", True, (255, 255, 255))
        screen.blit(txt, (self.orbit_checkbox.right + 10, self.orbit_checkbox.y))

        if self.orbit_mode:
            labels.append(("Eccentricity:", "eccentricity", 170))

        for label, key, y_off in labels:
            is_active = (self.active_input == key)
            color = (255, 255, 0) if is_active else (255, 255, 255)
            if key == "velocity" and self.orbit_mode:
                color = (120, 120, 120)

            txt_str = f"{label} {self.input_texts[key]}"
            txt_r = self.font.render(txt_str, True, color)
            pos = (self.rect.x + 10, self.rect.y + int(y_off * self.resolution_factor))
            screen.blit(txt_r, pos)

            if is_active:
                caret_x = pos[0] + self.font.size(txt_str)[0] + 2
                caret_y = pos[1]
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    pygame.draw.line(screen, (255, 255, 255),
                                     (caret_x, caret_y),
                                     (caret_x, caret_y + self.font.get_height()), 1)

        # Create button
        btn_color = (0, 80, 110) if self.active_input == "create_btn" else (0, 120, 160)
        pygame.draw.rect(screen, btn_color, self.create_btn)
        c_txt = self.font.render("Create", True, (255, 255, 255))
        screen.blit(c_txt, (self.create_btn.centerx - c_txt.get_width() // 2,
                            self.create_btn.centery - c_txt.get_height() // 2))"""
        
    def handle_event(self, event):
        if not self.is_visible:
            return

        if hasattr(event, "pos"):
            scaled_pos = (event.pos[0] * self.resolution_factor,
                          event.pos[1] * self.resolution_factor)
        else:
            scaled_pos = None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if scaled_pos and self.create_btn.collidepoint(scaled_pos):
                self.active_input = "create_btn"
                try:
                    self.name = self.input_texts["name"].strip() or "Station-1"
                    self.mass = float(self.input_texts["mass"])
                    self.speed_factor = float(self.input_texts["speed"])
                    if not self.orbit_mode:
                        velocity = [float(v) for v in self.input_texts["velocity"].split(",")]
                        ecc = 0.0
                    else:
                        velocity = [0.0, 0.0]
                        ecc = float(self.input_texts["eccentricity"])

                    self.pending_data = (self.name, self.mass, self.speed_factor, velocity, self.orbit_mode, ecc)
                    self.placing_station = True
                    self.awaiting_click = True

                    # Pause sim while placing
                    self.game.change_state(self.game.PAUSE_STATE)

                except Exception as e:
                    print("Invalid station input:", e)

            elif scaled_pos and self.orbit_checkbox.collidepoint(scaled_pos):
                self.orbit_mode = not self.orbit_mode
                self.active_input = None

            elif scaled_pos and self.rect.collidepoint(scaled_pos):
                y_rel = scaled_pos[1] - self.rect.y
                rf = self.resolution_factor
                if 20 * rf <= y_rel <= 40 * rf:
                    self.active_input = "name"
                elif 50 * rf <= y_rel <= 70 * rf:
                    self.active_input = "mass"
                elif 80 * rf <= y_rel <= 100 * rf:
                    self.active_input = "speed"
                elif 110 * rf <= y_rel <= 130 * rf and not self.orbit_mode:
                    self.active_input = "velocity"
                elif self.orbit_mode and 170 * rf <= y_rel <= 190 * rf:
                    self.active_input = "eccentricity"
                else:
                    self.active_input = None

        elif event.type == pygame.KEYDOWN and self.active_input:
            if self.active_input == "create_btn":
                return
            if event.key == pygame.K_RETURN:
                self.active_input = None
            elif event.key == pygame.K_BACKSPACE:
                self.input_texts[self.active_input] = self.input_texts[self.active_input][:-1]
            else:
                self.input_texts[self.active_input] += event.unicode
