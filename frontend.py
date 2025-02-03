import streamlit as st
import sqlite3
import pandas as pd
import os
import folium
from streamlit_folium import folium_static
import openai
import requests

# Conectar ao banco de dados
def get_db_connection():
    db_path = os.path.join(os.getcwd(), "imoveis.db")
    conn = sqlite3.connect(db_path)
    return conn

# Página de listagem de imóveis
import streamlit as st
import sqlite3
import pandas as pd
import os
import folium
from streamlit_folium import folium_static
# from folium.plugins import LayerControl
import matplotlib.pyplot as plt
import requests

# Adicionar estilização CSS personalizada
st.markdown("""
    <style>
        .stTitle { text-align: center; }
        div.stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 10px;
        }
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        .stDataFrame { border-radius: 10px; }
        input {
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Conectar ao banco de dados
def get_db_connection():
    db_path = os.path.join(os.getcwd(), "imoveis.db")
    conn = sqlite3.connect(db_path)
    return conn

# Página de listagem de imóveis
def pagina_lista_imoveis():
    from streamlit_folium import st_folium
    import folium
    st.title("📄 Lista de Imóveis")
    conn = get_db_connection()
    query = """
    SELECT endereco AS 'Endereço', 
           preco_avaliacao AS 'Preço de Avaliação', 
           desconto AS 'Desconto (%)' 
       FROM imovel_caixa
    ORDER BY desconto DESC;

    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    if not df.empty:
        df['Preço de Avaliação'] = df['Preço de Avaliação'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        df['Desconto (%)'] = df['Desconto (%)'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "-")
        st.write("### 🔍 Resultados Encontrados:")
        st.dataframe(df, use_container_width=True, height=600, width = 2400)
        
        # # Criar o mapa
        # mapa = folium.Map(location=[df["latitude"].mean(), df["longitude"].mean()], zoom_start=6)
        
        # # Adicionar marcadores no mapa
        # for _, row in df.dropna(subset=['latitude', 'longitude']).iterrows():
        #     marker = folium.Marker(
        #         [row["latitude"], row["longitude"]],
        #         popup=f"{row['Endereço']}<br>Preço: {row['Preço de Avaliação']}<br>Desconto: {row['Desconto (%)']}%",

        #         tooltip=row["Endereço"]
        #     )
        #     marker.add_to(mapa)
        
        # st_folium(mapa, width=700, height=500)
    else:
        st.warning("Nenhum imóvel encontrado.")


# Página do mapa com imóveis
def pagina_mapa():
    st.title("🗺️ Mapa de Imóveis")

    conn = get_db_connection()
    query = """
    SELECT endereco, cidade, latitude, longitude, preco_venda 
    FROM imovel_caixa;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df = df.dropna(subset=["latitude", "longitude"])

    if df.empty:
        st.warning("Nenhum imóvel encontrado com coordenadas válidas.")
        return

    # Adicionar Filtro de Preço
    min_preco, max_preco = int(df["preco_venda"].min()), int(df["preco_venda"].max())
    preco_selecionado = st.slider("Selecione o intervalo de preço (R$)", min_preco, max_preco, (min_preco, max_preco), format="R$ %d")
    # Filtrar imóveis pelo preço selecionado
    df_filtrado = df[(df["preco_venda"] >= preco_selecionado[0]) & (df["preco_venda"] <= preco_selecionado[1])]

    if df_filtrado.empty:
        st.warning("Nenhum imóvel dentro da faixa de preço selecionada.")
        return

    # Centralizar o mapa com base nos imóveis filtrados
    lat_mean, lon_mean = df_filtrado["latitude"].mean(), df_filtrado["longitude"].mean()
    mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=6)

    # Adicionar marcadores apenas com o preço do imóvel
    for _, row in df_filtrado.iterrows():
        preco_formatado = f"R$ {row['preco_venda']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        folium.Marker(
            [row["latitude"], row["longitude"]],
            popup=preco_formatado,
            tooltip=preco_formatado
        ).add_to(mapa)

    folium_static(mapa)



# Página da calculadora
def pagina_calculadora_modificada():
    st.title("📏 Calculadora de Investimento Imobiliário")
    
    # Botões de ação
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.button("💾 Salvar")
    with col2:
        st.button("📂 Abrir")
    with col3:
        st.button("🖨️ Imprimir")
    with col4:
        st.button("🗑️ Limpar")
    with col5:
        st.button("📊 Calcular")
    
    st.header("🔹 Premissas")
    valor_arrematacao = st.number_input("Arrematação (R$)", min_value=0.0, step=1000.0)
    preco_venda = st.number_input("Preço de venda do imóvel (R$)", min_value=0.0, step=1000.0)
    prazo_vendas = st.number_input("Prazo de vendas (meses)", min_value=1, step=1, value=12)
    entrada = st.slider("Entrada (%)", min_value=0, max_value=100, value=100)
    numero_parcelas = st.number_input("Número de Parcelas", min_value=1, step=1, value=1)
    taxa_juros = st.number_input("Taxa de Juros (% Anual)", min_value=0.0, step=0.1)
    taxa_mercado = st.number_input("Taxa de Mercado para Comparação (% Mensal)", min_value=0.0, step=0.1)
    
    st.header("💰 Custos na Aquisição")
    col1, col2 = st.columns(2)
    with col1:
        comissao_leiloeiro = st.number_input("Comissão Leiloeiro (R$)", min_value=0.0, step=100.0)
        itbi = st.number_input("ITBI (R$)", min_value=0.0, step=100.0)
        assessoria_aquisicao = st.number_input("Assessoria Aquisição (R$)", min_value=0.0, step=100.0)
    with col2:
        dividas = st.number_input("Dívidas Propter Rem (R$)", min_value=0.0, step=100.0)
        registro = st.number_input("Registro (R$)", min_value=0.0, step=100.0)
        reforma = st.number_input("Reforma (R$)", min_value=0.0, step=100.0)
    outros_custos = st.number_input("Outros Custos (R$)", min_value=0.0, step=100.0)
    
    st.header("💵 Custos na Venda")
    corretor = st.number_input("Corretor Imobiliário (R$)", min_value=0.0, step=100.0)
    assessoria_venda = st.number_input("Assessoria Venda (R$)", min_value=0.0, step=100.0)
    imposto_renda = st.number_input("Imposto de Renda (R$)", min_value=0.0, step=100.0)
    
    st.header("📈 Receita Mensal")
    col1, col2 = st.columns(2)
    with col1:
        inicio_receita = st.number_input("Prazo para Início de Receita (meses)", min_value=1, step=1)
        aluguel = st.number_input("Aluguel Mensal com Despesas (R$)", min_value=0.0, step=100.0)
    with col2:
        duracao_aluguel = st.number_input("Duração do aluguel (meses)", min_value=0, step=1)
        imposto_renda_recorrente = st.number_input("Imposto de Renda Recorrente (R$)", min_value=0.0, step=100.0)
    
    st.header("🏠 Custo Mensal")
    col1, col2 = st.columns(2)
    with col1:
        iptu = st.number_input("IPTU Mensal (R$)", min_value=0.0, step=100.0)
    with col2:
        condominio = st.number_input("Condomínio (R$)", min_value=0.0, step=100.0)

# Função para buscar informações na web
def buscar_info_web(cidade):
    try:
        query = f"custo imobiliário {cidade} preço médio metro quadrado tendências"
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return f"🔍 Confira mais sobre o mercado imobiliário de {cidade} [aqui]({url})"
        else:
            return "⚠️ Não foi possível obter informações da web no momento."
    except Exception as e:
        return "⚠️ Erro ao buscar informações na web."







    
# Menu lateral
st.sidebar.title("🏡 Menu")
pagina = st.sidebar.radio("Escolha a página:", ["Lista de Imóveis", "Calculadora", "Mapa de Imóveis"])

if pagina == "Lista de Imóveis":
    pagina_lista_imoveis()
elif pagina == "Calculadora":
    pagina_calculadora_modificada()
elif pagina == "Mapa de Imóveis":
    pagina_mapa()

