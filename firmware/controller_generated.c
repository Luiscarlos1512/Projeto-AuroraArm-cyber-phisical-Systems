/* ARQUIVO GERADO AUTOMATICAMENTE: nao editar.
 * Origem: auroraarm/codegen.py + auroraarm/control.py
 * Requisitos: REQ-CTRL-AA-001..004, REQ-SAFE-AA-001..004 (somente interface)
 * Observacao: corte eletrico de torque exige hardware de seguranca independente.
 */
#include <math.h>
/* Estado interno que persiste entre ciclos: erro integral. */
typedef struct { double integrator; } AAController;
/* Inicializa o integrador para iniciar um novo controle. */
void aa_reset(AAController *c) {c->integrator=0.0;}
double aa_step(AAController *c, double ref, double i, double w, double theta, int enabled) {
 /* Sem habilitacao: cancela o comando e reinicia integrador. Nao e corte fisico seguro. */
 if (!enabled) {c->integrator=0.0;return 0.0;}
 const double k0=0.23397142865598675,k1=0.71198569783537835,k2=45.485703570649669,k3=-88058.880133435581;
 /* Calcula o erro de posicao da junta (theta e angulo do eixo do motor). */
 double error=ref-theta/100;
 /* Realimentacao dos estados e do integrador com os ganhos calculados em Python. */
 double raw=-(k0*i+k1*w+k2*theta+k3*c->integrator);
 /* Satura a tensao no intervalo permitido pelo acionamento. */
 double u=fmax(-48,fmin(48,raw));
 if (i>=8 && (u-0.085000000000000006*w-0.80000000000000004*i)>0.0) u=fmin(u,0.80000000000000004*i+0.085000000000000006*w);
 if (i<=-8 && (u-0.085000000000000006*w-0.80000000000000004*i)<0.0) u=fmax(u,0.80000000000000004*i+0.085000000000000006*w);
 /* Prediz a corrente do proximo ciclo na ausencia do novo comando. */
 double baseline=0.25124845523188732*i+-0.077484683743010416*w+0*theta;
 u=fmax((-(8-0.1)-baseline)/0.91198241659238966,fmin(((8-0.1)-baseline)/0.91198241659238966,u));
 u=fmax(-48,fmin(48,u));
 /* Anti-windup: so integra quando nao agrava a saturacao. */
 if (fabs(raw-u)<1e-9 || ((error>0)-(error<0))!=((raw-u>0)-(raw-u<0))) c->integrator+=0.002*error;
 return u;
}
