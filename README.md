# Análise de Sentimento sobre Vacina da Dengue

Este projeto utiliza técnicas de processamento de linguagem natural para analisar os sentimentos em postagens sobre a vacina da dengue. Baseia-se no estudo "Análise de Sentimentos dos Usuários do X (antigo Twitter) sobre a Vacina da Dengue no Brasil".

## Descrição

O projeto inclui as seguintes etapas:
- **Coleta de Dados do X**: Utiliza métodos como web scraping para extrair postagens contendo termos específicos relacionados à vacina da dengue.
- **Pré-processamento de Postagens**: Filtra contas de notícias e realiza a limpeza de dados para obter textos mais relevantes para análise.
- **Análise de Sentimentos**: Emprega o LeIA, adaptado do VADER, para interpretar sentimentos em textos em português. O LeIA foi desenvolvido por Souza et al. (2018) como uma adaptação do léxico VADER para a língua portuguesa, sendo um recurso fundamental para análises semânticas em textos brasileiros.
- **Visualização de Dados**: Apresenta os resultados por meio de Word Clouds e gráficos.

Os scripts principais são:
- `coleta_dados_X.py`: Coleta dados do X.
- `PrePrecessamentoAnaliseSentimento.py`: Realiza o pré-processamento e a análise de sentimentos.
- `leia.py`: Script que utiliza o léxico LeIA para avaliação semântica.

Além do LeIA, o projeto utiliza uma variedade de léxicos, localizados na pasta `lexicons`, que são cruciais para a análise de sentimentos. Esses léxicos incluem palavras e expressões categorizadas por sentimentos, que auxiliam na determinação precisa do sentimento expresso em cada postagem.

## Funcionalidades

- **Coleta de Dados**: Extrai postagens sobre a vacina da dengue com critérios específicos.
- **Pré-processamento de Postagens**: Limpeza e seleção de postagens relevantes.
- **Análise de Sentimentos**: Utiliza o LeIA para analisar sentimentos expressos nos postagens. O LeIA, sendo uma adaptação específica para o português, oferece uma análise mais precisa em comparação com léxicos genéricos.
- **Visualização de Dados**: Geração de representações visuais como Word Clouds e gráficos para ilustrar os resultados.

## Resultados

Os resultados identificam o sentimento geral sobre a vacina da dengue e fornecem insights sobre as principais hashtags e termos associados, armazenados em arquivos Excel para análise posterior.

## Como Usar

1. Clone o repositório.
2. Instale as dependências.
3. Execute `coleta_dados_X.py` para coletar os dados.
4. Execute `PrePrecessamentoAnaliseSentimento.py` para análise.
5. Explore os resultados.