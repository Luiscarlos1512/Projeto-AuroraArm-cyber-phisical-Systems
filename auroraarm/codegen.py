"""Gera automaticamente fonte C da mesma equação de controle do modelo Python."""
# Importa o gravador de arquivos para salvar o firmware gerado.
from pathlib import Path
from .control import GAIN
from .plant import R,KE,TS,VMAX,IMAX,N,discretize

# Este texto é um MODELO de fonte C. Marcadores @@...@@ são substituídos por valores
# calculados pelo Python. O estudante não precisa escrever o firmware à mão.
TEMPLATE='''/* ARQUIVO GERADO AUTOMATICAMENTE: nao editar.\n * Origem: auroraarm/codegen.py + auroraarm/control.py\n * Requisitos: REQ-CTRL-AA-001..004, REQ-SAFE-AA-001..004 (somente interface)\n * Observacao: corte eletrico de torque exige hardware de seguranca independente.\n */
#include <math.h>
/* Estado interno que persiste entre ciclos: erro integral. */
typedef struct { double integrator; } AAController;
/* Inicializa o integrador para iniciar um novo controle. */
void aa_reset(AAController *c) {c->integrator=0.0;}
double aa_step(AAController *c, double ref, double i, double w, double theta, int enabled) {
 /* Sem habilitacao: cancela o comando e reinicia integrador. Nao e corte fisico seguro. */
 if (!enabled) {c->integrator=0.0;return 0.0;}
 const double k0=@@K0@@,k1=@@K1@@,k2=@@K2@@,k3=@@K3@@;
 /* Calcula o erro de posicao da junta (theta e angulo do eixo do motor). */
 double error=ref-theta/@@N@@;
 /* Realimentacao dos estados e do integrador com os ganhos calculados em Python. */
 double raw=-(k0*i+k1*w+k2*theta+k3*c->integrator);
 /* Satura a tensao no intervalo permitido pelo acionamento. */
 double u=fmax(-@@VMAX@@,fmin(@@VMAX@@,raw));
 if (i>=@@IMAX@@ && (u-@@KE@@*w-@@R@@*i)>0.0) u=fmin(u,@@R@@*i+@@KE@@*w);
 if (i<=-@@IMAX@@ && (u-@@KE@@*w-@@R@@*i)<0.0) u=fmax(u,@@R@@*i+@@KE@@*w);
 /* Prediz a corrente do proximo ciclo na ausencia do novo comando. */
 double baseline=@@F00@@*i+@@F01@@*w+@@F02@@*theta;
 u=fmax((-(@@IMAX@@-0.1)-baseline)/@@G0@@,fmin(((@@IMAX@@-0.1)-baseline)/@@G0@@,u));
 u=fmax(-@@VMAX@@,fmin(@@VMAX@@,u));
 /* Anti-windup: so integra quando nao agrava a saturacao. */
 if (fabs(raw-u)<1e-9 || ((error>0)-(error<0))!=((raw-u>0)-(raw-u<0))) c->integrator+=@@TS@@*error;
 return u;
}
'''

def generate(path):
    """Substitui ganhos e constantes no template e grava código C reproduzível."""
    s=TEMPLATE  # Faz uma cópia do template antes das substituições.
    F,G,_=discretize()  # Obtém matrizes discretas usadas no limitador de corrente.
    vals={"F00":F[0,0],"F01":F[0,1],"F02":F[0,2],"G0":G[0,0],**{f'K{j}':x for j,x in enumerate(GAIN)},'N':N,'VMAX':VMAX,'IMAX':IMAX,'KE':KE,'R':R,'TS':TS}
    # Insere números com precisão de double para equivalência numérica.
    for k,v in vals.items():s=s.replace('@@'+k+'@@',format(float(v),'.17g'))
    Path(path).write_text(s,encoding='utf8')  # Exporta o artefato para firmware/.
    return path
if __name__=='__main__': generate(Path(__file__).resolve().parents[1]/'firmware'/'controller_generated.c')
