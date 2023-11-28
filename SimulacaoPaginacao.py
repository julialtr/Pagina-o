# Imports
import os
import math
import random
import json

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from collections import deque
from matplotlib.colors import ListedColormap
from matplotlib import rc

# Classes auxiliares
class Pagina:
    def __init__(self, id = 0, id_processo = 0, valor = 0):
        self.id = id
        self.id_processo = id_processo
        self.valor = valor

class PaginaTabela: 
    def __init__(self, id_pagina, ponteiro_disco = -1, bit_validez = False, bit_modificacao = True):
        self.id_pagina = id_pagina
        self.ponteiro_disco = ponteiro_disco
        self.bit_validez = bit_validez
        self.bit_modificacao = bit_modificacao

class Processo:
    def __init__(self, id = 0, valor_inicial = 0, tamanho = 0):
        self.id = id
        self.valor_inicial = valor_inicial
        self.tamanho = tamanho

# Variáveis auxiliares
processos_input = []

tempo_visualizacao = 0
tam_disco = 0
tam_paginacao = 0
tam_pagina = 0
tam_ram = 0

disco_esta_preenchido = False
memoria_RAM = deque(maxlen=0)
qtd_paginas_ram = 0

# Leitura do arquivo de configuração JSON
def valida_dados_input():
    if tempo_visualizacao <= 0:
        print("É necessário informar o tempo de visualização\n")
        return False
    
    if tam_disco <= 0:
        print("É necessário informar o tamanho do disco\n")
        return False
    
    if tam_paginacao <= 0:
        print("É necessário informar o tamanho da paginação\n")
        return False
    
    if tam_pagina <= 0:
        print("É necessário informar o tamanho da página\n")
        return False
    
    if tam_ram <= 0:
        print("É necessário informar o tamanho da memória RAM\n")
        return False

    if tam_paginacao > tam_disco:
        print("O tamanho do arquivo de paginação não pode ser maior que o tamanho do disco\n")
        return False
    
    if tam_pagina > tam_paginacao:
        print("O tamanho da página não pode ser maior que o tamanho do arquivo de paginação\n")
        return False
    
    if tam_pagina > tam_ram:
        print("O tamanho da página não pode ser maior que o tamanho da memória RAM\n")
        return False
    
    if len(processos_input) > 6 or len(processos_input) == 0:
        print("São aceitos de 1-6 processos por causa da disponibilidade de cores para cada\n")
        return False
    
    for x in range(len(processos_input)):
        if processos_input[x].id <= 0:
            print("O id do processo deve ser maior que 0\n")
            return False
        
        if processos_input[x].tamanho <= 0:
            print("O tamanho do processo deve ser maior que 0\n")
            return False
    
    return True

def le_arquivo_input(caminho):
    global tempo_visualizacao
    global tam_disco
    global tam_paginacao
    global tam_pagina
    global tam_ram

    dados_input = {}

    with open(caminho, encoding="utf-8") as arquivo:
        dados_input = json.load(arquivo)
    
    tempo_visualizacao = dados_input['tempoVisualizacao']
    tam_disco = dados_input['tamanhoDisco']
    tam_paginacao = dados_input['tamanhoArquivoPaginacao']
    tam_pagina = dados_input['tamanhoPagina']
    tam_ram = dados_input['tamanhoRAM']

    for processo in dados_input['processos']:
        processo_atual = Processo(processo['id'], processo['valor'], processo['tamanho'])
        processos_input.append(processo_atual)

    if valida_dados_input() == False:
        return False

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
            memoria_virtual_aux.append(Pagina(i + 1, processo.id, processo.valor_inicial + i))
            etps.append(PaginaTabela(i + 1))

        lista_etps_por_processo.append([processo.id, etps])

    memoria_virtual = memoria_virtual_aux * 2
    random.shuffle(memoria_virtual)

# Criação do arquivo que simula a Memória Secundária (Disco)
file_path = "C:\\Paginacao\\disco.bin"
def cria_arquivo_disco():
    with open(file_path, "wb") as arquivo_disco:
	    arquivo_disco.write(bytes(tam_disco))

# Leitura/Gravação na Memória Principal (Memória RAM)
def ler_RAM(pagina_etp):
    if not(pagina_etp.bit_validez):
        return False

    return True

def grava_RAM(pagina_nova, pagina_etp):
    pagina_removida = Pagina()

    if len(memoria_RAM) == qtd_paginas_ram:
        pagina_removida = memoria_RAM.popleft() # FIFO
        print(f"Página {pagina_removida.id} do processo {pagina_removida.id_processo} | {pagina_removida.valor} foi removida da Memória Principal (Memória RAM) \n")

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

        valores = data.split(pipe_bytes) # ID_PAGINA | ID_PROCESSO | VALOR
        id_pagina = int(valores[0])
        id_processo = int(valores[1])
        valor = int(valores[2].decode('utf-8').rstrip('\x00'))

        return Pagina(id_pagina, id_processo, valor)

def grava_disco(pagina_removida, pagina_etp):
    data_gravar = f"{pagina_removida.id}|{pagina_removida.id_processo}|{pagina_removida.valor}"
    data_bytes = data_gravar.encode('utf-8')

    with open(file_path, 'rb+') as arquivo_disco:
        if pagina_etp.ponteiro_disco != -1:
            arquivo_disco.seek(pagina_etp.ponteiro_disco)
            arquivo_disco.write(data_bytes)
        else:
            qtd_paginas_lidas = 0

            while qtd_paginas_lidas < tam_paginacao:
                arquivo_disco.seek(qtd_paginas_lidas)
                data = arquivo_disco.read(tam_pagina)

                if all(byte == 0x00 for byte in data):
                    arquivo_disco.seek(qtd_paginas_lidas)
                    arquivo_disco.write(data_bytes)

                    pagina_etp.ponteiro_disco = qtd_paginas_lidas
                    break

                qtd_paginas_lidas += tam_pagina
        
    altera_disco(pagina_removida.id_processo, pagina_etp.id_pagina)

