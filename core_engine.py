"""
Core Game Engine: Handles game state, math formulas, upgrades, generators,
prestige, anomalies, achievements, fake donate cards, and persistence.
"""
import time
import json
import math
import os
import sys
import random

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(APP_DIR, "cyber_core_save.json")

# Database of Fake Bank Cards (Must be found via anomalies and manually typed in)
FAKE_CARDS_DATABASE = [
    {
        "id": "card_junior",
        "name": "Карта Стажера CyberCorp",
        "type": "VISA Classic",
        "number": "4276 3811 9024 1337",
        "clean_num": "4276381190241337",
        "holder": "ALEX_JUNIOR",
        "exp": "09/28",
        "cvv": "404",
        "color": (24, 48, 88),
        "accent": (0, 180, 255),
        "initial_balance": 150.0
    },
    {
        "id": "card_gold_corpo",
        "name": "Золотая Карта Нео-Олигарха",
        "type": "Mastercard Gold",
        "number": "5412 7534 8819 2048",
        "clean_num": "5412753488192048",
        "holder": "VIKTOR CORPO",
        "exp": "11/29",
        "cvv": "777",
        "color": (80, 60, 16),
        "accent": (255, 200, 30),
        "initial_balance": 1200.0
    },
    {
        "id": "card_platinum",
        "name": "Платиновая Карта Кибер-Магната",
        "type": "Cyber Platinum",
        "number": "4111 5678 9012 4096",
        "clean_num": "4111567890124096",
        "holder": "ELON CYBER",
        "exp": "04/30",
        "cvv": "321",
        "color": (40, 52, 72),
        "accent": (190, 220, 255),
        "initial_balance": 5000.0
    },
    {
        "id": "card_syndicate",
        "name": "Черная Карта Синдиката",
        "type": "Obsidian Black",
        "number": "4000 0012 3456 9999",
        "clean_num": "4000001234569999",
        "holder": "SHADOW SYNDICATE",
        "exp": "01/31",
        "cvv": "666",
        "color": (16, 16, 26),
        "accent": (192, 38, 211),
        "initial_balance": 15000.0
    },
    {
        "id": "card_streamer",
        "name": "Карта Стримера-Миллионника",
        "type": "Titanium Crypto",
        "number": "5500 2341 6789 7777",
        "clean_num": "5500234167897777",
        "holder": "MR_BEAST_TECH",
        "exp": "07/31",
        "cvv": "999",
        "color": (65, 18, 42),
        "accent": (255, 80, 140),
        "initial_balance": 50000.0
    },
    {
        "id": "card_matrix",
        "name": "Секретный Счет Архитектора",
        "type": "Quantum Infinity",
        "number": "7777 8888 9999 0001",
        "clean_num": "7777888899990001",
        "holder": "NEO ARCHITECT",
        "exp": "12/35",
        "cvv": "101",
        "color": (14, 42, 32),
        "accent": (0, 255, 180),
        "initial_balance": 250000.0
    },
    {
        "id": "card_ai_offshore",
        "name": "Офшор Сверхразума ИИ",
        "type": "AI Void Black",
        "number": "9999 0101 1010 4242",
        "clean_num": "9999010110104242",
        "holder": "OVERMIND AI",
        "exp": "99/99",
        "cvv": "000",
        "color": (10, 10, 18),
        "accent": (255, 215, 0),
        "initial_balance": 1000000.0
    }
]

