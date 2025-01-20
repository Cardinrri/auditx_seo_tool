
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
from scraping import scrape_google_results

# Cargar los estilos personalizados
def load_css():
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Interfaz de usuario
st.image("assets/logo.png", width=250)
st.title("AuditX")
st.subheader("Herramienta de auditoría SEO automatizada")

query = st.text_input("🔍 Buscar en Google:", placeholder="Ejemplo: auditoría SEO para empresas")
num_results = st.selectbox("Número de resultados:", [10, 20, 50], index=1)

if st.button("Iniciar Auditoría"):
    if query:
        with st.spinner("🔍 Buscando en Google, por favor espere..."):
            results_df = scrape_google_results(query, num_results)

        if not results_df.empty:
            st.success(f"🔍 Se encontraron {len(results_df)} resultados.")
            st.dataframe(results_df)

            # Análisis de palabras clave en gráficos
            st.subheader("🔎 Análisis de resultados")

            # Gráfico de barras de palabras clave encontradas
            keyword_counts = results_df["Palabras Clave Encontradas"].value_counts().reset_index()
            keyword_counts.columns = ["Palabra Clave", "Frecuencia"]

            st.write("**Distribución de palabras clave más frecuentes en los resultados:**")
            chart = alt.Chart(keyword_counts).mark_bar().encode(
                x="Palabra Clave",
                y="Frecuencia",
                tooltip=["Palabra Clave", "Frecuencia"]
            ).properties(width=700)
            st.altair_chart(chart)

            # Gráfico de pastel para rich snippets
            snippet_counts = results_df["Rich Snippets"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(snippet_counts, labels=snippet_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.write("**Distribución de Rich Snippets en los resultados:**")
            st.pyplot(fig)

            # Botón para descargar el informe
            csv = results_df.to_csv(index=False, sep=';', quotechar='"', encoding="utf-8").encode('utf-8')
            st.download_button("⬇ Descargar informe en CSV", data=csv, file_name="auditx_results.csv", mime="text/csv")
        else:
            st.warning("⚠ No se encontraron resultados. Intente con otro término.")
    else:
        st.warning("⚠ Por favor, ingrese un término de búsqueda.")

st.markdown("---")
st.text("© 2025 AuditX - SEO Auditing Tool")
