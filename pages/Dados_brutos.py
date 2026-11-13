import streamlit as st
import requests 
import pandas as pd
import time


@st.cache_data 
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon='✅')
    time.sleep(5)
    sucesso.empty()

st.title('Dados Brutos')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Filtro colunas
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# Filtro produto
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', list(dados['Produto'].unique()), list(dados['Produto'].unique()))

# filtro categoria
with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione categoria', list(dados['Categoria do Produto'].unique()), list(dados['Categoria do Produto'].unique()))

# Filtro preço
with st.sidebar.expander('Selecione o preço'):
    precos = st.slider('Selecione o preço', 0, 5000, (0,5000) )

#Filtro frete
with st.sidebar.expander('Frete do produto'):
    frete = st.slider('Selecione o valor do frete', 0, 217, (0,217))

#Filtro vendedor
with st.sidebar.expander('Vendedores'):
    vendedor = st.multiselect('Selecione o vendedor', list(dados['Vendedor'].unique()), list(dados['Vendedor'].unique()))

#Filtro estado
with st.sidebar.expander('Estado de compra'):
    estado = st.multiselect ('Selecione o estado', list(dados['Local da compra'].unique()), list(dados['Local da compra'].unique()))

#Filtro avaliação compra
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação', 0, 5, (0,5))

#Filtro tipo pagamento
with st.sidebar.expander('Tipo de pagamento'):
    pagamento = st.multiselect('Selecione o tipo de pagamento', list(dados['Tipo de pagamento'].unique()), list(dados['Tipo de pagamento'].unique()))

#Filtro parcela
with st.sidebar.expander('Quantidade de parcela'):
    parcela = st.slider('Selecione a quantide de parcela', 0, 12, (0,12))

#Filtro data compra
with st.sidebar.expander('Data da compra'):
    data = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

query = '''
    Produto in @produtos and \
    `Categoria do Produto` in @categoria and \
    @precos[0] <= Preço <= @precos[1] and \
    @frete[0] <= Frete <= @frete[1] and \
    Vendedor in @vendedor and \
    `Local da compra` in @estado and \
    @avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and \
    `Tipo de pagamento` in @pagamento and \
    @parcela[0] <= `Quantidade de parcelas` <= @parcela[1] and \
    @data[0] <= `Data da Compra` <= @data[1]
'''
dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'Esta tabela :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value= 'dados')
    nome_arquivo += '.csv'

with coluna2:
    st.download_button('Fazer o download da tabela em csv', data=converte_csv(dados_filtrados),file_name=nome_arquivo, mime= 'text/csv', on_click=mensagem_sucesso)
