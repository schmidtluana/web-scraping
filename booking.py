from playwright.sync_api import sync_playwright
import os

def scrape_city(city_name):
    with sync_playwright() as p:
        search_query = city_name.replace(" ", "+") + ",+Santa+Catarina,+Brasil"
        page_url = f'https://www.booking.com/searchresults.pt-br.html?ss={search_query}'

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

        print(f"\nTotal de hotéis encontrados em {city_name}: {len(filtered_hrefs)}")
        if len(filtered_hrefs) < 50:
            print(f"Atenção: Menos de 50 hotéis encontrados em {city_name}!")

        # Criar pasta para salvar os arquivos
        output_dir = os.path.join("hotels", city_name)
        os.makedirs(output_dir, exist_ok=True)

        # Itera sobre cada hotel e salva as informações relevantes
        for index, url in enumerate(filtered_hrefs):
            try:
                page.goto(url, timeout=60000)
                page.wait_for_timeout(4000)

                print(f"Visitando hotel {index + 1} em {city_name}: {url}")

                # Coleta apenas textos visíveis e relevantes
                extracted_texts = page.evaluate(
                    '''() => Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div'))
                        .map(el => el.innerText.trim())
                        .filter(text => text.length > 10)'''
                )

                if not extracted_texts:
                    print(f"Aviso: Nenhum texto relevante encontrado para {url}")

                # Salva em um arquivo TXT
                hotel_filename = os.path.join(output_dir, f"hotel_{index + 1}.txt")
                with open(hotel_filename, 'w', encoding='utf-8') as f:
                    f.write("\n".join(extracted_texts))
            except Exception as e:
                print(f"Erro ao processar {url}: {e}")

        print(f"Processo finalizado para {city_name}!")
        browser.close()

def main():
    cities = [
        "Apiúna", "Ascurra", "Benedito Novo", "Blumenau", "Botuverá",
        "Brusque", "Doutor Pedrinho", "Gaspar", "Guabiruba", "Indaial",
        "Pomerode", "Rio dos Cedros", "Rodeio", "Timbó"
    ]
    for city in cities:
        scrape_city(city)

if __name__ == '__main__':
    main()
