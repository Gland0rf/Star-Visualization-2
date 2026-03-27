import pygame
import re
import time
import math

class Slider:
    def __init__(self, window_size, other_instance, update_value, index,
                 resolution_factor, line_width, line_length, x_margin, y_margin,
                 dot_radius, slider_color, dot_color):
        line_length *= resolution_factor
        line_width *= resolution_factor
        dot_radius *= resolution_factor
        x_margin *= resolution_factor
        y_margin *= resolution_factor
        window_size = [c * resolution_factor for c in window_size]

        self.other_instance = other_instance
        self.update_value = update_value
        self.index = index
        self.resolution_factor = resolution_factor
        self.line_start = (window_size[0] - line_length - x_margin,
                           window_size[1] - y_margin - dot_radius)
        self.line_end = (window_size[0] - x_margin,
                         window_size[1] - y_margin - dot_radius)
        self.line_width = line_width
        self.line_length = line_length
        self.x_margin = x_margin
        self.y_margin = y_margin
        self.dot_radius = dot_radius
        self.slider_color = slider_color
        self.dot_color = dot_color

        self.dragging = False
        self.active = False
        self.input_text = ""
        self.last_blink = time.time()
        self.show_caret = True  # blinking cursor state

    def create_slider(self, label, font, min_val, max_val, slider_value, log_scale=False):
        """Initialize a slider, optionally with logarithmic scaling."""
        self.slider_value = slider_value
        self.label = label
        self.font = font
        self.min_val = min_val
        self.max_val = max_val
        self.log_scale = log_scale

        if self.log_scale:
            # Precompute log10 range for smooth exponential response
            self.min_log = math.log10(max(min_val, 1e-30))
            self.max_log = math.log10(max_val)
            pos_frac = (math.log10(slider_value) - self.min_log) / (self.max_log - self.min_log)
        else:
            pos_frac = (slider_value - min_val) / (max_val - min_val)

        pos_frac = max(0.0, min(1.0, pos_frac))
        self.dot_position = (
            self.line_start[0] + pos_frac * (self.line_end[0] - self.line_start[0]),
            self.line_start[1]
        )

    def draw(self, surface):
        # Draw slider line + dot
        pygame.draw.line(surface, self.slider_color, self.line_start, self.line_end, self.line_width)
        pygame.draw.circle(surface, self.dot_color,
                           (int(self.dot_position[0]), int(self.dot_position[1])),
                           self.dot_radius)

        # Determine value text to display
        label = self.label
        if self.active:
            display_value = self.input_text if self.input_text else self.format_value(self.slider_value)

            # blink caret
            if time.time() - self.last_blink > 0.5:
                self.show_caret = not self.show_caret
                self.last_blink = time.time()
            if self.show_caret:
                display_value += "|"
        else:
            display_value = self.format_value(self.slider_value)

        if "SLIDER_VALUE" in label:
            label = label.replace("SLIDER_VALUE", display_value)

        # Render text
        value_text = self.font.render(label, True, self.slider_color)
        text_rect = value_text.get_rect()
        text_rect.bottomleft = (self.line_start[0], self.line_start[1] - 5)
        self.label_rect = text_rect
        surface.blit(value_text, text_rect)

    def format_value(self, val):
        """Formats numeric values in readable scientific notation."""
        if abs(val) >= 1e5 or abs(val) < 1e-2:
            return f"{val:.3e}"  # scientific
        elif isinstance(val, float):
            return f"{val:.2f}"
        else:
            return str(val)

    def slider_events(self, event):
        # --- MOUSE ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            mouse_x *= self.resolution_factor
            mouse_y *= self.resolution_factor

            if (mouse_x - self.dot_position[0])**2 + (mouse_y - self.dot_position[1])**2 <= self.dot_radius**2:
                self.dragging = True
                self.active = False
            elif hasattr(self, "label_rect") and self.label_rect.collidepoint(event.pos):
                self.active = True
                self.input_text = ""
            else:
                self.active = False

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            raw_mouse_x = event.pos[0] * self.resolution_factor
            mouse_x = max(min(raw_mouse_x, self.line_end[0]), self.line_start[0])
            self.dot_position = (mouse_x, self.line_start[1])
            t = (mouse_x - self.line_start[0]) / (self.line_end[0] - self.line_start[0])

            if self.log_scale:
                val_log = self.min_log + t * (self.max_log - self.min_log)
                self.slider_value = 10 ** val_log
            else:
                self.slider_value = self.min_val + t * (self.max_val - self.min_val)

            self.change_value()

        # --- KEYBOARD ---
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # commit input
                self.commit_input()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if event.unicode.isprintable():
                    self.input_text += event.unicode

    def commit_input(self):
        """Handle manual numeric input."""
        try:
            cleaned = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", self.input_text)
            if cleaned:
                val = float(cleaned[0])
                val = max(self.min_val, min(self.max_val, val))
                self.slider_value = val

                # reposition dot
                if self.log_scale:
                    pos_frac = (math.log10(val) - self.min_log) / (self.max_log - self.min_log)
                else:
                    pos_frac = (val - self.min_val) / (self.max_val - self.min_val)

                pos_frac = max(0.0, min(1.0, pos_frac))
                self.dot_position = (
                    self.line_start[0] + pos_frac * (self.line_end[0] - self.line_start[0]),
                    self.line_start[1]
                )
                self.change_value()
        except ValueError:
            pass
        self.active = False

    def change_value(self):
        """Apply slider value to the linked object."""
        if hasattr(self.other_instance, self.update_value):
            attribute = getattr(self.other_instance, self.update_value)
            if isinstance(attribute, list):
                if self.index is not None:
                    try:
                        attribute[self.index] = self.slider_value
                    except IndexError:
                        raise IndexError(f"Index {self.index} out of range for '{self.update_value}'")
                else:
                    setattr(self.other_instance, self.update_value, self.slider_value)
            else:
                setattr(self.other_instance, self.update_value, self.slider_value)
        else:
            raise AttributeError(f"'{self.other_instance.__class__.__name__}' has no attribute '{self.update_value}'")
