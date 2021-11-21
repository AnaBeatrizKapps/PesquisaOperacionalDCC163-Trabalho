import gurobipy as gp

def main():
  # Parâmetros do problema
  qtd_pontos = 11
  # Matriz de custos
  mat_custos = [
      [0, 1.4, 6.0, 6.5, 6.8, 5.9, 3.8, 9.2, 5.5, 2.7, 3.0],
      [1.4, 0, 4.6, 6.2, 7.2, 5.3, 4.2, 9.6, 5.9, 2.1, 2.9],
      [6.0, 4.6, 0, 4.5, 3.0, 7.9, 6.0, 4.5, 7.1, 7.0, 7.1],
      [6.5, 6.2, 4.5, 0, 3.0, 9.1, 6.6, 6.2, 8.3, 6.3, 6.5],
      [6.8, 7.2, 3.0, 3.9, 0, 9.5, 6.8, 2.4, 8.5, 6.3, 6.4],
      [5.9, 5.3, 7.9, 9.1, 9.5, 0, 2.2, 14.1, 1.8, 4.7, 4.8],
      [3.8, 4.2, 6.0, 6.6, 6.8, 2.2, 0, 11.8, 2.6, 5.6, 6.7],
      [9.2, 9.6, 4.5, 6.2, 2.4, 14.1, 11.8, 0, 11.1, 8.6, 9.5],
      [5.5, 5.9, 7.1, 8.3, 8.5, 1.8, 2.6, 11.1, 0, 6.0, 6.1],
      [2.7, 2.1, 7.0, 6.3, 6.3, 4.7, 5.6, 8.6, 6.0, 0, 3.5],
      [3.0, 2.9, 7.1, 6.5, 6.4, 4.8, 6.7, 9.5, 6.1, 3.5,0]]

  # Índices dos pontos de origem e destino
  origens = [i + 1 for i in range(qtd_pontos)]
  destinos = [i + 1 for i in range(qtd_pontos)]

  # Dicionário dos custos; key: (origem,destino) e value: custo
  custos = dict()
  for i, origem in enumerate(origens):
      for j, destino in enumerate(destinos):
        custos[origem, destino] = mat_custos[i][j]

  # Inicializa o modelo
  m = gp.Model()

  # Variáveis de decisão
  h = m.addVars(origens, destinos, vtype=gp.GRB.BINARY) #variavel de decisão
  u = m.addVars(origens[1:], vtype=gp.GRB.INTEGER, ub=qtd_pontos - 1) # variavel que elimina os subcircuitos; origens[1:] --> cria uma variavel para cada um dos pontos a partir do 2; ub-->limite superior, valor maximo que o i pode atingir

  # Função Objetivo
  m.setObjective(h.prod(custos), sense=gp.GRB.MINIMIZE) 

  # Restrições que garantem que cada ponto será origem exatamente uma vez
  c1 = m.addConstrs(
      gp.quicksum(h[i, j] for j in destinos if i != j) == 1
      for i in origens)

  # Restrições que garantem que cada ponto será destino exatamente uma vez
  c2 = m.addConstrs(
      gp.quicksum(h[i, j] for i in origens if i != j) == 1
      for j in destinos)

  # Restrições de eliminação de subrotas
  c3 = m.addConstrs(
      u[i] - u[j] + qtd_pontos * h[i, j] <= qtd_pontos - 1
      for i in origens[1:] for j in destinos[1:] if i != j)

  m.write('solucao.lp')

  # Executa o modelo
  m.optimize()

  # Constrói o vetor com o circuito; procura qual variavel x que é igual a 1
  circuito = [1]
  anterior = 1
  for ponto in range(qtd_pontos):
      for j in destinos:
        if round(h[anterior, j].X) == 1:
          circuito.append(j)
          anterior = j
          break
            
  # Imprime o circuito
  print(circuito)

  # Imprime a matriz de valores da variável h
  for i in origens:
    print("{:02d}: ".format(i), end="")
    for j in destinos:
      print(round(h[i, j].X), "", end="")
    print("")
  

if __name__ == "__main__":
  main()