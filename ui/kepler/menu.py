import pygame

class MenuButton:
    def __init__(self, resolution_factor, x, y, width, height, text, menu):
        self.resolution_factor = resolution_factor
        self.rect = pygame.Rect(x * resolution_factor, y * resolution_factor, width * resolution_factor, height * resolution_factor)
        self.text = text
        self.menu = menu
        self.font = pygame.font.SysFont(None, 18 * resolution_factor)
        self.color = (0, 255, 0)
        self.hover_color = (255, 0, 0)
        
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        scaled_mouse_pos = (mouse_pos[0] * self.resolution_factor, mouse_pos[1] * self.resolution_factor)
        if self.rect.collidepoint(scaled_mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                  self.rect.y + (self.rect.height - text_surface.get_height()) // 2))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            scaled_mouse_pos = (event.pos[0] * self.resolution_factor, event.pos[1] * self.resolution_factor)
            if self.rect.collidepoint(scaled_mouse_pos):
                self.menu.toggle_visibility()
        elif event.type == pygame.KEYDOWN:
            if event.key ==  pygame.K_ESCAPE:
                self.menu.toggle_visibility()
                
class OptionButton:
    def __init__(self, resolution_factor, x, y, width, height, text, menu, action=None):
        self.resolution_factor = resolution_factor
        self.rect = pygame.Rect(x * resolution_factor, y * resolution_factor, width * resolution_factor, height * resolution_factor)
        self.text = text
        self.menu = menu
        self.font = pygame.font.SysFont(None, 18 * resolution_factor)
        self.color = (0, 255, 0)
        self.hover_color = (255, 0, 0)
        self.action = action
        
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        scaled_mouse_pos = (mouse_pos[0] * self.resolution_factor, mouse_pos[1] * self.resolution_factor)
        if self.rect.collidepoint(scaled_mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                  self.rect.y + (self.rect.height - text_surface.get_height()) // 2))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            scaled_mouse_pos = (event.pos[0] * self.resolution_factor, event.pos[1] * self.resolution_factor)
            if self.rect.collidepoint(scaled_mouse_pos):
                self.menu.toggle_visibility()
                pygame.display.update()
                self.action()
                

class Menu:
    def __init__(self, resolution_factor, x, y, width, height, main_instance):
        self.resolution_factor = resolution_factor
        self.rect = pygame.Rect(x * resolution_factor, y * resolution_factor, width * resolution_factor, height * resolution_factor)
        self.is_visible = False
        self.buttons = []
        self.font = pygame.font.SysFont(None, 18 * resolution_factor)
        self.main_instance = main_instance
    
    def add_button(self, text, x, y, width, height, action=None):
        button = OptionButton(self.resolution_factor, x, y, width, height, text, self, action)
        self.buttons.append(button)
        
    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), self.rect)
        for button in self.buttons:
            button.draw(screen)
    
    def toggle_visibility(self):
        self.is_visible = not self.is_visible
        
    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)
            
    def button_action(self, id):
        self.main_instance.change_state(3)
        if id == 'Sun Focus':
            self.main_instance.current_guide_active = 1
        elif id == 'Equal areas in equal times':
            self.main_instance.current_guide_active = 2