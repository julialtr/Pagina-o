# Imports
from collections import deque

import os
import math
import random
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Classes auxiliares
class Pagina:
    def __init__(self, id = 0, id_processo = 0, valor_processo = 0):
        self.id = id
        self.id_processo = id_processo
        self.valor_processo = valor_processo

class PaginaTabela: 
    def __init__(self, id_pagina, ponteiro_disco = -1, bit_validez = False, bit_modificacao = True):
        self.id_pagina = id_pagina
        self.ponteiro_disco = ponteiro_disco
        self.bit_validez = bit_validez
        self.bit_modificacao = bit_modificacao

class Processo:
    def __init__(self, id = 0, valor = 0, tamanho = 0):
        self.id = id
        self.valor = valor
        self.tamanho = tamanho

# TO DO -> Leitura, Validações
# Limitar entrada para 6 processos
# Arquivo de Input
    # tempoVisualizacao: 0
    # tamanhoDisco: 0
    # tamanhoRAM: 0
    # tamanhoPaginacao: 0
    # tamanhoPagina: 0
    # processos : [ processo: {id: 0, valor: 54486, tamanho (bytes): 20} ]       # talvez ver para fazer ter vários valores, aí fica mais fácil de entender a divisão em páginas 

def le_arquivo_input():
    pass

processos_input = [
    Processo(5, 10454, 100),
    Processo(6, 25645, 50),
    Processo(1, 33640, 20),
    Processo(2, 74109, 30),
    Processo(3, 85416, 110),
    Processo(4, 61220, 70) ]

tempoVisualizacao = 1 #temp
tam_disco = 300 #temp
tam_paginacao = 70 #temp
tam_pagina = 10 #temp
tam_ram = 100 #temp

disco_esta_preenchido = False

# Conversão dos processos do arquivo de input em páginas (Memória Virtual) e inicialização das ETP
memoria_virtual = []
lista_etps_por_processo = []

def inicializa_memoria_virtual_etps():
    global memoria_virtual
    memoria_virtual_aux = []
    for processo in processos_input:
        qtds_paginas = math.ceil(processo.tamanho / tam_pagina)

        etps = []

        for i in range(qtds_paginas):
            memoria_virtual_aux.append(Pagina(i + 1, processo.id, processo.valor))
            etps.append(PaginaTabela(i + 1))

        lista_etps_por_processo.append([processo.id, etps])

    memoria_virtual = memoria_virtual_aux * 2
    random.shuffle(memoria_virtual)

# Criação do arquivo que simula a Memória Secundária (Disco)
file_path = "C:\\Paginacao\\disco.bin"
def cria_arquivo_disco():
    with open(file_path, "wb") as arquivo_disco:
	    arquivo_disco.write(bytes(tam_disco))

# Criação da estrutura que simula a Memória Principal (Memória RAM)
qtd_paginas_ram = tam_ram // tam_pagina
memoria_RAM = deque(maxlen=qtd_paginas_ram)  

# Leitura/Gravação na Memória Principal (Memória RAM)
def ler_RAM(pagina_etp):
    if not(pagina_etp.bit_validez):
        return False

    return True

def grava_RAM(pagina_nova, pagina_etp):
    pagina_removida = Pagina()

    if len(memoria_RAM) == qtd_paginas_ram:
        pagina_removida = memoria_RAM.popleft() # FIFO
        print(f"Página {pagina_removida.id} do processo {pagina_removida.id_processo} | {pagina_removida.valor_processo} foi removida da Memória Principal (Memória RAM) \n")

    memoria_RAM.append(pagina_nova)
    pagina_etp.bit_validez = True

    altera_RAM(pagina_removida, pagina_nova)

    if pagina_removida.id != 0:
        pagina_etp_aux = encontra_pagina_etp(pagina_removida.id_processo, pagina_removida.id)
        pagina_etp_aux.bit_validez = False
        
        if pagina_etp_aux.bit_modificacao:
            grava_disco(pagina_removida, pagina_etp_aux)

