# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Dados Meteorológicos - Santa Helena/PR")

# 1. Entrada do usuário
st.sidebar.header("Selecione o intervalo de datas:")
data_inicial = st.sidebar.date_input("Data inicial", value=datetime(2023, 1, 1))
data_final = st.sidebar.date_input("Data final", value=datetime(2024, 12, 31))

# Validação de intervalo
if data_inicial > data_final:
    st.error("⚠️ A data inicial não pode ser posterior à data final.")
    st.stop()

# 2. Carregamento de dados
@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQABQ6C2vW_WgMOWICPPwoaUNp34JcThVJiFBgCPh2P7VvDW2PyqnkAEfdUxiesAwz5Hunuzeh5IykV/pub?gid=526963453&single=true&output=csv"
    df = pd.read_csv(url)
    datas = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    df = df.drop(columns=['Data'])
    df = df.replace({',': '.'}, regex=True).apply(pd.to_numeric, errors='coerce')
    df['Data'] = datas
    return df

df = carregar_dados()
df_inter_dia = df[(df['Data'] >= pd.to_datetime(data_inicial)) & (df['Data'] <= pd.to_datetime(data_final))]

st.success(f"Intervalo selecionado: `{data_inicial}` até `{data_final}`")
st.dataframe(df_inter_dia.head())

# 3. Gráficos
sns.set(style='ticks')
fig, axs = plt.subplots(2, 2, figsize=(18, 8), sharex=True)
x = df_inter_dia['Data']

# Temperaturas
axs[0, 0].set_title('Temperatura do ar')
axs[0, 0].plot(x, df_inter_dia['Tmax (°C)'], 'r--', label='Tmax')
axs[0, 0].plot(x, df_inter_dia['Tmed (°C)'], 'g--', label='Tmed')
axs[0, 0].plot(x, df_inter_dia['Tmin (°C)'], 'b--', label='Tmin')
axs[0, 0].legend()

# Chuvas
axs[0, 1].set_title('Chuvas')
axs[0, 1].plot(x, df_inter_dia['Chuva (mm)'], 'b--', label='Chuva')
axs2 = axs[0, 1].twinx()
axs2.plot(x, df_inter_dia['Chuva (mm)'].cumsum(), 'r-', label='Chuva acumulada')
axs[0, 1].legend(loc='upper left')
axs2.legend(loc='lower right')

# UR e vento
axs[1, 0].set_title('UR e Velocidade do vento')
axs[1, 0].plot(x, df_inter_dia['UR (%)'], 'b-', label='UR')
axs3 = axs[1, 0].twinx()
axs3.plot(x, df_inter_dia['Vel. Vento (m/s)'], 'r-', label='Vento')
axs[1, 0].legend(loc='upper left')
axs3.legend(loc='lower right')

# Radiação solar
axs[1, 1].set_title('Radiação solar')
axs[1, 1].plot(x, df_inter_dia['Radiação solar (MJ/m²d)'], color='orange', linestyle='--', label='Qg')
axs4 = axs[1, 1].twinx()
axs4.plot(x, df_inter_dia['Radiação solar (MJ/m²d)'].cumsum(), 'r-', label='Qg acumulado')
axs[1, 1].legend(loc='upper left')
axs4.legend(loc='lower right')

for ax in axs.flat:
    ax.tick_params(axis='x', rotation=45)

st.pyplot(fig)

# 4. Download do arquivo
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()

excel_bytes = converter_para_excel(df_inter_dia)
st.download_button(
    label="📥 Baixar dados em Excel",
    data=excel_bytes,
    file_name="dados_santa_helena.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption(f"Gráficos gerados para o intervalo de `{data_inicial}` a `{data_final}` - Santa Helena/PR - FONTE: SIMEPAR")

