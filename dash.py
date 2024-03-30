import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Análise do Preço da Gasolina", layout="wide")

# Definir o estilo CSS
custom_css = """
<style>
/* Estilo para o título */
h1 {
    color: #336666; /* Cor do título */
    font-size: 32px; /* Tamanho da fonte do título */
}

/* Estilo para o texto */
p {
    color: ##668c4d; /* Cor do texto */
    font-size: 18px; /* Tamanho da fonte do texto */
}

/* Estilo para o gráfico de barras */
div[data-testid="stHorizontalBlock"] .stHorizontalBlock .fullScreenFrame > div:first-child svg rect {
    fill: #f10c49; /* Cor da barra de seleção */
}

/* Estilo para os gráficos */
div[data-testid="stHorizontalBlock"] .stHorizontalBlock > div:first-child {
    margin-left: auto; /* Alinhar gráficos à direita */
    margin-right: auto; /* Alinhar gráficos à esquerda */
}
</style>
"""

# Aplicar o estilo personalizado
st.markdown(custom_css, unsafe_allow_html=True)


with st.container():
    

    st.title("Dashboard: Preço da Gasolina no Brasil (2004-2021)")
    
    st.write("Esse dashboard oferece uma análise abrangente do preço da gasolina no Brasil ao longo de 17 anos, de 2004 a 2021. Com base nos dados disponíveis no conjunto fornecido pelo Kaggle, é explorado as tendências de preços, sazonalidade e variações regionais.")


with st.container():
    st.write("---")
    
    df_main = pd.read_csv("data_gas.csv")
    
    
    # Erro no nome da coluna
    df_main.rename(columns={' DATA INICIAL': 'DATA INICIAL'}, inplace=True)

    # Estabelecendo datas, simplificando-as estabelecendo a ordem do DF por elas
    df_main['DATA INICIAL'] = pd.to_datetime(df_main['DATA INICIAL'])
    df_main['DATA FINAL'] = pd.to_datetime(df_main['DATA FINAL'])
    df_main['DATA MEDIA'] = ((df_main['DATA FINAL'] - df_main['DATA INICIAL'])/2) + df_main['DATA INICIAL']
    df_main = df_main.sort_values(by='DATA MEDIA',ascending=True)
    df_main.rename(columns = {'DATA MEDIA':'DATA'}, inplace = True)
    df_main.rename(columns = {'PREÇO MÉDIO REVENDA': 'VALOR REVENDA (R$/L)'}, inplace=True)

    # Criando uma coluna de Ano
    df_main["ANO"] = df_main["DATA"].apply(lambda x: str(x.year))

    # Resetando o index por uma questão organizacional
    df_main = df_main.reset_index()

    # Filtrando pois só falaremos da gasolina comum
    df_main = df_main[df_main.PRODUTO == 'GASOLINA COMUM'] # ou podemos deixar todos os produtos e depois utilizar como um filtro geral !!!!

    # Excluindo colunas que não usaremos
    df_main.drop(['UNIDADE DE MEDIDA', 'COEF DE VARIAÇÃO REVENDA', 'COEF DE VARIAÇÃO DISTRIBUIÇÃO', 
        'NÚMERO DE POSTOS PESQUISADOS', 'DATA INICIAL', 'DATA FINAL', 'PREÇO MÁXIMO DISTRIBUIÇÃO', 'PREÇO MÍNIMO DISTRIBUIÇÃO', 
        'DESVIO PADRÃO DISTRIBUIÇÃO', 'MARGEM MÉDIA REVENDA', 'PREÇO MÍNIMO REVENDA', 'PREÇO MÁXIMO REVENDA', 'DESVIO PADRÃO REVENDA', 
        'PRODUTO', 'PREÇO MÉDIO DISTRIBUIÇÃO'], inplace=True, axis=1)

