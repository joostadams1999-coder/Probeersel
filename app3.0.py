import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import os
from scipy.spatial import ConvexHull

# --- 0. TAAL CONFIGURATIE ---
TRANSLATIONS = {
    "nl": {
        "title": "Survey & Dashboard Kwaliteiten",
        "sidebar_header": "📊 Survey Invoer",
        "team_code": "Teamcode:",
        "team_code_custom": "Of voer nieuw team in:",
        "work_form": "Werkvorm (Y)",
        "work_approach": "Werkaanpak (X)",
        "your_qualities": "Jouw kwaliteiten:",
        "missed": "Gemist in team:",
        "seen": "Gezien bij collega's:",
        "save_button": "Sla gegevens op",
        "error_code": "Teamcode verplicht!",
        "success": "Gelukt! Pagina vernieuwd.",
        "view_team": "Bekijk team resultaten voor:",
        "no_data": "Geen data voor dit team.",
        "mapping_title": "1. Individuele Kwaliteiten Mapping",
        "mapping_desc": "Cirkels tonen de gemiddelde positie van teamleden die deze kwaliteit bezitten. Hover over een cirkel voor details.",
        "dna_title": "2. Team DNA (Expertise Overlap)",
        "dna_desc": "De gekleurde vlakken tonen de reikwijdte van de drie hoofd-kwaliteitgroepen binnen het team.",
        "admin": "⚙️ Beheer",
        "admin_password": "Reset wachtwoord",
        "admin_team": "Welk team wissen?",
        "admin_delete": "Verwijder data",
        "admin_success": "Gereset!",
        "quality": "Kwaliteit",
        "number": "Aantal",
        "language": "Taal:"
    },
    "en": {
        "title": "Survey & Dashboard Qualities",
        "sidebar_header": "📊 Survey Input",
        "team_code": "Team Code:",
        "team_code_custom": "Or enter new team:",
        "work_form": "Work Form (Y)",
        "work_approach": "Work Approach (X)",
        "your_qualities": "Your qualities:",
        "missed": "Missed in team:",
        "seen": "Seen at colleagues:",
        "save_button": "Save data",
        "error_code": "Team code required!",
        "success": "Success! Page refreshed.",
        "view_team": "View team results for:",
        "no_data": "No data for this team.",
        "mapping_title": "1. Individual Qualities Mapping",
        "mapping_desc": "Circles show the average position of team members who have this quality. Hover over a circle for details.",
        "dna_title": "2. Team DNA (Expertise Overlap)",
        "dna_desc": "The colored areas show the scope of the three main quality groups within the team.",
        "admin": "⚙️ Admin",
        "admin_password": "Reset password",
        "admin_team": "Which team to delete?",
        "admin_delete": "Delete data",
        "admin_success": "Reset!",
        "quality": "Quality",
        "number": "Number",
        "language": "Language:"
    }
}

