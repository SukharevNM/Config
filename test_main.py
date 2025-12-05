import unittest
import json
import tempfile
import subprocess
import sys
from pathlib import Path


class ConfigLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.TemporaryDirectory()
        cls.test_path = Path(cls.test_dir.name)
        cls.conversion_script = Path(__file__).parent / "main.py"

        # Создаем тестовые конфиги
        configs = {
            "web_server.conf": WEB_SERVER_CONF,
            "geometry.conf": GEOMETRY_CONF,
            "game.conf": GAME_CONF,
            "invalid_syntax.conf": INVALID_SYNTAX_CONF,
            "invalid_semantics.conf": INVALID_SEMANTICS_CONF
        }

        for filename, content in configs.items():
            (cls.test_path / filename).write_text(content, encoding='utf-8')

        # Ожидаемые результаты
        cls.expected_results = {
            "web_server.conf": json.loads(WEB_SERVER_JSON),
            "geometry.conf": json.loads(GEOMETRY_JSON),
            "game.conf": json.loads(GAME_JSON)
        }

    @classmethod
    def tearDownClass(cls):
        cls.test_dir.cleanup()

    def run_converter(self, input_file):
        """Запускает конвертер и возвращает результат"""
        cmd = [sys.executable, str(self.conversion_script), "--input", str(input_file)]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result

    def test_web_server_config(self):
        """Тест конфигурации веб-сервера"""
        input_file = self.test_path / "web_server.conf"
        result = self.run_converter(input_file)

        self.assertEqual(result.returncode, 0, f"Ошибка выполнения:\n{result.stderr}")
        self.assertEqual(result.stderr, "", "Ожидался пустой stderr")

        try:
            output_json = json.loads(result.stdout)
            self.assertEqual(output_json, self.expected_results["web_server.conf"])
        except json.JSONDecodeError as e:
            self.fail(f"Ошибка разбора JSON: {e}\nВывод:\n{result.stdout}")

    def test_geometry_config(self):
        """Тест геометрических вычислений"""
        input_file = self.test_path / "geometry.conf"
        result = self.run_converter(input_file)

        self.assertEqual(result.returncode, 0, f"Ошибка выполнения:\n{result.stderr}")
        self.assertEqual(result.stderr, "", "Ожидался пустой stderr")

        try:
            output_json = json.loads(result.stdout)
            # Обновленные ожидаемые координаты для unit_circle.points
            self.assertEqual(output_json, self.expected_results["geometry.conf"])
        except json.JSONDecodeError as e:
            self.fail(f"Ошибка разбора JSON: {e}\nВывод:\n{result.stdout}")

    def test_game_config(self):
        """Тест конфигурации игры"""
        input_file = self.test_path / "game.conf"
        result = self.run_converter(input_file)

        self.assertEqual(result.returncode, 0, f"Ошибка выполнения:\n{result.stderr}")
        self.assertEqual(result.stderr, "", "Ожидался пустой stderr")

        try:
            output_json = json.loads(result.stdout)
            self.assertEqual(output_json, self.expected_results["game.conf"])
        except json.JSONDecodeError as e:
            self.fail(f"Ошибка разбора JSON: {e}\nВывод:\n{result.stdout}")

# Ожидаемые JSON результаты (обновленные)
WEB_SERVER_JSON = r'''
{
  "server": {
    "port": 80,
    "ssl": {
      "port": 523,
      "certificate": "/etc/ssl/cert.pem"
    },
    "timeouts": {
      "read": 30,
      "write": 30,
      "keep_alive": 10
    }
  },
  "limits": {
    "max_connections": 1000,
    "max_body_size": 1048576,
    "rate_limit": [100, 200, 300]
  },
  "logging": {
    "level": "debug",
    "path": "/var/log/server.log",
    "retention": 52
  },
  "admins": [
    {
      "name": "John Doe",
      "email": "admin@example.com",
      "permissions": ["read", "write", "delete"]
    },
    {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "permissions": ["read", "write"]
    }
  ],
  "status_page": {
    "path": "/status",
    "secret_key": "A"
  }
}
'''