with st.container():
    
        # Dividindo essa parte da página em duas
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        # Gráfico 2: Bar Chart (Preço Médio de Revenda por Região e Estado)
        with st.expander("Seletor para os Gráficos de Preço Médio de Revenda por Região e Estado", expanded=True):
            # Definir as opções para os anos e regiões
            anos_disponiveis = df_main['ANO'].unique()
            regioes_disponiveis = df_main['REGIÃO'].unique()

            # Dividir em duas colunas
            col1, col2 = st.columns(2)
            
            with col1:
            # Adicionar widgets para selecionar o ano 
                ano_selecionado = st.selectbox('Selecione o ano:', anos_disponiveis)
            with col2:
            # Adicionar widgets para selecionar a região
                regiao_selecionada = st.selectbox('Selecione a região:', regioes_disponiveis)
    with coluna2:
            # Filtrar os dados com base no ano e na região selecionados
            df_filtered = df_main[(df_main['ANO'] == ano_selecionado) & (df_main['REGIÃO'] == regiao_selecionada)]

            # Agrupar os dados para os gráficos
            dff_regiao = df_filtered.groupby(['ANO', 'REGIÃO'])['VALOR REVENDA (R$/L)'].mean().reset_index()
            dff_regiao = dff_regiao.sort_values(by='VALOR REVENDA (R$/L)', ascending=True)
            dff_regiao['VALOR REVENDA (R$/L)'] = dff_regiao['VALOR REVENDA (R$/L)'].round(decimals=2)

            dff_estado = df_filtered.groupby(['ANO', 'ESTADO'])['VALOR REVENDA (R$/L)'].mean().reset_index()
            dff_estado = dff_estado.sort_values(by='VALOR REVENDA (R$/L)', ascending=True)
            dff_estado['VALOR REVENDA (R$/L)'] = dff_estado['VALOR REVENDA (R$/L)'].round(decimals=2)

            # Criar texto para o hover
            fig1_text = [f'R${y:.2f}' for y in dff_regiao['VALOR REVENDA (R$/L)']]
            fig2_text = [f'R${y:.2f}' for y in dff_estado['VALOR REVENDA (R$/L)']]

            # Criar o primeiro gráfico de barras (região)
            fig1 = go.Figure(go.Bar(
            x=dff_regiao['VALOR REVENDA (R$/L)'],
            y=dff_regiao['REGIÃO'],
            orientation='h',
            text=fig1_text,
            textposition='auto',
            insidetextanchor='end',
            insidetextfont=dict(family='Times', size=12),
            width=0.4,
            marker=dict(color="#00aabe")
        ))

            fig1.update_layout(title=f'Preço Médio de Revenda por Região no Ano {ano_selecionado}',
            width=800,  # Largura do gráfico em pixels
            height=300, # Altura do gráfico em pixels
            )

            # Criar o segundo gráfico de barras (estado)
            fig2 = go.Figure(go.Bar(
                x=dff_estado['VALOR REVENDA (R$/L)'],
                y=dff_estado['ESTADO'],
                orientation='h',
                text=fig2_text,
                insidetextanchor='end',
                insidetextfont=dict(family='Times', size=12),
                width=0.4,
                marker=dict(color="#00aabe")
            ))

            fig2.update_layout(title=f'Preço Médio de Revenda por Estado na Região {regiao_selecionada} no Ano {ano_selecionado}',
            width=800,  # Largura do gráfico em pixels
            height=448, # Altura do gráfico em pixels
            )    
    # Ajustar o espaçamento entre as barras

    # Exibir o primeiro gráfico na primeira coluna
    with coluna1:
        with st.expander("Preço Médio de Revenda por Região", expanded=True):
            st.plotly_chart(fig1, use_container_width=True)

    # Exibir o segundo gráfico na segunda coluna
    with coluna2:
        with st.expander("Preço Médio de Revenda por Estado", expanded=True):
            st.plotly_chart(fig2, use_container_width=True)
with st.container():
    
     with coluna1:
        # Gráfico 1: Área Chart
        with st.expander("Gráfico de Área", expanded=True):
            max_values = df_main.groupby('ANO')['VALOR REVENDA (R$/L)'].max()
            min_values = df_main.groupby('ANO')['VALOR REVENDA (R$/L)'].min()

            final_df = pd.DataFrame({'Máximo': max_values, 'Mínimo': min_values})

            st.area_chart(final_df, use_container_width=True, width=1)

with st.container():
        dff = pd.DataFrame(df_main)
        with coluna2:
            # Selecionar os estados (definindo dois estados por padrão)
            estados_selecionados = st.multiselect('Selecione os estados:', dff['ESTADO'].unique(), default=dff['ESTADO'].unique()[:2])