# --- 1. CONFIGURATIE ---
QUALITEITEN = {
    "1.1": {"naam": "Mobiliseren van actoren", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.2": {"naam": "Integratie van kennis", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.3": {"naam": "Benadrukken van kleine successen", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.4": {"naam": "Concretiseren van ambities", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.5": {"naam": "Framen van innovatie in context", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "2.1": {"naam": "Verifiëren waarde in pilot", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.2": {"naam": "Verifiëren waarde contexten", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.3": {"naam": "Testen beheersbaarheid", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.4": {"naam": "Overzicht bewaren", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.5": {"naam": "Momentum creëren ecosysteem", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.6": {"naam": "Leren van algemene lessen", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.7": {"naam": "Iteratief leren in innovatie", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "3.1": {"naam": "Coördinatie adaptie", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.2": {"naam": "Aanpassen routines", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.3": {"naam": "Creëer ondersteunend beleid", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.4": {"naam": "Verzeker gelijk speelveld", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.5": {"naam": "Vergaar waarde lange tijd", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"}
}

WERKVORM_LABELS_NL = ["Alleen operationeel", "Lichtelijk tactisch / Voornamelijk operationeel", "Voornamelijk tactisch / Lichtelijk operationeel", "Strategisch/tactisch/operationeel", "Lichtelijk strategisch / Voornamelijk tactisch", "Voornamelijk strategisch / Lichtelijk tactisch", "Alleen strategisch"]
WERKVORM_LABELS_EN = ["Operational only", "Slightly tactical / Mainly operational", "Mainly tactical / Slightly operational", "Strategic/tactical/operational", "Slightly strategic / Mainly tactical", "Mainly strategic / Slightly tactical", "Strategic only"]
WERKAANPAK_LABELS_NL = ["Alleen hiërarchisch", "Voornamelijk hiërarchisch", "Lichtelijk hiërarchisch", "Evenveel hiërarchisch als netwerk", "Lichtelijk netwerk", "Voornamelijk netwerk", "Alleen netwerk"]
WERKAANPAK_LABELS_EN = ["Hierarchical only", "Mainly hierarchical", "Slightly hierarchical", "Equal hierarchical and network", "Slightly network", "Mainly network", "Network only"]

def get_werkvorm_labels():
    lang = st.session_state.get("language", "nl")
    return WERKVORM_LABELS_EN if lang == "en" else WERKVORM_LABELS_NL

def get_werkaanpak_labels():
    lang = st.session_state.get("language", "nl")
    return WERKAANPAK_LABELS_EN if lang == "en" else WERKAANPAK_LABELS_NL

def get_available_teams():
    data = load_data()
    teams = sorted(set(r['team'] for r in data))
    return teams

DATA_FILE = "survey_data.json"

# --- 2. DATA FUNCTIES ---
def init_data():
    if not os.path.exists(DATA_FILE):
        start_data = [
            # --- INNO-2026 (23 mensen - groot team) ---
            {"team": "INNO-2026", "y": 1, "x": 3, "bezit": ["1.1", "2.4", "3.2"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 7, "x": 3, "bezit": ["1.1", "1.4", "3.5"], "gemist": ["2.4", "3.5"], "gezien": ["1.4"]},
            {"team": "INNO-2026", "y": 4, "x": 5, "bezit": ["2.1", "2.4", "3.5"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 6, "x": 2, "bezit": ["1.2", "1.3"], "gemist": ["2.1"], "gezien": ["3.1"]},
            {"team": "INNO-2026", "y": 5, "x": 4, "bezit": ["3.1", "3.3", "1.5"], "gemist": ["2.6"], "gezien": ["2.4"]},
            {"team": "INNO-2026", "y": 2, "x": 6, "bezit": ["2.2", "2.3", "2.7"], "gemist": ["1.1"], "gezien": ["3.5"]},
            {"team": "INNO-2026", "y": 3, "x": 5, "bezit": ["1.4", "2.5", "3.4"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 4, "x": 4, "bezit": ["1.1", "3.2"], "gemist": ["2.4"], "gezien": ["2.1"]},
            {"team": "INNO-2026", "y": 7, "x": 7, "bezit": ["3.5", "1.5"], "gemist": ["1.2"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 1, "x": 1, "bezit": ["2.6"], "gemist": ["3.3"], "gezien": ["2.4"]},
            {"team": "INNO-2026", "y": 5, "x": 3, "bezit": ["1.1", "1.3", "2.1"], "gemist": ["3.5"], "gezien": ["3.2"]},
            {"team": "INNO-2026", "y": 6, "x": 4, "bezit": ["3.1", "3.5"], "gemist": ["2.7"], "gezien": ["1.4"]},
            {"team": "INNO-2026", "y": 4, "x": 6, "bezit": ["2.4", "2.5"], "gemist": ["1.1"], "gezien": ["3.5"]},
            {"team": "INNO-2026", "y": 3, "x": 2, "bezit": ["1.2", "3.4"], "gemist": ["3.5"], "gezien": ["2.4"]},
            {"team": "INNO-2026", "y": 2, "x": 3, "bezit": ["2.1", "2.2"], "gemist": ["1.4"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 5, "x": 5, "bezit": ["1.1", "3.3"], "gemist": ["2.4"], "gezien": ["3.1"]},
            {"team": "INNO-2026", "y": 4, "x": 4, "bezit": ["2.7", "3.5"], "gemist": ["1.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 6, "x": 6, "bezit": ["1.4", "2.4"], "gemist": ["3.5"], "gezien": ["2.1"]},
            {"team": "INNO-2026", "y": 7, "x": 2, "bezit": ["3.1", "3.2"], "gemist": ["2.5"], "gezien": ["1.1"]},
            {"team": "INNO-2026", "y": 3, "x": 7, "bezit": ["1.5", "2.6"], "gemist": ["3.5"], "gezien": ["2.4"]},
            {"team": "INNO-2026", "y": 2, "x": 4, "bezit": ["1.1", "2.3"], "gemist": ["3.4"], "gezien": ["1.4"]},
            {"team": "INNO-2026", "y": 4, "x": 5, "bezit": ["3.5", "2.4"], "gemist": ["1.1"], "gezien": ["2.1"]},
            {"team": "INNO-2026", "y": 5, "x": 3, "bezit": ["1.3", "2.1", "3.1"], "gemist": ["3.5"], "gezien": ["1.1"]},

            # --- STARTUP-2026 (4 mensen - klein team) ---
            {"team": "STARTUP-2026", "y": 6, "x": 6, "bezit": ["1.1", "1.4", "2.1"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "STARTUP-2026", "y": 5, "x": 5, "bezit": ["2.4", "3.2", "3.5"], "gemist": ["1.2"], "gezien": ["2.4"]},
            {"team": "STARTUP-2026", "y": 7, "x": 4, "bezit": ["1.5", "2.7"], "gemist": ["3.1"], "gezien": ["1.4"]},
            {"team": "STARTUP-2026", "y": 4, "x": 7, "bezit": ["3.3", "3.4"], "gemist": ["2.6"], "gezien": ["3.5"]},

            # --- PROJECT-2026 (8 mensen - middelmatig team) ---
            {"team": "PROJECT-2026", "y": 3, "x": 4, "bezit": ["1.1", "2.4", "3.2"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "PROJECT-2026", "y": 5, "x": 3, "bezit": ["1.3", "1.5", "2.1"], "gemist": ["2.7"], "gezien": ["3.2"]},
            {"team": "PROJECT-2026", "y": 4, "x": 5, "bezit": ["2.2", "2.5", "3.4"], "gemist": ["1.4"], "gezien": ["2.4"]},
            {"team": "PROJECT-2026", "y": 6, "x": 2, "bezit": ["1.2", "3.1"], "gemist": ["3.5"], "gezien": ["1.5"]},
            {"team": "PROJECT-2026", "y": 2, "x": 6, "bezit": ["2.3", "2.6"], "gemist": ["1.1"], "gezien": ["3.4"]},
            {"team": "PROJECT-2026", "y": 7, "x": 4, "bezit": ["3.3", "3.5"], "gemist": ["2.1"], "gezien": ["1.2"]},
            {"team": "PROJECT-2026", "y": 4, "x": 3, "bezit": ["1.1", "2.4"], "gemist": ["3.3"], "gezien": ["2.5"]},
            {"team": "PROJECT-2026", "y": 5, "x": 5, "bezit": ["1.4", "2.7", "3.1"], "gemist": ["1.3"], "gezien": ["3.5"]},

            # --- CONSULT-2026 (6 mensen - middelmatig team) ---
            {"team": "CONSULT-2026", "y": 4, "x": 4, "bezit": ["1.1", "3.2"], "gemist": ["2.4"], "gezien": ["1.1"]},
            {"team": "CONSULT-2026", "y": 5, "x": 3, "bezit": ["1.3", "2.1", "3.5"], "gemist": ["1.5"], "gezien": ["3.2"]},
            {"team": "CONSULT-2026", "y": 3, "x": 5, "bezit": ["2.4", "2.5"], "gemist": ["3.1"], "gezien": ["1.3"]},
            {"team": "CONSULT-2026", "y": 6, "x": 2, "bezit": ["1.2", "3.4"], "gemist": ["2.7"], "gezien": ["2.4"]},
            {"team": "CONSULT-2026", "y": 2, "x": 6, "bezit": ["2.2", "2.6"], "gemist": ["1.4"], "gezien": ["3.5"]},
            {"team": "CONSULT-2026", "y": 7, "x": 4, "bezit": ["1.5", "3.3"], "gemist": ["2.1"], "gezien": ["1.2"]},

            # --- CORP-2026 (18 mensen - groot team) ---
            {"team": "CORP-2026", "y": 1, "x": 2, "bezit": ["2.6", "3.1"], "gemist": ["1.1"], "gezien": ["2.4"]},
            {"team": "CORP-2026", "y": 3, "x": 3, "bezit": ["1.1", "2.4", "3.2"], "gemist": ["3.5"], "gezien": ["1.1"]},
            {"team": "CORP-2026", "y": 5, "x": 4, "bezit": ["1.3", "1.5", "2.1"], "gemist": ["2.7"], "gezien": ["3.2"]},
            {"team": "CORP-2026", "y": 4, "x": 5, "bezit": ["2.2", "2.5", "3.4"], "gemist": ["1.4"], "gezien": ["2.4"]},
            {"team": "CORP-2026", "y": 6, "x": 3, "bezit": ["1.2", "3.1", "3.5"], "gemist": ["2.1"], "gezien": ["1.5"]},
            {"team": "CORP-2026", "y": 2, "x": 6, "bezit": ["2.3", "2.6"], "gemist": ["3.3"], "gezien": ["3.4"]},
            {"team": "CORP-2026", "y": 7, "x": 4, "bezit": ["3.3", "1.4"], "gemist": ["2.5"], "gezien": ["1.2"]},
            {"team": "CORP-2026", "y": 4, "x": 2, "bezit": ["1.1", "3.2"], "gemist": ["2.4"], "gezien": ["3.1"]},
            {"team": "CORP-2026", "y": 5, "x": 5, "bezit": ["2.4", "2.7", "3.5"], "gemist": ["1.3"], "gezien": ["2.1"]},
            {"team": "CORP-2026", "y": 3, "x": 7, "bezit": ["1.5", "2.5"], "gemist": ["3.2"], "gezien": ["1.4"]},
            {"team": "CORP-2026", "y": 6, "x": 4, "bezit": ["3.1", "3.4"], "gemist": ["1.1"], "gezien": ["2.6"]},
            {"team": "CORP-2026", "y": 2, "x": 3, "bezit": ["2.1", "2.2"], "gemist": ["3.5"], "gezien": ["1.3"]},
            {"team": "CORP-2026", "y": 4, "x": 6, "bezit": ["1.4", "2.3"], "gemist": ["1.5"], "gezien": ["3.4"]},
            {"team": "CORP-2026", "y": 7, "x": 5, "bezit": ["3.3", "3.5"], "gemist": ["2.2"], "gezien": ["1.1"]},
            {"team": "CORP-2026", "y": 1, "x": 4, "bezit": ["2.6", "3.2"], "gemist": ["1.2"], "gezien": ["2.5"]},
            {"team": "CORP-2026", "y": 5, "x": 2, "bezit": ["1.2", "1.3"], "gemist": ["3.4"], "gezien": ["3.1"]},
            {"team": "CORP-2026", "y": 3, "x": 5, "bezit": ["2.4", "2.7"], "gemist": ["1.4"], "gezien": ["2.3"]},
            {"team": "CORP-2026", "y": 6, "x": 7, "bezit": ["1.5", "3.3"], "gemist": ["2.1"], "gezien": ["3.5"]}
        ]
        with open(DATA_FILE, "w") as f:
            json.dump(start_data, f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def apply_jitter(df, amount=0.15):
    df = df.copy()
    for i in range(len(df)):
        mask = (df['x'] == df.iloc[i]['x']) & (df['y'] == df.iloc[i]['y'])
        if mask.sum() > 1:
            df.loc[mask, 'x'] += np.random.uniform(-amount, amount, mask.sum())
            df.loc[mask, 'y'] += np.random.uniform(-amount, amount, mask.sum())
    return df

init_data()

# --- 2b. HELPER FUNCTIES ---
def t(key):
    """Gets translated text based on current language"""
    lang = st.session_state.get("language", "nl")
    return TRANSLATIONS.get(lang, {}).get(key, key)

# --- 3. UI ---
st.set_page_config(
    page_title="Team Innovatie Tool", 
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom CSS voor blauw-oranje-wit thema
st.markdown("""
<style>
    /* Hoofdthema kleuren */
    :root {
        --primary-color: #1f77b4;
        --background-color: #ffffff;
        --secondary-background-color: #f8f9fa;
        --text-color: #2c3e50;
        --accent-color: #ff7f0e;
    }
    
    /* Streamlit component styling */
    .stApp {
        background-color: var(--background-color);
    }
    
    .stSidebar {
        background-color: var(--secondary-background-color);
        border-right: 3px solid var(--primary-color);
    }
    
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border: 2px solid var(--accent-color);
        border-radius: 8px;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: var(--accent-color);
        border-color: var(--primary-color);
    }
    
    .stSelectbox, .stMultiselect, .stTextInput {
        border-color: var(--primary-color);
    }
    
    .stSelectbox>div>div, .stMultiselect>div>div, .stTextInput>div>div {
        border-color: var(--primary-color);
        border-radius: 6px;
    }
    
    h1, h2, h3 {
        color: var(--primary-color);
    }
    
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 8px;
        border-left: 5px solid var(--accent-color);
    }
    
    .stExpander {
        border: 2px solid var(--primary-color);
        border-radius: 8px;
    }
    
    .stExpanderHeader {
        background-color: var(--secondary-background-color);
        color: var(--primary-color);
        font-weight: bold;
    }
    
    /* Slider styling */
    .stSlider .st-bs {
        background-color: var(--accent-color);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--secondary-background-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--primary-color);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialiseer session state
if "language" not in st.session_state:
    st.session_state.language = "nl"
if "view_team_code" not in st.session_state:
    st.session_state.view_team_code = "INNO-2026"

st.title(t("title"))

with st.sidebar:
    # Taal selector (links boven)
    col_lang1, col_lang2 = st.columns([0.5, 1])
    with col_lang1:
        st.write(t("language"))
    with col_lang2:
        lang = st.selectbox("", options=["nl", "en"], format_func=lambda x: "🇳🇱 Nederlands" if x == "nl" else "🇬🇧 English", label_visibility="collapsed", key="lang_select")
        if lang != st.session_state.get("language", "nl"):
            st.session_state.language = lang
            st.rerun()
    
    st.divider()
    st.header(t("sidebar_header"))
    with st.form("survey_form"):
        # Team selectie met dropdown
        available_teams = get_available_teams()
        team_options = available_teams + [""]
        selected_team = st.selectbox(t("team_code"), options=team_options, format_func=lambda x: x if x else "--- Nieuw team ---" if st.session_state.get("language", "nl") == "nl" else "--- New team ---", label_visibility="collapsed")
        
        if selected_team == "":
            team_code = st.text_input(t("team_code_custom")).strip().upper()
        else:
            team_code = selected_team
            st.write(f"**{team_code}**")
        
        y_val = st.select_slider(t("work_form"), options=range(1, 8), format_func=lambda x: get_werkvorm_labels()[x-1])
        x_val = st.select_slider(t("work_approach"), options=range(1, 8), format_func=lambda x: get_werkaanpak_labels()[x-1])
        
        q_list = [f"{k}: {v['naam']}" for k,v in QUALITEITEN.items()]
        bezit = st.multiselect(t("your_qualities"), q_list)
        gemist = st.multiselect(t("missed"), q_list)
        gezien = st.multiselect(t("seen"), q_list)
        
        if st.form_submit_button(t("save_button")):
            if not team_code:
                st.error(t("error_code"))
            else:
                d = load_data()
                d.append({"team": team_code, "x": x_val, "y": y_val, 
                          "bezit": [s.split(":")[0] for s in bezit],
                          "gemist": [s.split(":")[0] for s in gemist],
                          "gezien": [s.split(":")[0] for s in gezien]})
                save_data(d)
                st.session_state.view_team_code = team_code
                st.success(t("success"))
                st.rerun()

# --- 4. GRAFIEKEN (ONDER ELKAAR) ---
available_teams_view = get_available_teams()
if available_teams_view:
    kijk_team_input = st.selectbox(t("view_team"), options=available_teams_view, index=available_teams_view.index(st.session_state.view_team_code) if st.session_state.view_team_code in available_teams_view else 0)
else:
    kijk_team_input = st.text_input(t("view_team"), value=st.session_state.view_team_code).strip().upper()

st.session_state.view_team_code = kijk_team_input
team_responses = [r for r in load_data() if r['team'] == kijk_team_input]

if team_responses:
    qual_stats = []
    all_points_per_group = {"Absorptief": [], "Adoptief": [], "Adaptief": []}
    gemist_counts = {}
    gezien_counts = {}

    for r in team_responses:
        for q in r['gemist']: gemist_counts[q] = gemist_counts.get(q, 0) + 1
        for q in r['gezien']: gezien_counts[q] = gezien_counts.get(q, 0) + 1

    max_gemist = max(gemist_counts.values()) if gemist_counts else 0
    max_gezien = max(gezien_counts.values()) if gezien_counts else 0

    for q_id, info in QUALITEITEN.items():
        relevant = [r for r in team_responses if q_id in r['bezit']]
        if relevant:
            avg_x = sum(r['x'] for r in relevant) / len(relevant)
            avg_y = sum(r['y'] for r in relevant) / len(relevant)
            qual_stats.append({"id": q_id, "naam": info['naam'], "groep": info['groep'],
                               "x": avg_x, "y": avg_y, "count": len(relevant), "kleur": info['kleur']})
            all_points_per_group[info['groep']].append([avg_x, avg_y])

    df = apply_jitter(pd.DataFrame(qual_stats))

    # --- GRAFIEK 1: MAPPING ---
    st.subheader(t("mapping_title"))
    st.write(t("mapping_desc"))
    fig1 = go.Figure()
    for _, row in df.iterrows():
        is_g = (row['id'] in gemist_counts and gemist_counts[row['id']] == max_gemist and max_gemist > 0)
        is_z = (row['id'] in gezien_counts and gezien_counts[row['id']] == max_gezien and max_gezien > 0)
        fig1.add_trace(go.Scatter(
            x=[row['x']], y=[row['y']], mode='markers+text',
            marker=dict(size=row['count']*15 + 10, color=row['kleur'], line=dict(width=4 if is_z else 0, color='black')),
            text=[row['id']], textfont=dict(color='white' if is_g else 'black', size=11, family="Arial Black"),
            name=row['groep'], hovertemplate=f"<b>{t('quality')} {row['id']}</b><br>{row['naam']}<br>{t('number')}: {row['count']}<extra></extra>"
        ))
    fig1.update_layout(xaxis=dict(tickvals=list(range(1,8)), ticktext=get_werkaanpak_labels(), range=[0.5, 7.5]),
                      yaxis=dict(tickvals=list(range(1,8)), ticktext=get_werkvorm_labels(), range=[0.5, 7.5]),
                      height=800, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # --- GRAFIEK 2: DNA ---
    st.subheader(t("dna_title"))
    st.write(t("dna_desc"))
    fig2 = go.Figure()
    groep_kleuren = {"Absorptief": "orange", "Adoptief": "royalblue", "Adaptief": "gold"}
    for groep, points in all_points_per_group.items():
        if len(points) >= 3:
            pts = np.array(points)
            try:
                hull = ConvexHull(pts)
                hull_pts = pts[hull.vertices]
                hull_pts = np.vstack((hull_pts, hull_pts[0]))
                fig2.add_trace(go.Scatter(x=hull_pts[:,0], y=hull_pts[:,1], fill="toself", fillcolor=groep_kleuren[groep], 
                                         opacity=0.3, line=dict(color=groep_kleuren[groep], width=2), name=groep))
            except: 
                fig2.add_trace(go.Scatter(x=pts[:,0], y=pts[:,1], mode='lines+markers', line=dict(width=4), name=groep))
        elif len(points) > 0:
            pts = np.array(points)
            fig2.add_trace(go.Scatter(x=pts[:,0], y=pts[:,1], mode='markers', marker=dict(size=12, color=groep_kleuren[groep]), name=groep))
    fig2.update_layout(xaxis=dict(tickvals=list(range(1,8)), ticktext=get_werkaanpak_labels(), range=[0.5, 7.5]),
                      yaxis=dict(tickvals=list(range(1,8)), ticktext=get_werkvorm_labels(), range=[0.5, 7.5]), height=800)
    st.plotly_chart(fig2, use_container_width=True)

# Admin
with st.expander(t("admin")):
    if st.text_input(t("admin_password"), type="password") == "Ingrid_Bolier":
        available_teams_admin = get_available_teams()
        if available_teams_admin:
            t_del = st.selectbox(t("admin_team"), options=available_teams_admin)
            if st.button(t("admin_delete")):
                d = [r for r in load_data() if r['team'] != t_del]
                save_data(d)
                st.success(t("admin_success"))
                st.rerun()
        else:
            st.info("Geen teamdata beschikbaar" if st.session_state.get("language", "nl") == "nl" else "No team data available")