GEOMETRY_JSON = r'''
{
  "circle": {
    "radius": 5,
    "diameter": 10,
    "circumference": 30,
    "area": 75
  },
  "unit_circle": {
    "radius": 1,
    "area": 3,
    "points": [
      {"x": 1, "y": 0},
      {"x": 0, "y": 1},
      {"x": -1, "y": 0},
      {"x": 0, "y": -1}
    ]
  },
  "angles": {
    "full_angle_deg": 360,
    "full_angle_rad": 6,
    "deg_to_rad_factor": 60,
    "quadrant_angles": [0, 90, 180, 270],
    "radian_marks": [0, 0, 3, 6, 6]
  },
  "special_chars": {
    "pi_symbol": "π",
    "degree_symbol": "°",
    "diameter_symbol": "⌀"
  }
}
'''

GAME_JSON = r'''
{
  "player": {
    "name": "Hero",
    "position": [0, 0],
    "stats": {
      "health": 100,
      "damage": 10,
      "armor": 7,
      "critical_chance": 0
    },
    "inventory": ["sword", "shield", "potion"],
    "max_inventory_size": 10,
    "abilities": [
      {
        "name": "Heal",
        "effect": {
          "health_restore": 25,
          "cooldown": 5
        }
      },
      {
        "name": "Critical Strike",
        "effect": {
          "multiplier": 2,
          "cooldown": 8
        }
      }
    ]
  },
  "enemies": [
    {
      "type": "Goblin",
      "health": 50,
      "damage": 5,
      "loot": ["gold", "dagger"]
    },
    {
      "type": "Dragon",
      "health": 300,
      "damage": 30,
      "special_attack": {
        "name": "Fire Breath",
        "damage": 50,
        "effect": "burn"
      },
      "loot": ["dragon_scale", "fire_gem", "ancient_scroll"]
    }
  ],
  "world": {
    "size": [1000, 1000],
    "spawn_points": [[100, 200], [300, 400], [500, 600]],
    "terrain_types": ["forest", "mountain", "desert", "water"],
    "day_length": 1440
  },
  "game_rules": {
    "difficulty": "normal",
    "respawn_time": 10,
    "currency_symbol": "¤",
    "max_players": 4,
    "version": "1.0.0",
    "version_code": 5
  }
}
'''

# Обновленные тесты с ошибками
INVALID_SYNTAX_CONF = r'''
([
    invalid key "value"  % Пропущено двоеточие
])
'''

INVALID_SEMANTICS_CONF = r'''
(def ZERO 0);
({/ 10 ZERO});
'''

# Содержимое конфигов остается без изменений
WEB_SERVER_CONF = r'''
% Конфигурация веб-сервера
(def MAX_CONNECTIONS 1000);
(def DEFAULT_PORT 80);
(def PORT_OFFSET 443);
(def SSL_PORT {+ DEFAULT_PORT PORT_OFFSET});
(def ADMIN_EMAIL "admin@example.com");
(def LOG_LEVEL "debug");
(def MAX_BODY_SIZE { * 1024 1024 }); % 1MB

([
    server: ([
        port: DEFAULT_PORT,
        ssl: ([
            port: SSL_PORT,
            certificate: "/etc/ssl/cert.pem"
        ]),
        timeouts: ([
            read: 30,
            write: {+ 10 20},
            keep_alive: { * 5 2 }
        ])
    ]),

    limits: ([
        max_connections: MAX_CONNECTIONS,
        max_body_size: MAX_BODY_SIZE,
        rate_limit: array(100, 200, 300)
    ]),

    logging: ([
        level: LOG_LEVEL,
        path: "/var/log/server.log",
        retention: {/ 365 7} % недель в году
    ]),

    admins: array(
        ([
            name: "John Doe",
            email: ADMIN_EMAIL,
            permissions: array("read", "write", "delete")
        ]),
        ([
            name: "Jane Smith",
            email: "jane@example.com",
            permissions: array("read", "write")
        ])
    ),

    status_page: ([
        path: "/status",
        secret_key: {chr 65} % 'A'
    ])
])
'''

