#WEBSCRAPING PARA O SITE IMOVELWEB

#IMPORTS
import math
from urllib.request import Request, urlopen
from urllib.error import URLError,HTTPError
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlretrieve
from selenium.webdriver import Chrome

#URL BASE DA PESQUISA
url_base = 'https://www.imovelweb.com.br/apartamentos-venda-centro-curitiba-300000-5000000-reales-drc-centro.html'

#FUNÇÃO QUE RETORNA O HTML USANDO O SELENIUM
def get_html(url_base):
    driver = Chrome()
    driver.get(url_base)
    html = driver.page_source
    print(driver.current_url)
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
print(numero_de_imoveis)
numero_de_imoveis = int(numero_de_imoveis.split()[0])

#ENCONTRANDO O NUMERO DE PAGINAS
numero_de_paginas = numero_de_imoveis/21 #21 IMOVEIS POR PAG
numero_de_paginas = math.ceil(numero_de_paginas)
print(numero_de_paginas)

#LISTA QUE REPRESENTA TODAS OS ANUNCIOS DE TODAS AS PAGINAS
cards = []

#LOOP PARA CADA PAGINA
for i in range(numero_de_paginas):

    url = url_base
    url = url.replace('.html', f'-pagina-{i+1}.html')
    print(url)
    html = get_html(url)
    html = tratar_html(html)
    soup = BeautifulSoup(html, 'html.parser')
    anuncios = soup.find('div', id ='react-posting-cards').find('div', class_="list-card-container") #achou os anunciou
    anuncios = anuncios.find_all('div', class_ ="postingCardContent") #separados em uma lista

    #LOOP PARA LER O ANUNCIOS DE CADA PAG
    for anuncio in anuncios:
        card = {}

        # VALOR
        if anuncio.find('div', class_ ="postingCardPriceBlock").find('span'):
            valor = anuncio.find('div', class_ ="postingCardPriceBlock").find('span').get('data-price') #ok
            card['value'] = valor
        else:
            card['value'] = math.nan

        # AREA
        if anuncio.find('i', class_="iconArea"):
            area = anuncio.find('i', class_="iconArea").find_parent('li')  # ok
            card['area'] = area.get_text()
        else:
            card['area'] = math.nan

        # QUARTOS
        if anuncio.find('i', class_="iconBedrooms"):
            quarto = anuncio.find('i', class_="iconBedrooms").find_parent('li')  # ok
            card['quarto'] = quarto.get_text()
        else:
            card['quarto'] = math.nan

        # WC
        if anuncio.find('i', class_="iconBathrooms"):
            wc = anuncio.find('i', class_="iconBathrooms").find_parent('li')  # ok
            card['wc'] = wc.get_text()
        else:
            card['wc'] = math.nan

        # VAGAS
        if anuncio.find('i', class_="iconGarage"):
            vagas = anuncio.find('i', class_="iconGarage").find_parent('li')  # ok
            card['vagas'] = vagas.get_text()
        else:
            card['vagas'] = math.nan

        # RESUMO
        if anuncio.find('a', class_="go-to-posting"):
            resumo = anuncio.find('a', class_="go-to-posting")  # ok
            card['resumo'] = resumo.get_text()
        else:
            card['resumo'] = '-'

        # DESCRICAO
        if anuncio.find('div', class_="postingCardDescription"):
            descricao = anuncio.find('div', class_="postingCardDescription")  # ok
            card['descricao'] = descricao.get_text()
        else:
            card['descricao'] = '-'

        # ENDERECO
        if anuncio.find('span', class_="postingCardLocationTitle"):
            endereco = anuncio.find('span', class_="postingCardLocationTitle")  # ok
            card['endereco'] = endereco.get_text()
        else:
            card['endereco'] = math.nan

        # FONTE
        if anuncio.find_parent('div'):
            link = anuncio.find_parent('div').get('data-to-posting') # ok
            card['fonte'] = f'https://www.imovelweb.com.br{link}'
        else:
            card['fonte'] = '-'

        #INSERIR CADA CARD DA PAGINA NA LISTA DOS CARDS
        cards.append(card)

#CRIAR E EXPORTAR UM DATASET COM TODAS AS INFORMACOES
dataset = pd.DataFrame(cards)
dataset.to_csv(f'DataSet_Final.csv', index=False, sep=';', encoding='utf-8-sig')
