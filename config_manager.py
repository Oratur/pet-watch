# config_manager.py
import json

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "DEVICE_NAME": "COLEIRA_PET",
    "DEVICE_MAC_ADDRESS": None,
    "PERIMETER_RADIUS_METERS": 10.0,
    "TX_POWER_AT_1M": -59,
    "PATH_LOSS_EXPONENT_N": 2.0,
    "SCAN_INTERVAL_SECONDS": 5,
    "STATUS_UPDATE_URL": "http://example.com/api/pet_status"
}

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Garantir que todas as chaves default existam
            for key, value in DEFAULT_CONFIG.items():
                config.setdefault(key, value)
            return config
    except FileNotFoundError:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=2)

# Variável global para manter a configuração carregada
current_config = load_config()