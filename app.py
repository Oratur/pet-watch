
# from flask import Flask

# app = Flask(__name__)


# @app.route('/')
# def hello():
#     return 'Hello, World!'
# web_server.py
from flask import Flask, request, jsonify
import threading
from config_manager import current_config, save_config, load_config

app = Flask(__name__)

# Status global da coleira (será atualizado pelo main.py)
pet_status_info = {
    "dentro_do_perimetro": None,
    "distancia_aproximada_metros": None,
    "rssi": None,
    "ultimo_contato_timestamp": None,
    "mensagem": "Aguardando primeira leitura..."
}

def update_pet_status(status):
    global pet_status_info
    pet_status_info.update(status)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/configurar_perimetro', methods=['POST'])
def configurar_perimetro():
    global current_config
    try:
        data = request.get_json()
        novo_raio = float(data.get('raio_metros'))
        
        if novo_raio <= 0:
            return jsonify({"erro": "O raio deve ser um valor positivo."}), 400
            
        current_config["PERIMETER_RADIUS_METERS"] = novo_raio
        save_config(current_config)
        current_config = load_config() # Recarrega para garantir consistência se outras chaves forem adicionadas
        
        print(f"Raio do perímetro atualizado para: {novo_raio} metros")
        return jsonify({"mensagem": f"Raio do perímetro configurado para {novo_raio} metros."}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao configurar perímetro: {str(e)}"}), 400

@app.route('/status_coleira', methods=['GET'])
def get_status_coleira():
    # Adiciona o raio atual à resposta para referência
    status_com_raio = pet_status_info.copy()
    status_com_raio["raio_configurado_metros"] = current_config.get("PERIMETER_RADIUS_METERS")
    return jsonify(status_com_raio)

@app.route('/configuracao_atual', methods=['GET'])
def get_configuracao_atual():
    return jsonify(current_config)

def run_server(host='0.0.0.0', port=5000, use_https=False):
    print(f"Iniciando servidor Flask em http{'s' if use_https else ''}://{host}:{port}")
    if use_https:
        # Para HTTPS, você precisará de um certificado SSL.
        # Para desenvolvimento, Flask pode gerar um temporário "adhoc".
        # Para produção, use um certificado real (ex: Let's Encrypt) e um servidor WSGI como Gunicorn + Nginx.
        # Exemplo com 'adhoc' (não recomendado para produção):
        # app.run(host=host, port=port, ssl_context='adhoc', debug=False)
        # Exemplo com arquivos de certificado e chave:
        # context = ('path/to/your/cert.pem', 'path/to/your/key.pem')
        # app.run(host=host, port=port, ssl_context=context, debug=False)
        print("HTTPS com 'adhoc' (apenas para desenvolvimento). Use certificados adequados para produção.")
        app.run(host=host, port=port, ssl_context='adhoc', debug=False, use_reloader=False)
    else:
        app.run(host=host, port=port, debug=False, use_reloader=False)

# Para rodar o servidor em uma thread separada
# O 'use_reloader=False' é importante ao rodar em uma thread para evitar problemas.
def start_web_server_thread(host='0.0.0.0', port=5000, use_https=False):
    thread = threading.Thread(target=run_server, args=(host, port, use_https), daemon=True)
    thread.start()
    return thread

if __name__ == '__main__':
    # Teste rápido do servidor (sem o loop principal do main.py)
    print("Iniciando web_server.py diretamente para teste.")
    print(f"Configuração carregada: {current_config}")
    # Para HTTPS simples (desenvolvimento):
    # run_server(use_https=True)
    # Para HTTP:
    run_server(use_https=False)