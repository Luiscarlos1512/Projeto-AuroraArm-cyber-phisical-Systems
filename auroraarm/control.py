"""ETAPA 2 — Controle de posição discreto e restrições de atuador.

O controlador usa realimentação de estados, com integrador de erro.
O anti-windup impede acumular erro quando a tensão fica saturada.
O código é educativo e NÃO constitui uma função de parada segura certificada.
"""

import numpy as np
from scipy.signal import place_poles        # Calcula ganhos a partir de polos desejados.
from .plant import A3, B3, N, TS, VMAX, IMAX, R, KE, discretize

# Como theta é o ângulo do MOTOR, dividimos por N para obter ângulo da JUNTA.
Cpos = np.array([[0, 0, 1/N]], dtype=float)
# Novo estado z: integral (referência - posição da junta).
Aaug = np.block([[A3, np.zeros((3, 1))], [-Cpos, np.zeros((1, 1))]])
Baug = np.vstack((B3, [[0.0]]))
# Os polos definem a dinâmica desejada da malha fechada.
POLES = [-680.0, -52.0, -60.0, -70.0]
# GAIN contém quatro ganhos correspondentes a i, omega, theta e integral.
GAIN = place_poles(Aaug, Baug, POLES).gain_matrix[0]

# Modelo discretizado usado na previsão de corrente da próxima amostra.
F, G, _ = discretize()
F0, G0 = F[0, :], G[0, 0]


def clamp_voltage(command, current, speed, angle=0.0):
    """Restringe a tensão e prevê corrente para o próximo ciclo de 2 ms."""
    # Primeiro aplica o limite físico de +/-48 volts.
    voltage = max(-VMAX, min(VMAX, float(command)))
    # Se a corrente está no teto, bloqueia tensão que faria di/dt crescer.
    if current >= IMAX and voltage-KE*speed-R*current > 0:
        voltage = min(voltage, R*current+KE*speed)
    # Se está no piso negativo, bloqueia tensão que a tornaria mais negativa.
    if current <= -IMAX and voltage-KE*speed-R*current < 0:
        voltage = max(voltage, R*current+KE*speed)
    # Estima a corrente sem novo comando, com a dinâmica discreta da planta.
    base = float(F0 @ np.array([current, speed, angle]))
    # Calcula o intervalo de tensão que mantém a próxima amostra dentro de 7,9 A.
    lower = (-(IMAX-0.1)-base)/G0
    upper = ((IMAX-0.1)-base)/G0
    voltage = max(lower, min(upper, voltage))
    # Retorna comando final dentro do limite físico do acionamento.
    return max(-VMAX, min(VMAX, voltage))


class Controller:
    """Armazena a integral para executar um passo por chamada (500 Hz)."""

    def __init__(self):
        self.z = 0.0  # Inicializa o acumulador integral.

    def step(self, reference, state, enabled=True):
        # Quando o supervisor bloqueia o movimento, zera saída e integral.
        # ATENÇÃO: 0 V de comando não implica torque físico zero imediato.
        if not enabled:
            self.z = 0.0
            return 0.0
        current, speed, theta = state  # Separa as três variáveis de estado.
        error = reference - theta/N    # Erro angular medido na junta.
        # Calcula a ação de controle linear: u = -K*[i, omega, theta, integral].
        raw = -float(GAIN @ np.array([current, speed, theta, self.z]))
        # Impõe limites de tensão/corrente do motor.
        voltage = clamp_voltage(raw, current, speed, theta)
        # Anti-windup: integra quando não há saturação ou a integração ajuda a sair dela.
        if abs(raw-voltage) < 1e-9 or np.sign(error) != np.sign(raw-voltage):
            self.z += TS*error
        return voltage
