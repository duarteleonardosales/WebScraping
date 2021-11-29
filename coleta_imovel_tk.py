#WEBSCRAPING PARA O SITE IMOVELWEB

#IMPORTS
from tkinter import ttk
import tkinter
import math
from urllib.request import Request, urlopen
from urllib.error import URLError,HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlretrieve
from selenium.webdriver import Chrome

#INTERFACE
root = tkinter.Tk()
root.title('ColetaImovel  -  Desenvolvido pelo Eng. Leonardo Sales Duarte')
root.geometry('720x360')
root.maxsize(720,360)
root.minsize(720,360)

#label e entry
frame_url = tkinter.LabelFrame(root, text='',font='Arial 12', height=140, width=700)
frame_url.place(anchor="nw", x=10, y=10)
label_url = ttk.Label(root, text='URL:', font='Arial 10')
label_url.place(anchor="nw", x=30, y=40)
url_string_var=tkinter.StringVar()
entry_url = ttk.Entry(root, textvariable=url_string_var, width=102)
entry_url.place(anchor="nw", x=70, y=40)

def iniciar_busca():

    #URL BASE DA PESQUISA
    url_base = url_string_var.get()
    #url_base = 'https://www.imovelweb.com.br/apartamentos-venda-centro-curitiba-300000-5000000-reales-drc-centro.html'

    #FUNÇÃO QUE RETORNA O HTML USANDO O SELENIUM
    def get_html(url_base):
        driver = Chrome()
        driver.get(url_base)
        html = driver.page_source
        #print(driver.current_url)
        return html

    #FUNÇÃO PARA TRATAR O HTML
    def tratar_html(html_str):
        return " ".join(html_str.split()).replace('> <','><')

    #DEFINIR O HTML E CRIAR O SOUP DO BeautifulSoup
    html = get_html(url_base)
    html = tratar_html(html)
    soup = BeautifulSoup(html, 'html.parser')

    #NUMERO DE IMOVEIS
    numero_de_imoveis = soup.find('h1', {'class': 'list-result-title'}).get_text()
    numero_de_imoveis = int(numero_de_imoveis.split()[0])
    #print(f'\nFoi detectado um total de {numero_de_imoveis} imóveis.\n')
    label_processamento1 = ttk.Label(root, text=f'Foi detectado um total de {numero_de_imoveis} imóveis.', font='Arial 10')
    label_processamento1.place(anchor="nw", x=30, y=80)

    #ENCONTRANDO O NUMERO DE PAGINAS
    numero_de_paginas = numero_de_imoveis/21 #21 IMOVEIS POR PAG
    numero_de_paginas = math.ceil(numero_de_paginas)
    #print(f'Foi detectado um total de {numero_de_paginas} páginas.\n')
    #print(f'Buscando informações...\n')
    label_processamento2 = ttk.Label(root, text=f'Buscando informações...', font='Arial 10')
    label_processamento2.place(anchor="nw", x=30, y=100)
    root.update()

    #LISTA QUE REPRESENTA TODAS OS ANUNCIOS DE TODAS AS PAGINAS
    cards = []

    #LOOP PARA CADA PAGINA
    for i in range(numero_de_paginas):
        #print(f'Etapa {i+1} de {numero_de_paginas}')
        label_processamento3 = ttk.Label(root, text=f'Etapa {i+1} de {numero_de_paginas}', font='Arial 10')
        label_processamento3.place(anchor="nw", x=30, y=120)

        root.update()
        url = url_base
        url = url.replace('.html', f'-pagina-{i+1}.html')
        #print(url)
        html = get_html(url)
        html = tratar_html(html)
        soup = BeautifulSoup(html, 'html.parser')
        anuncios = soup.find('div', id ='react-posting-cards').find('div', class_="list-card-container") #achou os anunciou
        anuncios = anuncios.find_all('div', class_ ="postingCardContent") #separados em uma lista

        #LOOP PARA LER O ANUNCIOS DE CADA PAG
        for anuncio in anuncios:
            card = {}

            # FONTE
            if anuncio.find_parent('div'):
                link = anuncio.find_parent('div').get('data-to-posting')  # ok
                card['fonte'] = f'https://www.imovelweb.com.br{link}'
            else:
                card['fonte'] = '-'

            # CRIANDO SOUP ESPECIFICO PARA CADA ENTRAR NA PAGINA DE CADA ANUNCIO
            anuncio_url = f'https://www.imovelweb.com.br{link}'
            html_anuncio = get_html(anuncio_url)
            html_anuncio = tratar_html(html_anuncio)
            soup_anuncio = BeautifulSoup(html_anuncio, 'html.parser')

            # VALOR
            if soup_anuncio.find('div', class_ ="price-container").find('span'):
                valor = soup_anuncio.find('div', class_ ="price-container").find('span') #ok
                card['valor'] = valor.get_text()
                #print('valor')
                #print(valor)
            else:
                card['valor'] = math.nan

            # CONDOMINIO
            if soup_anuncio.find('div', class_="block-expensas block-row"):
                condominio = soup_anuncio.find('div', class_="block-expensas block-row").find('span')  # ok
                card['condominio'] = condominio.get_text()
                #print('cond')
                #print(soup_anuncio.find('div', class_="block-expensas block-row").get_text())
                #print(soup_anuncio.find('div', class_="block-expensas block-row").find('span').get_text())
            else:
                card['condominio'] = math.nan

            # IPTU
            if soup_anuncio.find('div', class_="block-expensas block-row"):
                if soup_anuncio.find('div', class_="block-expensas block-row").findNextSibling():
                    iptu = soup_anuncio.find('div', class_="block-expensas block-row").findNextSibling().find('span')  # ok
                    #print(iptu)
                    card['iptu'] = iptu.get_text()
                    #print(iptu)
            else:
                card['iptu'] = math.nan

            # AREA TOTAL
            if soup_anuncio.find('i', class_="icon-stotal"):
                area_total = soup_anuncio.find('i', class_="icon-stotal").find_parent('li')  # ok
                card['area_total'] = area_total.get_text()
                #print(area_total)
            else:
                card['area_total'] = math.nan

            # AREA UTIL
            if soup_anuncio.find('i', class_="icon-scubierta"):
                area_util = soup_anuncio.find('i', class_="icon-scubierta").find_parent('li')  # ok
                card['area_util'] = area_util.get_text()
                #print(area_util)
            else:
                card['area_util'] = math.nan

            # QUARTOS
            if soup_anuncio.find('i', class_="icon-dormitorio"):
                quarto = soup_anuncio.find('i', class_="icon-dormitorio").find_parent('li')  # ok
                card['quarto'] = quarto.get_text()
                #print(quarto)
            else:
                card['quarto'] = math.nan

            # SUITES
            if soup_anuncio.find('i', class_="icon-toilete"):
                suites = soup_anuncio.find('i', class_="icon-toilete").find_parent('li')  # ok
                card['suites'] = suites.get_text()
                #print(suites)
            else:
                card['suites'] = math.nan

            # WC
            if soup_anuncio.find('i', class_="icon-bano"):
                wc = soup_anuncio.find('i', class_="icon-bano").find_parent('li')  # ok
                card['wc'] = wc.get_text()
                #print(wc)
            else:
                card['wc'] = math.nan

            # VAGAS
            if soup_anuncio.find('i', class_="icon-cochera"):
                vagas = soup_anuncio.find('i', class_="icon-cochera").find_parent('li')  # ok
                card['vagas'] = vagas.get_text()
                #print(vagas)
            else:
                card['vagas'] = math.nan

            # RESUMO
            if soup_anuncio.find('div', class_="section-title"):
                resumo = soup_anuncio.find('div', class_="section-title").find('h1')  # ok
                card['resumo'] = resumo.get_text()
            else:
                card['resumo'] = '-'

            # DESCRICAO
            if soup_anuncio.find('div', id="longDescription"):
                descricao = soup_anuncio.find('div', id="longDescription").find('div') # ok
                #print('descricao')
                #print(descricao)
                card['descricao'] = descricao.get_text()
            else:
                card['descricao'] = '-'

            # ENDERECO
            if soup_anuncio.find('h2', class_="title-location"):
                endereco = soup_anuncio.find('h2', class_="title-location")  # ok
                card['endereco'] = endereco.get_text()
            else:
                card['endereco'] = '-'

            #INSERIR CADA CARD DA PAGINA NA LISTA DOS CARDS
            cards.append(card)

    #CRIAR E EXPORTAR UM DATASET COM TODAS AS INFORMACOES
    dataset = pd.DataFrame(cards)
    dataset.to_csv(f'DataSet_Final.csv', index=False, sep=';', encoding='utf-8-sig')

button = ttk.Button(root, text=f'BUSCAR', command=iniciar_busca)
button.place(anchor="nw", x=613, y=70)

root.mainloop()
