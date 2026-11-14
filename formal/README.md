# Verificação temporal e de transições

`auroraarm/safety.py` realiza busca exaustiva numa grade FINITA de atrasos inteiros em milissegundos para 0 ≤ sensor ≤ 20, jitter ∈ {0,2}, 0 ≤ comando ≤ 2 e 0 ≤ decaimento do torque ≤ 60.

Temos `G(mão_detectada -> F_[0,100ms] torque_nulo)` sob a premissa de decaimento ≤ 60 ms. Este não é model checking de tempo denso: a prova é apenas na grade declarada. O requisito de vivacidade é `G(rearmado ∧ zona_livre -> F movimento)` condicionado à execução do supervisor e disponibilidade da planta. O autômato distingue MOVE, STOPPING, STOPPED, WAIT_REARM, RESUME.

Contraexemplo de configuração preliminar: se o decaimento do torque alcançar 80 ms, então 20+2+2+80 = 104 ms (>100 ms). A configuração hipotética foi restringida a 60 ms para fins de estudo. Essa alteração não constitui comprovação da física de parada.

Necessário para uma avaliação completa: modelo UPPAAL e verificação temporal formal, especificações de hardware de corte de torque, ensaio de tempo de reação e cobertura de transições com relatório automático.
