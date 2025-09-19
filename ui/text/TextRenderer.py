import pygame
import time

class TextRenderer:
    def __init__(self, font_name, base_font_size, resolution_factor, color, position, char_delay=0.02):
        self.displayed_text = ""  # Text that will be shown character by character
        self.text_index = 0  # Index to keep track of which character to display next
        self.char_delay = char_delay  # Delay in seconds between each character
        self.last_char_time = time.time()  # Timer to control when the next character appears

        # Font setup
        font_size = int(base_font_size * resolution_factor)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.color = color
        
        position = [x * resolution_factor for x in position]
        self.position = position

    def add_text(self, text):
        # Add the next character based on the delay
        current_time = time.time()
        if current_time - self.last_char_time > self.char_delay and self.text_index < len(text):
            self.displayed_text += text[self.text_index]
            self.text_index += 1
            self.last_char_time = current_time
            
    def clear_text(self):
        self.displayed_text = ""
        self.text_index = 0
        self.text_displayed = False
        self.last_char_time = time.time()

    def render(self, screen):
        # Render the progressively appearing text
        text_surface = self.font.render(self.displayed_text, True, self.color)
        text_rect = text_surface.get_rect(center=self.position)
        screen.blit(text_surface, text_rect)