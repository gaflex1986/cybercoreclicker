"""
UI Components and Visual Effects for CyberCore Clicker.
High-tech aesthetic, smooth animations, particles, and custom widgets.
"""
import math
import random
import pygame

# Color Palette
COLOR_BG = (10, 14, 23)
COLOR_PANEL = (16, 23, 38)
COLOR_CARD = (23, 32, 53)
COLOR_CARD_HOVER = (32, 44, 73)
COLOR_CARD_BORDER = (40, 56, 88)

COLOR_CYAN = (0, 229, 255)
COLOR_CYAN_DIM = (0, 140, 160)
COLOR_PURPLE = (192, 38, 211)
COLOR_PURPLE_GLOW = (236, 72, 153)
COLOR_GOLD = (251, 191, 36)
COLOR_GREEN = (16, 185, 129)
COLOR_RED = (239, 68, 68)
COLOR_WHITE = (245, 248, 255)
COLOR_MUTED = (148, 163, 184)
COLOR_DARK_TEXT = (90, 105, 130)

class FontCache:
    _fonts = {}

    @classmethod
    def get(cls, size, bold=False):
        key = (size, bold)
        if key not in cls._fonts:
            try:
                # Prefer segoeui for great Cyrillic font rendering on Windows
                cls._fonts[key] = pygame.font.SysFont("segoeui", size, bold=bold)
            except Exception:
                try:
                    cls._fonts[key] = pygame.font.SysFont("arial", size, bold=bold)
                except Exception:
                    cls._fonts[key] = pygame.font.Font(None, size)
        return cls._fonts[key]

