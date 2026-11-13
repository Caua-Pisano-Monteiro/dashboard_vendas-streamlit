import streamlit as st
import requests 
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

def formata_numero(valor, prefixo=''):
    for unidades in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidades}'
        valor/= 1000
    return f'{prefixo} {valor:.2f} mi'    
    
st.title('DASHBORAD DE VENDAS :shopping_cart: ')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano':ano}
response = requests.get(url, params= query_string)
dados = pd.DataFrame.from_dict(response.json())

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

##** Tabelas **##
# Aba1 Receita
receitas_estados = dados.groupby('Local da compra')[['Preço']].sum()
receitas_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receitas_estados, left_on= 'Local da compra', right_index= True).sort_values('Preço', ascending= False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
#Criando uma coluna Ano dentro de receita_mensal 
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

#Aba2 Quantidade de venda
qtd_estados = dados.groupby('Local da compra')[['Preço']].count().sort_values('Preço',ascending=False)
coordenadas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']]
quantidade_estado = coordenadas_estados.merge(qtd_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

quantidade_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count().reset_index()
quantidade_mensal['ANO'] = quantidade_mensal['Data da Compra'].dt.year
quantidade_mensal['MES'] = quantidade_mensal['Data da Compra'].dt.month_name()

quantidade_categoria = (dados.groupby('Categoria do Produto')[['Preço']]
                        .count().sort_values('Preço',ascending=False)
                        .rename(columns={'Preço':'Quantidade'}))

#Aba3 Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

##Gráficos##
fig_mapa_receita = px.scatter_geo(receitas_estados,
                                  lat= 'lat',
                                  lon= 'lon',
                                  scope= 'south america',
                                  size= 'Preço',
                                  template= 'seaborn',
                                  hover_name= 'Local da compra',
                                  hover_data= {'lat': False, 'lon': False},
                                  title= 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers= True,
                             range_y=(0,receita_mensal['Preço'].max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estado = px.bar(receitas_estados.head(),
                               x = 'Local da compra',
                               y = 'Preço',
                               text_auto= True,
                               title= 'Top estados( Receita )')
fig_receita_estado.update_layout(yaxis_title='Receita')

fig_receita_categoria = px.bar(receita_categoria.head(),
                               text_auto=True,
                               title ='Receita por Categoria')
fig_receita_categoria.update_layout(yaxis_title= 'Receita')

fig_quantidade_estado = px.scatter_geo(quantidade_estado,
                                       lat= 'lat',
                                       lon= 'lon',
                                       scope= 'south america',
                                       size= 'Preço',
                                       template= 'seaborn',
                                       hover_name= 'Local da compra',
                                       hover_data= {'lat':False, 'lon':False},
                                       labels={'Preço':'Quantidade'},
                                       title= 'Quantidade vendido por estado')

fig_quantidade_mensal = px.line(quantidade_mensal,
                             x = 'MES',
                             y = 'Preço',
                             markers= True,
                             range_y=(0,quantidade_mensal['Preço'].max()),
                             color= 'ANO',
                             line_dash= 'ANO',
                             labels={'Preço':'Quantidade'},
                             title= 'Receita Mensal')
fig_quantidade_mensal.update_layout(yaxis_title='Quantidade')

fig_quantidade_max_venda = px.bar(qtd_estados.head().reset_index(),
                                   x= 'Local da compra',
                                   y='Preço',
                                   text_auto=True,
                                   labels={'Preço':'Quantidade'},
                                   title= 'Top estados com maior quantidade de venda')
fig_quantidade_max_venda.update_layout(yaxis_title='Quantidade')

fig_quantidade_categoria = px.bar(quantidade_categoria,
                                  text_auto=True,
                                  title= 'Quantidade vendida por categoria')

## Visualização no streamlit##
aba1, aba2, aba3, aba4 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores', 'Data Frame'])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita", formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estado, use_container_width= True)

    with col2:
        st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categoria, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita", formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_quantidade_estado, use_container_width=True)
        st.plotly_chart(fig_quantidade_max_venda, use_container_width=True)
    with col2:
        st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_quantidade_mensal, use_container_width=True)
        st.plotly_chart(fig_quantidade_categoria, use_container_width=True )


with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Receita", formata_numero(dados['Preço'].sum(),'R$'))
        top_vendedores = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores)
        fig_receita_vendedores = px.bar(top_vendedores,
                                        x = 'sum',
                                        y = top_vendedores.index,
                                        text_auto=True,
                                        title= f'Top {qtd_vendedores} vendedores (Receita)')
        fig_receita_vendedores.update_layout(xaxis_title= 'Receita')
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)
    with col2:
        st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
        top_vendedores = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores)
        fig_quantidade_vendedores = px.bar(top_vendedores,
                                        x = 'count',
                                        y = top_vendedores.index,
                                        text_auto=True,
                                        title= f'Top {qtd_vendedores} vendedores (Quantidade de vendas)')
        fig_quantidade_vendedores.update_layout(xaxis_title= 'Quantidade')
        st.plotly_chart(fig_quantidade_vendedores, use_container_width=True)

with aba4:
    container = st.container()
    container.dataframe(dados)