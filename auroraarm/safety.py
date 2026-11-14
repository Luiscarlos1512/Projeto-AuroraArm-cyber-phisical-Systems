"""ETAPA 3 — Supervisor lógico e análise limitada do requisito de 100 ms.

ESTE CÓDIGO NÃO IMPLEMENTA UMA PARADA SEGURA CERTIFICADA.
Uma função real exige corte físico independente, medição de decaimento
do torque, análise de falhas e verificação formal do autômato temporizado.
"""

# Estados do fluxo operacional (nomes preservados para os testes).
MOVE = 'MOVE'              # Operação normal.
STOPPING = 'STOPPING'      # Comando de interrupção solicitado.
STOPPED = 'STOPPED'        # Controlador informa que interrompeu o movimento.
WAIT_REARM = 'WAIT_REARM'  # Área limpa, esperando autorização humana.
RESUME = 'RESUME'          # Retomada supervisionada.


class Supervisor:
    """Transita entre estados conforme sensores e comandos da operação."""

    def __init__(self):
        self.state = MOVE  # Começa em movimento somente no exemplo simulado.

    def step(self, near=False, clear=False, rearm=False, ready=False):
        old = self.state  # Registra o estado anterior para relatórios/cobertura.
        if self.state == MOVE and near:
            self.state = STOPPING                 # Mão detectada: começa parada.
        elif self.state == STOPPING and ready:
            self.state = STOPPED                  # Confirmação lógica de parada.
        elif self.state == STOPPED and clear:
            self.state = WAIT_REARM               # Não volta automaticamente.
        elif self.state == WAIT_REARM and near:
            self.state = STOPPED                  # Nova presença cancela rearme.
        elif self.state == WAIT_REARM and rearm and clear:
            self.state = RESUME                   # Autoriza retomar se área livre.
        elif self.state == RESUME:
            self.state = STOPPING if near else MOVE  # Reage a nova proximidade.
        return old, self.state

    @property
    def motion_enabled(self):
        # Bloqueia o movimento em estados de parada e espera por rearme.
        return self.state in (MOVE, RESUME)


def bounded_deadline_check(max_sensor_ms=20, max_jitter_ms=2,
                           max_command_ms=2, max_torque_decay_ms=60):
    """Enumera uma grade FINITA de atrasos inteiros em ms.

    O valor de 60 ms para queda do torque é PREMISSA, NÃO MEDIÇÃO.
    Portanto, esta função NÃO demonstra o requisito na máquina real.
    """
    worst = (-1, None)    # Armazena o pior tempo e a combinação responsável.
    violations = []      # Coleta combinações cujo tempo ultrapassa 100 ms.
    cases = 0            # Conta o total de cenários investigados.
    for sensor in range(max_sensor_ms+1):          # 0 a 20 ms de sensor.
        for jitter in (0, max_jitter_ms):          # Sem falha ou perda de um ciclo.
            for command in range(max_command_ms+1): # 0 a 2 ms até comando.
                for torque in range(max_torque_decay_ms+1): # 0 a 60 ms HIPOTÉTICOS.
                    total = sensor+jitter+command+torque
                    cases += 1
                    if total > worst[0]:
                        worst = (total, (sensor, jitter, command, torque))
                    if total > 100:
                        violations.append((sensor, jitter, command, torque, total))
    return {
        'casos': cases, 'pior_tempo_ms': worst[0],
        'pior_combinacao_ms': worst[1], 'violacoes': len(violations),
        'primeira_violacao': violations[0] if violations else None,
        'escopo': 'grade finita; queda do torque de 60 ms e uma premissa sem validacao fisica',
    }
