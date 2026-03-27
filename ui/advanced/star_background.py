import pygame
import os
import math
import random


class StarBackground:
    """
    Parallax starfield with nebula overlay.
    - Automatically makes black parts of the starfield transparent.
    - Moves smoothly with camera and zoom.
    """

    def __init__(self, game,
                 star_image_path="assets/star_background.png",
                 nebula_image_path="assets/nebula_overlay.png"):
        self.game = game
        self.star_image_path = star_image_path
        self.nebula_image_path = nebula_image_path

        self.star_image = None
        self.nebula_image = None
        self.enabled = False
        self.nebula_enabled = False

        # Parallax & zoom behavior
        self.star_parallax = 0.15
        self.star_zoom_strength = 0.08
        self.nebula_parallax = 0.05
        self.nebula_zoom_strength = 0.03

        # Subtle animation for nebula
        self.nebula_phase = random.random() * 1000.0

    # --------------------------------------------------------
    def enable(self):
        if not self.star_image:
            self._load_images()
        self.enabled = True
        print("[StarBackground] Enabled (parallax mode).")

    def disable(self):
        self.enabled = False
        print("[StarBackground] Disabled.")

    def toggle(self, value: bool):
        self.enable() if value else self.disable()

    # --------------------------------------------------------
    def _make_black_transparent(self, image, threshold=40):
        """
        Return a copy of 'image' where near-black pixels become transparent.
        threshold: brightness (0–255) below which pixels are fully transparent.
        """
        image = image.convert_alpha()
        arr = pygame.surfarray.pixels3d(image)
        alpha = pygame.surfarray.pixels_alpha(image)

        # Compute brightness
        brightness = (arr[:, :, 0].astype(int) +
                      arr[:, :, 1].astype(int) +
                      arr[:, :, 2].astype(int)) // 3

        # Make dark pixels transparent
        alpha[:, :] = (brightness > threshold) * 255

        del arr, alpha  # unlock surface
        return image

    # --------------------------------------------------------
    def _load_images(self):
        """Load the starfield and nebula from disk, apply transparency to stars."""
        # --- Starfield ---
        if os.path.exists(self.star_image_path):
            self.star_image = pygame.image.load(self.star_image_path).convert_alpha()
            self.star_image = self._make_black_transparent(self.star_image, threshold=40)
            print(f"[StarBackground] Loaded starfield: {self.star_image_path}")
        else:
            print(f"[StarBackground] ⚠️ Starfield not found: {self.star_image_path}")
            self.star_image = None

        # --- Nebula ---
        if os.path.exists(self.nebula_image_path):
            self.nebula_image = pygame.image.load(self.nebula_image_path).convert_alpha()
            print(f"[StarBackground] Loaded nebula overlay: {self.nebula_image_path}")
        else:
            print(f"[StarBackground] ⚠️ Nebula not found: {self.nebula_image_path}")
            self.nebula_image = None

    # --------------------------------------------------------
    def _draw_layer(self, surface, image, parallax, zoom_strength, alpha=255):
        """Draw a parallax layer that shifts and zooms with camera."""
        if not image:
            return

        cam_x, cam_y = self.game.camera_offset
        zoom = self.game.base_scale / self.game.scale

        # Parallax scaling factor
        zoom_factor = 1 + (zoom - 1) * zoom_strength

        # Apply zoom scaling
        scaled_w = int(self.game.width * zoom_factor)
        scaled_h = int(self.game.height * zoom_factor)
        img = pygame.transform.smoothscale(image, (scaled_w, scaled_h))
        img.set_alpha(alpha)

        # Parallax offset: make it move *with* the camera subtly
        offset_x = -cam_x * parallax * zoom_factor
        offset_y = -cam_y * parallax * zoom_factor

        # Center around screen midpoint
        offset_x += (self.game.width - scaled_w) // 2
        offset_y += (self.game.height - scaled_h) // 2

        surface.blit(img, (offset_x, offset_y))

    # --------------------------------------------------------
    def draw(self, surface):
        """Draw the nebula and starfield layers."""
        if not self.enabled:
            return

        # 1️⃣ Nebula layer (only if enabled)
        if self.nebula_enabled and self.nebula_image:
            self.nebula_phase += 0.01
            brightness = 0.95 + 0.05 * math.sin(self.nebula_phase)
            hue_shift = 0.02 * math.sin(self.nebula_phase * 0.5)

            r_t = int(255 * (1.0 + hue_shift))
            g_t = int(255 * (1.0 - hue_shift * 0.5))
            b_t = 255
            color_tint = (
                max(0, min(255, r_t)),
                max(0, min(255, g_t)),
                max(0, min(255, b_t))
            )

            tinted = self.nebula_image.copy()
            tinted.fill(color_tint, special_flags=pygame.BLEND_RGB_MULT)
            alpha_val = int(100 * brightness)  # softer visibility

            self._draw_layer(surface, tinted,
                            self.nebula_parallax,
                            self.nebula_zoom_strength,
                            alpha=alpha_val)

        # 2️⃣ Starfield layer (always if background is on)
        if self.star_image:
            self._draw_layer(surface, self.star_image,
                            self.star_parallax,
                            self.star_zoom_strength,
                            alpha=220)