import csv
import re
import os
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

def extract_city_from_url(city_url):
    parsed_url = urlparse(city_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('ss', ['N/A'])[0]

def scrape_hotels(city_url, all_data):
    city = extract_city_from_url(city_url)
    
    print(city)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(city_url, timeout=60000)
        
        previous_height = 0
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == previous_height:
                break
            previous_height = new_height
        
        sticky_div = page.query_selector('[data-testid="sticky-container"]')
        sticky_position = sticky_div.bounding_box()['y'] if sticky_div else float('inf')
        
        hotel_cards = page.query_selector_all('[data-testid="property-card"]')
        hoteis_filtrados = [hotel for hotel in hotel_cards if hotel.bounding_box()['y'] < sticky_position]
        
        for hotel in hoteis_filtrados:
            link_element = hotel.query_selector('a')
            link = link_element.get_attribute('href') if link_element else 'N/A'
            
            nome_element = hotel.query_selector('[data-testid="title"]')
            nome = nome_element.inner_text() if nome_element else 'N/A'
            
            avaliacao_element = hotel.query_selector('[data-testid="review-score"]')
            avaliacoes_texto = avaliacao_element.inner_text() if avaliacao_element else 'N/A'
            
            match_nota = re.search(r'(\d+,\d+)', avaliacoes_texto)
            match_avaliacao = re.search(r'(Muito bom|Fabuloso|Fantástico|Excelente|Bom|Satisfatório)', avaliacoes_texto)
            match_quantidade = re.search(r'(\d{1,3}(?:\.\d{3})*) avaliações', avaliacoes_texto)
            
            nota = match_nota.group(1) if match_nota else 'N/A'
            avaliacao = match_avaliacao.group(1) if match_avaliacao else 'N/A'
            quantidade_avaliacoes = match_quantidade.group(1) if match_quantidade else 'N/A'
            
            preco_element = hotel.query_selector('span[data-testid="price-and-discounted-price"]')
            preco = preco_element.inner_text().replace('\xa0', '').strip() if preco_element else 'N/A'
            
            hotel_page = browser.new_page()
            hotel_page.goto(link, timeout=60000)
            try:
                info = hotel_page.locator('div.hp_desc_main_content').inner_text()
            except:
                info = "N/A"
            hotel_page.close()
            
            all_data.append([link, city, nome, nota, avaliacao, quantidade_avaliacoes, info, preco])
        
        browser.close()
        
def main():
    city_urls = [
        "https://www.booking.com/searchresults.pt-br.html?ss=Rodeio%2C+Santa+Catarina%2C+Brasil&ssne=Blumenau&ssne_untouched=Blumenau&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-666912&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=ffaca84277260104&ac_meta=GhBmZmFjYTg0Mjc3MjYwMTA0IAAoATICeGI6BnJvZGVpb0AASgBQAA%3D%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Api%C3%BAna&ssne=Api%C3%BAna&ssne_untouched=Api%C3%BAna&efdco=1&label=gen173nr-1FCAQoggJCDnNlYXJjaF9hcGnDum5hSC1YBGggiAEBmAEtuAEXyAEM2AEB6AEB-AEDiAIBqAIDuAKH24y_BsACAdICJGFkNjY0MDlkLTA1ODItNDhlZi04NDRhLTdkYzVmNDNjY2M5MtgCBeACAQ&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-625400&dest_type=city&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Blumenau&ssne=Blumenau&ssne_untouched=Blumenau&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-629420&dest_type=city&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Ascurra&ssne=Ascurra&ssne_untouched=Ascurra&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-626503&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=2&search_selected=true&search_pageview_id=4a34a06d5d590291&ac_meta=GhA0YTM0YTA2ZDVkNTkwMjkxIAAoATICeGI6B0FzY3VycmFAAEoAUAA%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Benedito+Novo&ssne=Benedito+Novo&ssne_untouched=Benedito+Novo&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-629191&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=2&search_selected=true&search_pageview_id=d5b2a08614000551&ac_meta=GhBkNWIyYTA4NjE0MDAwNTUxIAAoATICeGI6DUJlbmVkaXRvIE5vdm9AAEoAUAA%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Brusque&ssne=Brusque&ssne_untouched=Brusque&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-631607&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=2141a09aa4c407c2&ac_meta=GhAyMTQxYTA5YWE0YzQwN2MyIAAoATICeGI6B0JydXNxdWVAAEoAUAA%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Doutor+Pedrinho&ssne=Doutor+Pedrinho&ssne_untouched=Doutor+Pedrinho&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-640549&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=3&search_selected=true&search_pageview_id=9ba6a0d949190ef9&ac_meta=GhA5YmE2YTBkOTQ5MTkwZWY5IAAoATICeGI6D0RvdXRvciBQZWRyaW5ob0AASgBQAA%3D%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Gaspar&ssne=Gaspar&ssne_untouched=Gaspar&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-644623&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=229ba0ece1b411e3&ac_meta=GhAyMjliYTBlY2UxYjQxMWUzIAAoATICeGI6Bkdhc3BhckAASgBQAA%3D%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Guabiruba&ssne=Guabiruba&ssne_untouched=Guabiruba&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=900060634&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=1&search_selected=true&search_pageview_id=c47ba0fd5d16043d&ac_meta=GhBjNDdiYTBmZDVkMTYwNDNkIAAoATICeGI6CUd1YWJpcnViYUAASgBQAA%3D%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Indaial&ssne=Indaial&ssne_untouched=Indaial&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-646763&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=a87ea11c90b30611&ac_meta=GhBhODdlYTExYzkwYjMwNjExIAAoATICeGI6B0luZGFpYWxAAEoAUAA%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Pomerode&ssne=Pomerode&ssne_untouched=Pomerode&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-663019&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=72b2a12807e2077d&ac_meta=GhA3MmIyYTEyODA3ZTIwNzdkIAAoATICeGI6CFBvbWVyb2RlQABKAFAA&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Timb%C3%B3&ssne=Timb%C3%B3&ssne_untouched=Timb%C3%B3&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-676074&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=8aa0a136f558001f&ac_meta=GhA4YWEwYTEzNmY1NTgwMDFmIAAoATICeGI6BlRpbWLDs0AASgBQAA%3D%3D&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0",
        "https://www.booking.com/searchresults.pt-br.html?ss=Rio+dos+Cedros&ssne=Rio+dos+Cedros&ssne_untouched=Rio+dos+Cedros&label=gen173nr-1FCAQoggJCJ3NlYXJjaF9ibHVtZW5hdSwgc2FudGEgY2F0YXJpbmEsIGJyYXNpbEgtWARoIIgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gC-aWLvwbAAgHSAiRiOGZiOTZjYy03YmNhLTQ5YjItODEyZC0yMjc1ODg5ZWE1NDfYAgXgAgE&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-666653&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=xb&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=9a3aa145b8f8026f&ac_meta=GhA5YTNhYTE0NWI4ZjgwMjZmIAAoATICeGI6DlJpbyBkb3MgQ2Vkcm9zQABKAFAA&checkin=2025-04-15&checkout=2025-04-17&group_adults=2&no_rooms=1&group_children=0"
 ]
        
    all_data = []
    for url in city_urls:
        scrape_hotels(url, all_data)
    
    # Salvando em arquivo CSV
    with open('hotels_data.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Link", "Cidade", "Nome", "Nota", "Avaliação", "Quantidade Avaliações", "Informações", "Preço"])
        writer.writerows(all_data)

if __name__ == "__main__":
    main()