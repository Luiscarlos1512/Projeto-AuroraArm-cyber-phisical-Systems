# ETAPA 6: compila C gerado e compara 1.000 saídas com o modelo Python (SIL).
import ctypes,subprocess
import numpy as np
from auroraarm.codegen import generate
from auroraarm.control import Controller

def test_sil_equivalence(tmp_path):
 src=tmp_path/'controller_generated.c';so=tmp_path/'controller.so';generate(src)
 subprocess.run(['gcc','-shared','-fPIC','-O2',str(src),'-lm','-o',str(so)],check=True)
 lib=ctypes.CDLL(str(so))
 class CState(ctypes.Structure):_fields_=[('integrator',ctypes.c_double)]
 lib.aa_step.argtypes=[ctypes.POINTER(CState),ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_int]
 lib.aa_step.restype=ctypes.c_double
 c=CState(0); py=Controller(); diffs=[]
 for k in range(1000):
  t=k*.002; enabled=0 if 400<=k<410 else 1
  x=[6*np.sin(13*t),80*np.sin(1.3*t),3*np.sin(1.7*t)]; ref=.03*np.sin(.8*t)
  y1=py.step(ref,x,enabled);y2=lib.aa_step(ctypes.byref(c),ref,*x,enabled)
  diffs.append(abs(y1-y2))
 print(f"SIL: Emax={max(diffs):.17g}; epsilon_float64={np.finfo(float).eps:.17g}; amostras={len(diffs)}")
 assert max(diffs)<1e-10,max(diffs)
