# ETAPA 6: exercita o autômato e varre a grade limitada de atrasos de segurança.
from auroraarm.safety import *

def test_deadline_grid():
 r=bounded_deadline_check();assert r['violacoes']==0 and r['pior_tempo_ms']==84

def test_no_auto_restart():
 s=Supervisor();s.step(near=True);s.step(ready=True);s.step(clear=True)
 assert s.state==WAIT_REARM and not s.motion_enabled
 s.step(clear=True);assert s.state==WAIT_REARM
 s.step(clear=True,rearm=True); assert s.state==RESUME

def test_stop_on_reentry():
 s=Supervisor();s.step(near=True);s.step(ready=True);s.step(clear=True);s.step(near=True)
 assert s.state==STOPPED
