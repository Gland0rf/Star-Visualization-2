import pygame

class Slider:
    def __init__(self, manager, window_size, other_instance, update_value, resolution_factor, line_width, line_length, x_margin, y_margin, dot_radius, slider_color, dot_color):
        line_length *= resolution_factor
        line_width *= resolution_factor
        dot_radius *= resolution_factor
        x_margin *= resolution_factor
        y_margin *= resolution_factor
        window_size = [c * resolution_factor for c in window_size]
        
        self.other_instance = other_instance
        self.update_value = update_value
        self.resolution_factor = resolution_factor
        self.manager = manager
        self.line_start = (window_size[0] - line_length - x_margin, window_size[1] - y_margin - dot_radius)
        self.line_end = (window_size[0] - x_margin, window_size[1] - y_margin - dot_radius)
        self.line_width = line_width
        self.line_length = line_length
        self.x_margin = x_margin
        self.y_margin = y_margin
        self.dot_radius = dot_radius
        self.slider_color = slider_color
        self.dot_color = dot_color
        
        self.dragging = False
        
    def create_slider(self, label, font, min_val, max_val, slider_value):
        self.slider_value = slider_value
        self.label = label
        self.font = font
        self.min_val = min_val
        self.max_val = max_val
        
        self.dot_position = ((self.line_end[0] - self.line_start[0]) * ((self.slider_value + min_val) / max_val) + self.line_start[0], self.line_start[1])
        
    def draw(self, surface):
        pygame.draw.line(surface, self.slider_color, self.line_start, self.line_end, self.line_width)
        pygame.draw.circle(surface, self.dot_color, (int(self.dot_position[0]), int(self.dot_position[1])), self.dot_radius)
        
        label = self.label
        if("SLIDER_VALUE" in label):
            label = label.replace("SLIDER_VALUE", f"{self.slider_value}")
        
        value_text = self.font.render(label, True, self.slider_color)
        surface.blit(value_text, (self.line_start[0], self.line_start[1] - 40))
        
    def slider_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            mouse_x *= self.resolution_factor
            mouse_y *= self.resolution_factor
            
            if(mouse_x - self.dot_position[0]) ** 2 + (mouse_y - self.dot_position[1]) ** 2 <= self.dot_radius ** 2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            raw_mouse_x = event.pos[0] * self.resolution_factor
            
            mouse_x = max(min(raw_mouse_x, self.line_end[0]), self.line_start[0])
            self.dot_position = (mouse_x, self.line_start[1])
            self.slider_value = int((mouse_x - self.line_start[0]) / (self.line_end[0] - self.line_start[0]) * (self.max_val - self.min_val) + self.min_val)
            
            if hasattr(self.other_instance, self.update_value):
                setattr(self.other_instance, self.update_value, self.slider_value)
            else:
                raise AttributeError(f"'{self.other_instance.__class__.__name__}' object has no attribute '{self.update_value}'")