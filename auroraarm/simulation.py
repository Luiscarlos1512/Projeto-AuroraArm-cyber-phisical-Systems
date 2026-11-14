"""ETAPA 4 — Executa a simulação e salva gráficos, métricas e análise da planta."""

import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Permite salvar gráficos mesmo sem janela gráfica.
import matplotlib.pyplot as plt
from .plant import TS, N, IMAX, TLOAD, discretize, analysis
from .control import Controller
from .safety import bounded_deadline_check


def simulate(ref=.035, seconds=1.0, load=0.0):
    """Simula resposta a degrau de posição, devolvendo amostras e indicadores."""
    F, G, H = discretize()  # Recupera modelo discreto com tensão e torque de carga.
    x = np.zeros(3)       # Estado inicial: motor parado, posição e corrente zero.
    controller = Controller() # Cria controlador com integral inicialmente zerada.
    rows = []             # Guarda tempo, posição da junta, velocidade, corrente, tensão.
    for sample in range(round(seconds/TS)):
        command = controller.step(ref, x)  # Controla a planta na amostra atual.
        rows.append([sample*TS, x[2]/N, x[1], x[0], command])
        # Avança a planta por 2 ms aplicando tensão e perturbação de carga.
        x = F @ x + G[:, 0]*command + H[:, 0]*load
    data = np.array(rows)
    # Aproxima erro estacionário pela média das últimas 50 amostras da simulação.
    final_position = data[-50:, 1].mean()
    error = abs(ref-final_position)
    peak = data[:, 1].max()  # Maior posição atingida na simulação.
    overshoot = max(0.0, (peak-ref)/max(abs(ref), 1e-12)*100)
    # Define acomodação como permanência na banda de +/-2% da referência.
    outside = np.where(abs(data[:, 1]-ref) > 0.02*abs(ref))[0]
    settling = round((outside.max()+1)*TS, 5) if len(outside) else 0.0
    max_current = float(np.abs(data[:, 3]).max())
    max_voltage = float(np.abs(data[:, 4]).max())
    metrics = {
        'ref_rad': ref, 'erro_regime_rad': float(error),
        'sobressinal_percent': float(overshoot),
        'acomodacao_2pct_s': settling,
        'max_corrente_A': max_current, 'max_tensao_V': max_voltage,
        'corrente_limite_atendida': bool(max_current <= IMAX+1e-5),
    }
    return data, metrics


def main():
    # Localiza pasta de resultados automaticamente a partir deste arquivo.
    root = Path(__file__).resolve().parents[1]
    out = root/'results'
    out.mkdir(exist_ok=True)
    # Compara motor sem carga com motor sob o torque refletido de 0,25 N.m.
    data_free, metrics_free = simulate()
    data_loaded, metrics_loaded = simulate(load=TLOAD)
    payload = {
        'planta': analysis(), 'resposta_sem_carga': metrics_free,
        'resposta_com_carga_0_25Nm': metrics_loaded,
        'seguranca_grade': bounded_deadline_check(),
        'observacao': 'Posicao da junta 0,035 rad. 450 rad/s e ponto critico do motor, nao modo colaborativo.',
    }
    # Grava JSON que permite consultar todos os resultados numericamente.
    (out/'metricas.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf8')
    # Salva dois arquivos PNG, um por condição de torque.
    for filename, curve in [('resposta_posicao.png', data_free),
                            ('resposta_com_carga.png', data_loaded)]:
        fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)
        axes[0].plot(curve[:, 0], curve[:, 1], label='Posição da junta')
        axes[0].axhline(.035, linestyle='--', label='Referência')
        axes[0].set_ylabel('rad')
        axes[0].legend()
        axes[1].plot(curve[:, 0], curve[:, 3])
        axes[1].axhline(8, linestyle=':')
        axes[1].axhline(-8, linestyle=':')
        axes[1].set_ylabel('Corrente (A)')
        axes[2].plot(curve[:, 0], curve[:, 4])
        axes[2].set_ylabel('Tensão (V)')
        axes[2].set_xlabel('Tempo (s)')
        fig.tight_layout()
        fig.savefig(out/filename, dpi=160)
        plt.close(fig)  # Libera memória depois de gravar o gráfico.
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()  # Executa somente quando este módulo for iniciado diretament.******