# Montagem da visualização gráfica
visualizacao_cores = {} # CHAVE: id_processo e id_pagina | VALOR: cor
visualizacao_ram = [] # matriz com cor a partir do id_processo e id_pagina
visualizacao_disco = [] # matriz com cor a partir do id_processo e id_pagina
paleta_cores = [] # paleta de cores disponíveis de acordo com a quantidade de processos e de suas respectivas páginas

qtd_cores = 2
fig, axs = plt.subplots(1, 2, figsize=(16, 8))

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

def renderiza(inicial):
    renderiza_RAM(inicial)
    renderiza_disco(inicial)

    plt.tight_layout()

    plt.show(block=False)
    plt.pause(tempo_visualizacao)

def encontra_valor_ram_processo_pagina(id_processo, id_pagina):
    for i in range(len(memoria_RAM)):
        processo = memoria_RAM[i]

        if processo.id == id_pagina and processo.id_processo == id_processo:
            return processo.valor
    
    return 0

def encontra_valor_disco_processo_pagina(id_processo, id_pagina):
    pagina_etp = encontra_pagina_etp(id_processo, id_pagina)

    if pagina_etp.ponteiro_disco == -1:
        return 0
    
    with open(file_path, 'rb+') as arquivo_disco:
        arquivo_disco.seek(pagina_etp.ponteiro_disco)
        data = arquivo_disco.read(tam_pagina)

        pipe_character = "|"
        pipe_bytes = pipe_character.encode('utf-8')

        valores = data.split(pipe_bytes) # ID_PAGINA | ID_PROCESSO | VALOR
        valor = int(valores[2].decode('utf-8').rstrip('\x00'))

        return valor
    
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
            cor = visualizacao_cores[chave]

            id_processo = chave[0]
            id_pagina = chave[1]

            if (id_processo == -1 or id_processo == 0) and (id_pagina == -1 or id_pagina == 0):
                continue
            
            valor = encontra_valor_ram_processo_pagina(id_processo, id_pagina)

            texto = f"ID: {id_pagina}\nProcesso: {id_processo}\nValor:{valor}\nCor: {cor}"
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
            cor = visualizacao_cores[chave]

            id_processo = chave[0]
            id_pagina = chave[1]

            if (id_processo == -1 or id_processo == 0) and (id_pagina == -1 or id_pagina == 0):
                continue

            valor = encontra_valor_disco_processo_pagina(id_processo, id_pagina)

            texto = f"ID: {id_pagina}\nProcesso: {id_processo}\nValor:{valor}\nCor: {cor}"
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

# Rotina que atualiza randomicamente valores da página do processo
def altera_processo():
    altera_valor = bool(random.randint(0, 1))
    if not (altera_valor):
        return
    
    if memoria_RAM:
        novo_valor = random.randint(10000, 99999)
        idx_aleatorio = random.randint(0, len(memoria_RAM) - 1)

        print("\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
        print(f"Alterando valor da página -> ID: {memoria_RAM[idx_aleatorio].id} // Processo: {memoria_RAM[idx_aleatorio].id_processo} de {memoria_RAM[idx_aleatorio].valor} para {novo_valor}")
        print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * \n")

        memoria_RAM[idx_aleatorio].valor = novo_valor
        pagina_etp_atual = encontra_pagina_etp(memoria_RAM[idx_aleatorio].id_processo, memoria_RAM[idx_aleatorio].id)
        pagina_etp_atual.bit_modificacao = True

        renderiza(False)

def encontra_pagina_etp(id_processo, id_pagina):
    for etp_processo in lista_etps_por_processo:
        if id_processo == etp_processo[0]:
            return etp_processo[1][id_pagina - 1]
        
# Execução
def inicializa_sistema():
    # Parte lógica
    if le_arquivo_input("C:\\Paginacao\\entrada.json") == False:
        return False

    cria_arquivo_disco()
    inicializa_memoria_virtual_etps()

    # Criação da estrutura que simula a Memória Principal (Memória RAM)
    global memoria_RAM
    global qtd_paginas_ram
    qtd_paginas_ram = tam_ram // tam_pagina
    memoria_RAM = deque(maxlen=qtd_paginas_ram)

    # Parte gráfica
    gera_paleta()
    gera_cores()
    preenche_dados_visualizacao_RAM()
    preenche_dados_visualizacao_disco()
    renderiza(True)

    os.system('cls')

    return True

if inicializa_sistema() == True:
    for pagina in memoria_virtual:
        if len(memoria_RAM) == qtd_paginas_ram and disco_esta_preenchido:
            print(f"Não há mais espaço disponível para paginação\n")
            break

        altera_processo()

        print(f"Página atual -> ID: {pagina.id} // Processo: {pagina.id_processo} | {pagina.valor} \n")

        pagina_etp = encontra_pagina_etp(pagina.id_processo, pagina.id)

        if ler_RAM(pagina_etp):
            print(f"Encontrada página atual na Memória Principal (Memória RAM)\n")
            print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
            continue

        pagina_atualizada = ler_disco(pagina_etp)
        print(f"Não foi encontrada a página atual na Memória Secundária (Disco)\n") if (pagina_atualizada == None) else print(f"Encontrada página atual na Memória Secundária (Disco)\n")

        grava_RAM(pagina if (pagina_atualizada == None) else pagina_atualizada, pagina_etp)

        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

print("Simulação encerrada")
plt.pause(10000)
