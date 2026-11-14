"""ETAPA 1 — Modelo matemático do motor e da junta do AuroraArm.

Estados: corrente elétrica i (A), velocidade do motor omega (rad/s) e
posição angular do eixo do motor theta (rad). A junta gira theta/N.
A perturbação de carga TLOAD é torque REFLETIDO no eixo do motor.
"""

import numpy as np                       # Biblioteca para vetores, matrizes e autovalores.
from scipy.linalg import expm           # Exponencial matricial para discretização exata.

# PARÂMETROS DO ENUNCIADO: conservar unidades do Sistema Internacional.
R = 0.8                 # Resistência da armadura: ohm.
L = 1.2e-3              # Indutância da armadura: henry.
KT = 0.085              # Constante de torque: N.m/A.
KE = 0.085              # Constante de força contraeletromotriz: V.s/rad.
J = 4.2e-4              # Inércia equivalente no eixo do motor: kg.m².
B = 1.5e-4              # Atrito viscoso: N.m.s/rad.
N = 100.0               # Redução da transmissão harmônica: 100 para 1.
VMAX = 48.0             # Tensão máxima fornecida pelo acionamento: V.
IMAX = 8.0              # Corrente máxima admissível: A.
TS = 0.002              # Período do controlador: 2 ms, ou 500 Hz.
TLOAD = 0.25            # Torque de carga refletido para o teste crítico: N.m.

# EQUAÇÃO ELÉTRICA: L*di/dt = V - R*i - KE*omega.
# EQUAÇÃO MECÂNICA: J*domega/dt = KT*i - B*omega - torque_carga.
# Escolhemos x=[i, omega] para calcular o modelo elétrico-mecânico 2x2.
A = np.array([[-R/L, -KE/L], [KT/J, -B/J]], dtype=float)
Bu = np.array([[1/L], [0]], dtype=float)       # Entrada de controle: tensão V.
Bd = np.array([[0], [-1/J]], dtype=float)     # Entrada de perturbação: torque de carga.
C_omega = np.array([[0, 1]], dtype=float)    # Saída medida: velocidade do motor.
C_theta = np.array([[0, 0, 1/N]], dtype=float) # Saída de posição: posição da junta.

# Acrescenta theta como terceiro estado: dtheta/dt = omega.
A3 = np.array([[-R/L, -KE/L, 0], [KT/J, -B/J, 0], [0, 1, 0]], dtype=float)
B3 = np.array([[1/L], [0], [0]], dtype=float)
D3 = np.array([[0], [-1/J], [0]], dtype=float)


def _complex_pairs(values):
    """Converte números reais/complexos do NumPy em pares JSON [real, imaginário]."""
    return [
        [float(value.real), float(value.imag)]
        for value in np.asarray(values).reshape(-1)
    ]


def discretize():
    """Obtém x[k+1]=F*x[k]+G*V[k]+H*torque[k] via retenção de ordem zero."""
    # Monta uma matriz aumentada para discretizar estados e entradas juntos.
    bloco = np.zeros((5, 5), dtype=float)
    bloco[:3, :3] = A3
    bloco[:3, 3:4] = B3
    bloco[:3, 4:5] = D3
    # A exponencial de (bloco*TS) fornece a transição exata por amostra.
    discreto = expm(bloco * TS)
    F = discreto[:3, :3]       # Influência dos estados atuais.
    G = discreto[:3, 3:4]      # Influência da tensão aplicada.
    H = discreto[:3, 4:5]      # Influência do torque de carga.
    return F, G, H


def analysis():
    """Calcula números que devem ser explicados no memorial de cálculo."""
    # Controlabilidade: [B, A*B] precisa ter posto 2.
    controlabilidade = np.column_stack((Bu, A @ Bu))
    # Observabilidade de velocidade: [C; C*A] precisa ter posto 2.
    observabilidade = np.vstack((C_omega, C_omega @ A))
    autovalores = np.linalg.eigvals(A)
    # Regime estacionário com velocidade de motor 450 rad/s e carga de 0,25 N.m.
    corrente = (B * 450 + TLOAD) / KT
    tensao = R * corrente + KE * 450
    # Mantém o valor modal completo; polos complexos são preservados no resultado.
    taus = -1.0 / autovalores
    # O tempo de decaimento depende da parte real do polo e também funciona
    # quando os autovalores formam um par complexo conjugado.
    taus_decaimento = -1.0 / np.real(autovalores)
    return {
        'A': A.tolist(), 'B': Bu.tolist(), 'C_omega': C_omega.tolist(), 'D': [[0]],
        'autovalores_s-1': _complex_pairs(autovalores),
        'tau_modal_s': _complex_pairs(taus),
        'tau_eletrica_aprox_s': L/R,
        'tau_mecanica_sem_fcem_s': J/B,  # Aproximação isolada; não é o modo lento real.
        'posto_controlabilidade': int(np.linalg.matrix_rank(controlabilidade)),
        'posto_observabilidade_velocidade': int(np.linalg.matrix_rank(observabilidade)),
        'corrente_450_A': corrente, 'tensao_450_V': tensao,
        'folga_corrente_A': IMAX-corrente, 'folga_tensao_V': VMAX-tensao,
        'amostras_tau_modal_lenta': float(max(taus_decaimento)/TS),
        'limite_velocidade_motor_colaborativa_rad_s': .25*N/.35,
    }
