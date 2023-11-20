# coding: utf-8

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver
import unicodedata

X_USERNAME = 'usuarioX'
X_PASSWORD = 'senha'

# Função para realizar o login no X
def login_X(username, password, driver):
    driver.get('https://X.com/login')
    time.sleep(3)

    username_field = driver.find_element(By.CSS_SELECTOR, 'input')
    username_field.send_keys(username)

    login_button = driver.find_elements(By.CSS_SELECTOR, 'span')[9]
    login_button.click()

    time.sleep(3)

    password_field = driver.find_elements(By.CSS_SELECTOR, 'input')[1]
    password_field.send_keys(password)

    login_button = driver.find_elements(By.CSS_SELECTOR, 'span')[13]
    login_button.click()
    time.sleep(3)

# Função modificada para coletar postagens com base em uma palavra-chave e datas fornecidas
def get_postagens(query, start_date, end_date, driver_path):
    service = Service(driver_path)
    driver = WebDriver(service=service)

    login_X(X_USERNAME, X_PASSWORD, driver)

    url = f'https://X.com/search?l=brazil&q={query}%20lang%3Apt%20since%3A{start_date}%20until%3A{end_date}&src=typed_query&f=live'
    driver.get(url)
    time.sleep(3)

    body = driver.find_element(By.CSS_SELECTOR, 'body')

    postagens = []
    last_postagem_count = 0
    total_postagens = 0
    break_counter = 0

    while True:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(3)

        postagem_elements = driver.find_elements(By.CSS_SELECTOR, 'article')

        if total_postagens == last_postagem_count and total_postagens != 0:
            break_counter += 1
        else:
            break_counter = 0
            
        if break_counter == 3:
            break
        
        last_postagem_count = total_postagens

        for postagem in postagem_elements:
            try:
                user, username, date, text = extract_postagem_info(postagem)
                postagem_info = (user, username, date, text)

                if user and username and date and text and postagem_info not in postagens:
                    postagens.append(postagem_info)
                    total_postagens += 1
            except Exception as e:
                print(f"Erro ao obter o texto do postagem: {e}")

    driver.quit()
    return postagens

# Função para corrigir os caracteres especiais
def fix_special_characters(text):
    text = unicodedata.normalize('NFKD', text).encode('utf-8', 'ignore').decode('utf-8')
    return text

# Função para extrair informações do postagem
def extract_postagem_info(postagem):
    try:
        user_element = postagem.find_elements(By.CSS_SELECTOR, 'div')[0].find_elements(By.CSS_SELECTOR, 'span')[0]
        user = user_element.text.strip() if user_element else "Sem usuario"

        username_element = postagem.find_elements(By.CSS_SELECTOR, 'div')[0].find_elements(By.CSS_SELECTOR, 'span')[3]
        username = username_element.text.strip() if username_element else "Sem nome de usuario"

        date_element = postagem.find_elements(By.CSS_SELECTOR, 'div')[0].find_element(By.CSS_SELECTOR, 'time')
        date = date_element.text.strip() if date_element else "Sem data"

        # Extrair texto do postagem
        postagem_text_elements = postagem.find_elements(By.CSS_SELECTOR, 'div[data-testid="postagemText"] > span')
        text = ' '.join([element.text.strip() for element in postagem_text_elements])

        # Se estiver vazio ou tiver "Replying to", tenta pegar o texto do repostagem
        if text == "" or "Replying to" in text:
            repostagem_text_elements = postagem.find_elements(By.CSS_SELECTOR, 'div[data-testid="repostagemText"] > span')
            text = ' '.join([element.text.strip() for element in repostagem_text_elements])

        if text == "":
            text = "Sem texto"
        else:
            text = fix_special_characters(text)

        return (user, username, date, text)
    except Exception as e:
        print(f"Erro ao extrair informacoes do postagem: {e}")
        return ("", "", "", "")


# Função para salvar as informações no CSV
def save_to_csv(postagens, filename):
    df = pd.DataFrame(postagens, columns=['user', 'username', 'date', 'postagem'])
    df.replace(r'^\s*$', 'Sem texto', regex=True, inplace=True)
    df.dropna(how='all', inplace=True)
    df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')


if __name__ == '__main__':
    keyword = 'qdenga'
    start_date = '2023-06-20'
    end_date = '2023-09-29'
    driver_path = 'C:\Program Files (x86)\Microsoft\Edge\Application'

    postagens = get_postagens(keyword, start_date, end_date, driver_path)
    save_to_csv(postagens, 'vacina_dengue_qdenga_20jun2023-29set2023_v3.csv')

