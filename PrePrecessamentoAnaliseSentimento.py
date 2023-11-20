import pandas as pd
import numpy as np
import re
import string
from leia import SentimentIntensityAnalyzer 
from nltk.tokenize import TweetTokenizer

# Carrega os dados
df = pd.read_excel("vacina_dengue_qdenga_20jun2023-29set2023_v3.xlsx")

# Palavras-chave para procurar no nome do usuário
excluir_palavras = ['diario','sbt', 'band', 'uol', 'g1', 'radio', 'veja', 'noticia', 'news', 'jornal', 'folha', 'portal', 'cnn', 'cbn', 'estadao']

# Função para verificar se alguma palavra está contida no texto
def contem_palavra(texto, palavras):
    texto = str(texto)  # Converte o valor para string
    return any(palavra.lower() in texto.lower() for palavra in palavras)

# Filtrar o DataFrame
df_filtrado = df[~(df['user'].astype(str).apply(contem_palavra, palavras=excluir_palavras) |
                   df['username'].astype(str).apply(contem_palavra, palavras=excluir_palavras))]

# Função de pré-processamento
def preprocessamento(postagem):
    # Verifica se o postagem é uma string
    if isinstance(postagem, str):
        # Substitui quebras de linha por espaços
        postagem = postagem.replace('\n', ' ')
        # Remove URLs
        postagem = re.sub(r'http\S+|www\S+|https\S+', '', postagem, flags=re.MULTILINE)
        # Tokenização
        postagem_tokenizer = TweetTokenizer()
        tokens = postagem_tokenizer.tokenize(postagem)
        # Junta os tokens de volta em uma string
        postagem = ' '.join(tokens)
    else:
        postagem = ''
    return postagem

# Substitui NaN por uma string vazia
df_filtrado['postagem'] = df_filtrado['postagem'].fillna('')

# Aplica o pré-processamento
df_filtrado['postagem_processado'] = df_filtrado['postagem'].apply(preprocessamento)

s = SentimentIntensityAnalyzer()

def analisesentimento(postagem_processado):
 df_analisado = s.polarity_scores(postagem_processado)['compound'] 
 return df_analisado

# aplicando a função e guardando na coluna sentimento
df_filtrado['sentimento'] = df_filtrado['postagem_processado'].apply(analisesentimento)

# função que transforma valores do compound em positivo, negativo e neutro
def analisesentimento2(sentimento):
    if sentimento >= 0.05:
        return 'positivo'
    elif sentimento <= -0.05:    
        return 'negativo'
    else:
        return 'neutro'
  
 # aplicando
df_filtrado['sentimento'] = df_filtrado['sentimento'].apply(analisesentimento2)

# Especifica o nome do arquivo Excel
analise_sentimento = "analise_sentimento.xlsx"

# Exporta o DataFrame para um arquivo Excel
df_filtrado.to_excel(analise_sentimento, index=False)


# OUTRAS ANÁLISES

#%% Word Cloud
import re
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from wordcloud import WordCloud

# Baixar a lista de stopwords do NLTK
import nltk
nltk.download('stopwords')
nltk.download('punkt')

# Definir as stopwords
stop_words = set(stopwords.words('portuguese'))

# Função de pré-processamento
def preProc(texto):
    # Convertendo para minúsculas
    texto = texto.lower()
    # Removendo URLs, hashtags, menções, pontuações e números
    texto = re.sub(r'http\S+|www\S+|https\S+|@\w+|#\w+|[^\w\s]|\d', '', texto)
    # Tokenização
    tokens = word_tokenize(texto)
    # Removendo stopwords e palavras com menos de 4 letras
    tokens = [palavra for palavra in tokens if palavra not in stop_words and len(palavra) > 3]
    # Removendo termos especificos
    tokens = [palavra for palavra in tokens if palavra not in ['contra', 'tambem', 'porque', 'sera', 'fazer', 'voces', 'anos']]
    return tokens

# Aplicar a função de pré-processamento
df_filtrado['tokens'] = df_filtrado['postagem_processado'].apply(preProc)