class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, decay_rate=1.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.decay_rate = decay_rate

    def update(self, dt):
        self.x += self.vx * dt * 60.0
        self.y += self.vy * dt * 60.0
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= dt * self.decay_rate
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha_ratio = max(0.0, min(1.0, self.life / self.max_life))
        cur_size = max(1.0, self.size * alpha_ratio)
        r, g, b = self.color[:3]
        s = pygame.Surface((int(cur_size * 2 + 2), int(cur_size * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, int(255 * alpha_ratio)), (int(cur_size + 1), int(cur_size + 1)), int(cur_size))
        surface.blit(s, (int(self.x - cur_size), int(self.y - cur_size)))

class FloatingText:
    def __init__(self, x, y, text, color=COLOR_CYAN, size=20, duration=1.2, is_crit=False):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.duration = duration
        self.max_duration = duration
        self.is_crit = is_crit
        self.vy = -55.0 if not is_crit else -80.0
        self.vx = random.uniform(-15.0, 15.0)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy *= 0.96
        self.duration -= dt
        return self.duration > 0

    def draw(self, surface):
        if self.duration <= 0:
            return
        alpha = max(0, min(255, int(255 * (self.duration / self.max_duration))))
        font = FontCache.get(self.size, bold=self.is_crit)
        txt_surf = font.render(self.text, True, self.color)
        alpha_surf = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(txt_surf, (0, 0))
        alpha_surf.set_alpha(alpha)
        surface.blit(alpha_surf, (self.x - txt_surf.get_width() // 2, self.y - txt_surf.get_height() // 2))

class Shockwave:
    def __init__(self, x, y, max_radius=80, color=COLOR_CYAN, duration=0.4):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.color = color
        self.duration = duration
        self.max_duration = duration

    def update(self, dt):
        self.duration -= dt
        return self.duration > 0

    def draw(self, surface):
        if self.duration <= 0:
            return
        t = 1.0 - (self.duration / self.max_duration)
        cur_radius = int(t * self.max_radius)
        if cur_radius <= 2:
            return
        alpha = int(255 * (1.0 - t))
        s = pygame.Surface((cur_radius * 2 + 4, cur_radius * 2 + 4), pygame.SRCALPHA)
        r, g, b = self.color[:3]
        thickness = max(1, int(3 * (1.0 - t)))
        pygame.draw.circle(s, (r, g, b, alpha), (cur_radius + 2, cur_radius + 2), cur_radius, thickness)
        surface.blit(s, (self.x - cur_radius - 2, self.y - cur_radius - 2))

class ReactorCoreView:
    def __init__(self, cx, cy, radius=110):
        self.cx = cx
        self.cy = cy
        self.base_radius = radius
        self.scale = 1.0
        self.target_scale = 1.0
        self.rotation_1 = 0.0
        self.rotation_2 = 0.0
        self.pulse_phase = 0.0
        self.is_hovered = False

    def on_click(self):
        self.scale = 0.88  # spring compression

    def contains(self, pos):
        dist = math.hypot(pos[0] - self.cx, pos[1] - self.cy)
        return dist <= self.base_radius * self.scale

    def update(self, dt, is_hyper=False):
        # Rotation speeds
        rot_speed = 35.0 if not is_hyper else 120.0
        self.rotation_1 += rot_speed * dt
        self.rotation_2 -= rot_speed * 0.7 * dt
        self.pulse_phase += dt * (3.5 if not is_hyper else 8.0)

        # Scale spring physics
        target = 1.05 if self.is_hovered else 1.0
        if is_hyper:
            target += 0.05 * math.sin(self.pulse_phase * 2)
        self.scale += (target - self.scale) * min(1.0, 14.0 * dt)

    def draw(self, surface, is_hyper=False):
        r = self.base_radius * self.scale
        pulse = 0.08 * math.sin(self.pulse_phase)
        accent_color = COLOR_PURPLE if is_hyper else COLOR_CYAN
        glow_color = COLOR_PURPLE_GLOW if is_hyper else COLOR_CYAN

        # 1. Outer Radial Glow aura
        glow_rad = int(r * (1.4 + pulse))
        glow_surf = pygame.Surface((glow_rad * 2, glow_rad * 2), pygame.SRCALPHA)
        alpha_val = 35 if not is_hyper else 65
        pygame.draw.circle(glow_surf, (*glow_color[:3], alpha_val), (glow_rad, glow_rad), glow_rad)
        surface.blit(glow_surf, (self.cx - glow_rad, self.cy - glow_rad), special_flags=pygame.BLEND_ADD)

        # 2. Outer Ring with Arc segments and teeth
        outer_r = int(r * 1.15)
        rect_outer = pygame.Rect(self.cx - outer_r, self.cy - outer_r, outer_r * 2, outer_r * 2)
        for i in range(4):
            start_ang = math.radians(self.rotation_1 + i * 90)
            end_ang = start_ang + math.radians(65)
            pygame.draw.arc(surface, accent_color, rect_outer, start_ang, end_ang, 3)

        # 3. Middle Ring with counter-rotating markers
        mid_r = int(r * 0.85)
        for i in range(8):
            ang = math.radians(self.rotation_2 + i * 45)
            p1_x = self.cx + math.cos(ang) * (mid_r - 6)
            p1_y = self.cy + math.sin(ang) * (mid_r - 6)
            p2_x = self.cx + math.cos(ang) * (mid_r + 6)
            p2_y = self.cy + math.sin(ang) * (mid_r + 6)
            pygame.draw.line(surface, COLOR_CYAN_DIM if not is_hyper else COLOR_PURPLE, (p1_x, p1_y), (p2_x, p2_y), 2)

        # 4. Core Body
        core_r = int(r * (0.65 + pulse * 0.5))
        core_surf = pygame.Surface((core_r * 2 + 4, core_r * 2 + 4), pygame.SRCALPHA)
        # Deep inner sphere
        pygame.draw.circle(core_surf, (20, 32, 60), (core_r + 2, core_r + 2), core_r)
        # High-tech concentric layers
        pygame.draw.circle(core_surf, accent_color, (core_r + 2, core_r + 2), core_r, 3)
        pygame.draw.circle(core_surf, (255, 255, 255, 200), (core_r + 2, core_r + 2), int(core_r * 0.45))
        pygame.draw.circle(core_surf, (255, 255, 255), (core_r + 2, core_r + 2), int(core_r * 0.2))
        surface.blit(core_surf, (self.cx - core_r - 2, self.cy - core_r - 2))

class QuantumAnomalyOrb:
    def __init__(self, screen_w, screen_h):
        self.x = random.randint(100, int(screen_w * 0.45))
        self.y = random.randint(120, screen_h - 120)
        self.vx = random.choice([-1, 1]) * random.uniform(20.0, 40.0)
        self.vy = random.uniform(-20.0, 20.0)
        self.time_alive = 0.0
        self.max_life = 12.0  # seconds before despawning
        self.radius = 24
        # Random reward type
        self.reward_type = random.choice(["surge", "surge", "frenzy", "warp", "hyper", "card_leak", "card_leak"])
        self.pulse = 0.0

    def update(self, dt, bounds):
        self.time_alive += dt
        self.pulse += dt * 5.0
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce within chamber bounds
        min_x, max_x, min_y, max_y = bounds
        if self.x - self.radius < min_x:
            self.x = min_x + self.radius
            self.vx *= -1
        elif self.x + self.radius > max_x:
            self.x = max_x - self.radius
            self.vx *= -1

        if self.y - self.radius < min_y:
            self.y = min_y + self.radius
            self.vy *= -1
        elif self.y + self.radius > max_y:
            self.y = max_y - self.radius
            self.vy *= -1

        return self.time_alive < self.max_life

    def contains(self, pos):
        return math.hypot(pos[0] - self.x, pos[1] - self.y) <= self.radius + 6

    def draw(self, surface):
        alpha_fade = min(1.0, (self.max_life - self.time_alive) / 1.5)
        pulse_r = self.radius + int(3.0 * math.sin(self.pulse))
        s = pygame.Surface((pulse_r * 2 + 10, pulse_r * 2 + 10), pygame.SRCALPHA)
        center = (pulse_r + 5, pulse_r + 5)

        # Pulsing golden/magenta/emerald aura
        alpha = int(180 * alpha_fade)
        aura_color = (16, 185, 129, alpha) if self.reward_type == "card_leak" else (251, 191, 36, alpha)
        pygame.draw.circle(s, aura_color, center, pulse_r)
        pygame.draw.circle(s, (255, 255, 255, int(230 * alpha_fade)), center, int(pulse_r * 0.5))

        # Diamond / Card core
        ang = self.time_alive * 2.0
        points = []
        for i in range(4):
            a = ang + i * (math.pi / 2)
            px = center[0] + math.cos(a) * (pulse_r * 0.8)
            py = center[1] + math.sin(a) * (pulse_r * 0.8)
            points.append((px, py))
        poly_color = (0, 229, 255, int(220 * alpha_fade)) if self.reward_type == "card_leak" else (217, 70, 239, int(220 * alpha_fade))
        pygame.draw.polygon(s, poly_color, points, 2)

        surface.blit(s, (int(self.x - center[0]), int(self.y - center[1])), special_flags=pygame.BLEND_ADD)

class ToastNotification:
    def __init__(self, title, desc, icon="🏆", duration=4.0):
        self.title = title
        self.desc = desc
        self.icon = icon
        self.duration = duration
        self.max_duration = duration
        self.slide = 0.0  # 0 to 1

    def update(self, dt):
        self.duration -= dt
        if self.duration > self.max_duration - 0.5:
            # sliding in
            self.slide = min(1.0, (self.max_duration - self.duration) / 0.5)
        elif self.duration < 0.5:
            # sliding out
            self.slide = max(0.0, self.duration / 0.5)
        else:
            self.slide = 1.0
        return self.duration > 0

    def draw(self, surface, top_y=20):
        w, h = 320, 68
        x = surface.get_width() - int(w * self.slide) - 20
        y = top_y

        toast_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Background card
        pygame.draw.rect(toast_surf, (20, 28, 46, 240), (0, 0, w, h), border_radius=10)
        pygame.draw.rect(toast_surf, COLOR_GOLD, (0, 0, w, h), width=2, border_radius=10)

        # Accent bar
        pygame.draw.rect(toast_surf, COLOR_GOLD, (0, 0, 6, h), border_top_left_radius=10, border_bottom_left_radius=10)

        # Title and Description
        font_t = FontCache.get(16, bold=True)
        font_d = FontCache.get(13)
        t_surf = font_t.render(f"{self.icon} {self.title}", True, COLOR_GOLD)
        d_surf = font_d.render(self.desc, True, COLOR_WHITE)

        toast_surf.blit(t_surf, (16, 12))
        toast_surf.blit(d_surf, (16, 36))

        surface.blit(toast_surf, (x, y))

def draw_rounded_rect(surface, rect, color, border_color=None, border_width=1, radius=8):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)
