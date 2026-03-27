import os
import math
import pygame
import pygame_gui
from .star_background import StarBackground
from presets.preset_loader import load_preset


class AdvancedMenu:
    """
    Advanced tabbed settings panel with subsections:
    - Time
    - Interaction
    - View
    """

    def __init__(self, resolution_factor, x, y, width, height, game):
        self.game = game
        self.manager = game.manager
        self.is_visible = False

        self.disable_blackholes = True
        self.font_small = pygame.font.SysFont(None, 24)

        # Star background visuals
        self.star_background = StarBackground(game)
        self.parallax_enabled = False

        # Planet speed multiplier (for simulation view only)
        self.planet_speed_percent = 100
        self.planet_speed_multiplier = 1.0

        # Integration Method
        self.integration_method = "Euler"

        # --- Main button ---
        self.button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(x, y, width, 40),
            text="Advanced",
            manager=self.manager
        )

        # --- Fixed-height panel ---
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y + 45, width, height),
            starting_height=1,
            manager=self.manager,
            visible=True
        )
        self.panel.background_colour = pygame.Color(50, 50, 50)
        self.panel.hide()

        # =========================================================
        # SUBSECTION TABS
        # =========================================================
        tab_width = width // 4
        self.sub_tabs = {
            "Time": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, 0, tab_width, 30),
                text="Time",
                manager=self.manager,
                container=self.panel
            ),
            "Interaction": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(tab_width, 0, tab_width, 30),
                text="Interaction",
                manager=self.manager,
                container=self.panel
            ),
            "Science": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(tab_width * 2, 0, tab_width, 30),
                text="Science",
                manager=self.manager,
                container=self.panel
            ),
            "View": pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(tab_width * 3, 0, tab_width, 30),
                text="View",
                manager=self.manager,
                container=self.panel
            )
        }

        self.active_tab = "Time"
        self._build_tab_content()

    # =========================================================
    # TAB CONTENT BUILDER
    # =========================================================
    def _build_tab_content(self):
        # Clear old UI elements except for tabs
        for element in list(self.panel.get_container().elements):
            if element not in self.sub_tabs.values():
                element.kill()

        width = self.panel.relative_rect.width
        height = self.panel.relative_rect.height

        # -------------------------------------------------
        # 🕰️ TIME TAB
        # -------------------------------------------------
        if self.active_tab == "Time":
            self.time_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 40, width - 20, 30),
                text="Simulation Time Controls",
                manager=self.manager,
                container=self.panel
            )
            self.time_label.text_colour = pygame.Color(0, 200, 255)
            self.time_label.rebuild()

            current_exp = math.log10(self.game.time_scale) if self.game.time_scale > 0 else 0

            self.time_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(10, 90, width - 20, 25),
                start_value=current_exp,
                value_range=(0, 20),
                manager=self.manager,
                container=self.panel,
            )

            self.time_value_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 120, width - 20, 30),
                text=f"Time Scale: {self.game.time_scale:.2e}x",
                manager=self.manager,
                container=self.panel,
            )
            self.time_value_label.text_colour = pygame.Color(255, 255, 255)
            self.time_value_label.rebuild()

            # --- Planet Speed % ---
            self.planet_speed_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 160, width - 20, 30),
                text=f"Planet Speed: {self.planet_speed_percent}%",
                manager=self.manager,
                container=self.panel,
            )
            self.planet_speed_label.text_colour = pygame.Color(0, 200, 255)
            self.planet_speed_label.rebuild()

            self.planet_speed_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(10, 190, width - 20, 25),
                start_value=self.planet_speed_percent,
                value_range=(1, 200),
                manager=self.manager,
                container=self.panel,
            )

        # -------------------------------------------------
        # ⚙️ INTERACTION TAB
        # -------------------------------------------------
        elif self.active_tab == "Interaction":
            self.disable_bh_checkbox = pygame_gui.elements.UICheckBox(
                relative_rect=pygame.Rect(10, 50, 25, 25),
                text="",
                manager=self.manager,
                container=self.panel
            )
            self.disable_bh_checkbox.is_checked = getattr(self, "disable_blackholes", True)
            self.disable_bh_checkbox.rebuild()

            self.disable_bh_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(40, 50, width - 50, 30),
                text="Disable Black Hole Interaction",
                manager=self.manager,
                container=self.panel
            )
            self.disable_bh_label.text_colour = pygame.Color(255, 255, 255)
            self.disable_bh_label.rebuild()

            self.load_preset_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10, height - 40, width - 20, 30),
                text="Load Preset",
                manager=self.manager,
                container=self.panel
            )

        # -------------------------------------------------
        # 👁️ SCIENCE TAB
        # -------------------------------------------------
        elif self.active_tab == "Science":
            self.integrator_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 90, width - 20, 30),
                text="Integrator:",
                manager=self.manager,
                container=self.panel
            )
            self.integrator_label.text_colour = pygame.Color(255, 255, 255)
            self.integrator_label.rebuild()

            self.integrator_dropdown = pygame_gui.elements.UIDropDownMenu(
                options_list=["Euler", "Leapfrog", "Runge-Kutta-4"],
                starting_option=self.integration_method,
                relative_rect=pygame.Rect(10, 120, width - 20, 30),
                manager=self.manager,
                container=self.panel
            )

        # -------------------------------------------------
        # 👁️ VIEW TAB
        # -------------------------------------------------
        elif self.active_tab == "View":
            self.enable_star_bg_checkbox = pygame_gui.elements.UICheckBox(
                relative_rect=pygame.Rect(10, 50, 25, 25),
                text="",
                manager=self.manager,
                container=self.panel
            )

            self.enable_star_bg_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(40, 50, width - 50, 30),
                text="Enable Star Background",
                manager=self.manager,
                container=self.panel
            )
            self.enable_star_bg_label.text_colour = pygame.Color(255, 255, 255)
            self.enable_star_bg_label.rebuild()

            self.enable_parallax_checkbox = pygame_gui.elements.UICheckBox(
                relative_rect=pygame.Rect(10, 90, 25, 25),
                text="",
                manager=self.manager,
                container=self.panel
            )

            self.enable_parallax_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(40, 90, width - 50, 30),
                text="Enable Parallax Nebula",
                manager=self.manager,
                container=self.panel
            )
            self.enable_parallax_label.text_colour = pygame.Color(255, 255, 255)
            self.enable_parallax_checkbox.disable()
            self.enable_parallax_label.rebuild()

    # =========================================================
    # EVENT HANDLING
    # =========================================================
    def handle_event(self, event):
        # --- Hover to show/hide panel ---
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            over_button = self.button.relative_rect.collidepoint(mouse_pos)
            over_panel = self.panel.relative_rect.collidepoint(mouse_pos)
            gap_rect = pygame.Rect(
                self.button.relative_rect.left,
                self.button.relative_rect.bottom,
                self.button.relative_rect.width,
                5
            )
            over_gap = gap_rect.collidepoint(mouse_pos)

            if over_button:
                if not self.is_visible:
                    self.show_panel()
            elif self.is_visible:
                if not (over_button or over_panel or over_gap):
                    self.hide_panel()

        # --- Tabs ---
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            for name, btn in self.sub_tabs.items():
                if event.ui_element == btn:
                    self.active_tab = name
                    self._build_tab_content()
                    return

            if self.active_tab == "Interaction":
                if event.ui_element == getattr(self, "load_preset_button", None):
                    preset_path = os.path.join("data", "solar_system.json")
                    try:
                        load_preset(self.game, preset_path)
                        print(f"✅ Loaded preset: {preset_path}")
                    except Exception as e:
                        print(f"❌ Failed to load preset: {e}")

        # --- Checkboxes ---
        elif event.type in (pygame_gui.UI_CHECK_BOX_CHECKED, pygame_gui.UI_CHECK_BOX_UNCHECKED):
            if self.active_tab == "Interaction":
                if event.ui_element == getattr(self, "disable_bh_checkbox", None):
                    self.disable_blackholes = self.disable_bh_checkbox.is_checked
            elif self.active_tab == "View":
                if event.ui_element == getattr(self, "enable_star_bg_checkbox", None):
                    val = self.enable_star_bg_checkbox.is_checked
                    self.star_background.toggle(val)
                    if not val:
                        self.enable_parallax_checkbox.is_checked = False
                        self.enable_parallax_checkbox.disable()
                        self.star_background.nebula_enabled = False
                        self.parallax_enabled = False
                    else:
                        self.enable_parallax_checkbox.enable()
                elif event.ui_element == getattr(self, "enable_parallax_checkbox", None):
                    val = self.enable_parallax_checkbox.is_checked
                    self.star_background.nebula_enabled = val
                    self.parallax_enabled = val

        # --- Sliders ---
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            # Time scale
            if hasattr(self, "time_slider") and event.ui_element == self.time_slider:
                exponent = self.time_slider.get_current_value()
                self.game.time_scale = 10 ** exponent
                self.time_value_label.set_text(f"Time Scale: {self.game.time_scale:.2e}x")

            # Planet Speed %
            elif hasattr(self, "planet_speed_slider") and event.ui_element == self.planet_speed_slider:
                new_value = self.planet_speed_slider.get_current_value()
                self.planet_speed_percent = new_value
                self.planet_speed_multiplier = new_value / 100.0
                self.planet_speed_label.set_text(f"Planet Speed: {new_value:.0f}%")

    # =========================================================
    # VISIBILITY CONTROL
    # =========================================================
    def show_panel(self):
        self.is_visible = True
        self.panel.show()

    def hide_panel(self):
        self.is_visible = False
        self.panel.hide()

    # =========================================================
    # DRAW VISUALS
    # =========================================================
    def draw(self, surface):
        if self.star_background.enabled:
            self.star_background.draw(surface)
