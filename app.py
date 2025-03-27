cleimport streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
import os

# Configuração da página
st.set_page_config(
    page_title="IoT Temperature Monitoring Dashboard",
    page_icon="🌡️",
    layout="wide"
)

# Conectar ao Supabase
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase = create_client(url, key)

# Baixar o arquivo CSV
def carregar_dados():
    try:
        data = supabase.storage.from_("tempiot").download("IOT-temp.csv")
        with open("IOT-temp.csv", "wb") as f:
            f.write(data)
        df = pd.read_csv("IOT-temp.csv")
        
        # Converter a coluna de data para o formato correto
        df["noted_date"] = pd.to_datetime(df["noted_date"], format="%d-%m-%Y %H:%M", errors="coerce")
        
        # Renomear a coluna para evitar caracteres especiais
        df.rename(columns={"room_id/id": "room_id"}, inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Supabase: {e}")
        return None

df = carregar_dados()

if df is not None:
    st.title('Dashboard de Monitoramento de Temperaturas IoT')

    # Resumo de dados
    st.header('Resumo de Dados')
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Média de Temperatura", value=f"{df['temp'].mean():.1f}°C")
    with col2:
        st.metric(label="Temperatura Máxima", value=f"{df['temp'].max()}°C")
    with col3:
        st.metric(label="Temperatura Mínima", value=f"{df['temp'].min()}°C")
    with col4:
        st.metric(label="Total de Leituras", value=len(df))

    # Gráfico de temperatura ao longo do tempo
    fig1 = px.line(df, x="noted_date", y="temp", title="Temperatura ao longo do tempo", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico de contagem de leituras por hora
    df["hour"] = df["noted_date"].dt.hour
    fig4 = df.groupby("hour").size().reset_index(name="contagem")
    fig4 = px.bar(fig4, x="hour", y="contagem", title="Contagem de Leituras por Hora")
    st.plotly_chart(fig4, use_container_width=True)

    # Gráfico de temperaturas máximas e mínimas por dia
    df["date"] = df["noted_date"].dt.date
    fig5 = df.groupby("date").agg({"temp": ["max", "min"]}).reset_index()
    fig5.columns = ["date", "temp_max", "temp_min"]
    fig5 = px.line(fig5, x="date", y=["temp_max", "temp_min"], title="Temperaturas Máximas e Mínimas por Dia")
    st.plotly_chart(fig5, use_container_width=True)

    # Informações adicionais
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: gray; font-size: 0.8em;'>IoT Temperature Monitoring Dashboard.</div>", unsafe_allow_html=True)
