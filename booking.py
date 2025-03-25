import csv
import re
from playwright.sync_api import sync_playwright
import os

def main():
    # Defina o caminho absoluto do arquivo
    output_file = os.path.expanduser('~') + '/Documents/hotels_rodeio.csv'  # Substitua por outro diretório se necessário

    with sync_playwright() as p:
        page_url = 'https://www.booking.com/searchresults.pt-br.html?ss=Rodeio&ssne=Rodeio&ssne_untouched=Rodeio&efdco=1&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-629420&dest_type=city&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0'

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(page_url, timeout=60000)

        # Scroll para carregar mais hotéis
        previous_height = 0
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)

            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height

        # Coletar os links dos hotéis
        hrefs = page.locator('a').evaluate_all(
            'elements => elements.map(element => element.href)'
        )
        filtered_hrefs = list(set(href for href in hrefs if href.startswith(
            "https://www.booking.com/hotel/br")))

        # Coletar os nomes dos hotéis
        nomes = page.locator('[data-testid="title"]').all_inner_texts()

        # Coletar as avaliações dos hotéis
        avaliacoes = page.locator('[data-testid="review-score"]').all_inner_texts()

        precos_raw = page.locator('span[data-testid="price-and-discounted-price"]').all_inner_texts()

        # Limpeza dos valores de preço
        precos = [preco.replace('\xa0', '').strip() for preco in precos_raw]

        # Inicializar listas para armazenar os dados
        notas = []
        avaliacao_texto = []
        quantidade_avaliacoes = []
        informacoes = []

        for avaliacao in avaliacoes:
            # Usar expressão regular para extrair a nota
            match_nota = re.search(r'(\d+,\d+)', avaliacao)
            match_avaliacao = re.search(r'(Muito bom|Fabuloso|Fantástico|Excelente|Bom|Satisfatório)', avaliacao)
            match_quantidade = re.search(r'(\d{1,3}(?:\.\d{3})*) avaliações', avaliacao)

            if match_nota:
                notas.append(match_nota.group(1))  # Adiciona a nota
            else:
                notas.append('N/A')

            if match_avaliacao:
                avaliacao_texto.append(match_avaliacao.group(1))  # Adiciona a avaliação
            else:
                avaliacao_texto.append('N/A')

            if match_quantidade:
                quantidade_avaliacoes.append(match_quantidade.group(1))  # Adiciona a quantidade de avaliações
            else:
                quantidade_avaliacoes.append('N/A')

        # Coletar as informações adicionais de cada hotel
        for href in filtered_hrefs:
            hotel_page = browser.new_page()
            hotel_page.goto(href, timeout=60000)

            # Buscar a descrição (informações do hotel)
            try:
                info = hotel_page.locator('div.hp_desc_main_content').inner_text()
            except:
                info = "N/A"

            informacoes.append(info)

            hotel_page.close()

        # Salvar os dados em um arquivo CSV com codificação utf-8-sig
        if len(filtered_hrefs) > 0 and len(nomes) > 0 and len(notas) > 0:
            with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(['Link', 'Nome', 'Nota', 'Avaliação', 'Quantidade Avaliações', 'Informações', 'Preço'])

                for link, nome, nota, avaliacao, qtd_avaliacoes, info, preco in zip(filtered_hrefs, nomes, notas, avaliacao_texto, quantidade_avaliacoes, informacoes, precos):
                    writer.writerow([link, nome, nota, avaliacao, qtd_avaliacoes, info, preco])

            print(f"Dados salvos em '{output_file}'")
        else:
            print("Não foi possível coletar dados suficientes para salvar no CSV.")

        browser.close()

if __name__ == '__main__':
    main()