# Gráfico 3: Preço Médio de Revenda por Estado
with st.container():
    with coluna2:
        with st.expander("Comparativo do Preço Médio de Revenda por Estado", expanded=True):
            # Filtrar os dados para os estados selecionados
            df_filtered = dff[dff['ESTADO'].isin(estados_selecionados)]

            # Agrupar os dados por mês e calcular a média do preço de revenda para cada estado
            df_estado = df_filtered.groupby(['ESTADO', pd.Grouper(key='DATA', freq='M')])['VALOR REVENDA (R$/L)'].mean().reset_index()

            # Criar o gráfico de linhas
            fig3 = go.Figure()

            # Adicionar linhas para cada estado selecionado
            for estado in estados_selecionados:
                df_estado_estado = df_estado[df_estado['ESTADO'] == estado]
                fig3.add_trace(go.Scatter(x=df_estado_estado['DATA'], y=df_estado_estado['VALOR REVENDA (R$/L)'], mode='lines', name=estado))

            # Atualizar o layout do gráfico
            fig3.update_layout(
                title='Preço Médio de Revenda por Estado',
                xaxis_title='Data',
                yaxis_title='Preço Médio de Revenda (R$/L)',
                width=800,  # Largura do gráfico em pixels
                height=265, # Altura do gráfico em pixels
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig3)

# Gráfico 4: Indicador de Preço Médio de Revenda por Estado (primeiro estado selecionado)
with st.container():
    colu1, colu2 = st.columns(2)
    with colu1:
            with st.expander("Indicador de Preço Médio de Revenda por Estado", expanded=True):
                # Selecionar o estado (usando o primeiro estado da lista de estados selecionados)
                estado_1 = estados_selecionados[0] if estados_selecionados else None

                if estado_1:
                    # Filtrar os dados para o estado selecionado
                    df_final_1 = df_filtered[df_filtered['ESTADO'] == estado_1]

                    # Definir o intervalo de datas
                    data1 = str(int(dff['ANO'].min()) - 1)
                    data2 = str(dff['ANO'].max())

                    # Criar o gráfico
                    fig4 = go.Figure()

                    # Adicionar o indicador
                    fig4.add_trace(go.Indicator(
                        mode="number+delta",
                        title={"text": f"<span style='font-size:60%'>{estado_1}</span><br><span style='font-size:0.7em'>{data1} - {data2}</span>"},
                        value=df_final_1['VALOR REVENDA (R$/L)'].iloc[-1],
                        number={"prefix": "R$", "valueformat": ".2f"},
                        delta={"relative": True, "valueformat": ".1%", "reference": df_final_1['VALOR REVENDA (R$/L)'].iloc[0]}
                    ))

                    # Atualizar o layout do gráfico
                    fig4.update_layout(height=250)

                    # Exibir o gráfico no Streamlit
                    st.plotly_chart(fig4)
    with colu2:
            with st.expander("Indicador de Preço Médio de Revenda por Estado", expanded=True):
                # Selecionar o estado (usando o segundo estado da lista de estados selecionados)
                estado_2 = estados_selecionados[1] if len(estados_selecionados) > 1 else None

                if estado_2:
                    # Filtrar os dados para o estado selecionado
                    df_final_2 = df_filtered[df_filtered['ESTADO'] == estado_2]

                    # Definir o intervalo de datas
                    data1 = str(int(dff['ANO'].min()) - 1)
                    data2 = str(dff['ANO'].max())

                    # Criar o gráfico
                    fig5 = go.Figure()

                    # Adicionar o indicador
                    fig5.add_trace(go.Indicator(
                        mode="number+delta",
                        title={"text": f"<span style='font-size:60%'>{estado_2}</span><br><span style='font-size:0.7em'>{data1} - {data2}</span>"},
                        value=df_final_2['VALOR REVENDA (R$/L)'].iloc[-1],
                        delta={"relative": True, "valueformat": ".1%", "reference": df_final_2['VALOR REVENDA (R$/L)'].iloc[0]}
                    ))

                    # Atualizar o layout do gráfico
                    fig5.update_layout(height=250)

                    # Exibir o gráfico no Streamlit
                    st.plotly_chart(fig5)