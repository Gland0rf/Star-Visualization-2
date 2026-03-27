import pygame
import pygame_gui

class CreatePlanetMenu:
    def __init__(self, rect, manager, game):
        self.manager = manager
        self.game = game
        self.is_visible = True

        # Defaults
        self.mass = 5.972e24
        self.speed_factor = 60 * 60 * 24
        self.velocity = [0.0, 0.0]
        self.eccentricity = 0.0
        self.orbit_mode = False

        # Placement state
        self.placing_planet = False
        self.pending_data = None
        self.awaiting_click = False

        # Panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=rect,
            starting_height=1,
            manager=manager
        )

        y = 10

        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, rect.width - 20, 30),
            text="Create Planet",
            manager=manager,
            container=self.panel
        )
        y += 40

        def label(text):
            nonlocal y
            lbl = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y, 120, 25),
                text=text,
                manager=manager,
                container=self.panel
            )
            return lbl

        def input_box(default):
            box = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(140, y, 120, 25),
                manager=manager,
                container=self.panel
            )
            box.set_text(str(default))
            return box

        label("Mass")
        self.mass_input = input_box(self.mass)
        y += 35

        label("Speed")
        self.speed_input = input_box(self.speed_factor)
        y += 35

        label("Velocity x,y")
        self.velocity_input = input_box("0,0")
        y += 35

        # Orbit toggle
        self.orbit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y, rect.width - 20, 30),
            text="Orbit Star: OFF",
            manager=manager,
            container=self.panel
        )
        y += 40

        label("Eccentricity")
        self.ecc_input = input_box(self.eccentricity)
        self.ecc_input.hide()

        # Create button
        self.create_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, rect.height - 45, rect.width - 20, 35),
            text="Create",
            manager=manager,
            container=self.panel
        )

    def set_visible(self, visible: bool):
        self.is_visible = visible
        self.panel.set_visible(visible)

    def handle_event(self, event):
        if not self.is_visible:
            return

        if event.type == pygame_gui.UI_BUTTON_PRESSED:

            if event.ui_element == self.orbit_button:
                self.orbit_mode = not self.orbit_mode
                self.orbit_button.set_text(
                    f"Orbit Star: {'ON' if self.orbit_mode else 'OFF'}"
                )
                if self.orbit_mode:
                    self.velocity_input.hide()
                    self.ecc_input.show()
                else:
                    self.velocity_input.show()
                    self.ecc_input.hide()

            elif event.ui_element == self.create_button:
                try:
                    mass = float(self.mass_input.get_text())
                    speed = float(self.speed_input.get_text())

                    if self.orbit_mode:
                        velocity = [0.0, 0.0]
                        ecc = float(self.ecc_input.get_text())
                    else:
                        velocity = [
                            float(v) for v in self.velocity_input.get_text().split(",")
                        ]
                        ecc = 0.0

                    self.pending_data = (
                        mass,
                        speed,
                        velocity,
                        self.orbit_mode,
                        ecc
                    )
                    self.placing_planet = True
                    self.awaiting_click = True

                except Exception as e:
                    print("Invalid input:", e)
