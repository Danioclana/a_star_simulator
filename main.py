import copy
import math
import heapq
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

class Node:
    def __init__(self, row, col, parent=None, usos_fruta_restantes=0):
        self.indice = [row, col]
        self.pai = parent
        self.distancia_percorrida = 0
        self.h = 0
        self.fe = 0
        self.usos_fruta_restantes = usos_fruta_restantes

    def __lt__(self, other):
        return self.fe < other.fe

    def __eq__(self, other):
        return self.indice == other.indice and self.usos_fruta_restantes == other.usos_fruta_restantes

    def __hash__(self):
        return hash(tuple(self.indice) + (self.usos_fruta_restantes,))

direcoes_movimento = [
    ("cima", -1, 0), ("baixo", 1, 0), ("esquerda", 0, -1), ("direita", 0, 1),
    ("diagonal superior esquerda", -1, -1), ("diagonal superior direita", -1, 1), ("diagonal inferior esquerda", 1, -1), ("diagonal inferior direita", 1, 1)
]

mapa = [
    ['C','','','','B',''],
    ['','B','','','',''],
    ['','','F','','',''],
    ['','','','B','B',''],
    ['','','','A','',''],
    ['','','','','','S']
]

def is_valido(linha, coluna, grade):
    return 0 <= linha < len(grade) and 0 <= coluna < len(grade[0])

def is_obstaculo(linha, coluna, grade, usos_fruta_restantes):
    return grade[linha][coluna] == 'B' and usos_fruta_restantes == 0

def obter_vizinhos(no, grade):
    filhos = []
    movimentos = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    for dl, dc in movimentos:
        nova_linha, nova_coluna = no.indice[0] + dl, no.indice[1] + dc
        if is_valido(nova_linha, nova_coluna, grade) and not is_obstaculo(nova_linha, nova_coluna, grade, no.usos_fruta_restantes):
            usos_fruta_restantes_filho = no.usos_fruta_restantes
            if grade[nova_linha][nova_coluna] == 'A':
                 usos_fruta_restantes_filho += 1
            if grade[nova_linha][nova_coluna] == 'B' and no.usos_fruta_restantes > 0:
                 usos_fruta_restantes_filho -= 1
            filho = Node(nova_linha, nova_coluna, parent=no, usos_fruta_restantes=usos_fruta_restantes_filho)
            filhos.append(filho)

    return filhos

def calcular_h(no, objetivo):
    linha1, coluna1 = no.indice
    linha2, coluna2 = objetivo.indice
    return math.sqrt((linha2 - linha1)**2 + (coluna2 - coluna1)**2)

def obter_custo_passo(no_atual, filho_no, grade):
    dl = abs(no_atual.indice[0] - filho_no.indice[0])
    dc = abs(no_atual.indice[1] - filho_no.indice[1])
    custo_base = 1.414 if dl > 0 and dc > 0 else 1
    return custo_base

def astar(grade):
    linha_inicio, coluna_inicio = -1, -1
    linha_objetivo, coluna_objetivo = -1, -1

    for l in range(len(grade)):
        for c in range(len(grade[0])):
            if grade[l][c] == 'C':
                linha_inicio, coluna_inicio = l, c
            elif grade[l][c] == 'S':
                linha_objetivo, coluna_objetivo = l, c

    if linha_inicio == -1 or linha_objetivo == -1:
        print("Inicio ('C') ou Objetivo ('S') nao encontrados no mapa.")
        return None

    no_inicio = Node(linha_inicio, coluna_inicio)
    no_objetivo = Node(linha_objetivo, coluna_objetivo)
    lista_aberta = []
    heapq.heappush(lista_aberta, no_inicio)
    lista_fechada = set()
    dicionario_lista_aberta = {no_inicio: no_inicio}
    print("--- Iniciando A* ---")
    print(f"Inicio: {no_inicio.indice}, Objetivo: {no_objetivo.indice}")

    while lista_aberta:
        no_atual = heapq.heappop(lista_aberta)
        del dicionario_lista_aberta[no_atual]

        print(f"\nProcessando no: {no_atual.indice}, Distancia percorrida (g): {no_atual.distancia_percorrida:.2f}, Heuristica (h): {no_atual.h:.2f}, Custo Total (f): {no_atual.fe:.2f}, Usos Fruta Restantes: {no_atual.usos_fruta_restantes}")

        lista_fechada.add(no_atual)

        if no_atual == no_objetivo:
            print("!!! Objetivo encontrado !!!")
            caminho = []
            atual = no_atual
            while atual is not None:
                caminho.append(atual.indice)
                atual = atual.pai
            caminho.reverse()
            print(f"Caminho encontrado: {caminho}")
            return caminho
        filhos = obter_vizinhos(no_atual, grade)
        print(f"Numero de filhos/vizinhos validos para {no_atual.indice}: {len(filhos)}")

        for filho in filhos:
            print(f"  Considerando filho: {filho.indice}, Usos Fruta Restantes (filho): {filho.usos_fruta_restantes}")

            if filho in lista_fechada:
                print(f"    Filho {filho.indice} ja na lista fechada. Pulando.")
                continue
            custo_tentativo_g = no_atual.distancia_percorrida + obter_custo_passo(no_atual, filho, grade)
            print(f"    Custo tentativo g para {filho.indice}: {custo_tentativo_g:.2f}")
            if filho in dicionario_lista_aberta and custo_tentativo_g >= dicionario_lista_aberta[filho].distancia_percorrida:
                print(f"    Filho {filho.indice} ja na lista aberta com custo igual ou pior. Pulando.")
                continue
            filho.pai = no_atual
            filho.distancia_percorrida = custo_tentativo_g
            filho.h = calcular_h(filho, no_objetivo)
            filho.fe = filho.distancia_percorrida + filho.h

            if filho not in dicionario_lista_aberta:
                print(f"    Adicionando filho {filho.indice} a lista aberta (novo no/estado). Custo f: {filho.fe:.2f}")
                heapq.heappush(lista_aberta, filho)
                dicionario_lista_aberta[filho] = filho
            else:
                 print(f"    Atualizando custo para filho {filho.indice} na lista aberta. Novo custo f: {filho.fe:.2f}")
                 dicionario_lista_aberta[filho] = filho
                 heapq.heappush(lista_aberta, filho)

    print("--- Lista aberta vazia. Nao foi possivel encontrar um caminho. ---")
    return None