GEOMETRY_CONF = r'''
% Геометрические константы и вычисления
(def PI 3);
(def RADIUS 5);
(def DIAMETER { * RADIUS 2 });
(def CIRCUMFERENCE { * PI DIAMETER });
(def AREA { * PI { * RADIUS RADIUS }});
(def UNIT_CIRCLE_RADIUS 1);
(def FULL_ANGLE 360);
(def DEG_TO_RAD { / FULL_ANGLE { * 2 PI }});

([
    circle: ([
        radius: RADIUS,
        diameter: DIAMETER,
        circumference: CIRCUMFERENCE,
        area: AREA
        ]),

    unit_circle: ([
        radius: UNIT_CIRCLE_RADIUS,
        area: { * PI { * UNIT_CIRCLE_RADIUS UNIT_CIRCLE_RADIUS }},
        points: array(
            ([ x: 1, y: 0 ]),
            ([ x: 0, y: 1 ]),
            ([ x: {- 0 1}, y: 0 ]),
            ([ x: 0, y: {- 0 1} ])
        )
    ]),

    angles: ([
        full_angle_deg: FULL_ANGLE,
        full_angle_rad: { * 2 PI },
        deg_to_rad_factor: DEG_TO_RAD,
        quadrant_angles: array(0, 90, 180, 270),
        radian_marks: array(
            { * 0 PI },
            { * 0 PI },
            { * 1 PI },
            { * 2 PI },
            { * 2 PI }
        )
    ]),

    special_chars: ([
        pi_symbol: {chr 960}, % 'π'
        degree_symbol: {chr 176}, % '°'
        diameter_symbol: {chr 8960} % '⌀'
    ])
])
'''

GAME_CONF = r'''
% Конфигурация игрового мира
(def MAX_HEALTH 100);
(def DEFAULT_DAMAGE 10);
(def ARMOR_BONUS 5);
(def CRITICAL_MULTIPLIER 2);
(def START_X 0);
(def START_Y 0);
(def MAX_INVENTORY_SIZE 10);
(def HEAL_AMOUNT 25);
(def BOSS_HEALTH { * MAX_HEALTH 3 });

([
    player: ([
        name: "Hero",
        position: array(START_X, START_Y),
        stats: ([
            health: MAX_HEALTH,
            damage: DEFAULT_DAMAGE,
            armor: {+ ARMOR_BONUS 2},
            critical_chance: 0
        ]),
        inventory: array(
            "sword",
            "shield",
            "potion"
        ),
        max_inventory_size: MAX_INVENTORY_SIZE,
        abilities: array(
            ([
                name: "Heal",
                effect: ([
                    health_restore: HEAL_AMOUNT,
                    cooldown: 5
                ])
            ]),
            ([
                name: "Critical Strike",
                effect: ([
                    multiplier: CRITICAL_MULTIPLIER,
                    cooldown: 8
                ])
            ])
        )
    ]),

    enemies: array(
        ([
            type: "Goblin",
            health: {/ MAX_HEALTH 2},
            damage: 5,
            loot: array("gold", "dagger")
        ]),
        ([
            type: "Dragon",
            health: BOSS_HEALTH,
            damage: { * DEFAULT_DAMAGE 3},
            special_attack: ([
                name: "Fire Breath",
                damage: { * DEFAULT_DAMAGE 5},
                effect: "burn"
            ]),
            loot: array("dragon_scale", "fire_gem", "ancient_scroll")
        ])
    ),

    world: ([
        size: array(1000, 1000),
        spawn_points: array(
            array(100, 200),
            array(300, 400),
            array(500, 600)
        ),
        terrain_types: array("forest", "mountain", "desert", "water"),
        day_length: { * 60 24 } % минут в дне
    ]),

    game_rules: ([
        difficulty: "normal",
        respawn_time: 10,
        currency_symbol: {chr 164}, % '¤'
        max_players: 4,
        version: "1.0.0",
        version_code: {len "1.0.0"}
    ])
])
'''

if __name__ == "__main__":
    print("Запуск тестов конфигурационного языка...")
    unittest.main(verbosity=2)