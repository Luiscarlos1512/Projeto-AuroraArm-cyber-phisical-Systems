# ETAPA 6: confirma que o motor é controlável/observável e que o ponto crítico é viável.
import json
import numpy as np
from auroraarm.plant import analysis,A,Bu,C_omega

def test_ranks():
 a=analysis();assert a['posto_controlabilidade']==2;assert a['posto_observabilidade_velocidade']==2

def test_equilibrium():
 a=analysis();assert 0<a['tensao_450_V']<48;assert 0<a['corrente_450_A']<8

def test_analysis_is_json_serializable():
 a=analysis();json.dumps(a)
 assert all(len(valor)==2 for valor in a['autovalores_s-1'])
 assert all(len(valor)==2 for valor in a['tau_modal_s'])