# Leitura/Gravação na Memória Secundária (Disco)
def ler_disco(pagina_etp):
    if pagina_etp.ponteiro_disco == -1:
        return None
    
    with open(file_path, 'rb+') as arquivo_disco:
        arquivo_disco.seek(pagina_etp.ponteiro_disco)
        data = arquivo_disco.read(tam_pagina)

        pipe_character = "|"
        pipe_bytes = pipe_character.encode('utf-8')

        id_valor = data.split(pipe_bytes) # ID | VALOR
        id_encontrado = int(id_valor[0])
        valor_encontrado = int(id_valor[1].decode('utf-8').rstrip('\x00'))

        return Pagina(pagina_etp.id_pagina, id_encontrado, valor_encontrado)

def grava_disco(pagina_removida, pagina_etp):
    with open(file_path, 'rb+') as arquivo_disco:
        if pagina_etp.ponteiro_disco != -1:
            data_gravar = f"{pagina_removida.id_processo}|{pagina_removida.valor_processo}"
            data_bytes = data_gravar.encode('utf-8')
            arquivo_disco.seek(pagina_etp.ponteiro_disco)
            arquivo_disco.write(data_bytes)
        else:
            qtd_paginas_lidas = 0

            while qtd_paginas_lidas < tam_paginacao:
                arquivo_disco.seek(qtd_paginas_lidas)
                data = arquivo_disco.read(tam_pagina)

                if all(byte == 0x00 for byte in data):
                    data_gravar = f"{pagina_removida.id_processo}|{pagina_removida.valor_processo}"
                    data_bytes = data_gravar.encode('utf-8')
                    arquivo_disco.seek(qtd_paginas_lidas)
                    arquivo_disco.write(data_bytes)

                    pagina_etp.ponteiro_disco = qtd_paginas_lidas
                    break

                qtd_paginas_lidas += tam_pagina
        
            altera_disco(pagina_removida.id_processo, pagina_etp.id_pagina)

        #novo_processo = Processo(processo.id, processo.valor, 0)
        #altera_processo_lista(novo_processo)

# Montagem da visualização gráfica
visualizacao_cores = {} # chave: id_processo e id_pagina | valor: cor
visualizacao_ram = [] # matriz com cor a partir do id_processo e id_pagina
visualizacao_disco = [] # matriz com cor a partir do id_processo e id_pagina
paleta_cores = [] # paleta de cores disponíveis de acordo com a quantidade de processos e de suas respectivas páginas

qtd_cores = 2

def gera_paleta():
    cores_disponiveis = ['Blues', 'Greens', 'Oranges', 'Reds', 'Purples', 'PuRd']
    
    cinza = plt.cm.get_cmap('Greys', 2)
    lista_escalas = [cinza(np.linspace(0, 0, 1))]

    lista_etps_por_processo_ordenado = sorted(lista_etps_por_processo, key=lambda x: x[0])

    for x in range(len(lista_etps_por_processo_ordenado)):
        id_processo = lista_etps_por_processo_ordenado[x][0]
        etps = lista_etps_por_processo_ordenado[x][1]

        qtd_paginas_processo = len(etps)

        global qtd_cores
        qtd_cores += qtd_paginas_processo

        cor = plt.cm.get_cmap(cores_disponiveis[id_processo - 1], qtd_paginas_processo)
        lista_escalas.append(cor(np.linspace(0, 0.8, qtd_paginas_processo)))

    lista_escalas.append(cinza(np.linspace(1, 1, 1)))
    
    global paleta_cores
    paleta_cores = ListedColormap(np.concatenate(lista_escalas)) 

def solicita_cor(id_processo, id_pagina):
    return visualizacao_cores[(id_processo, id_pagina)]

def gera_cores():
    cor_atual = 0

    visualizacao_cores[(0, 0)] = cor_atual

    cor_atual += 1

    lista_etps_por_processo_ordenado = sorted(lista_etps_por_processo, key=lambda x: x[0])

    for x in range(len(lista_etps_por_processo_ordenado)):
        id_processo = lista_etps_por_processo_ordenado[x][0]
        etps = lista_etps_por_processo_ordenado[x][1]

        for y in range(len(etps)):
            id_pagina = etps[y].id_pagina
            visualizacao_cores[(id_processo, id_pagina)] = cor_atual
            cor_atual += 1

    visualizacao_cores[(-1, -1)] = cor_atual