# Donate Shop Items
DONATE_SHOP_ITEMS = [
    # Permanent Boosters
    {
        "id": "donate_vip_status",
        "name": "👑 VIP Статус Станции",
        "desc": "+100% ко всей генерации энергии навсегда!",
        "price": 49.0,
        "type": "permanent",
        "category": "vip",
        "effect": "vip_global_mult",
        "val": 2.0
    },
    {
        "id": "donate_turbo_click",
        "name": "⚡ Турбо-Кликер Про",
        "desc": "Ручной клик получает гигантские +10% от ВСЕГО пассивного EPS!",
        "price": 99.0,
        "type": "permanent",
        "category": "vip",
        "effect": "vip_click_eps",
        "val": 0.10
    },
    {
        "id": "donate_chrono_speed",
        "name": "⏳ Хроно-Ускоритель ИИ",
        "desc": "Утраивает выработку всех генераторов станции навсегда (3x EPS)!",
        "price": 199.0,
        "type": "permanent",
        "category": "vip",
        "effect": "vip_eps_mult",
        "val": 3.0
    },
    {
        "id": "donate_perm_hyper",
        "name": "🔥 Перманентный Овердрайв",
        "desc": "Шкала комбо никогда не остывает ниже 75% (всегда от 3.0x до 5.0x)!",
        "price": 399.0,
        "type": "permanent",
        "category": "vip",
        "effect": "vip_hyper_lock",
        "val": 75.0
    },
    {
        "id": "donate_gold_core",
        "name": "✨ Золотой Скин Ядра Магната",
        "desc": "Золотой статус! +500% ко всему производству и +20% шанс крита!",
        "price": 999.0,
        "type": "permanent",
        "category": "vip",
        "effect": "vip_gold_core",
        "val": 5.0
    },
    # Instant Energy Packages
    {
        "id": "donate_energy_small",
        "name": "💼 Чемоданчик Квантов",
        "desc": "Мгновенно начисляет +500,000 ⚡ энергии в энергосеть",
        "price": 15.0,
        "type": "instant_energy",
        "category": "energy",
        "val": 500000.0
    },
    {
        "id": "donate_energy_mid",
        "name": "🏦 Хранилище Энергии",
        "desc": "Мгновенно начисляет +50,000,000 ⚡ энергии в энергосеть",
        "price": 75.0,
        "type": "instant_energy",
        "category": "energy",
        "val": 50000000.0
    },
    {
        "id": "donate_energy_huge",
        "name": "🚀 Квантовый Госрезерв",
        "desc": "Мгновенно начисляет +2,000,000,000 ⚡ (2 Миллиарда энергии!)",
        "price": 250.0,
        "type": "instant_energy",
        "category": "energy",
        "val": 2000000000.0
    },
    # Dark Matter Packages
    {
        "id": "donate_dm_small",
        "name": "✦ Партия Темной Материи",
        "desc": "Мгновенно начисляет +10 ✦ Темной Материи (+100% перманентно)",
        "price": 35.0,
        "type": "instant_dm",
        "category": "dm",
        "val": 10
    },
    {
        "id": "donate_dm_large",
        "name": "🌌 Сундук Сингулярности",
        "desc": "Мгновенно начисляет +50 ✦ Темной Материи (+500% перманентно)",
        "price": 150.0,
        "type": "instant_dm",
        "category": "dm",
        "val": 50
    },
    {
        "id": "donate_dm_mega",
        "name": "👑 Ящик Бога Пустоты",
        "desc": "Мгновенно начисляет +250 ✦ Темной Материи (+2500% перманентно)!",
        "price": 500.0,
        "type": "instant_dm",
        "category": "dm",
        "val": 250
    }
]

GENERATOR_DEFS = [
    {
        "id": "gen_chip",
        "name": "Квантовый Микрочип",
        "desc": "Базовый кремниево-квантовый процессор для сбора фоновой энергии",
        "tag": "µCHIP",
        "base_cost": 15,
        "cost_multiplier": 1.15,
        "base_eps": 0.5
    },
    {
        "id": "gen_converter",
        "name": "Нано-Конвертер",
        "desc": "Преобразует молекулярные колебания в стабильный поток энергии",
        "tag": "NANO",
        "base_cost": 100,
        "cost_multiplier": 1.15,
        "base_eps": 4.0
    },
    {
        "id": "gen_plasma",
        "name": "Плазменный Инжектор",
        "desc": "Генерирует высокотемпературную плазму в магнитной ловушке",
        "tag": "PLZMA",
        "base_cost": 1100,
        "cost_multiplier": 1.15,
        "base_eps": 32.0
    },
    {
        "id": "gen_reactor",
        "name": "Термоядерный Блок",
        "desc": "Синтез легких ядер обеспечивает гигантский приток мощности",
        "tag": "FUSION",
        "base_cost": 12000,
        "cost_multiplier": 1.15,
        "base_eps": 260.0
    },
    {
        "id": "gen_collider",
        "name": "Фотонный Коллайдер",
        "desc": "Сталкивает фотоны на околосветовой скорости, извлекая кванты",
        "tag": "COLLID",
        "base_cost": 130000,
        "cost_multiplier": 1.15,
        "base_eps": 1400.0
    },
    {
        "id": "gen_antimatter",
        "name": "Сборщик Антиматерии",
        "desc": "Ловит позитроны из вакуума с коэффициентом аннигиляции 99.9%",
        "tag": "ANTIM",
        "base_cost": 1400000,
        "cost_multiplier": 1.15,
        "base_eps": 8500.0
    },
    {
        "id": "gen_dyson",
        "name": "Кольцо Сферы Дайсона",
        "desc": "Орбитальный рой зеркал поглощает радиацию ближайшей звезды",
        "tag": "DYSON",
        "base_cost": 20000000,
        "cost_multiplier": 1.15,
        "base_eps": 55000.0
    },
    {
        "id": "gen_singularity",
        "name": "Двигатель Сингулярности",
        "desc": "Искривляет пространство-время, выкачивая энергию из горизонта событий",
        "tag": "SINGUL",
        "base_cost": 350000000,
        "cost_multiplier": 1.15,
        "base_eps": 420000.0
    }
]

