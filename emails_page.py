import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import plotly.express as px


st.title("Análise de Emails - 2025")



# ===============================
# 🔑 Configurar conexão com Google Sheets
# ===============================

# Substitua pelo ID da sua planilha do Google Sheets
SHEET_ID = "1JEtySzoYxddq_mA958vMnCGtcL024JsEDdor_txjoQ4"
SHEET_NAME = "Página1"  # Nome da aba da planilha

creds = st.secrets["gcp_service_account"]
# Escopo de permissões
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Criar credenciais usando o dicionário do secrets
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)

# Autorizar o cliente
client = gspread.authorize(credentials)

# Acessar a planilha
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()
df = pd.DataFrame(data)


# Limpeza dos dados
def extrair_metricas(status):
    """Extrai Pending, Sent, Read e Taxa de Abertura"""
    pending = sent = read = taxa = None
    match_pending = re.search(r"(\d+)\s*Pending", str(status))
    match_sent = re.search(r"(\d+)\s*Sent", str(status))
    match_read = re.search(r"(\d+)\s*Read", str(status))
    match_taxa = re.search(r"(\d+\.?\d*)%\s*Read", str(status))

    if match_pending: pending = int(match_pending.group(1))
    if match_sent: sent = int(match_sent.group(1))
    if match_read: read = int(match_read.group(1))
    if match_taxa: taxa = float(match_taxa.group(1))

    return pending, sent, read, taxa

def extrair_data(nome):
    """Extrai a data (YYYYMMDD) do início do campo Nome"""
    match = re.match(r"^(\d{8})", str(nome))
    if match:
        return pd.to_datetime(match.group(1), format="%Y%m%d", errors="coerce")
    return None


# Criar colunas limpas
df[["Pending", "Sent", "Read", "Taxa de Abertura (%)"]] = df["Status"].apply(
    lambda x: pd.Series(extrair_metricas(x))
)
df["Data"] = df["Nome"].apply(extrair_data)


# Criar coluna de Ano-Mês para agrupamentos
df["AnoMes"] = df["Data"].dt.to_period("M").astype(str)


# Filtrar apenas 2025
df_2025 = df[df["Data"].dt.year == 2025].copy()

##st.subheader("📋 Prévia dos Dados Limpos")
##st.dataframe(df_2025.head(10), use_container_width=True)


#Filtro de pesquisa
with st.container(border=True):
		st.text("Filtro")
		col1, col2 = st.columns(2)


		with col1:
								meses = sorted(df_2025["AnoMes"].unique())
								mes_selecionado = st.selectbox("Selecione o mês", options=["Todos"] + list(meses))
		with col2:
								categorias = sorted(df_2025["Categoria"].unique())
								categoria_selecionada = st.selectbox("Selecione a categoria", options=["Todas"] + list(categorias))
		if st.button("Limpar", type="primary"):
			st.write("Em desenvolvimento")

df_filtrado = df_2025.copy()
if mes_selecionado != "Todos":
  df_filtrado = df_filtrado[df_filtrado["AnoMes"] == mes_selecionado]
if categoria_selecionada != "Todas":
  df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_selecionada]

# Métricas Gerais
st.subheader(" Métricas Gerais")
total_emails = df_2025["Nome"].nunique()
media_mensal = df_filtrado.groupby(df_filtrado["Data"].dt.month)["Nome"].nunique().mean()

with st.container(border=True):
    col1, col2 = st.columns(2)
    col1.metric("Total de Emails (2025)", total_emails)
    col2.metric("Média de Emails por Mês", f"{media_mensal:.1f}")



col1, col2 = st.columns(2)

with col1:
    # Gráfico 1 - Pizza por Categoria

    categoria_sum = df_filtrado.groupby("Categoria")["Sent"].sum().reset_index()
    fig_pizza = px.pie(categoria_sum, values="Sent", names="Categoria", title="E-mails Enviados por Categoria")
    st.plotly_chart(fig_pizza)

with col2:
    # Gráfico 2 - Barras por Mês
    mes_sum = df_filtrado.groupby("AnoMes")["Sent"].sum().reset_index()
    fig_bar = px.bar(mes_sum, x="AnoMes", y="Sent", title="E-mails Enviados por Mês", text="Sent")
    fig_bar.update_traces(texttemplate='%{text:.1f,}', textposition='outside')
    st.plotly_chart(fig_bar)

with st.container(border=True):
		# Ranking - Top 10 melhores taxas de leitura
		st.subheader("🏆 Top 10 E-mails com Melhor Taxa de Leitura")
		top10 = df_filtrado.sort_values(by="Taxa de Abertura (%)", ascending=False).head(10)
		fig_rank = px.bar(
				top10,
				x="Taxa de Abertura (%)",
				y="Nome",
				orientation="h",
				text="Taxa de Abertura (%)"
		)
		fig_rank.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
		st.plotly_chart(fig_rank)


#Gráfico de Linha - Evolução Mensal
df_linha = df_filtrado.groupby(df_filtrado["Data"].dt.to_period("M"))["Nome"].nunique().reset_index()
df_linha["Data"] = df_linha["Data"].dt.to_timestamp()

sdf_linha = df_linha.set_index("Data")  # coloca Data no índice

st.line_chart(sdf_linha["Nome"])
