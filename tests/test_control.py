# ETAPA 6: confere estabilidade, acomodação, corrente e tensão em dois cenários.
from auroraarm.simulation import simulate

def test_no_load_response():
 ar,m=simulate()
 assert m['sobressinal_percent']<=8 and m['acomodacao_2pct_s']<=.3, m
 assert m['max_tensao_V']<=48+1e-8
 assert m['corrente_limite_atendida'],m
 assert m['erro_regime_rad']<1e-4,m


def test_loaded_response():
 from auroraarm.plant import TLOAD
 _,m=simulate(load=TLOAD)
 assert m["sobressinal_percent"]<=8 and m["acomodacao_2pct_s"]<=.3,m
 assert m["max_tensao_V"]<=48 and m["max_corrente_A"]<=8,m
