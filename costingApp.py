import streamlit as st
import pandas as pd
import plotly.figure_factory as ff

# Gradient background CSS
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #89CFF0, #FF69B4);
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SolidWorks Costing Template Generator")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Šablony strojů", "Řezné podmínky", "Korekční tabulky", "Produktivita obrábění", "Dashboard", "Export a Uložení"]
)

# Sample correction matrix data
correction_data = {
    "Group": ["P", "P", "P", "M", "M", "M", "K", "K", "K", "N", "N", "N", "S", "S", "S", "H", "H", "H"],
    "Operation": ["soustružení", "frézování", "vrtání"] * 6,
    "Hrubování_Vc": [1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    "Hrubování_Ap": [1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    "Hrubování_Fz": [1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    "Zbytkové_Vc": [1] * 18,
    "Zbytkové_Ap": [1] * 18,
    "Zbytkové_Fz": [1] * 18,
    "Dokončování_Vc": [1] * 18,
    "Dokončování_Ap": [1] * 18,
    "Dokončování_Fz": [1] * 18,
}

df = pd.DataFrame(correction_data)

import streamlit as st
import pandas as pd

# Gradientní background
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #89CFF0, #FF69B4);
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Správa strojů - SolidWorks Costing")

# Základní seznam strojů
if "machines" not in st.session_state:
    st.session_state["machines"] = []

# Formulář pro přidání nového stroje
st.header("Přidat nový stroj")

with st.form("machine_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Název stroje")
        frezka = st.number_input("Frézka", min_value=0, max_value=1, value=0)
        soustruh = st.number_input("Soustruh", min_value=0, max_value=1, value=0)
        vrtacka = st.number_input("Vrtačka", min_value=0, max_value=1, value=0)
        max_otacky = st.number_input("Max počet otáček za min.", min_value=0, value=1000)

    with col2:
        naklady_oprac = st.number_input("Náklady na opracování", min_value=0.0, value=0.0)
        pracovni_naklady = st.number_input("Pracovní náklady", min_value=0.0, value=0.0)
        doba_nacteni = st.number_input("Doba načtení či uvolnění (min)", min_value=0.0, value=0.0)
        doba_nastaveni = st.number_input("Doba nastavení stroje (min)", min_value=0.0, value=0.0)
        rozlozeni_pripravy = st.number_input("Rozložení přípravy na výrobu", min_value=0.0, value=0.0)
        produktivita = st.slider("Produktivita obrábění (%)", 0, 100, 50)

    submitted = st.form_submit_button("Přidat stroj")
    if submitted:
        st.session_state["machines"].append({
            "Název": name,
            "Frézka": frezka,
            "Soustruh": soustruh,
            "Vrtačka": vrtacka,
            "Náklady na opracování": naklady_oprac,
            "Pracovní náklady": pracovni_naklady,
            "Max otáčky/min": max_otacky,
            "Doba načtení": doba_nacteni,
            "Doba nastavení": doba_nastaveni,
            "Rozložení přípravy": rozlozeni_pripravy,
            "Produktivita obrábění": produktivita
        })
        st.success(f"Stroj '{name}' byl úspěšně přidán!")

# Zobrazení uložených strojů
st.header("Seznam strojů")
if len(st.session_state["machines"]) > 0:
    machines_df = pd.DataFrame(st.session_state["machines"])
    st.dataframe(machines_df, use_container_width=True)
else:
    st.info("Zatím nejsou přidány žádné stroje.")


# Tab 2: Řezné podmínky
with tab2:
    st.header("Řezné podmínky")
    st.write("Nastavte limity pro referenční materiál.")
    for i in ["Hrubování", "Zbytkové obrábění", "Dokončování"]:
        st.subheader(i)
        vc = st.slider(f"{i} - Řezná rychlost (Vc)", 50, 500, 150)
        ap = st.slider(f"{i} - Hloubka řezu (Ap)", 0.5, 10.0, 2.0)
        fz = st.slider(f"{i} - Posuv (Fz)", 0.05, 0.5, 0.2)

# Tab 3: Korekční tabulky
with tab3:
    st.header("Korekční tabulky")
    st.write("Nastavte korekce pro různé materiálové skupiny a operace.")
    for group in df["Group"].unique():
        st.subheader(f"Skupina {group}")
        operations = df[df["Group"] == group]["Operation"].unique()
        for operation in operations:
            st.write(f"**{operation}**")
            vc = st.slider(f"{group} - {operation} - Hrubování Vc", 0.0, 2.0, 1.0)
            ap = st.slider(f"{group} - {operation} - Hrubování Ap", 0.0, 2.0, 1.0)
            fz = st.slider(f"{group} - {operation} - Hrubování Fz", 0.0, 2.0, 1.0)

# Tab 4: Produktivita obrábění
with tab4:
    st.header("Produktivita obrábění")
    st.write("Nastavte úroveň konzervativnosti/agresivity obrábění.")
    productivity_level = st.slider("Produktivita obrábění", 0, 100, 50)

# Tab 5: Dashboard (Heatmap)
with tab5:
    st.header("Dashboard")
    st.write("Grafická vizualizace korekcí jako heatmapy.")

    # Creating a heatmap-friendly dataframe
    heatmap_data = df.drop(columns=["Group", "Operation"]).astype(float)
    y_labels = [f"{row['Group']} - {row['Operation']}" for _, row in df.iterrows()]  # Labels for rows

    st.write("### Heatmapa korekcí (Hrubování, Zbytkové obrábění, Dokončování)")

    # Plot heatmap using Plotly
    fig = ff.create_annotated_heatmap(
        z=heatmap_data.values,
        x=list(heatmap_data.columns),  # Convert Index to list
        y=y_labels,  # Already a list
        colorscale="Blues",
        showscale=True
    )
    st.plotly_chart(fig)

# Tab 6: Export a Uložení
with tab6:
    st.header("Export a Uložení")
    st.write("Uložit šablonu do JSON nebo SQLite.")
    if st.button("Exportovat do JSON"):
        df.to_json("correction_matrix.json", orient="records")
        st.success("Data byla exportována do JSON!")
    if st.button("Exportovat do Excelu"):
        df.to_excel("correction_matrix.xlsx", index=False)
        st.success("Data byla exportována do Excelu!")