UPGRADE_DEFS = [
    {
        "id": "upg_click_1",
        "name": "Кибер-Перчатка",
        "desc": "+100% к базовой силе ручного клика",
        "cost": 100,
        "type": "click_mult",
        "val": 2.0,
        "req_energy": 50
    },
    {
        "id": "upg_click_2",
        "name": "Нейро-Интерфейс",
        "desc": "+150% к базовой силе ручного клика",
        "cost": 800,
        "type": "click_mult",
        "val": 2.5,
        "req_energy": 500
    },
    {
        "id": "upg_synergy_1",
        "name": "Квантовая Связь",
        "desc": "Ручной клик получает +1.5% от суммарного EPS генераторов",
        "cost": 2500,
        "type": "click_eps_pct",
        "val": 0.015,
        "req_energy": 1500
    },
    {
        "id": "upg_crit_1",
        "name": "Лазерная Фокусировка",
        "desc": "+10% шанс критического удара и +1.5x крит-множитель",
        "cost": 6000,
        "type": "crit_boost",
        "chance_val": 0.10,
        "mult_val": 1.5,
        "req_energy": 4000
    },
    {
        "id": "upg_gen1_boost",
        "name": "Разгон Микрочипов",
        "desc": "Квантовые Микрочипы вырабатывают в 2x больше энергии",
        "cost": 1200,
        "type": "gen_mult",
        "target": "gen_chip",
        "val": 2.0,
        "req_energy": 800
    },
    {
        "id": "upg_gen2_boost",
        "name": "Субатомная Стабилизация",
        "desc": "Нано-Конвертеры вырабатывают в 2x больше энергии",
        "cost": 8000,
        "type": "gen_mult",
        "target": "gen_converter",
        "val": 2.0,
        "req_energy": 5000
    },
    {
        "id": "upg_drone_1",
        "name": "Автономный Дрон v1",
        "desc": "Встроенный ИИ кликает по ядру 3 раза каждую секунду",
        "cost": 25000,
        "type": "autoclick",
        "val": 3.0,
        "req_energy": 15000
    },
    {
        "id": "upg_combo_1",
        "name": "Сверхпроводники Охлаждения",
        "desc": "Шкала перегрузки комбо остывает на 40% медленнее",
        "cost": 45000,
        "type": "combo_decay",
        "val": 0.6,
        "req_energy": 25000
    },
    {
        "id": "upg_gen3_boost",
        "name": "Магнитные Торы",
        "desc": "Плазменные Инжекторы удваивают выработку (2x)",
        "cost": 90000,
        "type": "gen_mult",
        "target": "gen_plasma",
        "val": 2.0,
        "req_energy": 50000
    },
    {
        "id": "upg_synergy_2",
        "name": "Гармонический Резонанс",
        "desc": "Клик получает еще +3.0% от суммарного EPS генераторов",
        "cost": 200000,
        "type": "click_eps_pct",
        "val": 0.030,
        "req_energy": 100000
    },
    {
        "id": "upg_crit_2",
        "name": "Квантовый Пробой",
        "desc": "+15% шанс крита и крит наносит 5.0x энергии!",
        "cost": 650000,
        "type": "crit_boost",
        "chance_val": 0.15,
        "mult_val": 2.5,
        "req_energy": 350000
    },
    {
        "id": "upg_gen4_boost",
        "name": "Тяжелый Дейтерий",
        "desc": "Термоядерные Блоки вырабатывают в 2x больше энергии",
        "cost": 1500000,
        "type": "gen_mult",
        "target": "gen_reactor",
        "val": 2.0,
        "req_energy": 800000
    },
    {
        "id": "upg_all_boost_1",
        "name": "Поле Темной Энергии",
        "desc": "Все генераторы станции вырабатывают на 50% больше энергии",
        "cost": 5000000,
        "type": "all_gen_mult",
        "val": 1.5,
        "req_energy": 2500000
    },
    {
        "id": "upg_drone_2",
        "name": "Нейро-Сверхразум v2",
        "desc": "Дроны кликают ядро 8 раз каждую секунду!",
        "cost": 18000000,
        "type": "autoclick",
        "val": 8.0,
        "req_energy": 10000000
    },
    {
        "id": "upg_hyper_1",
        "name": "Хроно-Стабилизатор",
        "desc": "Режим Hyperdrive длится 15 секунд вместо 8",
        "cost": 60000000,
        "type": "hyper_duration",
        "val": 15.0,
        "req_energy": 30000000
    },
    {
        "id": "upg_singularity_matrix",
        "name": "Абсолютная Матрица",
        "desc": "Удваивает абсолютно всю выработку энергии (2x глобально)!",
        "cost": 250000000,
        "type": "global_mult",
        "val": 2.0,
        "req_energy": 100000000
    }
]

ARTIFACT_DEFS = [
    {
        "id": "art_void_core",
        "name": "Ядро Пустоты",
        "desc": "+25% к силе каждого кристалла Темной Материи",
        "cost": 2,
        "type": "dm_power",
        "val": 0.25
    },
    {
        "id": "art_chrono_loop",
        "name": "Петля Времени",
        "desc": "Квантовые аномалии появляются на 40% чаще",
        "cost": 5,
        "type": "anomaly_freq",
        "val": 0.40
    },
    {
        "id": "art_dark_spark",
        "name": "Темная Искра",
        "desc": "Начало каждого цикла с 10,000 стартовой энергии и +25 к клику",
        "cost": 10,
        "type": "start_boost",
        "val": 10000
    },
    {
        "id": "art_hyper_reactor",
        "name": "Гипер-Реактор",
        "desc": "Максимальный множитель Overdrive увеличен до 8.0x",
        "cost": 20,
        "type": "combo_cap",
        "val": 8.0
    }
]

