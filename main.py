# main.py
import time
import datetime
from config_manager import current_config, load_config
from bluetooth_manager import get_device_rssi_sync, get_last_rssi_info
from distance_calculator import estimate_distance
from app import start_web_server_thread, update_pet_status
from status_reporter import send_status_update # Opcional

# Estado da aplicação
# (o web_server.py também tem uma cópia, idealmente deveria ser compartilhado de forma mais robusta,
# mas para este escopo, sincronizar via update_pet_status é suficiente)
internal_pet_status = {
    "dentro_do_perimetro": None,
    "distancia_aproximada_metros": None,
    "rssi": None,
    "ultimo_contato_timestamp": None,
    "mensagem": "Iniciando monitoramento..."
}

def main_loop():
    global current_config, internal_pet_status
    print("Iniciando loop principal de monitoramento...")
    
    # Carregar configuração mais recente ao iniciar
    current_config = load_config()
    print(f"Configuração inicial: Raio={current_config['PERIMETER_RADIUS_METERS']}m, Dispositivo='{current_config.get('DEVICE_NAME') or current_config.get('DEVICE_MAC_ADDRESS')}'")

    while True:
        # Recarregar configuração periodicamente ou após alteração via API
        # (Flask já recarrega em config_manager quando /configurar_perimetro é chamado)
        # Se precisar ter certeza que o loop principal usa a config mais nova imediatamente:
        # current_config = load_config() # Descomente se achar necessário
        
        device_id = current_config.get("DEVICE_MAC_ADDRESS") or current_config.get("DEVICE_NAME")
        use_mac = bool(current_config.get("DEVICE_MAC_ADDRESS"))

        if not device_id:
            print("ERRO: Nome ou MAC do dispositivo não configurado. Verifique config.json.")
            internal_pet_status.update({
                "mensagem": "Erro: Dispositivo não configurado.",
                "ultimo_contato_timestamp": time.time()
            })
            update_pet_status(internal_pet_status.copy()) # Atualiza o servidor web
            time.sleep(current_config["SCAN_INTERVAL_SECONDS"])
            continue

        # 1. Obter RSSI
        rssi = get_device_rssi_sync(device_id, is_mac_address=use_mac)
        
        if rssi is not None:
            internal_pet_status["rssi"] = rssi
            internal_pet_status["ultimo_contato_timestamp"] = time.time()
            
            # 2. Calcular Distância
            distancia = estimate_distance(
                rssi,
                current_config["TX_POWER_AT_1M"],
                current_config["PATH_LOSS_EXPONENT_N"]
            )
            internal_pet_status["distancia_aproximada_metros"] = round(distancia, 2) if distancia is not None else None
            
            # 3. Verificar Perímetro
            if distancia is not None:
                raio_atual = current_config["PERIMETER_RADIUS_METERS"]
                if distancia <= raio_atual:
                    internal_pet_status["dentro_do_perimetro"] = True
                    internal_pet_status["mensagem"] = f"Dentro do perímetro ({distancia:.2f}m <= {raio_atual}m)."
                else:
                    internal_pet_status["dentro_do_perimetro"] = False
                    internal_pet_status["mensagem"] = f"Fora do perímetro ({distancia:.2f}m > {raio_atual}m)."
                print(f"[{datetime.datetime.now()}] RSSI: {rssi}, Dist: {distancia:.2f}m. Status: {internal_pet_status['mensagem']}")
            else:
                internal_pet_status["dentro_do_perimetro"] = None # Ou False, dependendo da lógica desejada
                internal_pet_status["mensagem"] = "Não foi possível calcular a distância (RSSI disponível, mas cálculo falhou)."
                print(f"[{datetime.datetime.now()}] RSSI: {rssi}, Dist: N/A. Status: {internal_pet_status['mensagem']}")

        else: # Se RSSI é None (dispositivo não encontrado)
            # Considerar quanto tempo esperar antes de declarar "fora" ou "perdido"
            # Aqui, simplesmente atualizamos que não há contato recente.
            internal_pet_status["rssi"] = None
            internal_pet_status["distancia_aproximada_metros"] = None
            internal_pet_status["dentro_do_perimetro"] = False # Ou None, dependendo da política
            internal_pet_status["mensagem"] = f"Coleira '{device_id}' não detectada no último scan."
            # Mantém o último timestamp de contato válido, se houver, ou atualiza para o atual se nunca visto.
            if internal_pet_status.get("ultimo_contato_timestamp") is None:
                 internal_pet_status["ultimo_contato_timestamp"] = time.time() # Primeira vez que não encontra
            print(f"[{datetime.datetime.now()}] Coleira '{device_id}' não encontrada.")

        # 4. Atualizar status para o servidor web
        update_pet_status(internal_pet_status.copy()) # Envia cópia para evitar race conditions
        
        # 5. (Opcional) Enviar status para servidor externo
        if current_config.get("STATUS_UPDATE_URL"):
             send_status_update(internal_pet_status.copy())

        time.sleep(current_config["SCAN_INTERVAL_SECONDS"])

if __name__ == "__main__":
    # Iniciar o servidor web em uma thread separada
    # Defina use_https=True para habilitar HTTPS (requer configuração de certificado ou 'adhoc')
    USE_HTTPS_SERVER = False # Mude para True se quiser HTTPS
    web_server_thread = start_web_server_thread(port=5001, use_https=USE_HTTPS_SERVER) 
    # Usando porta 5001 para não conflitar com outros serviços comuns.
    
    print("Servidor Web iniciado em background. Pressione Ctrl+C para sair.")

    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nEncerrando aplicação...")
    finally:
        print("Aplicação finalizada.")