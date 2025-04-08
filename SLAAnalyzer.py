import streamlit as st
import pandas as pd
from datetime import datetime

# ⚠️ Esta línea debe ser la primera llamada de Streamlit
st.set_page_config(page_title="3M Metrics Dashboard", layout="wide")

# 🎨 Estilo personalizado con los colores Blanco y Rojo
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, .stApp {
    background: #FFFFFF !important;
    color: #2B2B2B !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #F5F5F5 !important;
    border-right: 1px solid #D6D1C8;
}
[data-testid="stSidebar"] * {
    color: #2B2B2B !important;
}
[data-testid="stHeader"] {
    background: transparent;
}
h1, h2, h3, h4, h5, h6 {
    color: #2B2B2B !important;
    font-weight: 600;
}
.stButton > button {
    background: #E60012 !important;  /* Rojo 3M */
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    padding: 10px 22px;
    font-weight: 600;
}
.stButton > button:hover {
    background: #A40000 !important; /* Rojo más oscuro */
}
.stSelectbox>div,.stTextInput>div>div>input,.stFileUploader>div {
    background: #FFFFFF !important;
    color: #2B2B2B !important;
    border: 1px solid #D6D1C8 !important;
    border-radius: 6px;
}
.stTabs [role="tablist"] {
    background: transparent;
    border-bottom: 1px solid #D6D1C8;
}
.stTabs [role="tab"] {
    background: #F5F5F5;
    border: 1px solid #D6D1C8;
    border-bottom: none;
    color: #2B2B2B;
    padding: 8px 18px;
    border-radius: 6px 6px 0 0;
}
.stTabs [role="tab"][aria-selected="true"] {
    background: #E60012;
    color: #FFFFFF;
    border-color: #E60012;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.title("📊 SLAAnalyzer:")

# 📁 Tabs
tab1, tab2 = st.tabs(["📦 GRNI", "💳 Match Exceptions (ME)"])

# ======================== TAB GRNI ========================
with tab1:
    st.header("Análisis de GRNI")
    grni_file = st.file_uploader("Sube tu archivo GRNI (.xlsx)", type=["xlsx"], key="grni")

    if grni_file:
        df_grni = pd.read_excel(grni_file)

        # Verificamos si las columnas necesarias están presentes
        required_columns_grni = [
            "Buyer", "Aging", "Comment Indicator", "Team"
        ]
        
        if all(col in df_grni.columns for col in required_columns_grni):
            buyers = df_grni["Buyer"].unique()
            selected_buyer = st.selectbox("Filtrar por Buyer", options=["Todos"] + list(buyers))

            # Filtramos por buyer si es necesario
            if selected_buyer != "Todos":
                df_grni = df_grni[df_grni["Buyer"] == selected_buyer]

            # Filtramos por equipo (opcional)
            teams = df_grni["Team"].unique()
            selected_team = st.selectbox("Filtrar por Team", options=["Todos"] + list(teams))

            if selected_team != "Todos":
                df_grni = df_grni[df_grni["Team"] == selected_team]

            # Métricas
            total_rows = len(df_grni)
            over_90 = df_grni[df_grni["Aging"] > 90].shape[0]
            with_comment = df_grni[df_grni["Comment Indicator"].str.lower() == "yes"].shape[0]

            # Porcentajes
            pct_over_90 = round((over_90 / total_rows) * 100, 2) if total_rows else 0
            pct_with_comment = round((with_comment / total_rows) * 100, 2) if total_rows else 0

            st.metric("🔴 % Items con Aging > 90 días", f"{pct_over_90}%")
            st.metric("🟢 % Items con Comment", f"{pct_with_comment}%")

            st.subheader("Vista previa de datos")
            st.dataframe(df_grni)

        else:
            st.error(f"El archivo debe contener las columnas: {', '.join(required_columns_grni)}")

# ======================== TAB ME ========================
with tab2:
    st.header("Análisis de Match Exceptions")
    me_file = st.file_uploader("Sube tu archivo ME (.xlsx)", type=["xlsx"], key="me")

    if me_file:
        df_me = pd.read_excel(me_file)

        # Verificamos si las columnas necesarias están presentes
        required_columns_me = [
            "Buyer Name", "Net Due Date", "Past Due?", "Aging bucket", "Days Past Due"
        ]
        
        if all(col in df_me.columns for col in required_columns_me):
            df_me["Net Due Date"] = pd.to_datetime(df_me["Net Due Date"], errors="coerce")
            buyers_me = df_me["Buyer Name"].unique()
            selected_buyer_me = st.selectbox("Filtrar por Buyer", options=["Todos"] + list(buyers_me), key="buyer_me")

            # Filtramos por buyer si es necesario
            if selected_buyer_me != "Todos":
                df_me = df_me[df_me["Buyer Name"] == selected_buyer_me]

            # Métricas
            total_rows = len(df_me)
            today = pd.Timestamp(datetime.today().date())
            outside_sla = df_me[df_me["Net Due Date"] >= today].shape[0]
            past_due = df_me[df_me["Past Due?"].str.lower() == "yes"].shape[0]

            # Porcentajes
            pct_outside_sla = round((outside_sla / total_rows) * 100, 2) if total_rows else 0
            pct_past_due = round((past_due / total_rows) * 100, 2) if total_rows else 0

            st.metric("🔴 % Items fuera de SLA (Net Due Date >= hoy)", f"{pct_outside_sla}%")
            st.metric("🟡 % Items Past Due", f"{pct_past_due}%")

            # Filtro por Aging bucket
            aging_buckets = df_me["Aging bucket"].unique()
            selected_aging = st.selectbox("Filtrar por Aging Bucket", options=["Todos"] + list(aging_buckets))

            if selected_aging != "Todos":
                df_me = df_me[df_me["Aging bucket"] == selected_aging]

            st.subheader("Vista previa de datos")
            st.dataframe(df_me)
        else:
            st.error(f"El archivo debe contener las columnas: {', '.join(required_columns_me)}")