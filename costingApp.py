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

# Inicializace řezných parametrů
if "p1_params" not in st.session_state:
    st.session_state["p1_params"] = {
        "Soustružení": {"Vc": [50.0, 500.0], "Fz": [0.05, 1.0], "Ap": [0.5, 10.0]},
        "Frézování": {"Vc": [100.0, 600.0], "Fz": [0.02, 0.5], "Ap": [0.2, 5.0]},
    }

# Inicializace korekční tabulky
if "correction_matrix" not in st.session_state:
    st.session_state["correction_matrix"] = pd.DataFrame({
        "Group": ["P", "M", "K", "N", "S", "H"],
        "Soustružení_Ap": [1.0, 0.8, 0.7, 1.2, 1.0, 0.9],
        "Soustružení_Fz": [1.0, 0.9, 0.8, 1.1, 1.0, 0.8],
        "Frézování_Ap": [1.0, 0.7, 0.6, 1.3, 1.0, 0.8],
        "Frézování_Fz": [1.0, 0.8, 0.7, 1.2, 1.0, 0.7],
    })

# Tabs
tab1, tab2, tab3 = st.tabs(["Šablony strojů", "Řezné parametry P1", "Korekční Tabulka"])

# Tab 1: Šablony strojů
with tab1:
    st.subheader("Správa šablon strojů")

    # Formulář pro přidání nového stroje
    with st.form("add_machine_form", clear_on_submit=True):
        name = st.text_input("Název stroje")

        # Checkboxy
        st.write("### Typ stroje:")
        freza = st.checkbox("Fréza")
        soustruh = st.checkbox("Soustruh")
        vrtacka = st.checkbox("Vrtačka")

        # Inputboxy
        naklady_opracovani = st.number_input("Náklady na opracování (v Kč)", min_value=0.0, step=1.0)
        pracovni_naklady = st.number_input("Pracovní náklady (v Kč)", min_value=0.0, step=1.0)
        max_otacky = st.number_input("Max počet otáček za min.", min_value=0, step=1)
        doba_nacteni = st.number_input("Doba načtení či uvolnění (min)", min_value=0.0, step=0.1)
        doba_nastaveni = st.number_input("Doba nastavení stroje (min)", min_value=0.0, step=0.1)

        # Listbox
        rozlozeni_pripravy = st.selectbox(
            "Rozložení přípravy na výrobu",
            ["Děleno celkovým množstvím", "Děleno velikostí série", "Použito jednou na díl"]
        )

        # Posuvník pro výběr rychlosti obrábění
        st.write("### Nastavení obrábění")
        rychlost_obrabeni = st.slider(
            "Vyberte rychlost obrábění: pomalé - střední - rychlé",
            min_value=0, max_value=100, value=50, step=1
        )

        submitted = st.form_submit_button("Přidat stroj")
        if submitted and name:
            st.session_state["machines"].append({
                "Název": name,
                "Fréza": freza,
                "Soustruh": soustruh,
                "Vrtačka": vrtacka,
                "Náklady na opracování (Kč)": naklady_opracovani,
                "Pracovní náklady (Kč)": pracovni_naklady,
                "Max otáčky/min": max_otacky,
                "Doba načtení (min)": doba_nacteni,
                "Doba nastavení (min)": doba_nastaveni,
                "Rozložení přípravy": rozlozeni_pripravy,
                "Rychlost obrábění": rychlost_obrabeni
            })
            st.success(f"Stroj '{name}' byl úspěšně přidán!")

    # Zobrazení a editace tabulky strojů
    st.write("### Seznam šablon strojů")
    if st.session_state["machines"]:
        machines_df = pd.DataFrame(st.session_state["machines"])
        updated_df = st.data_editor(machines_df, num_rows="dynamic", use_container_width=True)
        st.session_state["machines"] = updated_df.to_dict(orient="records")
    else:
        st.info("Zatím nebyly přidány žádné šablony strojů.")

# Tab 2: Řezné parametry P1
with tab2:
    st.subheader("Řezné parametry - P1 (Automatové oceli)")

    # Soustružení
    st.markdown("### Soustružení")
    col1, col2, col3 = st.columns(3)
    with col1:
        vc_min, vc_max = st.slider("Řezná rychlost Vc (m/min)", 50.0, 500.0,
                                   value=st.session_state["p1_params"]["Soustružení"]["Vc"], step=1.0)
    with col2:
        fz_min, fz_max = st.slider("Posuv Fz (mm/ot)", 0.05, 1.0,
                                   value=st.session_state["p1_params"]["Soustružení"]["Fz"], step=0.01)
    with col3:
        ap_min, ap_max = st.slider("Hloubka řezu Ap (mm)", 0.5, 10.0,
                                   value=st.session_state["p1_params"]["Soustružení"]["Ap"], step=0.1)

    st.session_state["p1_params"]["Soustružení"] = {"Vc": [vc_min, vc_max], "Fz": [fz_min, fz_max], "Ap": [ap_min, ap_max]}

    # Frézování
    st.markdown("### Frézování")
    col1, col2, col3 = st.columns(3)
    with col1:
        vc_min, vc_max = st.slider("Řezná rychlost Vc (m/min)", 100.0, 600.0,
                                   value=st.session_state["p1_params"]["Frézování"]["Vc"], step=1.0)
    with col2:
        fz_min, fz_max = st.slider("Posuv Fz (mm/ot)", 0.02, 0.5,
                                   value=st.session_state["p1_params"]["Frézování"]["Fz"], step=0.01)
    with col3:
        ap_min, ap_max = st.slider("Hloubka řezu Ap (mm)", 0.2, 5.0,
                                   value=st.session_state["p1_params"]["Frézování"]["Ap"], step=0.1)

    st.session_state["p1_params"]["Frézování"] = {"Vc": [vc_min, vc_max], "Fz": [fz_min, fz_max], "Ap": [ap_min, ap_max]}

# Tab 3: Korekční tabulka
with tab3:
    st.subheader("Editovatelná Korekční Tabulka s Heatmapou")

    # Editace tabulky
    correction_df = st.data_editor(st.session_state["correction_matrix"], num_rows="dynamic")
    st.session_state["correction_matrix"] = correction_df

    # Heatmapa
    st.write("### Heatmapa korekcí")
    values = correction_df.drop(columns=["Group"]).values.astype(float)
    fig = ff.create_annotated_heatmap(
        z=values,
        x=correction_df.columns[1:].tolist(),
        y=correction_df["Group"].tolist(),
        colorscale="RdYlBu_r",  # Modrá -> Zelená -> Červená
        showscale=True
    )
    st.plotly_chart(fig, use_container_width=True)
