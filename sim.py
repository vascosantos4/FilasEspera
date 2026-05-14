import simpy
import random
import statistics

TEMPO_SIMULACAO = 8 * 60
TEMPO_MEDIO_ENTRE_CHEGADAS = 3
TEMPO_MEDIO_ATENDIMENTO = 5

NUM_REPETICOES = 100
CENARIOS_CAIXAS = [1, 2, 3, 4, 5]


def correr_simulacao(num_caixas, seed):
    random.seed(seed)

    tempos_espera = []
    tempos_sistema = []
    tempos_atendimento = []
    clientes_atendidos = 0

    def cliente(env, nome, caixas):
        nonlocal clientes_atendidos

        tempo_chegada = env.now

        with caixas.request() as pedido:
            yield pedido

            inicio_atendimento = env.now
            tempo_espera = inicio_atendimento - tempo_chegada
            tempos_espera.append(tempo_espera)

            tempo_atendimento = random.expovariate(1 / TEMPO_MEDIO_ATENDIMENTO)
            tempos_atendimento.append(tempo_atendimento)

            yield env.timeout(tempo_atendimento)

            fim_atendimento = env.now
            tempos_sistema.append(fim_atendimento - tempo_chegada)

            clientes_atendidos += 1

    def chegada_clientes(env, caixas):
        numero_cliente = 0

        while True:
            tempo_ate_proximo = random.expovariate(1 / TEMPO_MEDIO_ENTRE_CHEGADAS)
            yield env.timeout(tempo_ate_proximo)

            numero_cliente += 1
            env.process(cliente(env, f"Cliente {numero_cliente}", caixas))

    env = simpy.Environment()
    caixas = simpy.Resource(env, capacity=num_caixas)

    env.process(chegada_clientes(env, caixas))
    env.run(until=TEMPO_SIMULACAO)

    if len(tempos_espera) == 0:
        return None

    utilizacao = sum(tempos_atendimento) / (num_caixas * TEMPO_SIMULACAO)
    percentagem_mais_10min = sum(t > 10 for t in tempos_espera) / len(tempos_espera) * 100

    return {
        "num_caixas": num_caixas,
        "clientes_atendidos": clientes_atendidos,
        "espera_media": statistics.mean(tempos_espera),
        "espera_maxima": max(tempos_espera),
        "tempo_total_medio": statistics.mean(tempos_sistema),
        "utilizacao": utilizacao * 100,
        "percentagem_mais_10min": percentagem_mais_10min
    }


for num_caixas in CENARIOS_CAIXAS:
    resultados = []

    for repeticao in range(NUM_REPETICOES):
        resultado = correr_simulacao(num_caixas, seed=1000 + repeticao)
        resultados.append(resultado)

    print("\n=================================")
    print(f"CENÁRIO: {num_caixas} CAIXA(S)")
    print("=================================")

    print(f"Clientes atendidos: {statistics.mean([r['clientes_atendidos'] for r in resultados]):.1f}")
    print(f"Tempo médio de espera: {statistics.mean([r['espera_media'] for r in resultados]):.2f} min")
    print(f"Tempo máximo médio de espera: {statistics.mean([r['espera_maxima'] for r in resultados]):.2f} min")
    print(f"Tempo médio total no sistema: {statistics.mean([r['tempo_total_medio'] for r in resultados]):.2f} min")
    print(f"Utilização média das caixas: {statistics.mean([r['utilizacao'] for r in resultados]):.2f}%")
    print(f"% clientes com espera > 10 min: {statistics.mean([r['percentagem_mais_10min'] for r in resultados]):.2f}%")