# Contando frequências dos termos individuais
counter_individual = Counter()
df_filtrado['tokens'].apply(counter_individual.update)

# Gerando combinações de pares de palavras
counter_pares = Counter()
df_filtrado['tokens'].apply(lambda tokens: counter_pares.update([" ".join(pair) for pair in zip(tokens, tokens[1:])]))

# Eliminar pares que são permutações de outros com menor frequência
for termo in list(counter_pares):
    palavras = termo.split()
    permutacoes = [" ".join(palavras[::-1])]
    frequencias = [counter_pares[permutacao] for permutacao in permutacoes if permutacao in counter_pares]
    if frequencias and counter_pares[termo] < max(frequencias):
        del counter_pares[termo]

# Combinar contadores e excluir termos com menos de 100 ocorrências
counter_total = counter_individual + counter_pares
termos_finais = {termo: freq for termo, freq in counter_total.items() if freq >= 50}


# Criando a Word Cloud
wordcloud = WordCloud(width=800, height=800, background_color='white', min_font_size=10)
wordcloud.generate_from_frequencies(termos_finais)

# Plota a imagem da Word Cloud
plt.figure(figsize=(8, 8), facecolor=None)
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.tight_layout(pad=0)

# Salva a imagem
wordcloud.to_file("wordcloud.png")

# Mostra a imagem
plt.show()

# Listando termos e frequências
print("Termo\tFrequência")
for termo, freq in termos_finais.items():
    print(f"{termo}\t{freq}")


# Criar um DataFrame a partir do dicionário de termos e frequências
df_termos = pd.DataFrame(list(termos_finais.items()), columns=['Termo', 'Frequência'])

# Ordenar o DataFrame pela frequência em ordem decrescente
df_termos = df_termos.sort_values(by='Frequência', ascending=False)

# Exportar o DataFrame para um arquivo Excel
df_termos.to_excel("termos_frequencia.xlsx", index=False)




#%% Análise hashtags
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import unicodedata

