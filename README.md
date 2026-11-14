# AuroraArm — parte prática COMENTADA

## Objetivo

Este repositório contém uma implementação **educacional** de modelagem baseada em modelos de um motor de corrente contínua da junta do cotovelo do AuroraArm. Todos os arquivos Python têm comentários em português explicando ações e cálculos. O firmware C é **gerado automaticamente**: não edite o arquivo gerado, pois uma nova geração irá sobrescrevê-lo.

## Como executar no VS Code (Windows 11)

1. Extraia o ZIP e abra a pasta `AuroraArm_Comentado` no VS Code (Arquivo → Abrir pasta).
2. Instale Python 3.10+ e a extensão Python do VS Code, caso ainda não estejam instalados.
3. Abra **Terminal → Novo Terminal** e execute, um comando de cada vez:

```powershell
python -m pip install -r requirements.txt
python -m auroraarm.simulation
python -m auroraarm.codegen
python -m pytest -v
```

- **Primeiro comando:** instala NumPy, SciPy, Matplotlib e pytest.
- **Segundo comando:** executa a simulação e grava gráficos e `results/metricas.json`.
- **Terceiro comando:** gera de novo `firmware/controller_generated.c` a partir do modelo Python.
- **Quarto comando:** verifica o funcionamento do modelo, controlador, supervisor e código C.

**Requisito adicional:** para rodar `tests/test_codegen.py`, instale um compilador GCC e deixe o comando `gcc` disponível no terminal. O teste usa opções de biblioteca compartilhada próprias de Unix/Linux; no Windows, execute esse teste via **WSL (Ubuntu)** ou adapte a compilação para produzir uma DLL. Sem GCC, o teste SIL falhará. Os demais testes são independentes de GCC.

## Por onde começar a estudar o código

1. `auroraarm/plant.py`: lê os valores físicos e calcula A, B, C, D, polos e ponto crítico.
2. `auroraarm/control.py`: calcula ganhos, limita tensão/corrente e implementa anti-windup.
3. `auroraarm/safety.py`: simula a lógica do supervisor e enumera atrasos em uma grade.
4. `auroraarm/simulation.py`: executa a simulação e constrói gráficos/indicadores.
5. `auroraarm/codegen.py`: converte parâmetros do modelo em código C gerado.
6. `tests/`: contém testes de verificação que podem ser repetidos a qualquer momento.
7. `docs/rastreabilidade.csv`: relaciona os oito requisitos do enunciado aos arquivos e evidências.

## Limitações a declarar no trabalho e no vídeo

- **Não usar este firmware em robô físico.** O comando 0 V não garante torque 0 imediatamente.
- A hipótese de **60 ms** para queda do torque **não foi medida**. A varredura de tempos inteiros em milissegundos não prova segurança universal em tempo contínuo.
- Não existe neste pacote um modelo UPPAAL completo com verificação de propriedades temporizadas nem cobertura formal exaustiva de todas as transições.
- A checagem de corrente usa a planta simulada e não equivale a certificação de sobrecorrente no motor real.
- O limitador de velocidade colaborativa de 250 mm/s foi calculado, mas não foi implementado como canal físico independente e certificado.
- Foram feitos testes SIL em `double` (quando GCC está disponível). O desempenho de tempo e memória num ARM Cortex-M4 não foi medido em placa real.
- Para uma auditoria real, são necessários mais testes, modelo formal completo e validação de hardware.

## Resultados

Os arquivos em `results/` são gerados pela simulação e podem ser recriados pelos comandos informados. Não apresente resultados de simulação como certificação de segurança física.
