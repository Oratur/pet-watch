# status_reporter.py
import requests
import json
import time
from config_manager import current_config

def send_status_update(status_data):
    url = current_config.get("STATUS_UPDATE_URL")
    if not url:
        # print("URL de atualização de status não configurada. Não enviando.")
        return

    try:
        payload = {
            "timestamp": time.time(),
            "pet_id": current_config.get("DEVICE_NAME", "coleira_desconhecida"), # Ou algum ID fixo
            "status": status_data
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"Status enviado com sucesso para {url}.")
        else:
            print(f"Erro ao enviar status para {url}: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Falha na conexão ao enviar status para {url}: {e}")
    except Exception as e:
        print(f"Erro inesperado ao enviar status: {e}")


if __name__ == '__main__':
    # Teste
    from config_manager import load_config
    current_config = load_config() # Garante que está atualizado
    
    print(f"Testando envio de status para: {current_config.get('STATUS_UPDATE_URL')}")
    test_status = {
        "dentro_do_perimetro": True,
        "distancia_aproximada_metros": 2.5,
        "rssi": -60
    }
    send_status_update(test_status)