def astar_visualize(grade):
    linha_inicio, coluna_inicio = -1, -1
    linha_objetivo, coluna_objetivo = -1, -1

    for l in range(len(grade)):
        for c in range(len(grade[0])):
            if grade[l][c] == 'C':
                linha_inicio, coluna_inicio = l, c
            elif grade[l][c] == 'S':
                linha_objetivo, coluna_objetivo = l, c
    if linha_inicio == -1 or linha_objetivo == -1:
        print("Inicio ('C') ou Objetivo ('S') nao encontrados no mapa.")
        return [], []

    no_inicio = Node(linha_inicio, coluna_inicio)
    no_objetivo = Node(linha_objetivo, coluna_objetivo)

    lista_aberta = []
    heapq.heappush(lista_aberta, no_inicio)
    lista_fechada = set()
    dicionario_lista_aberta = {no_inicio: no_inicio}
    etapas_visualizacao = []

    while lista_aberta:
        no_atual = heapq.heappop(lista_aberta)
        del dicionario_lista_aberta[no_atual]

        lista_fechada.add(no_atual)
        etapas_visualizacao.append({'type': 'move', 'coords': no_atual.indice})

        if no_atual == no_objetivo:
            caminho = []
            atual = no_atual
            while atual is not None:
                caminho.append(atual.indice)
                atual = atual.pai
            caminho.reverse()
            return caminho, etapas_visualizacao

        for nome_movimento, dl, dc in direcoes_movimento:
            nova_linha, nova_coluna = no_atual.indice[0] + dl, no_atual.indice[1] + dc
            etapas_visualizacao.append({'type': 'attempt', 'from': no_atual.indice, 'to': [nova_linha, nova_coluna], 'direction': nome_movimento})

            if not is_valido(nova_linha, nova_coluna, grade) or is_obstaculo(nova_linha, nova_coluna, grade, no_atual.usos_fruta_restantes):
                etapas_visualizacao.append({'type': 'blocked', 'coords': [nova_linha, nova_coluna]})
                continue

            filho = Node(nova_linha, nova_coluna, parent=no_atual)

            if filho in lista_fechada:
                etapas_visualizacao.append({'type': 'skipped_closed', 'coords': [nova_linha, nova_coluna]})
                continue

            custo_tentativo_g = no_atual.distancia_percorrida + obter_custo_passo(no_atual, filho, grade)

            if filho in dicionario_lista_aberta and custo_tentativo_g >= dicionario_lista_aberta[filho].distancia_percorrida:
                etapas_visualizacao.append({'type': 'skipped_open', 'coords': [nova_linha, nova_coluna]})
                continue

            filho.pai = no_atual
            filho.distancia_percorrida = custo_tentativo_g
            filho.h = calcular_h(filho, no_objetivo)
            filho.fe = filho.distancia_percorrida + filho.h

            if filho not in dicionario_lista_aberta:
                heapq.heappush(lista_aberta, filho)
                dicionario_lista_aberta[filho] = filho
                etapas_visualizacao.append({'type': 'add_open', 'coords': [nova_linha, nova_coluna]})
            else:
                 pass

    return None, etapas_visualizacao

def traduzir_caminho_para_comandos(caminho):
    comandos = []
    for i in range(len(caminho) - 1):
        posicao_atual = caminho[i]
        proxima_posicao = caminho[i+1]

        dl = proxima_posicao[0] - posicao_atual[0]
        dc = proxima_posicao[1] - posicao_atual[1]

        if dl == -1 and dc == 0:
            comandos.append("cima")
        elif dl == 1 and dc == 0:
            comandos.append("baixo")
        elif dl == 0 and dc == -1:
            comandos.append("esquerda")
        elif dl == 0 and dc == 1:
            comandos.append("direita")
        elif dl == -1 and dc == -1:
            comandos.append("diagonal superior esquerda")
        elif dl == -1 and dc == 1:
            comandos.append("diagonal superior direita")
        elif dl == 1 and dc == -1:
            comandos.append("diagonal inferior esquerda")
        elif dl == 1 and dc == 1:
            comandos.append("diagonal inferior direita")
    return comandos

class AStarHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get_path':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            caminho_encontrado = astar(mapa)

            if caminho_encontrado:
                comandos_movimento = traduzir_caminho_para_comandos(caminho_encontrado)
                dados_resposta = json.dumps(comandos_movimento)
            else:
                dados_resposta = json.dumps([])

            self.wfile.write(dados_resposta.encode('utf-8'))

        elif self.path == '/get_visualization_steps':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            _, etapas_visualizacao = astar_visualize(mapa)
            dados_resposta = json.dumps(etapas_visualizacao)

            self.wfile.write(dados_resposta.encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def executar_servidor(server_class=HTTPServer, handler_class=AStarHandler, porta=8000):
    endereco_servidor = ('', porta)
    httpd = server_class(endereco_servidor, handler_class)
    print(f'Iniciando servidor httpd na porta {porta}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Parando servidor httpd.')

if __name__ == '__main__':
    executar_servidor()

      