# Função para extrair hashtags no formato utf8
def extrair_hashtags(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = texto.lower()
    return re.findall(r'#\w+', texto)

# Aplicar a função e extrair as hashtags
df_filtrado['hashtags'] = df_filtrado['postagem_processado'].apply(extrair_hashtags)

# Criar uma lista com todas as hashtags
lista_hashtags = sum(df_filtrado['hashtags'].tolist(), [])

# Contar a frequência das hashtags
frequencia_hashtags = Counter(lista_hashtags)

# Remover hashtags com menos de x ocorrências (se necessário)
frequencia_hashtags = {k: v for k, v in frequencia_hashtags.items() if v >= 0}

# Gerar a Word Cloud
wordcloud = WordCloud(width=600, height=400, background_color='white').generate_from_frequencies(frequencia_hashtags)

# Mostrar a Word Cloud
plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# Imprimir as hashtags e suas frequências
for hashtag, frequencia in frequencia_hashtags.items():
    print(f'{hashtag}: {frequencia}')


# Converter o contador de hashtags em um DataFrame
hashtags_df = pd.DataFrame(frequencia_hashtags.items(), columns=['Hashtag', 'Frequência'])

# Ordenar o DataFrame pela frequência (opcional)
hashtags_df = hashtags_df.sort_values(by='Frequência', ascending=False)

# Exportar para Excel
nome_arquivo_excel = "hashtags_frequencia.xlsx"
hashtags_df.to_excel(nome_arquivo_excel, index=False)


#%%TOP 10 HASHTAGS

# Identificar as 10 hashtags mais frequentes
top_hashtags = hashtags_df.head(10)

# Inicializar um dicionário para armazenar a contagem de sentimentos
sentimento_hashtags = {hashtag: {'positivo': 0, 'negativo': 0, 'neutro': 0} for hashtag in top_hashtags['Hashtag']}

# Função para atualizar a contagem de sentimentos para as hashtags
def contar_sentimento(row):
    for hashtag in row['hashtags']:
        if hashtag in sentimento_hashtags:
            sentimento_hashtags[hashtag][row['sentimento']] += 1

# Aplicar a função em cada linha do DataFrame
df_filtrado.apply(contar_sentimento, axis=1)

# Converter o dicionário de volta para um DataFrame para fácil visualização e análise
hashtags_sentimento_df = pd.DataFrame(sentimento_hashtags).transpose().reset_index()
hashtags_sentimento_df.columns = ['Hashtag', 'Positivo', 'Negativo', 'Neutro']

# Salvar o DataFrame para um arquivo Excel
hashtags_sentimento_df.to_excel("hashtags_sentimento.xlsx", index=False)

hashtags_sentimento_df

#%%TOP 5 HASHTAGS COM A PALAVRA "DENGUE"

# Filtrar hashtags que contêm 'dengue'
hashtags_com_dengue = hashtags_df[hashtags_df['Hashtag'].str.contains('vacina', case=False)]

# Identificar as 5 hashtags mais frequentes que contêm 'dengue'
top_hashtags_dengue = hashtags_com_dengue.head(5)

# Inicializar um dicionário para armazenar a contagem de sentimentos
sentimento_hashtags_dengue = {hashtag: {'positivo': 0, 'negativo': 0, 'neutro': 0} for hashtag in top_hashtags_dengue['Hashtag']}

# Função para atualizar a contagem de sentimentos para as hashtags
def contar_sentimento_dengue(row):
    for hashtag in row['hashtags']:
        if hashtag in sentimento_hashtags_dengue:
            sentimento_hashtags_dengue[hashtag][row['sentimento']] += 1

# Aplicar a função em cada linha do DataFrame
df_filtrado.apply(contar_sentimento_dengue, axis=1)

# Converter o dicionário de volta para um DataFrame para fácil visualização e análise
hashtags_sentimento_dengue_df = pd.DataFrame(sentimento_hashtags_dengue).transpose().reset_index()
hashtags_sentimento_dengue_df.columns = ['Hashtag', 'Positivo', 'Negativo', 'Neutro']

# Salvar o DataFrame para um arquivo Excel
hashtags_sentimento_dengue_df.to_excel("hashtags_vacina_sentimento.xlsx", index=False)

# Mostrar o DataFrame
print(hashtags_sentimento_dengue_df)


#%% GRÁFICO BARRAS TWEET POR SEMANA

import pandas as pd
import matplotlib.pyplot as plt

# 'date' no formato datetime
df_filtrado['date'] = pd.to_datetime(df_filtrado['date'], format='%d/%m/%Y %H:%M:%S')

# Adicionar uma coluna com o número da semana do ano
df_filtrado['week_of_year'] = df_filtrado['date'].dt.isocalendar().week

# Agrupar por semana e sentimento e contar as frequências
postagens_por_semana_e_sentimento = df_filtrado.groupby(['week_of_year', 'sentimento']).size().unstack(fill_value=0)

# Obter uma lista das semanas para o eixo x
weeks = postagens_por_semana_e_sentimento.index

# Obter a largura das barras
bar_width = 0.35

# Configurar a posição das barras no eixo x
r1 = np.arange(len(weeks))
r2 = [x + bar_width for x in r1]
r3 = [x + bar_width for x in r2]

# Criar barras
plt.figure(figsize=(15, 8))

plt.bar(r1, postagens_por_semana_e_sentimento['positivo'], color='green', width=bar_width, edgecolor='gray', label='Positivo')
plt.bar(r2, postagens_por_semana_e_sentimento['negativo'], color='red', width=bar_width, edgecolor='gray', label='Negativo')
plt.bar(r3, postagens_por_semana_e_sentimento['neutro'], color='blue', width=bar_width, edgecolor='gray', label='Neutro')

# Adicionar rótulos e título
plt.xlabel('Semana do Ano', fontweight='bold')
plt.xticks([r + bar_width for r in range(len(weeks))], weeks)
plt.ylabel('Quantidade de Postagens')
plt.title('Quantidade de Postagens por Semana e Sentimento')

# Criar legenda e mostrar gráfico
plt.legend()
plt.tight_layout()
plt.show()

