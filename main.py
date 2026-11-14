"""
CYBER CORE: QUANTUM OVERDRIVE (Кибер-Ядро: Квантовый Реактор)
A feature-rich Sci-Fi Clicker with glowing UI, particles, combo overdrive,
anomalies, procedural audio, upgrades, prestige singularity, fake donate terminal
with manual card credential input, and offline progress.
"""
import sys
import os
import math
import random
import time

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pygame

from sound_manager import SoundManager
from core_engine import (
    CoreEngine, format_number, GENERATOR_DEFS, UPGRADE_DEFS,
    ARTIFACT_DEFS, ACHIEVEMENT_DEFS, FAKE_CARDS_DATABASE, DONATE_SHOP_ITEMS
)
from ui_elements import (
    FontCache, Particle, FloatingText, Shockwave,
    ReactorCoreView, QuantumAnomalyOrb, ToastNotification,
    draw_rounded_rect,
    COLOR_BG, COLOR_PANEL, COLOR_CARD, COLOR_CARD_HOVER, COLOR_CARD_BORDER,
    COLOR_CYAN, COLOR_CYAN_DIM, COLOR_PURPLE, COLOR_PURPLE_GLOW,
    COLOR_GOLD, COLOR_GREEN, COLOR_RED, COLOR_WHITE, COLOR_MUTED, COLOR_DARK_TEXT
)

SCREEN_WIDTH = 1140
SCREEN_HEIGHT = 720
FPS = 60

class CyberCoreApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("CYBER CORE: Quantum Reactor")

        icon_path = os.path.join(BASE_DIR, "icon.png")
        if os.path.exists(icon_path):
            try:
                icon_surf = pygame.image.load(icon_path)
                pygame.display.set_icon(icon_surf)
            except Exception:
                pass

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Systems
        self.sound = SoundManager()
        self.engine = CoreEngine()

        # Visual Elements
        self.core_view = ReactorCoreView(cx=255, cy=350, radius=110)
        self.particles = []
        self.ambient_stars = [
            {
                "x": random.randint(0, SCREEN_WIDTH),
                "y": random.randint(0, SCREEN_HEIGHT),
                "speed": random.uniform(5.0, 15.0),
                "size": random.uniform(1.0, 2.5),
                "alpha": random.randint(60, 180)
            }
            for _ in range(70)
        ]
        self.floating_texts = []
        self.shockwaves = []
        self.toasts = []
        self.active_anomaly = None
        self.anomaly_timer = random.uniform(20.0, 35.0)

        # UI State
        self.current_tab = "generators"  # "generators", "upgrades", "donate", "prestige", "stats"
        self.buy_mode = "x1"             # "x1", "x10", "x25", "MAX"
        self.scroll_offsets = {
            "generators": 0.0,
            "upgrades": 0.0,
            "donate": 0.0,
            "prestige": 0.0,
            "stats": 0.0
        }
        self.max_scroll = {
            "generators": 0.0,
            "upgrades": 0.0,
            "donate": 0.0,
            "prestige": 0.0,
            "stats": 0.0
        }

        # Manual Card Input Terminal State
        self.input_card_num = ""
        self.input_card_exp = ""
        self.input_card_cvv = ""
        self.active_input_field = "num"  # "num", "exp", "cvv", or None
        self.cursor_timer = 0.0
        self.show_terminal_mode = False  # If True, shows input terminal even if active card exists

        # Modals
        self.active_modal = None         # "offline", "prestige_confirm", "reset_confirm", "card_leak", "leaks_journal"
        self.leaked_card_info = None
        self.save_notification_timer = 0.0

        # Check for offline report
        if self.engine.offline_report:
            self.active_modal = "offline"

        # Calibration Mini-Hack event
        self.calibration_active = False
        self.calibration_targets = []
        self.calibration_timer = 0.0
        self.next_calibration_time = time.time() + 90.0

    def spawn_particles(self, x, y, count=15, is_crit=False, is_hyper=False):
        has_gold_skin = "donate_gold_core" in self.engine.purchased_vip_items
        colors = [COLOR_GOLD, (255, 235, 120), (255, 255, 255)] if (is_crit or has_gold_skin) else (
            [COLOR_PURPLE, COLOR_PURPLE_GLOW, (255, 255, 255)] if is_hyper else
            [COLOR_CYAN, (180, 240, 255), (100, 200, 255)]
        )
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 8.0) if not is_crit else random.uniform(4.0, 12.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice(colors)
            size = random.uniform(2.0, 5.0)
            life = random.uniform(0.35, 0.75)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def trigger_core_click(self, mouse_pos):
        gain, is_crit = self.engine.click_core()
        self.core_view.on_click()
        self.spawn_particles(mouse_pos[0], mouse_pos[1], count=18 if not is_crit else 32, is_crit=is_crit, is_hyper=self.engine.is_hyperdrive)

        has_gold_skin = "donate_gold_core" in self.engine.purchased_vip_items
        shock_color = COLOR_GOLD if (is_crit or has_gold_skin) else (COLOR_PURPLE if self.engine.is_hyperdrive else COLOR_CYAN)
        self.shockwaves.append(Shockwave(self.core_view.cx, self.core_view.cy, max_radius=135, color=shock_color))

        txt = f"+{format_number(gain)}⚡"
        if is_crit:
            txt = f"КРИТ! +{format_number(gain)}⚡"
            self.sound.play("crit")
        else:
            self.sound.play("click")

        txt_color = COLOR_GOLD if (is_crit or has_gold_skin) else (COLOR_PURPLE_GLOW if self.engine.is_hyperdrive else COLOR_CYAN)
        self.floating_texts.append(FloatingText(mouse_pos[0], mouse_pos[1], txt, color=txt_color, size=24 if is_crit else 19, is_crit=is_crit))

        if self.engine.is_hyperdrive and self.engine.hyperdrive_timer >= self.engine.hyperdrive_duration - 0.1:
            self.sound.play("hyperdrive")
            self.toasts.append(ToastNotification("HYPERDRIVE АКТИВИРОВАН!", "Множитель перегрузки на максимуме!", icon="⚡"))

    def start_calibration(self):
        self.calibration_active = True
        self.calibration_timer = 8.0
        self.calibration_targets = []
        for i in range(3):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(60, 105)
            tx = self.core_view.cx + math.cos(ang) * dist
            ty = self.core_view.cy + math.sin(ang) * dist
            self.calibration_targets.append({"x": tx, "y": ty, "radius": 18, "clicked": False})

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.1)

            self.handle_events()
            self.update(dt)
            self.draw()

            pygame.display.flip()

        self.engine.save_game()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEWHEEL:
                if mouse_pos[0] > 520:
                    current_tab = self.current_tab
                    cur = self.scroll_offsets[current_tab]
                    max_s = self.max_scroll[current_tab]
                    new_val = cur - event.y * 38.0
                    self.scroll_offsets[current_tab] = max(0.0, min(max_s, new_val))

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_click(mouse_pos)

    def handle_keydown(self, event):
        # Keyboard typing for the manual card input terminal
        if self.current_tab == "donate" and not self.active_modal and self.active_input_field:
            if event.key == pygame.K_BACKSPACE:
                if self.active_input_field == "num":
                    # Remove last character, skip trailing spaces
                    self.input_card_num = self.input_card_num.rstrip()
                    if self.input_card_num:
                        self.input_card_num = self.input_card_num[:-1].rstrip()
                elif self.active_input_field == "exp":
                    self.input_card_exp = self.input_card_exp.rstrip()
                    if self.input_card_exp:
                        self.input_card_exp = self.input_card_exp[:-1]
                        if self.input_card_exp.endswith("/"):
                            self.input_card_exp = self.input_card_exp[:-1]
                elif self.active_input_field == "cvv":
                    if self.input_card_cvv:
                        self.input_card_cvv = self.input_card_cvv[:-1]

            elif event.key == pygame.K_TAB:
                # Cycle between input fields
                order = ["num", "exp", "cvv"]
                cur_idx = order.index(self.active_input_field)
                self.active_input_field = order[(cur_idx + 1) % len(order)]
                self.sound.play("click")

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.submit_card_credentials()

            else:
                # Text / Digit entry
                char = event.unicode
                if char:
                    if self.active_input_field == "num" and (char.isdigit() or char in " -"):
                        clean = self.input_card_num.replace(" ", "").replace("-", "")
                        if char.isdigit() and len(clean) < 16:
                            clean += char
                            # Format with space every 4 digits
                            self.input_card_num = " ".join([clean[i:i+4] for i in range(0, len(clean), 4)])

                    elif self.active_input_field == "exp" and (char.isdigit() or char == "/"):
                        clean = self.input_card_exp.replace("/", "")
                        if char.isdigit() and len(clean) < 4:
                            clean += char
                            if len(clean) >= 3:
                                self.input_card_exp = f"{clean[:2]}/{clean[2:]}"
                            elif len(clean) == 2:
                                self.input_card_exp = f"{clean}/"
                            else:
                                self.input_card_exp = clean

                    elif self.active_input_field == "cvv" and char.isdigit():
                        if len(self.input_card_cvv) < 4:
                            self.input_card_cvv += char

    def submit_card_credentials(self):
        success, card, msg = self.engine.link_card_manual(
            self.input_card_num, self.input_card_exp, self.input_card_cvv
        )
        if success:
            self.sound.play("cash")
            self.spawn_particles(700, 200, count=45, is_crit=True)
            self.toasts.append(ToastNotification("КАРТА ПРИВЯЗАНА!", msg, icon="💳", duration=5.0))
            self.show_terminal_mode = False
            # Clear input fields
            self.input_card_num = ""
            self.input_card_exp = ""
            self.input_card_cvv = ""
            self.active_input_field = None
        else:
            self.sound.play("error")
            self.toasts.append(ToastNotification("Ошибка Привязки", msg, icon="⚠️", duration=4.0))

    def handle_mouse_click(self, pos):
        if self.active_modal:
            self.handle_modal_click(pos)
            return

        # Calibration mini-game node click
        if self.calibration_active:
            clicked_any = False
            for target in self.calibration_targets:
                if not target["clicked"]:
                    if math.hypot(pos[0] - target["x"], pos[1] - target["y"]) <= target["radius"] + 5:
                        target["clicked"] = True
                        clicked_any = True
                        self.sound.play("buy")
                        self.spawn_particles(target["x"], target["y"], count=15, is_crit=True)
                        break
            if clicked_any:
                if all(t["clicked"] for t in self.calibration_targets):
                    self.calibration_active = False
                    self.engine.active_buffs["eps_mult"]["factor"] = 2.0
                    self.engine.active_buffs["eps_mult"]["time_left"] = 45.0
                    self.sound.play("achievement")
                    self.toasts.append(ToastNotification("Синхронизация Успешна!", "+100% ко всему EPS на 45 секунд!", icon="🎯"))
                    self.next_calibration_time = time.time() + random.uniform(90.0, 150.0)
                return

        # Anomaly Orb Click
        if self.active_anomaly and self.active_anomaly.contains(pos):
            reward_type = self.active_anomaly.reward_type
            res_type, res_data = self.engine.apply_anomaly_reward(reward_type)

            if res_type == "card_leak":
                self.sound.play("cash")
                self.spawn_particles(pos[0], pos[1], count=40, is_crit=True)
                self.active_modal = "card_leak"
                self.leaked_card_info = res_data
            else:
                self.sound.play("anomaly_catch")
                self.spawn_particles(pos[0], pos[1], count=35, is_crit=True)
                self.floating_texts.append(FloatingText(pos[0], pos[1], "АНОМАЛИЯ ПОЙМАНА!", color=COLOR_GOLD, size=22, is_crit=True))
                self.toasts.append(ToastNotification("Квантовая Аномалия", res_data, icon="🌌"))

            self.active_anomaly = None
            self.anomaly_timer = random.uniform(25.0, 45.0)
            return

        # Top Utility Buttons (Audio toggle, Save)
        if 1085 <= pos[0] <= 1125 and 14 <= pos[1] <= 46:
            new_state = self.sound.toggle()
            status_text = "Звук: ВКЛ" if new_state else "Звук: ВЫКЛ"
            self.toasts.append(ToastNotification("Настройки Аудио", status_text, icon="🔊" if new_state else "🔇", duration=2.0))
            return

        if 1045 <= pos[0] <= 1080 and 14 <= pos[1] <= 46:
            self.engine.save_game()
            self.save_notification_timer = 2.0
            self.sound.play("buy")
            return

        # Left Reactor Core Click
        if pos[0] < 520:
            if self.core_view.contains(pos):
                self.trigger_core_click(pos)
                return

            if not self.calibration_active and time.time() >= self.next_calibration_time:
                if 40 <= pos[0] <= 470 and 645 <= pos[1] <= 680:
                    self.start_calibration()
                    self.sound.play("buy")
                    return

        # Right Panel Clicks
        if pos[0] >= 520:
            # 5 Tab buttons
            tab_defs = [
                ("generators", "⚡ Генераторы", 525, 105),
                ("upgrades", "🧪 Апгрейды", 634, 98),
                ("donate", "💳 Донат", 736, 94),
                ("prestige", "🌌 Престиж", 834, 98),
                ("stats", "📊 Инфо", 936, 92)
            ]
            for tab_id, _, tx, tw in tab_defs:
                if tx <= pos[0] <= tx + tw and 15 <= pos[1] <= 55:
                    self.current_tab = tab_id
                    self.sound.play("click")
                    return

            # Multiplier bar buttons (for Generators tab)
            if self.current_tab == "generators":
                mult_defs = [
                    ("x1", 530, 60),
                    ("x10", 600, 60),
                    ("x25", 670, 60),
                    ("MAX", 740, 70)
                ]
                for mode, mx, mw in mult_defs:
                    if mx <= pos[0] <= mx + mw and 68 <= pos[1] <= 102:
                        self.buy_mode = mode
                        self.sound.play("click")
                        return

            # Handle tab-specific items
            if self.current_tab == "generators" and 114 <= pos[1] <= 705:
                self.handle_generator_click(pos)
            elif self.current_tab == "upgrades" and 70 <= pos[1] <= 705:
                self.handle_upgrade_click(pos)
            elif self.current_tab == "donate":
                self.handle_donate_click(pos)
            elif self.current_tab == "prestige":
                self.handle_prestige_click(pos)
            elif self.current_tab == "stats":
                self.handle_stats_click(pos)

    def handle_generator_click(self, pos):
        offset = self.scroll_offsets["generators"]
        card_y = 114 - offset
        card_w = 580
        card_h = 76

        for g in GENERATOR_DEFS:
            gid = g["id"]
            if card_y + card_h > 114 and card_y < 705:
                btn_rect = pygame.Rect(970, card_y + 16, 130, 44)
                if btn_rect.collidepoint(pos):
                    success, count, cost = self.engine.buy_generator(gid, self.buy_mode)
                    if success:
                        self.sound.play("buy")
                        self.spawn_particles(pos[0], pos[1], count=10)
                        self.floating_texts.append(FloatingText(pos[0], pos[1], f"+{count} {g['tag']}", color=COLOR_GREEN, size=18))
                    else:
                        self.sound.play("error")
                    return
            card_y += card_h + 10

    def handle_upgrade_click(self, pos):
        offset = self.scroll_offsets["upgrades"]
        card_y = 75 - offset
        card_w = 580
        card_h = 78

        for upg in UPGRADE_DEFS:
            uid = upg["id"]
            if card_y + card_h > 70 and card_y < 705:
                btn_rect = pygame.Rect(970, card_y + 18, 130, 42)
                if btn_rect.collidepoint(pos):
                    if uid not in self.engine.purchased_upgrades:
                        if self.engine.buy_upgrade(uid):
                            self.sound.play("achievement")
                            self.spawn_particles(pos[0], pos[1], count=18, is_crit=True)
                            self.toasts.append(ToastNotification("Технология Изучена!", upg["name"], icon="🧪"))
                        else:
                            self.sound.play("error")
                    return
            card_y += card_h + 10

    def handle_donate_click(self, pos):
        active_card = self.engine.get_active_card()
        has_active_card = (active_card is not None) and (not self.show_terminal_mode)

        if has_active_card:
            # Active Card Mode: y: 68 to 175 is card
            # Switcher and Link Another button at y: 185 to 215
            # Prev Card: x: 535 to 635
            if 535 <= pos[0] <= 635 and 185 <= pos[1] <= 217:
                self.engine.cycle_card(-1)
                self.sound.play("click")
                return

            # Next Card: x: 745 to 845
            if 745 <= pos[0] <= 845 and 185 <= pos[1] <= 217:
                self.engine.cycle_card(1)
                self.sound.play("click")
                return

            # Button to open manual terminal input: x: 860 to 1095
            if 860 <= pos[0] <= 1095 and 185 <= pos[1] <= 217:
                self.show_terminal_mode = True
                self.active_input_field = "num"
                self.sound.play("click")
                return

            # Donate items purchases: y: 225 to 705
            if 225 <= pos[1] <= 705:
                offset = self.scroll_offsets["donate"]
                item_y = 225 - offset
                item_h = 74

                for item in DONATE_SHOP_ITEMS:
                    iid = item["id"]
                    if item_y + item_h > 225 and item_y < 705:
                        btn_rect = pygame.Rect(965, item_y + 16, 135, 42)
                        if btn_rect.collidepoint(pos):
                            success, msg = self.engine.buy_vip_item(iid)
                            if success:
                                self.sound.play("cash")
                                self.spawn_particles(pos[0], pos[1], count=30, is_crit=True)
                                self.floating_texts.append(FloatingText(pos[0], pos[1], f"-${item['price']:.2f}", color=COLOR_RED, size=20))
                                self.toasts.append(ToastNotification("VIP Оплата Успешна!", msg, icon="💳", duration=4.0))
                            else:
                                self.sound.play("error")
                                self.toasts.append(ToastNotification("Ошибка Оплаты", msg, icon="⚠️", duration=3.0))
                            return
                    item_y += item_h + 8

        else:
            # Manual Terminal Input Mode (y: 68 to 220)
            # Field 1: Card Number (x: 545, y: 100, w: 320, h: 36)
            if 545 <= pos[0] <= 865 and 100 <= pos[1] <= 136:
                self.active_input_field = "num"
                self.sound.play("click")
                return

            # Field 2: Expiry (x: 875, y: 100, w: 105, h: 36)
            if 875 <= pos[0] <= 980 and 100 <= pos[1] <= 136:
                self.active_input_field = "exp"
                self.sound.play("click")
                return

            # Field 3: CVV (x: 990, y: 100, w: 105, h: 36)
            if 990 <= pos[0] <= 1095 and 100 <= pos[1] <= 136:
                self.active_input_field = "cvv"
                self.sound.play("click")
                return

            # Button: [💳 ПРИВЯЗАТЬ КАРТУ] (x: 545, y: 148, w: 260, h: 38)
            if 545 <= pos[0] <= 805 and 148 <= pos[1] <= 186:
                self.submit_card_credentials()
                return

            # Button: [📋 Журнал Утечек] (x: 815, y: 148, w: 280, h: 38)
            if 815 <= pos[0] <= 1095 and 148 <= pos[1] <= 186:
                self.active_modal = "leaks_journal"
                self.sound.play("click")
                return

            # If user has unlocked cards and wants to return to active card view
            if self.engine.get_unlocked_cards() and 545 <= pos[0] <= 780 and 192 <= pos[1] <= 218:
                self.show_terminal_mode = False
                self.sound.play("click")
                return

            # Donate items purchases (locked state warning or direct purchase attempt)
            if 225 <= pos[1] <= 705:
                offset = self.scroll_offsets["donate"]
                item_y = 225 - offset
                item_h = 74

                for item in DONATE_SHOP_ITEMS:
                    if item_y + item_h > 225 and item_y < 705:
                        btn_rect = pygame.Rect(965, item_y + 16, 135, 42)
                        if btn_rect.collidepoint(pos):
                            self.sound.play("error")
                            self.toasts.append(ToastNotification("Нет Карты!", "Сначала введите реквизиты перехваченной карты выше!", icon="⚠️", duration=3.0))
                            return
                    item_y += item_h + 8

    def handle_prestige_click(self, pos):
        if 550 <= pos[0] <= 1090 and 310 <= pos[1] <= 364:
            if self.engine.can_prestige():
                self.active_modal = "prestige_confirm"
                self.sound.play("click")
            else:
                self.sound.play("error")
            return

        art_y = 440
        for art in ARTIFACT_DEFS:
            aid = art["id"]
            btn_rect = pygame.Rect(970, art_y + 14, 120, 40)
            if btn_rect.collidepoint(pos):
                if aid not in self.engine.purchased_artifacts:
                    if self.engine.buy_artifact(aid):
                        self.sound.play("achievement")
                        self.spawn_particles(pos[0], pos[1], count=25, is_crit=True)
                        self.toasts.append(ToastNotification("Реликвия Активирована!", art["name"], icon="🌌"))
                    else:
                        self.sound.play("error")
                return
            art_y += 66

    def handle_stats_click(self, pos):
        if 550 <= pos[0] <= 770 and 640 <= pos[1] <= 682:
            self.active_modal = "reset_confirm"
            self.sound.play("click")

    def handle_modal_click(self, pos):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        if self.active_modal == "offline":
            if cx - 80 <= pos[0] <= cx + 80 and cy + 80 <= pos[1] <= cy + 122:
                self.active_modal = None
                self.sound.play("buy")

        elif self.active_modal == "card_leak":
            # Leak dialog: OK button (x: cx - 110, y: cy + 115, w: 220, h: 42)
            if cx - 110 <= pos[0] <= cx + 110 and cy + 115 <= pos[1] <= cy + 157:
                # Pre-fill input fields with intercepted credentials so user can inspect or link!
                if self.leaked_card_info:
                    self.input_card_num = self.leaked_card_info["number"]
                    self.input_card_exp = self.leaked_card_info["exp"]
                    self.input_card_cvv = self.leaked_card_info["cvv"]
                self.current_tab = "donate"
                self.show_terminal_mode = True
                self.active_modal = None
                self.sound.play("click")

        elif self.active_modal == "leaks_journal":
            # Journal dialog: close button (x: cx - 80, y: cy + 170, w: 160, h: 40)
            if cx - 80 <= pos[0] <= cx + 80 and cy + 170 <= pos[1] <= cy + 210:
                self.active_modal = None
                self.sound.play("click")
                return

            # Check if clicked any [Вставить данные] button in journal rows
            jy = cy - 130
            for cid in self.engine.intercepted_leaks:
                c = next((item for item in FAKE_CARDS_DATABASE if item["id"] == cid), None)
                if c:
                    btn_paste = pygame.Rect(cx + 140, jy + 8, 120, 32)
                    if btn_paste.collidepoint(pos):
                        self.input_card_num = c["number"]
                        self.input_card_exp = c["exp"]
                        self.input_card_cvv = c["cvv"]
                        self.active_modal = None
                        self.current_tab = "donate"
                        self.show_terminal_mode = True
                        self.sound.play("click")
                        self.toasts.append(ToastNotification("Данные Подставлены", f"Реквизиты карты {c['name']} внесены в поля!", icon="📋"))
                        return
                    jy += 48

        elif self.active_modal == "prestige_confirm":
            if cx - 160 <= pos[0] <= cx - 20 and cy + 60 <= pos[1] <= cy + 102:
                success, gain = self.engine.trigger_prestige()
                if success:
                    self.sound.play("hyperdrive")
                    self.spawn_particles(cx, cy, count=50, is_crit=True)
                    self.toasts.append(ToastNotification("Квантовая Сингулярность!", f"+{gain}✦ Темной Материи получено!", icon="🌌"))
                self.active_modal = None
            elif cx + 20 <= pos[0] <= cx + 160 and cy + 60 <= pos[1] <= cy + 102:
                self.active_modal = None
                self.sound.play("click")

        elif self.active_modal == "reset_confirm":
            if cx - 160 <= pos[0] <= cx - 20 and cy + 60 <= pos[1] <= cy + 102:
                self.engine.reset_save()
                self.active_modal = None
                self.sound.play("error")
                self.toasts.append(ToastNotification("Сброс Данных", "Прогресс станции сброшен до нуля.", icon="⚠️"))
            elif cx + 20 <= pos[0] <= cx + 160 and cy + 60 <= pos[1] <= cy + 102:
                self.active_modal = None
                self.sound.play("click")

    def update(self, dt):
        new_achs = self.engine.update(dt)
        for ach in new_achs:
            self.sound.play("achievement")
            self.toasts.append(ToastNotification("ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!", f"{ach['name']}: {ach['desc']}", icon="🏆", duration=5.0))

        # Cursor blink timer for text fields
        self.cursor_timer = (self.cursor_timer + dt) % 1.0

        m_pos = pygame.mouse.get_pos()
        self.core_view.is_hovered = self.core_view.contains(m_pos) and m_pos[0] < 520
        self.core_view.update(dt, is_hyper=self.engine.is_hyperdrive)

        for star in self.ambient_stars:
            star["y"] -= star["speed"] * dt
            if star["y"] < 0:
                star["y"] = SCREEN_HEIGHT
                star["x"] = random.randint(0, SCREEN_WIDTH)

        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]
        self.shockwaves = [sw for sw in self.shockwaves if sw.update(dt)]
        self.toasts = [t for t in self.toasts if t.update(dt)]

        if self.active_anomaly:
            chamber_bounds = (40, 480, 140, 540)
            if not self.active_anomaly.update(dt, chamber_bounds):
                self.active_anomaly = None
                self.anomaly_timer = random.uniform(25.0, 45.0)
        else:
            self.anomaly_timer -= dt
            if self.anomaly_timer <= 0:
                self.active_anomaly = QuantumAnomalyOrb(SCREEN_WIDTH, SCREEN_HEIGHT)
                if self.active_anomaly.reward_type == "card_leak":
                    self.sound.play("cash")
                    self.toasts.append(ToastNotification("УТЕЧКА ДАННЫХ!", "В реакторе обнаружены реквизиты банковской карты! Поймайте их!", icon="💳", duration=5.0))
                else:
                    self.sound.play("anomaly_spawn")
                    self.toasts.append(ToastNotification("КВАНТОВАЯ АНОМАЛИЯ!", "В реакторе обнаружен разлом энергии! Кликните по нему!", icon="✨", duration=4.0))

        if self.save_notification_timer > 0:
            self.save_notification_timer = max(0.0, self.save_notification_timer - dt)

        if self.calibration_active:
            self.calibration_timer -= dt
            if self.calibration_timer <= 0:
                self.calibration_active = False
                self.sound.play("error")
                self.toasts.append(ToastNotification("Калибровка Провалена", "Время вышло. Попробуйте снова позже.", icon="❌"))
                self.next_calibration_time = time.time() + 60.0

        self.calculate_max_scroll()

    def calculate_max_scroll(self):
        self.max_scroll["generators"] = max(0.0, len(GENERATOR_DEFS) * 86 - 570)
        self.max_scroll["upgrades"] = max(0.0, len(UPGRADE_DEFS) * 88 - 570)
        self.max_scroll["donate"] = max(0.0, len(DONATE_SHOP_ITEMS) * 82 - 470)
        self.max_scroll["prestige"] = max(0.0, 720 - 570)
        self.max_scroll["stats"] = max(0.0, 700 - 570)

    def draw(self):
        self.screen.fill(COLOR_BG)

        for star in self.ambient_stars:
            surf = pygame.Surface((int(star["size"] * 2), int(star["size"] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (200, 230, 255, star["alpha"]), (int(star["size"]), int(star["size"])), int(star["size"]))
            self.screen.blit(surf, (int(star["x"]), int(star["y"])))

        self.draw_left_panel()
        self.draw_right_panel()

        for sw in self.shockwaves:
            sw.draw(self.screen)
        for p in self.particles:
            p.draw(self.screen)
        for ft in self.floating_texts:
            ft.draw(self.screen)

        if self.active_anomaly:
            self.active_anomaly.draw(self.screen)

        toast_y = 20
        for toast in self.toasts:
            toast.draw(self.screen, top_y=toast_y)
            toast_y += 74

        if self.active_modal:
            self.draw_modal()

        if self.engine.is_hyperdrive:
            pulse = abs(math.sin(time.time() * 8.0))
            border_alpha = int(90 + pulse * 140)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (*COLOR_PURPLE[:3], border_alpha), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), width=6)
            self.screen.blit(overlay, (0, 0))

    def draw_left_panel(self):
        header_rect = pygame.Rect(20, 16, 480, 110)
        draw_rounded_rect(self.screen, header_rect, COLOR_PANEL, border_color=COLOR_CARD_BORDER, radius=12)

        font_sub = FontCache.get(13, bold=True)
        status_text = "● РЕАКТОР В РЕЖИМЕ HYPERDRIVE" if self.engine.is_hyperdrive else "● РЕАКТОР АКТИВЕН"
        status_color = COLOR_PURPLE_GLOW if self.engine.is_hyperdrive else COLOR_GREEN
        self.screen.blit(font_sub.render(status_text, True, status_color), (36, 26))

        font_big = FontCache.get(34, bold=True)
        energy_str = f"{format_number(self.engine.energy)} ⚡"
        txt_energy = font_big.render(energy_str, True, COLOR_CYAN if not self.engine.is_hyperdrive else COLOR_PURPLE_GLOW)
        self.screen.blit(txt_energy, (36, 44))

        font_stat = FontCache.get(14)
        eps_str = f"Генерация: +{format_number(self.engine.get_eps())}/сек"
        click_pow = self.engine.get_base_click_power() + self.engine.get_synergy_click_bonus()
        click_str = f"Клик: {format_number(click_pow)}⚡"
        if self.engine.dark_matter > 0:
            click_str += f" | {int(self.engine.dark_matter)}✦ ТМ"

        self.screen.blit(font_stat.render(eps_str, True, COLOR_GOLD), (36, 88))
        self.screen.blit(font_stat.render(click_str, True, COLOR_MUTED), (265, 88))

        chamber_rect = pygame.Rect(20, 136, 480, 410)
        draw_rounded_rect(self.screen, chamber_rect, (12, 17, 28), border_color=(25, 38, 62), radius=14)

        self.core_view.draw(self.screen, is_hyper=self.engine.is_hyperdrive)

        if self.calibration_active:
            for target in self.calibration_targets:
                if not target["clicked"]:
                    pulse_r = target["radius"] + int(3 * math.sin(time.time() * 10))
                    surf = pygame.Surface((pulse_r * 2 + 6, pulse_r * 2 + 6), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (*COLOR_GOLD, 220), (pulse_r + 3, pulse_r + 3), pulse_r, width=3)
                    pygame.draw.circle(surf, (255, 255, 255, 240), (pulse_r + 3, pulse_r + 3), 6)
                    self.screen.blit(surf, (int(target["x"] - pulse_r - 3), int(target["y"] - pulse_r - 3)))

        bar_bg_rect = pygame.Rect(40, 560, 440, 26)
        draw_rounded_rect(self.screen, bar_bg_rect, (18, 24, 38), border_color=(38, 52, 78), radius=8)

        ratio = self.engine.combo_meter / 100.0 if not self.engine.is_hyperdrive else (self.engine.hyperdrive_timer / self.engine.hyperdrive_duration)
        fill_w = max(4, int(436 * max(0.0, min(1.0, ratio))))
        fill_color = COLOR_PURPLE if self.engine.is_hyperdrive else (COLOR_GOLD if ratio > 0.6 else COLOR_CYAN)
        fill_rect = pygame.Rect(42, 562, fill_w, 22)
        draw_rounded_rect(self.screen, fill_rect, fill_color, radius=6)

        font_bar = FontCache.get(12, bold=True)
        if self.engine.is_hyperdrive:
            lbl = f"⚡⚡ HYPERDRIVE: {self.engine.get_combo_multiplier():.1f}x [{self.engine.hyperdrive_timer:.1f}s] ⚡⚡"
            txt_bar = font_bar.render(lbl, True, (255, 255, 255))
        else:
            lbl = f"ПЕРЕГРУЗКА: {self.engine.get_combo_multiplier():.1f}x  ({int(self.engine.combo_meter)}%)"
            txt_bar = font_bar.render(lbl, True, (255, 255, 255))
        self.screen.blit(txt_bar, (bar_bg_rect.centerx - txt_bar.get_width() // 2, bar_bg_rect.centery - txt_bar.get_height() // 2))

        if not self.calibration_active:
            time_until_cal = max(0, int(self.next_calibration_time - time.time()))
            cal_btn_rect = pygame.Rect(40, 600, 440, 36)
            is_cal_ready = time_until_cal == 0
            cal_bg = (30, 45, 75) if is_cal_ready else (18, 24, 36)
            cal_border = COLOR_CYAN if is_cal_ready else (35, 45, 65)
            draw_rounded_rect(self.screen, cal_btn_rect, cal_bg, border_color=cal_border, radius=8)

            font_cal = FontCache.get(13, bold=is_cal_ready)
            if is_cal_ready:
                txt_c = font_cal.render("🎯 Калибровка Ядра Готова! (Кликните для буста +100% EPS)", True, COLOR_CYAN)
            else:
                txt_c = font_cal.render(f"Синхронизация охлаждения: доступна через {time_until_cal} сек", True, COLOR_DARK_TEXT)
            self.screen.blit(txt_c, (cal_btn_rect.centerx - txt_c.get_width() // 2, cal_btn_rect.centery - txt_c.get_height() // 2))
        else:
            prompt_rect = pygame.Rect(40, 600, 440, 36)
            draw_rounded_rect(self.screen, prompt_rect, (45, 30, 60), border_color=COLOR_GOLD, radius=8)
            font_p = FontCache.get(13, bold=True)
            txt_p = font_p.render(f"Кликните 3 светящиеся точки на ядре! [{self.calibration_timer:.1f}с]", True, COLOR_GOLD)
            self.screen.blit(txt_p, (prompt_rect.centerx - txt_p.get_width() // 2, prompt_rect.centery - txt_p.get_height() // 2))

        buff_y = 648
        for b_key, b_val in self.engine.active_buffs.items():
            if b_val["time_left"] > 0:
                badge_rect = pygame.Rect(40, buff_y, 440, 24)
                draw_rounded_rect(self.screen, badge_rect, (35, 20, 45), border_color=COLOR_PURPLE, radius=6)
                font_b = FontCache.get(12, bold=True)
                txt_b = font_b.render(f"✨ {b_val['name']}: {b_val['time_left']:.1f}s", True, COLOR_PURPLE_GLOW)
                self.screen.blit(txt_b, (badge_rect.centerx - txt_b.get_width() // 2, badge_rect.centery - txt_b.get_height() // 2))
                buff_y += 28

    def draw_right_panel(self):
        panel_rect = pygame.Rect(515, 16, 605, 688)
        draw_rounded_rect(self.screen, panel_rect, COLOR_PANEL, border_color=COLOR_CARD_BORDER, radius=12)

        tab_defs = [
            ("generators", "⚡ Генераторы", 525, 105),
            ("upgrades", "🧪 Апгрейды", 634, 98),
            ("donate", "💳 Донат", 736, 94),
            ("prestige", "🌌 Престиж", 834, 98),
            ("stats", "📊 Инфо", 936, 92)
        ]

        m_pos = pygame.mouse.get_pos()
        for tab_id, tab_label, tx, tw in tab_defs:
            is_active = self.current_tab == tab_id
            rect = pygame.Rect(tx, 15, tw, 40)
            is_hover = rect.collidepoint(m_pos)

            bg_c = COLOR_CARD if is_active else ((28, 38, 60) if is_hover else (18, 25, 40))
            border_c = COLOR_CYAN if is_active else ((45, 62, 95) if is_hover else (30, 40, 60))
            draw_rounded_rect(self.screen, rect, bg_c, border_color=border_c, radius=8)

            font_tab = FontCache.get(13, bold=is_active)
            text_c = COLOR_WHITE if is_active else COLOR_MUTED
            txt_t = font_tab.render(tab_label, True, text_c)
            self.screen.blit(txt_t, (rect.centerx - txt_t.get_width() // 2, rect.centery - txt_t.get_height() // 2))

        # Save button
        save_rect = pygame.Rect(1040, 15, 34, 40)
        draw_rounded_rect(self.screen, save_rect, (24, 34, 52), border_color=(45, 62, 95), radius=8)
        font_icon = FontCache.get(16)
        save_icon = font_icon.render("💾", True, COLOR_WHITE if self.save_notification_timer == 0 else COLOR_GREEN)
        self.screen.blit(save_icon, (save_rect.centerx - save_icon.get_width() // 2, save_rect.centery - save_icon.get_height() // 2))

        # Audio toggle button
        snd_rect = pygame.Rect(1080, 15, 34, 40)
        draw_rounded_rect(self.screen, snd_rect, (24, 34, 52), border_color=(45, 62, 95), radius=8)
        snd_txt = font_icon.render("🔊" if self.sound.enabled else "🔇", True, COLOR_WHITE)
        self.screen.blit(snd_txt, (snd_rect.centerx - snd_txt.get_width() // 2, snd_rect.centery - snd_txt.get_height() // 2))

        # Tab Content
        if self.current_tab == "generators":
            self.draw_generators_tab()
        elif self.current_tab == "upgrades":
            self.draw_upgrades_tab()
        elif self.current_tab == "donate":
            self.draw_donate_tab()
        elif self.current_tab == "prestige":
            self.draw_prestige_tab()
        elif self.current_tab == "stats":
            self.draw_stats_tab()

    def draw_generators_tab(self):
        mult_defs = [
            ("x1", 530, 60),
            ("x10", 600, 60),
            ("x25", 670, 60),
            ("MAX", 740, 70)
        ]
        m_pos = pygame.mouse.get_pos()
        for mode, mx, mw in mult_defs:
            is_sel = self.buy_mode == mode
            rect = pygame.Rect(mx, 68, mw, 34)
            is_hover = rect.collidepoint(m_pos)
            bg_c = (0, 160, 180) if is_sel else ((35, 48, 75) if is_hover else (22, 30, 48))
            border_c = COLOR_CYAN if is_sel else (40, 55, 85)
            draw_rounded_rect(self.screen, rect, bg_c, border_color=border_c, radius=6)
            font_m = FontCache.get(13, bold=is_sel)
            txt_m = font_m.render(mode, True, COLOR_WHITE)
            self.screen.blit(txt_m, (rect.centerx - txt_m.get_width() // 2, rect.centery - txt_m.get_height() // 2))

        font_info = FontCache.get(13)
        total_eps_str = f"Всего выработка: +{format_number(self.engine.get_eps())}/сек"
        self.screen.blit(font_info.render(total_eps_str, True, COLOR_GOLD), (830, 76))

        viewport_rect = pygame.Rect(525, 114, 585, 580)
        self.screen.set_clip(viewport_rect)

        offset = self.scroll_offsets["generators"]
        card_y = 114 - offset
        card_w = 575
        card_h = 76

        for g in GENERATOR_DEFS:
            gid = g["id"]
            state = self.engine.generators[gid]
            count = state["count"]
            cost, buy_count = self.engine.get_generator_cost(gid, self.buy_mode)
            can_afford = self.engine.energy >= cost and buy_count > 0

            if card_y + card_h > 114 and card_y < 705:
                card_rect = pygame.Rect(530, card_y, card_w, card_h)
                is_hover = card_rect.collidepoint(m_pos)

                card_bg = COLOR_CARD_HOVER if is_hover else COLOR_CARD
                border_col = COLOR_CYAN_DIM if can_afford else COLOR_CARD_BORDER
                draw_rounded_rect(self.screen, card_rect, card_bg, border_color=border_col, radius=8)

                tag_rect = pygame.Rect(542, card_y + 16, 52, 44)
                draw_rounded_rect(self.screen, tag_rect, (16, 22, 36), border_color=(35, 48, 75), radius=6)
                font_tag = FontCache.get(11, bold=True)
                txt_tag = font_tag.render(g["tag"], True, COLOR_CYAN)
                self.screen.blit(txt_tag, (tag_rect.centerx - txt_tag.get_width() // 2, tag_rect.centery - txt_tag.get_height() // 2))

                font_name = FontCache.get(15, bold=True)
                txt_name = font_name.render(g["name"], True, COLOR_WHITE)
                self.screen.blit(txt_name, (604, card_y + 14))

                font_desc = FontCache.get(12)
                cur_gen_eps = count * g["base_eps"] * state["multiplier"] * self.engine.get_global_multiplier()
                desc_str = f"Уровень: {count}  |  Дает: +{format_number(cur_gen_eps)}/с (+{format_number(g['base_eps'] * state['multiplier'])}/шт)"
                txt_desc = font_desc.render(desc_str, True, COLOR_MUTED)
                self.screen.blit(txt_desc, (604, card_y + 42))

                btn_rect = pygame.Rect(970, card_y + 16, 125, 44)
                btn_hover = btn_rect.collidepoint(m_pos)
                btn_bg = ((20, 160, 90) if btn_hover else (16, 130, 75)) if can_afford else (30, 36, 48)
                btn_border = COLOR_GREEN if can_afford else (50, 60, 80)
                draw_rounded_rect(self.screen, btn_rect, btn_bg, border_color=btn_border, radius=8)

                font_btn_t = FontCache.get(12, bold=True)
                buy_lbl = f"КУПИТЬ ({buy_count})" if buy_count > 0 else "КУПИТЬ (0)"
                txt_btn_t = font_btn_t.render(buy_lbl, True, COLOR_WHITE if can_afford else COLOR_MUTED)
                self.screen.blit(txt_btn_t, (btn_rect.centerx - txt_btn_t.get_width() // 2, btn_rect.y + 6))

                font_btn_c = FontCache.get(12, bold=True)
                cost_lbl = f"{format_number(cost)} ⚡"
                txt_btn_c = font_btn_c.render(cost_lbl, True, COLOR_GOLD if can_afford else COLOR_DARK_TEXT)
                self.screen.blit(txt_btn_c, (btn_rect.centerx - txt_btn_c.get_width() // 2, btn_rect.y + 24))

            card_y += card_h + 10

        self.screen.set_clip(None)
        self.draw_scrollbar("generators", 525, 114, 580)

    def draw_upgrades_tab(self):
        viewport_rect = pygame.Rect(525, 70, 585, 624)
        self.screen.set_clip(viewport_rect)

        m_pos = pygame.mouse.get_pos()
        offset = self.scroll_offsets["upgrades"]
        card_y = 75 - offset
        card_w = 575
        card_h = 78

        for upg in UPGRADE_DEFS:
            uid = upg["id"]
            is_bought = uid in self.engine.purchased_upgrades
            can_afford = self.engine.energy >= upg["cost"] and not is_bought

            if card_y + card_h > 70 and card_y < 705:
                card_rect = pygame.Rect(530, card_y, card_w, card_h)
                is_hover = card_rect.collidepoint(m_pos)

                card_bg = (18, 28, 42) if is_bought else (COLOR_CARD_HOVER if is_hover else COLOR_CARD)
                border_col = (40, 70, 60) if is_bought else (COLOR_CYAN if can_afford else COLOR_CARD_BORDER)
                draw_rounded_rect(self.screen, card_rect, card_bg, border_color=border_col, radius=8)

                icon_rect = pygame.Rect(542, card_y + 16, 48, 46)
                draw_rounded_rect(self.screen, icon_rect, (16, 22, 36), border_color=(35, 48, 75), radius=6)
                font_ic = FontCache.get(18)
                ic_text = font_ic.render("✓" if is_bought else "⚡", True, COLOR_GREEN if is_bought else COLOR_CYAN)
                self.screen.blit(ic_text, (icon_rect.centerx - ic_text.get_width() // 2, icon_rect.centery - ic_text.get_height() // 2))

                font_name = FontCache.get(15, bold=True)
                txt_name = font_name.render(upg["name"], True, COLOR_WHITE if not is_bought else COLOR_MUTED)
                self.screen.blit(txt_name, (600, card_y + 14))

                font_desc = FontCache.get(12)
                txt_desc = font_desc.render(upg["desc"], True, COLOR_GOLD if not is_bought else (100, 120, 140))
                self.screen.blit(txt_desc, (600, card_y + 42))

                btn_rect = pygame.Rect(970, card_y + 18, 125, 42)
                if is_bought:
                    draw_rounded_rect(self.screen, btn_rect, (18, 35, 28), border_color=(30, 80, 50), radius=8)
                    font_b = FontCache.get(12, bold=True)
                    txt_b = font_b.render("ИЗУЧЕНО", True, COLOR_GREEN)
                    self.screen.blit(txt_b, (btn_rect.centerx - txt_b.get_width() // 2, btn_rect.centery - txt_b.get_height() // 2))
                else:
                    btn_hover = btn_rect.collidepoint(m_pos)
                    btn_bg = ((18, 140, 180) if btn_hover else (12, 110, 145)) if can_afford else (30, 36, 48)
                    btn_border = COLOR_CYAN if can_afford else (50, 60, 80)
                    draw_rounded_rect(self.screen, btn_rect, btn_bg, border_color=btn_border, radius=8)

                    font_btn_t = FontCache.get(12, bold=True)
                    txt_btn_t = font_btn_t.render("ИЗУЧИТЬ", True, COLOR_WHITE if can_afford else COLOR_MUTED)
                    self.screen.blit(txt_btn_t, (btn_rect.centerx - txt_btn_t.get_width() // 2, btn_rect.y + 6))

                    font_btn_c = FontCache.get(12, bold=True)
                    cost_lbl = f"{format_number(upg['cost'])} ⚡"
                    txt_btn_c = font_btn_c.render(cost_lbl, True, COLOR_GOLD if can_afford else COLOR_DARK_TEXT)
                    self.screen.blit(txt_btn_c, (btn_rect.centerx - txt_btn_c.get_width() // 2, btn_rect.y + 22))

            card_y += card_h + 10

        self.screen.set_clip(None)
        self.draw_scrollbar("upgrades", 525, 70, 624)

    def draw_donate_tab(self):
        m_pos = pygame.mouse.get_pos()
        active_card = self.engine.get_active_card()
        has_card = (active_card is not None) and (not self.show_terminal_mode)

        if has_card:
            # 1. Active Virtual Credit Card Widget
            card_rect = pygame.Rect(535, 68, 565, 110)
            bg_col = active_card["color"]
            accent_col = active_card["accent"]
            draw_rounded_rect(self.screen, card_rect, bg_col, border_color=accent_col, border_width=2, radius=12)

            # Microchip Icon
            chip_rect = pygame.Rect(552, 78, 36, 26)
            draw_rounded_rect(self.screen, chip_rect, (220, 180, 50), border_color=(170, 130, 30), radius=4)

            # Network Logo
            font_net = FontCache.get(13, bold=True)
            txt_net = font_net.render(active_card["type"], True, accent_col)
            self.screen.blit(txt_net, (card_rect.right - 20 - txt_net.get_width(), 78))

            # Card Title & Number
            font_ct = FontCache.get(14, bold=True)
            self.screen.blit(font_ct.render(active_card["name"], True, COLOR_WHITE), (600, 78))

            font_num = FontCache.get(17, bold=True)
            self.screen.blit(font_num.render(active_card["number"], True, COLOR_WHITE), (552, 112))

            # Holder & Balance
            font_hold = FontCache.get(11)
            holder_str = f"ВЛАДЕЛЕЦ: {active_card['holder']}   EXP: {active_card['exp']}   CVV: {active_card['cvv']}"
            self.screen.blit(font_hold.render(holder_str, True, COLOR_MUTED), (552, 138))

            cur_bal = self.engine.player_cards.get(active_card["id"], {}).get("balance", 0.0)
            font_bal = FontCache.get(17, bold=True)
            txt_bal = font_bal.render(f"БАЛАНС: ${cur_bal:,.2f}", True, COLOR_GREEN)
            self.screen.blit(txt_bal, (card_rect.right - 20 - txt_bal.get_width(), 148))

            # Navigation bar (y: 185 to 217)
            prev_rect = pygame.Rect(535, 185, 100, 32)
            prev_h = prev_rect.collidepoint(m_pos)
            draw_rounded_rect(self.screen, prev_rect, (35, 48, 75) if prev_h else (22, 32, 50), border_color=(50, 70, 105), radius=6)
            txt_prev = FontCache.get(12, bold=True).render("◀ Пред.", True, COLOR_WHITE)
            self.screen.blit(txt_prev, (prev_rect.centerx - txt_prev.get_width() // 2, prev_rect.centery - txt_prev.get_height() // 2))

            unlocked = self.engine.get_unlocked_cards()
            try:
                c_idx = next(i for i, c in enumerate(unlocked) if c["id"] == self.engine.active_card_id) + 1
            except Exception:
                c_idx = 1
            font_cnt = FontCache.get(12)
            txt_cnt = font_cnt.render(f"Карта {c_idx} из {len(unlocked)}", True, COLOR_MUTED)
            self.screen.blit(txt_cnt, (655, 192))

            next_rect = pygame.Rect(745, 185, 100, 32)
            next_h = next_rect.collidepoint(m_pos)
            draw_rounded_rect(self.screen, next_rect, (35, 48, 75) if next_h else (22, 32, 50), border_color=(50, 70, 105), radius=6)
            txt_next = FontCache.get(12, bold=True).render("След. ▶", True, COLOR_WHITE)
            self.screen.blit(txt_next, (next_rect.centerx - txt_next.get_width() // 2, next_rect.centery - txt_next.get_height() // 2))

            term_btn_rect = pygame.Rect(860, 185, 235, 32)
            term_h = term_btn_rect.collidepoint(m_pos)
            draw_rounded_rect(self.screen, term_btn_rect, (20, 80, 70) if term_h else (16, 60, 52), border_color=COLOR_CYAN, radius=6)
            txt_tb = FontCache.get(12, bold=True).render("+ Ввести новую карту", True, COLOR_WHITE)
            self.screen.blit(txt_tb, (term_btn_rect.centerx - txt_tb.get_width() // 2, term_btn_rect.centery - txt_tb.get_height() // 2))

        else:
            # 2. Manual Terminal Input Widget (y: 68 to 216)
            term_rect = pygame.Rect(535, 68, 565, 150)
            draw_rounded_rect(self.screen, term_rect, (16, 24, 38), border_color=COLOR_CYAN, border_width=2, radius=12)

            font_tt = FontCache.get(15, bold=True)
            self.screen.blit(font_tt.render("💳 Терминал Привязки Карты (Ввод Реквизитов)", True, COLOR_CYAN), (550, 76))

            # Input Field 1: Card Number
            fn_rect = pygame.Rect(545, 102, 320, 36)
            is_fn_act = (self.active_input_field == "num")
            draw_rounded_rect(self.screen, fn_rect, (24, 34, 52), border_color=COLOR_CYAN if is_fn_act else (50, 65, 90), radius=6)

            txt_fn = self.input_card_num
            if not txt_fn and not is_fn_act:
                self.screen.blit(FontCache.get(13).render("Номер карты (16 цифр)", True, COLOR_DARK_TEXT), (555, 111))
            else:
                cursor = "|" if (is_fn_act and self.cursor_timer < 0.5) else ""
                self.screen.blit(FontCache.get(14, bold=True).render(txt_fn + cursor, True, COLOR_WHITE), (555, 110))

            # Input Field 2: Expiry MM/YY
            fe_rect = pygame.Rect(875, 102, 105, 36)
            is_fe_act = (self.active_input_field == "exp")
            draw_rounded_rect(self.screen, fe_rect, (24, 34, 52), border_color=COLOR_CYAN if is_fe_act else (50, 65, 90), radius=6)

            txt_fe = self.input_card_exp
            if not txt_fe and not is_fe_act:
                self.screen.blit(FontCache.get(12).render("Срок MM/YY", True, COLOR_DARK_TEXT), (885, 111))
            else:
                cursor = "|" if (is_fe_act and self.cursor_timer < 0.5) else ""
                self.screen.blit(FontCache.get(14, bold=True).render(txt_fe + cursor, True, COLOR_WHITE), (885, 110))

            # Input Field 3: CVV
            fc_rect = pygame.Rect(990, 102, 105, 36)
            is_fc_act = (self.active_input_field == "cvv")
            draw_rounded_rect(self.screen, fc_rect, (24, 34, 52), border_color=COLOR_CYAN if is_fc_act else (50, 65, 90), radius=6)

            txt_fc = self.input_card_cvv
            if not txt_fc and not is_fc_act:
                self.screen.blit(FontCache.get(12).render("CVV код", True, COLOR_DARK_TEXT), (1000, 111))
            else:
                cursor = "|" if (is_fc_act and self.cursor_timer < 0.5) else ""
                self.screen.blit(FontCache.get(14, bold=True).render(txt_fc + cursor, True, COLOR_WHITE), (1000, 110))

            # Button: Link Card
            link_btn = pygame.Rect(545, 148, 260, 36)
            link_h = link_btn.collidepoint(m_pos)
            draw_rounded_rect(self.screen, link_btn, (20, 160, 90) if link_h else (16, 130, 75), border_color=COLOR_GREEN, radius=6)
            txt_link = FontCache.get(13, bold=True).render("💳 ПРИВЯЗАТЬ КАРТУ", True, COLOR_WHITE)
            self.screen.blit(txt_link, (link_btn.centerx - txt_link.get_width() // 2, link_btn.centery - txt_link.get_height() // 2))

            # Button: Leaks Journal
            leaks_count = len(self.engine.intercepted_leaks)
            journ_btn = pygame.Rect(815, 148, 280, 36)
            journ_h = journ_btn.collidepoint(m_pos)
            draw_rounded_rect(self.screen, journ_btn, (35, 48, 75) if journ_h else (24, 34, 52), border_color=(60, 80, 110), radius=6)
            txt_j = FontCache.get(12, bold=True).render(f"📋 Журнал Утечек ({leaks_count})", True, COLOR_GOLD if leaks_count > 0 else COLOR_MUTED)
            self.screen.blit(txt_j, (journ_btn.centerx - txt_j.get_width() // 2, journ_btn.centery - txt_j.get_height() // 2))

            # Return to active card link if cards exist
            if self.engine.get_unlocked_cards():
                ret_font = FontCache.get(11)
                self.screen.blit(ret_font.render("↩ Вернуться к просмотру активной карты", True, COLOR_CYAN), (550, 194))

        # 3. Donate Items Viewport: y: 226 to 705
        viewport_rect = pygame.Rect(525, 226, 585, 476)
        self.screen.set_clip(viewport_rect)

        offset = self.scroll_offsets["donate"]
        item_y = 226 - offset
        item_h = 74

        cur_bal = self.engine.player_cards.get(active_card["id"], {}).get("balance", 0.0) if active_card else 0.0

        for item in DONATE_SHOP_ITEMS:
            iid = item["id"]
            is_bought = iid in self.engine.purchased_vip_items
            can_afford = (cur_bal >= item["price"]) and (not is_bought) and (active_card is not None)

            if item_y + item_h > 226 and item_y < 705:
                card_r = pygame.Rect(535, item_y, 565, item_h)
                is_hover = card_r.collidepoint(m_pos)

                card_bg = (18, 28, 42) if is_bought else (COLOR_CARD_HOVER if is_hover else COLOR_CARD)
                border_c = (40, 75, 60) if is_bought else (COLOR_GREEN if can_afford else (45, 60, 85))
                draw_rounded_rect(self.screen, card_r, card_bg, border_color=border_c, radius=8)

                cat_tag = "VIP БУСТЕР" if item["category"] == "vip" else ("ЭНЕРГИЯ" if item["category"] == "energy" else "ТЕМНАЯ МАТЕРИЯ")
                cat_col = COLOR_GOLD if item["category"] == "vip" else (COLOR_CYAN if item["category"] == "energy" else COLOR_PURPLE_GLOW)
                font_tag = FontCache.get(10, bold=True)
                txt_cat = font_tag.render(cat_tag, True, cat_col)
                self.screen.blit(txt_cat, (548, item_y + 10))

                font_in = FontCache.get(14, bold=True)
                txt_in = font_in.render(item["name"], True, COLOR_WHITE if not is_bought else COLOR_MUTED)
                self.screen.blit(txt_in, (548, item_y + 26))

                font_id = FontCache.get(12)
                txt_id = font_id.render(item["desc"], True, COLOR_MUTED)
                self.screen.blit(txt_id, (548, item_y + 48))

                btn_rect = pygame.Rect(965, item_y + 16, 125, 42)
                if is_bought:
                    draw_rounded_rect(self.screen, btn_rect, (20, 40, 30), border_color=COLOR_GREEN, radius=6)
                    font_b = FontCache.get(12, bold=True)
                    txt_b = font_b.render("✓ КУПЛЕНО", True, COLOR_GREEN)
                    self.screen.blit(txt_b, (btn_rect.centerx - txt_b.get_width() // 2, btn_rect.centery - txt_b.get_height() // 2))
                else:
                    btn_h = btn_rect.collidepoint(m_pos)
                    btn_bg = ((20, 160, 90) if btn_h else (16, 130, 75)) if can_afford else (35, 40, 52)
                    btn_bor = COLOR_GREEN if can_afford else (55, 65, 80)
                    draw_rounded_rect(self.screen, btn_rect, btn_bg, border_color=btn_bor, radius=6)

                    font_btn_t = FontCache.get(12, bold=True)
                    txt_btn_t = font_btn_t.render("КУПИТЬ", True, COLOR_WHITE if can_afford else COLOR_MUTED)
                    self.screen.blit(txt_btn_t, (btn_rect.centerx - txt_btn_t.get_width() // 2, btn_rect.y + 6))

                    font_btn_p = FontCache.get(12, bold=True)
                    txt_btn_p = font_btn_p.render(f"${item['price']:.2f}", True, COLOR_GOLD if can_afford else COLOR_DARK_TEXT)
                    self.screen.blit(txt_btn_p, (btn_rect.centerx - txt_btn_p.get_width() // 2, btn_rect.y + 22))

            item_y += item_h + 8

        self.screen.set_clip(None)
        self.draw_scrollbar("donate", 525, 226, 476)

    def draw_prestige_tab(self):
        m_pos = pygame.mouse.get_pos()

        banner_rect = pygame.Rect(535, 75, 565, 215)
        draw_rounded_rect(self.screen, banner_rect, (20, 18, 38), border_color=COLOR_PURPLE, border_width=2, radius=12)

        font_title = FontCache.get(18, bold=True)
        txt_t = font_title.render("🌌 Квантовая Сингулярность (Престиж)", True, COLOR_PURPLE_GLOW)
        self.screen.blit(txt_t, (555, 92))

        font_desc = FontCache.get(13)
        lore_lines = [
            "Инициируйте контролируемый гравитационный коллапс реактора.",
            "Сбросит текущую энергию и генераторы станции в обмен на Темную Материю (✦).",
            f"Каждый кристалл Темной Материи дает постоянный бонус +10% ко всей выработке!",
            f"Текущий запас ТМ: {int(self.engine.dark_matter)}✦  |  Бонус мощности: +{int((self.engine.get_dark_matter_bonus()-1)*100)}%"
        ]
        ly = 125
        for line in lore_lines:
            self.screen.blit(font_desc.render(line, True, COLOR_WHITE if "Текущий" in line else COLOR_MUTED), (555, ly))
            ly += 22

        dm_gain = self.engine.get_prestige_dark_matter_gain()
        can_p = self.engine.can_prestige()

        p_btn_rect = pygame.Rect(550, 310, 540, 56)
        p_hover = p_btn_rect.collidepoint(m_pos)
        p_bg = ((140, 30, 160) if p_hover else (110, 20, 130)) if can_p else (28, 24, 38)
        p_border = COLOR_PURPLE_GLOW if can_p else (60, 50, 80)
        draw_rounded_rect(self.screen, p_btn_rect, p_bg, border_color=p_border, border_width=2, radius=10)

        font_pbtn = FontCache.get(16, bold=True)
        if can_p:
            lbl = f"ЗАПУСТИТЬ КОЛЛАПС (Получить +{dm_gain}✦ Темной Материи)"
            txt_p = font_pbtn.render(lbl, True, (255, 255, 255))
        else:
            needed = 1000000 - self.engine.total_energy_earned
            lbl = f"Требуется еще {format_number(max(0, needed))}⚡ для первой Сингулярности"
            txt_p = font_pbtn.render(lbl, True, COLOR_MUTED)
        self.screen.blit(txt_p, (p_btn_rect.centerx - txt_p.get_width() // 2, p_btn_rect.centery - txt_p.get_height() // 2))

        font_art_h = FontCache.get(16, bold=True)
        self.screen.blit(font_art_h.render("✦ Реликвии Темной Материи", True, COLOR_GOLD), (535, 385))

        art_y = 415
        for art in ARTIFACT_DEFS:
            aid = art["id"]
            is_bought = aid in self.engine.purchased_artifacts
            can_afford = self.engine.dark_matter >= art["cost"] and not is_bought

            card_rect = pygame.Rect(535, art_y, 565, 58)
            draw_rounded_rect(self.screen, card_rect, (24, 20, 38) if is_bought else COLOR_CARD, border_color=COLOR_CARD_BORDER, radius=8)

            font_an = FontCache.get(14, bold=True)
            self.screen.blit(font_an.render(art["name"], True, COLOR_PURPLE_GLOW if not is_bought else COLOR_MUTED), (550, art_y + 10))

            font_ad = FontCache.get(12)
            self.screen.blit(font_ad.render(art["desc"], True, COLOR_MUTED), (550, art_y + 32))

            btn_rect = pygame.Rect(970, art_y + 11, 120, 36)
            if is_bought:
                draw_rounded_rect(self.screen, btn_rect, (25, 45, 35), border_color=COLOR_GREEN, radius=6)
                txt_b = FontCache.get(12, bold=True).render("АКТИВНО", True, COLOR_GREEN)
                self.screen.blit(txt_b, (btn_rect.centerx - txt_b.get_width() // 2, btn_rect.centery - txt_b.get_height() // 2))
            else:
                b_hover = btn_rect.collidepoint(m_pos)
                b_bg = ((120, 30, 140) if b_hover else (90, 20, 110)) if can_afford else (35, 30, 48)
                draw_rounded_rect(self.screen, btn_rect, b_bg, border_color=COLOR_PURPLE if can_afford else (60, 50, 75), radius=6)
                font_cb = FontCache.get(12, bold=True)
                txt_b = font_cb.render(f"{art['cost']}✦ ТМ", True, COLOR_WHITE if can_afford else COLOR_MUTED)
                self.screen.blit(txt_b, (btn_rect.centerx - txt_b.get_width() // 2, btn_rect.centery - txt_b.get_height() // 2))

            art_y += 66

    def draw_stats_tab(self):
        m_pos = pygame.mouse.get_pos()

        stats_rect = pygame.Rect(535, 70, 565, 260)
        draw_rounded_rect(self.screen, stats_rect, COLOR_CARD, border_color=COLOR_CARD_BORDER, radius=10)

        font_title = FontCache.get(16, bold=True)
        self.screen.blit(font_title.render("📊 Статистика Станции", True, COLOR_CYAN), (555, 86))

        font_st = FontCache.get(13)
        stat_entries = [
            ("Всего выработано энергии:", f"{format_number(self.engine.total_energy_earned)} ⚡"),
            ("Кликов по ядру:", f"{self.engine.total_clicks:,}"),
            ("Критических кликов:", f"{self.engine.total_crits:,}"),
            ("Поймано аномалий:", f"{self.engine.anomalies_caught}"),
            ("Привязано карт:", f"{len(self.engine.get_unlocked_cards())} из {len(FAKE_CARDS_DATABASE)}"),
            ("Куплено VIP предметов:", f"{self.engine.vip_items_bought_count}"),
            ("Максимальный комбо:", f"{self.engine.highest_combo:.1f}x"),
            ("Сингулярностей (Престижей):", f"{self.engine.prestige_count}")
        ]

        sy = 118
        for label, val in stat_entries:
            self.screen.blit(font_st.render(label, True, COLOR_MUTED), (555, sy))
            txt_v = font_st.render(val, True, COLOR_WHITE)
            self.screen.blit(txt_v, (stats_rect.right - 25 - txt_v.get_width(), sy))
            sy += 24

        self.screen.blit(font_title.render("🏆 Достижения станции", True, COLOR_GOLD), (535, 345))

        ach_y = 375
        for ach in ACHIEVEMENT_DEFS[:4]:
            aid = ach["id"]
            is_unl = aid in self.engine.unlocked_achievements
            c_rect = pygame.Rect(535, ach_y, 565, 54)
            draw_rounded_rect(self.screen, c_rect, (20, 28, 45) if is_unl else (16, 20, 32),
                              border_color=(45, 80, 60) if is_unl else (30, 40, 58), radius=8)

            font_an = FontCache.get(14, bold=True)
            self.screen.blit(font_an.render(f"{'✓ ' if is_unl else '○ '}{ach['name']}", True, COLOR_GOLD if is_unl else COLOR_MUTED), (550, ach_y + 8))

            font_ad = FontCache.get(12)
            self.screen.blit(font_ad.render(ach["desc"], True, COLOR_WHITE if is_unl else COLOR_DARK_TEXT), (550, ach_y + 28))

            ach_y += 62

        reset_rect = pygame.Rect(550, 642, 220, 38)
        r_hover = reset_rect.collidepoint(m_pos)
        draw_rounded_rect(self.screen, reset_rect, (60, 20, 25) if r_hover else (40, 16, 20), border_color=COLOR_RED, radius=8)
        font_rb = FontCache.get(13, bold=True)
        txt_rb = font_rb.render("⚠️ Сброс Прогресса", True, (255, 120, 120))
        self.screen.blit(txt_rb, (reset_rect.centerx - txt_rb.get_width() // 2, reset_rect.centery - txt_rb.get_height() // 2))

    def draw_scrollbar(self, tab_id, x, y, h):
        max_s = self.max_scroll[tab_id]
        if max_s <= 0:
            return
        cur_s = self.scroll_offsets[tab_id]
        bar_h = max(25, int(h * (h / (h + max_s))))
        bar_y = y + int((cur_s / max_s) * (h - bar_h))

        pygame.draw.rect(self.screen, (20, 28, 44), (x + 580, y, 6, h), border_radius=3)
        pygame.draw.rect(self.screen, COLOR_CYAN_DIM, (x + 580, bar_y, 6, bar_h), border_radius=3)

    def draw_modal(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 195))
        self.screen.blit(overlay, (0, 0))

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        m_pos = pygame.mouse.get_pos()

        if self.active_modal == "offline":
            m_rect = pygame.Rect(cx - 240, cy - 130, 480, 260)
            draw_rounded_rect(self.screen, m_rect, COLOR_PANEL, border_color=COLOR_CYAN, border_width=2, radius=14)

            font_mt = FontCache.get(20, bold=True)
            txt_mt = font_mt.render("🔋 С возвращением, Инженер!", True, COLOR_CYAN)
            self.screen.blit(txt_mt, (cx - txt_mt.get_width() // 2, cy - 90))

            report = self.engine.offline_report or {}
            secs = report.get("seconds", 0)
            gain = report.get("energy", 0.0)

            mins = secs // 60
            hrs = mins // 60
            time_str = f"{hrs} ч {mins % 60} мин" if hrs > 0 else f"{mins} мин {secs % 60} сек"

            font_md = FontCache.get(14)
            t_msg = font_md.render(f"Ваша станция функционировала оффлайн: {time_str}", True, COLOR_WHITE)
            self.screen.blit(t_msg, (cx - t_msg.get_width() // 2, cy - 40))

            font_mg = FontCache.get(22, bold=True)
            g_msg = font_mg.render(f"+{format_number(gain)} ⚡ Энергии получено!", True, COLOR_GOLD)
            self.screen.blit(g_msg, (cx - g_msg.get_width() // 2, cy - 5))

            btn_rect = pygame.Rect(cx - 80, cy + 70, 160, 44)
            btn_hover = btn_rect.collidepoint(m_pos)
            draw_rounded_rect(self.screen, btn_rect, (0, 160, 180) if btn_hover else (0, 120, 140), border_color=COLOR_CYAN, radius=8)
            txt_ok = FontCache.get(15, bold=True).render("ПРИНЯТЬ", True, COLOR_WHITE)
            self.screen.blit(txt_ok, (cx - txt_ok.get_width() // 2, cy + 82))

        elif self.active_modal == "card_leak":
            # Modal showing intercepted card details
            m_rect = pygame.Rect(cx - 260, cy - 170, 520, 340)
            draw_rounded_rect(self.screen, m_rect, (16, 22, 38), border_color=COLOR_GREEN, border_width=2, radius=14)

            font_lt = FontCache.get(18, bold=True)
            txt_lt = font_lt.render("💳 КВАНТОВЫЙ ПЕРЕХВАТ ДАННЫХ!", True, COLOR_GREEN)
            self.screen.blit(txt_lt, (cx - txt_lt.get_width() // 2, cy - 145))

            card = self.leaked_card_info or {}
            font_sub = FontCache.get(13)
            self.screen.blit(font_sub.render("Аномалия расшифровала виртуальную карту:", True, COLOR_WHITE), (cx - 220, cy - 110))

            # Blueprint Data Box
            b_box = pygame.Rect(cx - 220, cy - 85, 440, 180)
            draw_rounded_rect(self.screen, b_box, (10, 14, 25), border_color=(35, 55, 80), radius=10)

            font_k = FontCache.get(13, bold=True)
            font_v = FontCache.get(14, bold=True)

            rows = [
                ("Название:", card.get("name", ""), COLOR_GOLD),
                ("Номер карты:", card.get("number", ""), (255, 255, 255)),
                ("Срок / CVV:", f"{card.get('exp', '')}   /   CVV: {card.get('cvv', '')}", COLOR_CYAN),
                ("Владелец:", card.get("holder", ""), COLOR_MUTED),
                ("Баланс:", f"${card.get('initial_balance', 0):,.2f}", COLOR_GREEN)
            ]
            ry = cy - 75
            for k, val, col in rows:
                self.screen.blit(font_k.render(k, True, COLOR_MUTED), (cx - 205, ry))
                self.screen.blit(font_v.render(val, True, col), (cx - 70, ry))
                ry += 32

            # Accept Button
            btn_ok = pygame.Rect(cx - 110, cy + 112, 220, 42)
            b_h = btn_ok.collidepoint(m_pos)
            draw_rounded_rect(self.screen, btn_ok, (20, 160, 90) if b_h else (16, 130, 75), border_color=COLOR_GREEN, radius=8)
            txt_b = FontCache.get(14, bold=True).render("ВВЕСТИ В ТЕРМИНАЛ", True, COLOR_WHITE)
            self.screen.blit(txt_b, (btn_ok.centerx - txt_b.get_width() // 2, btn_ok.centery - txt_b.get_height() // 2))

        elif self.active_modal == "leaks_journal":
            # Modal showing list of all intercepted leaks
            m_rect = pygame.Rect(cx - 290, cy - 210, 580, 430)
            draw_rounded_rect(self.screen, m_rect, (16, 22, 38), border_color=COLOR_CYAN, border_width=2, radius=14)

            font_jt = FontCache.get(18, bold=True)
            txt_jt = font_jt.render("📋 Журнал Перехваченных Утечек", True, COLOR_CYAN)
            self.screen.blit(txt_jt, (cx - txt_jt.get_width() // 2, cy - 185))

            leaks = self.engine.intercepted_leaks
            if not leaks:
                font_empty = FontCache.get(14)
                self.screen.blit(font_empty.render("Вы еще не поймали ни одной утечки из аномалий!", True, COLOR_MUTED), (cx - 190, cy - 50))
                self.screen.blit(font_empty.render("Кликайте светящиеся аномалии в камере реактора.", True, COLOR_DARK_TEXT), (cx - 170, cy - 20))
            else:
                jy = cy - 145
                for cid in leaks[:5]:  # show up to 5
                    c = next((item for item in FAKE_CARDS_DATABASE if item["id"] == cid), None)
                    if c:
                        is_linked = self.engine.player_cards.get(cid, {}).get("unlocked", False)
                        row_r = pygame.Rect(cx - 265, jy, 530, 50)
                        draw_rounded_rect(self.screen, row_r, (22, 30, 48), border_color=(40, 60, 85), radius=8)

                        font_rn = FontCache.get(13, bold=True)
                        self.screen.blit(font_rn.render(c["name"], True, COLOR_GOLD), (cx - 250, jy + 6))

                        font_rd = FontCache.get(12)
                        d_str = f"№: {c['number']}  |  Exp: {c['exp']}  |  CVV: {c['cvv']}  |  ${c['initial_balance']:,.0f}"
                        self.screen.blit(font_rd.render(d_str, True, COLOR_WHITE), (cx - 250, jy + 26))

                        paste_btn = pygame.Rect(cx + 140, jy + 8, 115, 34)
                        p_h = paste_btn.collidepoint(m_pos)
                        if is_linked:
                            draw_rounded_rect(self.screen, paste_btn, (20, 40, 30), border_color=COLOR_GREEN, radius=6)
                            txt_pb = FontCache.get(11, bold=True).render("✓ ПРИВЯЗАНА", True, COLOR_GREEN)
                        else:
                            draw_rounded_rect(self.screen, paste_btn, (0, 140, 160) if p_h else (0, 110, 130), border_color=COLOR_CYAN, radius=6)
                            txt_pb = FontCache.get(11, bold=True).render("ВСТАВИТЬ", True, COLOR_WHITE)
                        self.screen.blit(txt_pb, (paste_btn.centerx - txt_pb.get_width() // 2, paste_btn.centery - txt_pb.get_height() // 2))

                        jy += 58

            close_btn = pygame.Rect(cx - 80, cy + 165, 160, 40)
            c_h = close_btn.collidepoint(m_pos)
            draw_rounded_rect(self.screen, close_btn, (45, 55, 75) if c_h else (30, 38, 55), border_color=(60, 75, 100), radius=8)
            txt_cb = FontCache.get(14, bold=True).render("ЗАКРЫТЬ", True, COLOR_WHITE)
            self.screen.blit(txt_cb, (close_btn.centerx - txt_cb.get_width() // 2, close_btn.centery - txt_cb.get_height() // 2))

        elif self.active_modal == "prestige_confirm":
            m_rect = pygame.Rect(cx - 220, cy - 110, 440, 220)
            draw_rounded_rect(self.screen, m_rect, COLOR_PANEL, border_color=COLOR_PURPLE, border_width=2, radius=14)

            txt_pt = FontCache.get(18, bold=True).render("Подтверждение Сингулярности", True, COLOR_PURPLE_GLOW)
            self.screen.blit(txt_pt, (cx - txt_pt.get_width() // 2, cy - 80))

            gain = self.engine.get_prestige_dark_matter_gain()
            font_pd = FontCache.get(13)
            p_msg1 = font_pd.render(f"Вы получите: +{gain}✦ Темной Материи", True, COLOR_GOLD)
            p_msg2 = font_pd.render("Энергия и генераторы будут сброшены до нуля.", True, COLOR_WHITE)
            self.screen.blit(p_msg1, (cx - p_msg1.get_width() // 2, cy - 40))
            self.screen.blit(p_msg2, (cx - p_msg2.get_width() // 2, cy - 15))

            btn_c = pygame.Rect(cx - 160, cy + 45, 140, 42)
            c_hover = btn_c.collidepoint(m_pos)
            draw_rounded_rect(self.screen, btn_c, (140, 30, 160) if c_hover else (100, 20, 120), border_color=COLOR_PURPLE_GLOW, radius=8)
            txt_c = FontCache.get(14, bold=True).render("КОЛЛАПС", True, COLOR_WHITE)
            self.screen.blit(txt_c, (btn_c.centerx - txt_c.get_width() // 2, btn_c.centery - txt_c.get_height() // 2))

            btn_can = pygame.Rect(cx + 20, cy + 45, 140, 42)
            can_hover = btn_can.collidepoint(m_pos)
            draw_rounded_rect(self.screen, btn_can, (45, 55, 75) if can_hover else (30, 38, 55), border_color=(60, 75, 100), radius=8)
            txt_can = FontCache.get(14, bold=True).render("ОТМЕНА", True, COLOR_MUTED)
            self.screen.blit(txt_can, (btn_can.centerx - txt_can.get_width() // 2, btn_can.centery - txt_can.get_height() // 2))

        elif self.active_modal == "reset_confirm":
            m_rect = pygame.Rect(cx - 200, cy - 90, 400, 180)
            draw_rounded_rect(self.screen, m_rect, COLOR_PANEL, border_color=COLOR_RED, border_width=2, radius=14)

            txt_rt = FontCache.get(17, bold=True).render("Сбросить весь прогресс?", True, COLOR_RED)
            self.screen.blit(txt_rt, (cx - txt_rt.get_width() // 2, cy - 65))

            font_rd = FontCache.get(13)
            r_msg = font_rd.render("Все данные будут удалены безвозвратно!", True, COLOR_WHITE)
            self.screen.blit(r_msg, (cx - r_msg.get_width() // 2, cy - 30))

            btn_r = pygame.Rect(cx - 150, cy + 20, 130, 40)
            r_hover = btn_r.collidepoint(m_pos)
            draw_rounded_rect(self.screen, btn_r, (160, 30, 40) if r_hover else (120, 20, 30), border_color=COLOR_RED, radius=8)
            txt_r = FontCache.get(14, bold=True).render("УДАЛИТЬ", True, COLOR_WHITE)
            self.screen.blit(txt_r, (btn_r.centerx - txt_r.get_width() // 2, btn_r.centery - txt_r.get_height() // 2))

            btn_can = pygame.Rect(cx + 20, cy + 20, 130, 40)
            can_hover = btn_can.collidepoint(m_pos)
            draw_rounded_rect(self.screen, btn_can, (45, 55, 75) if can_hover else (30, 38, 55), border_color=(60, 75, 100), radius=8)
            txt_can = FontCache.get(14, bold=True).render("ОТМЕНА", True, COLOR_MUTED)
            self.screen.blit(txt_can, (btn_can.centerx - txt_can.get_width() // 2, btn_can.centery - txt_can.get_height() // 2))

if __name__ == "__main__":
    app = CyberCoreApp()
    app.run()