def preenche_dados_visualizacao(qtd_colunas, qtd_celulas, eh_RAM):
    qtd_linhas = qtd_colunas

    for x in range(qtd_colunas):
        linha = []

        for l in range(qtd_linhas):
            if qtd_celulas:
                linha.append(solicita_cor(0, 0))
                qtd_celulas -= 1
            else:
                linha.append(solicita_cor(-1, -1))
        
        if eh_RAM:
            visualizacao_ram.append(linha)
        else:
            visualizacao_disco.append(linha)

def preenche_dados_visualizacao_RAM():
    qtd_colunas = math.ceil(math.sqrt(qtd_paginas_ram))
    qtd_celulas = qtd_paginas_ram

    preenche_dados_visualizacao(qtd_colunas, qtd_celulas, True)

def preenche_dados_visualizacao_disco():
    qtd_paginas_paginacao = tam_paginacao // tam_pagina
    qtd_paginas_restantes = math.ceil((tam_disco - tam_paginacao) // tam_pagina)

    qtd_paginas_disco = qtd_paginas_paginacao + qtd_paginas_restantes

    qtd_colunas = math.ceil(math.sqrt(qtd_paginas_disco))
    qtd_celulas = qtd_paginas_paginacao

    preenche_dados_visualizacao(qtd_colunas, qtd_celulas, False)

fig, axs = plt.subplots(1, 2, figsize=(16, 8))

def renderiza(inicial):
    renderiza_RAM(inicial)
    renderiza_disco(inicial)

    plt.tight_layout()

    plt.show(block=False)
    plt.pause(tempoVisualizacao)

def renderiza_RAM(inicial):
    ax = axs[0]

    ax.cla()

    if inicial:
        sns.heatmap(data=visualizacao_ram, cmap=paleta_cores, vmin=0, vmax=qtd_cores, ax=ax, cbar=True)
    else:
        sns.heatmap(data=visualizacao_ram, cmap=paleta_cores, vmin=0, vmax=qtd_cores, ax=ax, cbar=False)
    
    for i in range(len(visualizacao_ram)):
        for j in range(len(visualizacao_ram[0])):
            chave = list(visualizacao_cores.keys())[list(visualizacao_cores.values()).index(visualizacao_ram[i][j])]
            valor = visualizacao_cores[chave]

            id_processo = chave[0]
            id_pagina = chave[1]

            if (id_processo == -1 or id_processo == 0) and (id_pagina == -1 or id_pagina == 0):
                continue

            texto = f"ID: {id_pagina}\nProcesso: {id_processo}\nCor: {valor}"
            ax.text(j + 0.5, i + 0.5, texto, ha='center', va='center', fontsize=10, color='black')

    ax.set_title("Memória Principal (Memória RAM)")

def renderiza_disco(inicial):
    ax = axs[1]

    ax.cla()

    if inicial:
        sns.heatmap(data=visualizacao_disco, cmap=paleta_cores, vmin=0, vmax=qtd_cores, ax=ax, cbar=True)
    else:
        sns.heatmap(data=visualizacao_disco, cmap=paleta_cores, vmin=0, vmax=qtd_cores, ax=ax, cbar=False)
    
    for i in range(len(visualizacao_disco)):
        for j in range(len(visualizacao_disco[0])):
            chave = list(visualizacao_cores.keys())[list(visualizacao_cores.values()).index(visualizacao_disco[i][j])]
            valor = visualizacao_cores[chave]

            id_processo = chave[0]
            id_pagina = chave[1]

            if (id_processo == -1 or id_processo == 0) and (id_pagina == -1 or id_pagina == 0):
                continue

            texto = f"ID: {id_pagina}\nProcesso: {id_processo}\nCor: {valor}"
            ax.text(j + 0.5, i + 0.5, texto, ha='center', va='center', fontsize=10, color='black')

    ax.set_title("Memória Secundária (Disco)")

def altera_RAM(pagina_removida, pagina_nova):
    encontrou_pagina = False

    for x in range(len(visualizacao_ram)):
        linha = visualizacao_ram[x]

        for y in range(len(linha)):
            cor = linha[y]

            id_pagina_removida = 0

            if pagina_removida.id_processo != 0 and pagina_removida.id != 0:
                pagina_etp_removida = encontra_pagina_etp(pagina_removida.id_processo, pagina_removida.id)
                id_pagina_removida = pagina_etp_removida.id_pagina

            if cor == solicita_cor(pagina_removida.id_processo, id_pagina_removida):
                pagina_etp = encontra_pagina_etp(pagina_nova.id_processo, pagina_nova.id)
                visualizacao_ram[x][y] = solicita_cor(pagina_nova.id_processo, pagina_etp.id_pagina)
                encontrou_pagina = True
                break

        if encontrou_pagina:
            break
    
    renderiza(False)

def altera_disco(id_processo, id_pagina):
    global disco_esta_preenchido

    encontrou_pagina = False
    verifica_disco_esta_preenchido = True

    for x in range(len(visualizacao_disco)):
        linha = visualizacao_disco[x]

        for y in range(len(linha)):
            cor = linha[y]

            if cor != solicita_cor(0, 0) and cor != solicita_cor(-1, -1):
                continue

            if cor == solicita_cor(-1, -1):
                disco_esta_preenchido = True

            if verifica_disco_esta_preenchido and encontrou_pagina:
                verifica_disco_esta_preenchido = False
                break
            
            visualizacao_disco[x][y] = solicita_cor(id_processo, id_pagina)
            encontrou_pagina = True

        if verifica_disco_esta_preenchido == False:
            break
    
    renderiza(False)

# Rotina que atualiza randomicamente valores do processo da página
def altera_processo(id_processo):
    altera_valor = bool(random.randint(0, 1))
    if not (altera_valor):
        return
    
    novo_valor = random.randint(10000, 99999)
    print(f"Alterando valor da página atual para {novo_valor}\n")
    
    for i in range(len(memoria_virtual)):
        if id_processo == memoria_virtual[i].id:
            try:    
                posicao = memoria_RAM.index(memoria_virtual[i])
                memoria_RAM[posicao].valor_processo = novo_valor
            except:
                break

            memoria_virtual[i].valor_processo = novo_valor

            break

def encontra_pagina_etp(id_processo, id_pagina):
    for etp_processo in lista_etps_por_processo:
        if id_processo == etp_processo[0]:
            return etp_processo[1][id_pagina - 1]
        
# Execução
def inicializa_sistema():
    # Parte lógica
    le_arquivo_input()
    cria_arquivo_disco()
    inicializa_memoria_virtual_etps()

    # Parte gráfica
    gera_paleta()
    gera_cores()
    preenche_dados_visualizacao_RAM()
    preenche_dados_visualizacao_disco()
    renderiza(True)

    os.system('cls')

inicializa_sistema()

for pagina in memoria_virtual:
    if len(memoria_RAM) == qtd_paginas_ram and disco_esta_preenchido:
        print(f"Não há mais espaço disponível para paginação\n")
        break

    print(f"Página atual -> ID: {pagina.id} // Processo: {pagina.id_processo} | {pagina.valor_processo} \n")

    pagina_etp = encontra_pagina_etp(pagina.id_processo, pagina.id)
    
    if ler_RAM(pagina_etp):
        print(f"Encontrada página atual na Memória Principal (Memória RAM)\n")
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        #altera_processo(pagina.id_processo)
        continue

    pagina_atualizada = ler_disco(pagina_etp)
    print(f"Não foi encontrada a página atual na Memória Secundária (Disco)\n") if (pagina_atualizada == None) else print(f"Encontrada página atual na Memória Secundária (Disco)\n")

    grava_RAM(pagina if (pagina_atualizada == None) else pagina_atualizada, pagina_etp)

    #altera_processo(pagina.id_processo)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

print("Simulação encerrada")
plt.pause(10000)

# O que falta:
    # Pedro = CRIAR ARQUIVO DE INPUT para valores de disco, ram... (se invalido, randomizar os valores)
    # Bruna = Thread que retira processos da RAM + alteraprocesso()
    # Julia - Atualizar visualização quando são retirados processos da RAM
    # Julia - Atualizar visualização quando são alterados processos da RAM