# bluetooth_manager.py
import asyncio
from bleak import BleakScanner
import time

# Variáveis globais para armazenar o último RSSI e timestamp
# Isso é para simplificar o exemplo. Em uma app maior, você poderia usar classes.
last_rssi_info = {"rssi": None, "timestamp": 0}

async def scan_for_device_rssi(device_identifier, is_mac_address=False):
    """
    Escaneia por um dispositivo BLE específico e retorna seu RSSI.
    device_identifier: Nome ou endereço MAC do dispositivo.
    is_mac_address: True se o identifier for um MAC address, False se for um nome.
    """
    global last_rssi_info
    try:
        print(f"Escaneando por {device_identifier}...")
        device = None
        # O timeout aqui é importante para não bloquear indefinidamente
        # A biblioteca bleak pode usar um timeout interno no discover,
        # ou você pode gerenciar o tempo de varredura externamente.
        # Para este exemplo, faremos uma varredura curta.
        devices_found = await BleakScanner.discover(timeout=3.0)

        for d in devices_found:
            if is_mac_address:
                if d.address.upper() == device_identifier.upper():
                    device = d
                    break
            else: # by name
                if d.name and d.name.strip().upper() == device_identifier.strip().upper():
                    device = d
                    break
        
        if device:
            # print(f"Dispositivo encontrado: {device.name} ({device.address}), RSSI: {device.rssi}")
            last_rssi_info["rssi"] = device.rssi
            last_rssi_info["timestamp"] = time.time()
            return device.rssi
        else:
            # print(f"Dispositivo {device_identifier} não encontrado.")
            # Considerar se o RSSI deve ser None ou manter o último válido por um tempo
            # Para este exemplo, se não encontrado, RSSI é None
            last_rssi_info["rssi"] = None 
            # last_rssi_info["timestamp"] = time.time() # ou não atualizar o timestamp
            return None
            
    except Exception as e:
        print(f"Erro durante o scan BLE: {e}")
        last_rssi_info["rssi"] = None
        return None

def get_last_rssi_info():
    """Retorna o último RSSI lido e quando foi lido."""
    return last_rssi_info

# Função wrapper para rodar a função async de forma síncrona no loop principal
def get_device_rssi_sync(device_identifier, is_mac_address=False):
    return asyncio.run(scan_for_device_rssi(device_identifier, is_mac_address))

if __name__ == '__main__':
    # Teste rápido
    from config_manager import current_config
    
    DEVICE_NAME_TO_SCAN = current_config.get("DEVICE_NAME")
    DEVICE_MAC_TO_SCAN = current_config.get("DEVICE_MAC_ADDRESS")

    if DEVICE_MAC_TO_SCAN:
        print(f"Tentando obter RSSI para o MAC: {DEVICE_MAC_TO_SCAN}")
        rssi = get_device_rssi_sync(DEVICE_MAC_TO_SCAN, is_mac_address=True)
    elif DEVICE_NAME_TO_SCAN:
        print(f"Tentando obter RSSI para o nome: {DEVICE_NAME_TO_SCAN}")
        rssi = get_device_rssi_sync(DEVICE_NAME_TO_SCAN, is_mac_address=False)
    else:
        print("Nome do dispositivo ou MAC não configurado.")
        rssi = None
        
    if rssi is not None:
        print(f"RSSI obtido: {rssi}")
    else:
        print("Não foi possível obter o RSSI.")