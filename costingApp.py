import streamlit as st
import pandas as pd
import plotly.figure_factory as ff

# CSS pro gradientní pozadí
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #89CFF0, #FF69B4);
        background-size: cover;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SolidWorks Costing Template Generator")

# Inicializace strojů
if "machines" not in st.session_state:
    st.session_state["machines"] = []

# Inicializace sloučené tabulky řezných parametrů a korekcí
if "combined_table" not in st.session_state:
    st.session_state["combined_table"] = pd.DataFrame({
        "SKUPINA": ["P", "M", "K", "N", "S", "H"],
        "VC MIN": [100, 50, 150, 200, 10, 50],
        "VC MAX": [300, 180, 450, 1000, 50, 150],
        "FZ MIN": [0.1, 0.08, 0.1, 0.2, 0.08, 0.05],
        "FZ MAX": [0.4, 0.3, 0.5, 0.8, 0.25, 0.2],
        "AP HRUB MIN": [1, 0.5, 1, 1, 0.2, 0],
        "AP HRUB MAX": [6, 4, 8, 10, 3, 0],
        "AP DOK MIN": [0.2, 0.1, 0.2, 0.5, 0.1, 0.2],
        "AP DOK MAX": [1, 1, 2, 4, 1, 2]
    })

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Šablony strojů", "Řezné parametry a korekce", "Heatmapa tabulky", "Materiálové skupiny"])

# Tab 1: Šablony strojů
with tab1:
    st.subheader("Správa šablon strojů")
    with st.form("add_machine_form", clear_on_submit=True):
        name = st.text_input("Název stroje")
        st.write("### Typ stroje:")
        freza = st.checkbox("Fréza")
        soustruh = st.checkbox("Soustruh")
        vrtacka = st.checkbox("Vrtačka")
        naklady_opracovani = st.number_input("Náklady na opracování (v Kč)", min_value=0.0, step=1.0)
        pracovni_naklady = st.number_input("Pracovní náklady (v Kč)", min_value=0.0, step=1.0)
        max_otacky = st.number_input("Max počet otáček za min.", min_value=0, step=1)
        doba_nacteni = st.number_input("Doba načtení či uvolnění (min)", min_value=0.0, step=0.1)
        doba_nastaveni = st.number_input("Doba nastavení stroje (min)", min_value=0.0, step=0.1)
        rozlozeni_pripravy = st.selectbox("Rozložení přípravy na výrobu", ["Děleno celkovým množstvím", "Děleno velikostí série", "Použito jednou na díl"])
        rychlost_obrabeni = st.slider("Vyberte rychlost obrábění: pomalé - střední - rychlé", min_value=0, max_value=100, value=50, step=1)

        submitted = st.form_submit_button("Přidat stroj")
        if submitted and name:
            st.session_state["machines"].append({
                "Název": name,
                "Fréza": freza, "Soustruh": soustruh, "Vrtačka": vrtacka,
                "Náklady na opracování (Kč)": naklady_opracovani,
                "Pracovní náklady (Kč)": pracovni_naklady, "Max otáčky/min": max_otacky,
                "Doba načtení (min)": doba_nacteni, "Doba nastavení (min)": doba_nastaveni,
                "Rozložení přípravy": rozlozeni_pripravy, "Rychlost obrábění": rychlost_obrabeni
            })
            st.success(f"Stroj '{name}' byl úspěšně přidán!")

    st.write("### Seznam šablon strojů")
    if st.session_state["machines"]:
        machines_df = pd.DataFrame(st.session_state["machines"])
        updated_df = st.data_editor(machines_df, num_rows="dynamic", use_container_width=True)
        st.session_state["machines"] = updated_df.to_dict(orient="records")
    else:
        st.info("Zatím nebyly přidány žádné šablony strojů.")

# Tab 2: Sloučená tabulka řezných parametrů a korekcí
with tab2:
    st.subheader("Editovatelná tabulka řezných parametrů a korekcí")
    combined_df = st.data_editor(st.session_state["combined_table"], num_rows="dynamic", use_container_width=True)
    st.session_state["combined_table"] = combined_df

# Tab 3: Heatmapa sloučené tabulky
with tab3:
    st.subheader("Heatmapa parametrů")
    values = st.session_state["combined_table"].drop(columns=["SKUPINA"]).values.astype(float)
    fig = ff.create_annotated_heatmap(
        z=values,
        x=st.session_state["combined_table"].columns[1:].tolist(),
        y=st.session_state["combined_table"]["SKUPINA"].tolist(),
        colorscale="RdYlBu_r", showscale=True
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Materiálové skupiny
with tab4:
    st.subheader("Materiálové skupiny podle ISO 513")
    st.write("Tabulka materiálových skupin a jejich koeficientů obrobitelnosti.")
    material_groups_df = pd.DataFrame({
        "Skupina": ["P", "M", "K", "N", "S", "H"],
        "Popis": ["Oceli", "Nerezové oceli", "Liatiny", "Hliník a slitiny", "Žáruvzdorné slitiny", "Tvrdé materiály"],
        "Koeficient obrobitelnosti": [1.0, 0.8, 0.7, 1.2, 0.5, 0.4]
    })
    st.dataframe(material_groups_df, use_container_width=True)
