# distance_calculator.py
import math

def estimate_distance(rssi, tx_power_at_1m, path_loss_exponent_n):
    """
    Estima a distância com base no RSSI.
    RSSI: Received Signal Strength Indication (dBm).
    tx_power_at_1m: Potência do sinal medida a 1 metro de distância (dBm).
    path_loss_exponent_n: Expoente de perda de caminho (geralmente entre 2 e 4).
    Retorna a distância em metros.
    """
    if rssi is None or tx_power_at_1m is None or path_loss_exponent_n is None:
        return None
    
    # Fórmula de propagação do log da distância
    # distance = 10 ^ ((tx_power - RSSI) / (10 * n))
    try:
        # Evitar erros matemáticos se path_loss_exponent_n for zero ou muito pequeno.
        if path_loss_exponent_n == 0:
            return float('inf') # Ou algum outro indicador de erro/distância desconhecida
            
        distance_val = 10 ** ((tx_power_at_1m - rssi) / (10 * path_loss_exponent_n))
        return distance_val
    except Exception as e:
        print(f"Erro ao calcular distância: {e}")
        return None

if __name__ == '__main__':
    # Teste
    rssi_test = -65  # Exemplo de RSSI lido
    tx_power_test = -59 # RSSI a 1 metro (calibrado)
    n_test = 2.0       # Fator ambiental (calibrado)
    
    dist = estimate_distance(rssi_test, tx_power_test, n_test)
    if dist is not None:
        print(f"Para RSSI {rssi_test}, TxPower {tx_power_test}, N {n_test}, a distância estimada é: {dist:.2f} metros")
    
    dist_far = estimate_distance(-80, tx_power_test, n_test)
    if dist_far is not None:
        print(f"Para RSSI -80, a distância estimada é: {dist_far:.2f} metros")

    dist_near = estimate_distance(-50, tx_power_test, n_test)
    if dist_near is not None:
        print(f"Para RSSI -50, a distância estimada é: {dist_near:.2f} metros")