import pygame

class StarDetails:
    def __init__(self, screen, star, game):
        self.screen = screen
        self.star = star
        self.game = game
        self.white = (255, 255, 255)

    def calculate_progress(self):
        SECONDS_PER_YEAR = 31_557_600
        age_years = self.star.age / SECONDS_PER_YEAR
        lifetime_years = self.star.lifetime / SECONDS_PER_YEAR
        pct = min(100.0 * self.star.age / self.star.lifetime, 100.0)
        return age_years, lifetime_years, pct

    # 👇 Helper to make times human readable
    def format_years(self, years):
        if years < 1e-6:
            return f"{years * 31_557_600:.1f} sec"
        elif years < 1/365.25:  # less than 1 day
            return f"{years * 365.25 * 24:.1f} hr"
        elif years < 1:         # less than 1 year
            return f"{years * 365.25:.1f} days"
        elif years < 1e3:
            return f"{years:.2f} years"
        elif years < 1e6:
            return f"{years/1e3:.2f} K years"
        elif years < 1e9:
            return f"{years/1e6:.2f} M years"
        else:
            return f"{years/1e9:.2f} B years"

    def draw(self):
        age, lifetime, pct = self.calculate_progress()
        font = pygame.font.SysFont(None, 24)

        age_str = self.format_years(age)
        life_str = self.format_years(lifetime)

        lines = [
            f"Star Age: {age_str}",
            f"Expected Lifetime: {life_str}",
            f"Life Completed: {pct:.2f}%"
        ]

        y = self.game.height - 100
        for i, line in enumerate(lines):
            text = font.render(line, True, self.white)
            self.screen.blit(text, (20, y + i * 22))

        name_text = font.render(self.star.name or "Unnamed Star", False, self.white)
        name_text_rect = name_text.get_rect(center=(self.game.width // 2, 20))
        self.screen.blit(name_text, name_text_rect)