ACHIEVEMENT_DEFS = [
    {"id": "ach_click_1", "name": "Первая Искра", "desc": "Совершить первый клик по ядру", "req_type": "clicks", "req_val": 1},
    {"id": "ach_click_100", "name": "Энергетик", "desc": "Совершить 100 кликов по ядру", "req_type": "clicks", "req_val": 100},
    {"id": "ach_click_1000", "name": "Кибер-Мастер", "desc": "Совершить 1,000 кликов по ядру", "req_type": "clicks", "req_val": 1000},
    {"id": "ach_energy_1k", "name": "Киловатты", "desc": "Заработать 1,000 энергии за все время", "req_type": "all_energy", "req_val": 1000},
    {"id": "ach_energy_1m", "name": "Мегаваттный Заряд", "desc": "Заработать 1,000,000 энергии за все время", "req_type": "all_energy", "req_val": 1000000},
    {"id": "ach_energy_1b", "name": "Гигаваттный Титан", "desc": "Заработать 1,000,000,000 энергии за все время", "req_type": "all_energy", "req_val": 1000000000},
    {"id": "ach_hyper", "name": "Полный Разгон", "desc": "Активировать режим Hyperdrive перегрузки", "req_type": "hyper", "req_val": 1},
    {"id": "ach_anomaly_1", "name": "Охотник за Аномалиями", "desc": "Поймать первую квантовую аномалию", "req_type": "anomalies", "req_val": 1},
    {"id": "ach_anomaly_10", "name": "Квантовый Ловец", "desc": "Поймать 10 квантовых аномалий", "req_type": "anomalies", "req_val": 10},
    {"id": "ach_crit_50", "name": "Критическая Точность", "desc": "Совершить 50 критических кликов", "req_type": "crits", "req_val": 50},
    {"id": "ach_gens_50", "name": "Техно-Империя", "desc": "Владеть суммарно 50 генераторами", "req_type": "total_gens", "req_val": 50},
    {"id": "ach_prestige_1", "name": "Сингулярность", "desc": "Совершить первый квантовый коллапс (Престиж)", "req_type": "prestige", "req_val": 1},
    {"id": "ach_card_leak", "name": "Кибер-Хакер", "desc": "Перехватить первую виртуальную карту из аномалии", "req_type": "card_leak", "req_val": 1},
    {"id": "ach_vip_buy", "name": "Донатный Барон", "desc": "Купить первый предмет в Донат-магазине", "req_type": "vip_buy", "req_val": 1}
]

def format_number(val):
    if val < 0:
        return "0"
    if val < 1000:
        if val >= 10:
            return f"{val:.1f}" if val != int(val) else f"{int(val)}"
        return f"{val:.2f}" if val != int(val) else f"{int(val)}"
    suffixes = [
        (1e15, "Q"),
        (1e12, "T"),
        (1e9, "B"),
        (1e6, "M"),
        (1e3, "K")
    ]
    for threshold, suffix in suffixes:
        if val >= threshold:
            num = val / threshold
            if num >= 100:
                return f"{num:.1f}{suffix}"
            else:
                return f"{num:.2f}{suffix}"
    return f"{int(val):,}"

