import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# CSS pro gradientní pozadí
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #ffffff, #d5d5d5);
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
tab1, tab2, tab3 = st.tabs(["Šablony strojů", "Řezné parametry a korekce", "DASHBOARD"])

# Tab 1: Šablony strojů
with tab1:
    st.subheader("Správa šablon strojů")

    # Formulář pro přidání nového stroje
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

        rozlozeni_pripravy = st.selectbox(
            "Rozložení přípravy na výrobu",
            ["Děleno celkovým množstvím", "Děleno velikostí série", "Použito jednou na díl"]
        )

        rychlost_obrabeni = st.slider(
            "Vyberte rychlost obrábění: pomalé - střední - rychlé", min_value=0, max_value=100, value=50, step=1
        )

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

# Tab 2: Editovatelná tabulka
with tab2:
    st.subheader("tabulka řezných parametrů a korekcí")
    combined_df = st.data_editor(st.session_state["combined_table"], num_rows="dynamic", use_container_width=True)
    st.session_state["combined_table"] = combined_df

# Tab 3: 3D Surface graf VC MIN/VC MAX
with tab3:
    st.subheader("zobrazení rozsahů VC MIN a VC MAX hodnot")

    # Data pro surface plot
    skupiny = ["P", "M", "K", "N", "S", "H"]  # Skupiny zleva doprava
    vc_min = st.session_state["combined_table"]["VC MIN"]
    vc_max = st.session_state["combined_table"]["VC MAX"]

    # Příprava dat
    x = list(range(len(skupiny)))  # Indexy pro skupiny materiálů
    y = ["VC MIN", "VC MAX"]  # Parametry
    z = [vc_min.tolist(), vc_max.tolist()]  # Hodnoty (MIN a MAX)

    # Vytvoření surface grafu
    fig = go.Figure(data=[go.Surface(
        z=z,  # Hodnoty na ose Z
        x=x,  # Skupiny materiálů (P, M, K, ...)
        y=y,  # VC MIN a VC MAX
        colorscale="Viridis"
    )])

    # Popisky os a pořadí
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Skupiny materiálů", tickvals=x, ticktext=skupiny),
            yaxis=dict(title="Parametry", autorange="reversed"),  # VC MIN blíž k pozorovateli
            zaxis=dict(title="Hodnota VC")
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )

    # Zobrazení grafu
    st.plotly_chart(fig, use_container_width=True)

    # Heatmapa koeficientů vůči P
    st.subheader("Heatmapa koeficientů vůči P (VC, FZ, AP)")

    # Výpočet průměrných hodnot z MIN a MAX pro VC, FZ, AP
    combined_table = st.session_state["combined_table"]
    combined_table["VC AVG"] = (combined_table["VC MIN"] + combined_table["VC MAX"]) / 2
    combined_table["FZ AVG"] = (combined_table["FZ MIN"] + combined_table["FZ MAX"]) / 2
    combined_table["AP AVG"] = (combined_table["AP HRUB MIN"] + combined_table["AP HRUB MAX"]) / 2

    # Referenční hodnoty pro skupinu P
    reference_vc = combined_table["VC AVG"].iloc[0]
    reference_fz = combined_table["FZ AVG"].iloc[0]
    reference_ap = combined_table["AP AVG"].iloc[0]

    # Výpočet koeficientů vůči referenční skupině P
    combined_table["Koeficient VC"] = combined_table["VC AVG"] / reference_vc
    combined_table["Koeficient FZ"] = combined_table["FZ AVG"] / reference_fz
    combined_table["Koeficient AP"] = combined_table["AP AVG"] / reference_ap

    # Příprava dat pro heatmapu
    heatmap_data = pd.DataFrame({
        "Skupina": combined_table["SKUPINA"],
        "VC": combined_table["Koeficient VC"].round(2),
        "FZ": combined_table["Koeficient FZ"].round(2),
        "AP": combined_table["Koeficient AP"].round(2)
    })

    # Vytvoření heatmapy
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data[["VC", "FZ", "AP"]].values.T,
        x=heatmap_data["Skupina"],
        y=["VC", "FZ", "AP"],
        colorscale="Viridis",
        text=heatmap_data[["VC", "FZ", "AP"]].values.T,  # Přidání číselných hodnot
        texttemplate="%{text:.2f}",  # Formátování hodnot
        hoverinfo="text"
    ))

    # Aktualizace layoutu heatmapy
    fig_heatmap.update_layout(
        xaxis=dict(title="Skupiny materiálů"),
        yaxis=dict(title="Parametry (VC, FZ, AP)"),
        margin=dict(l=0, r=0, b=0, t=0)
    )

    # Zobrazení heatmapy
    st.plotly_chart(fig_heatmap, use_container_width=True)