class CoreEngine:
    def __init__(self):
        self.energy = 0.0
        self.dark_matter = 0.0
        self.total_energy_earned = 0.0
        self.total_clicks = 0
        self.total_crits = 0
        self.highest_combo = 1.0
        self.anomalies_caught = 0
        self.prestige_count = 0
        self.cards_intercepted = 0
        self.vip_items_bought_count = 0
        self.play_time = 0.0
        self.last_save_time = time.time()
        self.offline_report = None

        # Fake Bank Cards system: ALL CARDS LOCKED FROM THE BOX!
        self.player_cards = {}
        for c in FAKE_CARDS_DATABASE:
            self.player_cards[c["id"]] = {
                "balance": float(c["initial_balance"]),
                "unlocked": False  # NONE UNLOCKED BY DEFAULT
            }
        self.active_card_id = None
        self.intercepted_leaks = []  # IDs of leaked cards that player has discovered
        self.purchased_vip_items = set()

        # Combo system
        self.combo_meter = 0.0
        self.is_hyperdrive = False
        self.hyperdrive_timer = 0.0
        self.hyperdrive_duration = 8.0

        # Buffs from anomalies
        self.active_buffs = {
            "click_mult": {"factor": 1.0, "time_left": 0.0, "name": "Перегрузка Мощности (7x Клик)"},
            "eps_mult": {"factor": 1.0, "time_left": 0.0, "name": "Ускорение Времени (3x EPS)"}
        }

        # Generators
        self.generators = {}
        for g in GENERATOR_DEFS:
            self.generators[g["id"]] = {
                "count": 0,
                "multiplier": 1.0
            }

        # Upgrades & Artifacts
        self.purchased_upgrades = set()
        self.purchased_artifacts = set()
        self.unlocked_achievements = set()

        # Autoclick accumulator
        self.autoclick_accumulator = 0.0

        # Load saved game
        self.load_game()

    def get_unlocked_cards(self):
        unlocked = []
        for c in FAKE_CARDS_DATABASE:
            cid = c["id"]
            if self.player_cards.get(cid, {}).get("unlocked", False):
                card_data = dict(c)
                card_data["balance"] = self.player_cards[cid]["balance"]
                unlocked.append(card_data)
        return unlocked

    def get_active_card(self):
        unlocked = self.get_unlocked_cards()
        if not unlocked:
            return None
        active = next((c for c in unlocked if c["id"] == self.active_card_id), None)
        if not active:
            active = unlocked[0]
            self.active_card_id = active["id"]
        return active

    def cycle_card(self, direction=1):
        unlocked = self.get_unlocked_cards()
        if not unlocked:
            return
        ids = [c["id"] for c in unlocked]
        try:
            cur_idx = ids.index(self.active_card_id)
        except (ValueError, TypeError):
            cur_idx = 0
        new_idx = (cur_idx + direction) % len(ids)
        self.active_card_id = ids[new_idx]

    def link_card_manual(self, num_input, exp_input, cvv_input):
        """
        Validates manually typed card credentials against FAKE_CARDS_DATABASE.
        Normalizes spaces and dashes.
        """
        clean_typed_num = num_input.replace(" ", "").replace("-", "").strip()
        clean_typed_exp = exp_input.strip()
        clean_typed_cvv = cvv_input.strip()

        matched_card = None
        for c in FAKE_CARDS_DATABASE:
            c_num = c["clean_num"]
            if clean_typed_num == c_num:
                # Number matches, check exp and cvv if entered
                matched_card = c
                break

        if not matched_card:
            return False, None, "Неверный номер карты! Данные не найдены в банковском реестре."

        # Verify exp and cvv
        if clean_typed_exp and clean_typed_exp != matched_card["exp"]:
            return False, None, f"Неверный срок действия! Проверьте дату (формат MM/YY)."

        if clean_typed_cvv and clean_typed_cvv != matched_card["cvv"]:
            return False, None, f"Неверный CVV код безопасности!"

        cid = matched_card["id"]
        if self.player_cards[cid]["unlocked"]:
            self.active_card_id = cid
            return False, matched_card, f"Карта '{matched_card['name']}' уже привязана к терминалу!"

        # Success: unlock the card!
        self.player_cards[cid]["unlocked"] = True
        self.active_card_id = cid
        self.cards_intercepted = max(self.cards_intercepted, len(self.get_unlocked_cards()))
        return True, matched_card, f"Карта '{matched_card['name']}' успешно привязана! Доступен баланс: ${matched_card['initial_balance']:,.2f}"

    def buy_vip_item(self, item_id):
        item = next((it for it in DONATE_SHOP_ITEMS if it["id"] == item_id), None)
        if not item:
            return False, "Предмет не найден!"

        if item["type"] == "permanent" and item_id in self.purchased_vip_items:
            return False, "Этот VIP-бустер уже активирован!"

        active_card = self.get_active_card()
        if not active_card:
            return False, "Сначала привяжите банковскую карту, введя ее реквизиты!"

        cid = active_card["id"]
        cur_bal = self.player_cards[cid]["balance"]
        price = item["price"]

        if cur_bal < price:
            return False, f"Недостаточно средств на карте! Баланс: ${cur_bal:,.2f}, цена: ${price:,.2f}"

        self.player_cards[cid]["balance"] -= price

        if item["type"] == "permanent":
            self.purchased_vip_items.add(item_id)
        elif item["type"] == "instant_energy":
            self.energy += item["val"]
            self.total_energy_earned += item["val"]
        elif item["type"] == "instant_dm":
            self.dark_matter += item["val"]

        self.vip_items_bought_count += 1
        return True, f"Успешно куплено: {item['name']}!"

    def get_base_click_power(self):
        base = 1.0
        if "art_dark_spark" in self.purchased_artifacts:
            base += 25.0
        for upg in UPGRADE_DEFS:
            if upg["id"] in self.purchased_upgrades and upg["type"] == "click_mult":
                base *= upg["val"]
        return base

    def get_synergy_click_bonus(self):
        pct = 0.0
        for upg in UPGRADE_DEFS:
            if upg["id"] in self.purchased_upgrades and upg["type"] == "click_eps_pct":
                pct += upg["val"]
        if "donate_turbo_click" in self.purchased_vip_items:
            pct += 0.10
        return self.get_eps() * pct

    def get_crit_chance_and_mult(self):
        chance = 0.05
        mult = 3.0
        for upg in UPGRADE_DEFS:
            if upg["id"] in self.purchased_upgrades and upg["type"] == "crit_boost":
                chance += upg["chance_val"]
                mult += upg["mult_val"]
        if "donate_gold_core" in self.purchased_vip_items:
            chance += 0.20
            mult += 2.0
        return min(chance, 0.85), mult

    def get_dark_matter_bonus(self):
        dm_power = 0.10
        if "art_void_core" in self.purchased_artifacts:
            dm_power += 0.25 * 0.10
        ach_mult = 1.0 + (len(self.unlocked_achievements) * 0.02)
        return (1.0 + self.dark_matter * dm_power) * ach_mult

    def get_global_multiplier(self):
        mult = self.get_dark_matter_bonus()
        for upg in UPGRADE_DEFS:
            if upg["id"] in self.purchased_upgrades and upg["type"] == "global_mult":
                mult *= upg["val"]
        if "donate_vip_status" in self.purchased_vip_items:
            mult *= 2.0
        if "donate_gold_core" in self.purchased_vip_items:
            mult *= 5.0
        return mult

    def get_eps(self):
        total_eps = 0.0
        all_gen_mult = 1.0
        for upg in UPGRADE_DEFS:
            if upg["id"] in self.purchased_upgrades and upg["type"] == "all_gen_mult":
                all_gen_mult *= upg["val"]

        for g in GENERATOR_DEFS:
            gid = g["id"]
            state = self.generators[gid]
            count = state["count"]
            if count > 0:
                gen_mult = state["multiplier"]
                for upg in UPGRADE_DEFS:
                    if upg["id"] in self.purchased_upgrades and upg["type"] == "gen_mult":
                        if upg.get("target") == gid:
                            gen_mult *= upg["val"]
                total_eps += count * g["base_eps"] * gen_mult

        total_eps *= all_gen_mult
        total_eps *= self.get_global_multiplier()

        if "donate_chrono_speed" in self.purchased_vip_items:
            total_eps *= 3.0

        if self.active_buffs["eps_mult"]["time_left"] > 0:
            total_eps *= self.active_buffs["eps_mult"]["factor"]

        if self.is_hyperdrive:
            total_eps *= 1.5

        return total_eps

    def get_combo_multiplier(self):
        max_cap = 8.0 if "art_hyper_reactor" in self.purchased_artifacts else 5.0
        if self.is_hyperdrive:
            return max_cap
        if self.combo_meter < 25.0:
            return 1.0
        elif self.combo_meter < 50.0:
            return 1.5
        elif self.combo_meter < 75.0:
            return 2.0
        elif self.combo_meter < 95.0:
            return 3.0
        else:
            return 4.0

    def click_core(self):
        self.total_clicks += 1
        base = self.get_base_click_power() + self.get_synergy_click_bonus()
        base *= self.get_global_multiplier()

        if self.active_buffs["click_mult"]["time_left"] > 0:
            base *= self.active_buffs["click_mult"]["factor"]

        combo_mult = self.get_combo_multiplier()
        base *= combo_mult

        crit_chance, crit_mult = self.get_crit_chance_and_mult()
        is_crit = random.random() < crit_chance
        if is_crit:
            base *= crit_mult
            self.total_crits += 1

        self.energy += base
        self.total_energy_earned += base

        if not self.is_hyperdrive:
            self.combo_meter = min(100.0, self.combo_meter + 3.5)
            if self.combo_meter >= 100.0:
                self.trigger_hyperdrive()

        if combo_mult > self.highest_combo:
            self.highest_combo = combo_mult

        return base, is_crit

    def trigger_hyperdrive(self):
        self.is_hyperdrive = True
        duration = 8.0
        for upg in UPGRADE_DEFS:
            if upg["id"] in self.purchased_upgrades and upg["type"] == "hyper_duration":
                duration = upg["val"]
        self.hyperdrive_duration = duration
        self.hyperdrive_timer = duration
        self.combo_meter = 100.0

    def get_generator_cost(self, gen_id, buy_mode="x1"):
        g_def = next(g for g in GENERATOR_DEFS if g["id"] == gen_id)
        current_count = self.generators[gen_id]["count"]
        r = g_def["cost_multiplier"]
        b = g_def["base_cost"]

        if buy_mode == "x1":
            cost = b * (r ** current_count)
            return int(cost), 1
        elif buy_mode in ("x10", "x25"):
            k = 10 if buy_mode == "x10" else 25
            cost = b * (r ** current_count) * ((r ** k) - 1.0) / (r - 1.0)
            return int(cost), k
        elif buy_mode == "MAX":
            if self.energy < b * (r ** current_count):
                return int(b * (r ** current_count)), 0
            val = 1.0 + self.energy * (r - 1.0) / (b * (r ** current_count))
            k = max(1, int(math.floor(math.log(val) / math.log(r))))
            cost = b * (r ** current_count) * ((r ** k) - 1.0) / (r - 1.0)
            return int(cost), k

        return int(b * (r ** current_count)), 1

    def buy_generator(self, gen_id, buy_mode="x1"):
        cost, count = self.get_generator_cost(gen_id, buy_mode)
        if count > 0 and self.energy >= cost:
            self.energy -= cost
            self.generators[gen_id]["count"] += count
            return True, count, cost
        return False, 0, cost

    def buy_upgrade(self, upg_id):
        upg = next((u for u in UPGRADE_DEFS if u["id"] == upg_id), None)
        if upg and upg_id not in self.purchased_upgrades:
            if self.energy >= upg["cost"]:
                self.energy -= upg["cost"]
                self.purchased_upgrades.add(upg_id)
                return True
        return False

    def buy_artifact(self, art_id):
        art = next((a for a in ARTIFACT_DEFS if a["id"] == art_id), None)
        if art and art_id not in self.purchased_artifacts:
            if self.dark_matter >= art["cost"]:
                self.dark_matter -= art["cost"]
                self.purchased_artifacts.add(art_id)
                return True
        return False

    def get_prestige_dark_matter_gain(self):
        if self.total_energy_earned < 1000000:
            return 0
        return int(math.floor(math.sqrt(self.total_energy_earned / 1000000.0)))

    def can_prestige(self):
        return self.get_prestige_dark_matter_gain() > 0

    def trigger_prestige(self):
        gain = self.get_prestige_dark_matter_gain()
        if gain <= 0:
            return False, 0

        self.dark_matter += gain
        self.prestige_count += 1

        start_energy = 0.0
        if "art_dark_spark" in self.purchased_artifacts:
            start_energy = 10000.0
        self.energy = start_energy
        self.combo_meter = 0.0
        self.is_hyperdrive = False

        for g in self.generators.values():
            g["count"] = 0
            g["multiplier"] = 1.0

        self.purchased_upgrades.clear()
        self.save_game()
        return True, gain

    def apply_anomaly_reward(self, reward_type):
        self.anomalies_caught += 1

        if reward_type == "surge":
            val = max(self.get_eps() * 30.0, self.get_base_click_power() * 150.0)
            self.energy += val
            self.total_energy_earned += val
            return ("surge", f"Квантовый Скачок: +{format_number(val)}⚡ энергии!")

        elif reward_type == "frenzy":
            self.active_buffs["click_mult"]["factor"] = 7.0
            self.active_buffs["click_mult"]["time_left"] = 15.0
            return ("frenzy", "Гипер-Фокус: Мощность клика x7 на 15 сек!")

        elif reward_type == "warp":
            self.active_buffs["eps_mult"]["factor"] = 3.0
            self.active_buffs["eps_mult"]["time_left"] = 20.0
            return ("warp", "Хроно-Варп: Выработка генераторов x3 на 20 сек!")

        elif reward_type == "hyper":
            self.trigger_hyperdrive()
            return ("hyper", "Синхронизация Реактора: Мгновенный HYPERDRIVE!")

        elif reward_type == "card_leak":
            # Select unintercepted cards first
            unintercepted = [c for c in FAKE_CARDS_DATABASE if c["id"] not in self.intercepted_leaks]
            if unintercepted:
                target_card = unintercepted[0]
                self.intercepted_leaks.append(target_card["id"])
            else:
                target_card = random.choice(FAKE_CARDS_DATABASE)

            return ("card_leak", target_card)

        return ("none", "")

    def update(self, dt):
        self.play_time += dt

        eps = self.get_eps()
        if eps > 0:
            gain = eps * dt
            self.energy += gain
            self.total_energy_earned += gain

        autoclick_rate = 0.0
        for upg in UPGRADE_DEFS:
            if upg["id"] in self.purchased_upgrades and upg["type"] == "autoclick":
                autoclick_rate += upg["val"]

        if autoclick_rate > 0:
            self.autoclick_accumulator += autoclick_rate * dt
            while self.autoclick_accumulator >= 1.0:
                self.autoclick_accumulator -= 1.0
                self.click_core()

        for b in self.active_buffs.values():
            if b["time_left"] > 0:
                b["time_left"] = max(0.0, b["time_left"] - dt)

        if "donate_perm_hyper" in self.purchased_vip_items:
            self.combo_meter = max(75.0, self.combo_meter)

        if self.is_hyperdrive:
            self.hyperdrive_timer -= dt
            if self.hyperdrive_timer <= 0:
                self.is_hyperdrive = False
                self.combo_meter = 75.0 if "donate_perm_hyper" in self.purchased_vip_items else 35.0
        else:
            decay_rate = 14.0
            for upg in UPGRADE_DEFS:
                if upg["id"] in self.purchased_upgrades and upg["type"] == "combo_decay":
                    decay_rate *= upg["val"]
            if self.combo_meter > 0:
                min_floor = 75.0 if "donate_perm_hyper" in self.purchased_vip_items else 0.0
                self.combo_meter = max(min_floor, self.combo_meter - decay_rate * dt)

        # Check achievements
        new_achievements = []
        total_gens = sum(g["count"] for g in self.generators.values())
        unlocked_cards_count = len(self.get_unlocked_cards())

        for ach in ACHIEVEMENT_DEFS:
            if ach["id"] not in self.unlocked_achievements:
                unlocked = False
                t = ach["req_type"]
                v = ach["req_val"]
                if t == "clicks" and self.total_clicks >= v:
                    unlocked = True
                elif t == "all_energy" and self.total_energy_earned >= v:
                    unlocked = True
                elif t == "hyper" and self.is_hyperdrive:
                    unlocked = True
                elif t == "anomalies" and self.anomalies_caught >= v:
                    unlocked = True
                elif t == "crits" and self.total_crits >= v:
                    unlocked = True
                elif t == "total_gens" and total_gens >= v:
                    unlocked = True
                elif t == "prestige" and self.prestige_count >= v:
                    unlocked = True
                elif t == "card_leak" and unlocked_cards_count >= v:
                    unlocked = True
                elif t == "vip_buy" and self.vip_items_bought_count >= v:
                    unlocked = True

                if unlocked:
                    self.unlocked_achievements.add(ach["id"])
                    new_achievements.append(ach)

        if time.time() - self.last_save_time > 15:
            self.save_game()

        return new_achievements

    def save_game(self):
        try:
            data = {
                "energy": self.energy,
                "dark_matter": self.dark_matter,
                "total_energy_earned": self.total_energy_earned,
                "total_clicks": self.total_clicks,
                "total_crits": self.total_crits,
                "highest_combo": self.highest_combo,
                "anomalies_caught": self.anomalies_caught,
                "prestige_count": self.prestige_count,
                "cards_intercepted": self.cards_intercepted,
                "vip_items_bought_count": self.vip_items_bought_count,
                "play_time": self.play_time,
                "last_timestamp": time.time(),
                "generators": self.generators,
                "purchased_upgrades": list(self.purchased_upgrades),
                "purchased_artifacts": list(self.purchased_artifacts),
                "unlocked_achievements": list(self.unlocked_achievements),
                "player_cards": self.player_cards,
                "active_card_id": self.active_card_id,
                "intercepted_leaks": self.intercepted_leaks,
                "purchased_vip_items": list(self.purchased_vip_items)
            }
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.last_save_time = time.time()
        except Exception as e:
            print(f"Error saving game: {e}")

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.energy = data.get("energy", 0.0)
            self.dark_matter = data.get("dark_matter", 0.0)
            self.total_energy_earned = data.get("total_energy_earned", 0.0)
            self.total_clicks = data.get("total_clicks", 0)
            self.total_crits = data.get("total_crits", 0)
            self.highest_combo = data.get("highest_combo", 1.0)
            self.anomalies_caught = data.get("anomalies_caught", 0)
            self.prestige_count = data.get("prestige_count", 0)
            self.cards_intercepted = data.get("cards_intercepted", 0)
            self.vip_items_bought_count = data.get("vip_items_bought_count", 0)
            self.play_time = data.get("play_time", 0.0)

            saved_gens = data.get("generators", {})
            for gid, gstate in saved_gens.items():
                if gid in self.generators:
                    self.generators[gid]["count"] = gstate.get("count", 0)
                    self.generators[gid]["multiplier"] = gstate.get("multiplier", 1.0)

            self.purchased_upgrades = set(data.get("purchased_upgrades", []))
            self.purchased_artifacts = set(data.get("purchased_artifacts", []))
            self.unlocked_achievements = set(data.get("unlocked_achievements", []))
            self.purchased_vip_items = set(data.get("purchased_vip_items", []))
            self.intercepted_leaks = data.get("intercepted_leaks", [])

            saved_cards = data.get("player_cards", {})
            for cid, cstate in saved_cards.items():
                if cid in self.player_cards:
                    self.player_cards[cid]["balance"] = cstate.get("balance", 0.0)
                    self.player_cards[cid]["unlocked"] = cstate.get("unlocked", False)

            self.active_card_id = data.get("active_card_id", None)

            last_ts = data.get("last_timestamp", 0)
            if last_ts > 0:
                elapsed = time.time() - last_ts
                if elapsed > 15:
                    capped_elapsed = min(elapsed, 24 * 3600)
                    offline_eps = self.get_eps() * 0.5
                    offline_gain = offline_eps * capped_elapsed
                    if offline_gain > 0:
                        self.energy += offline_gain
                        self.total_energy_earned += offline_gain
                        self.offline_report = {
                            "seconds": int(capped_elapsed),
                            "energy": offline_gain
                        }
        except Exception as e:
            print(f"Error loading save: {e}")

    def reset_save(self):
        try:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            self.__init__()
        except Exception as e:
            print(f"Error resetting save: {e}")
