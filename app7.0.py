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
        "title": "Survey & Dashboard Innovative Capabilities",
        "sidebar_header": "📊 Survey Invoer",
        "team_code": "Teamcode:",
        "team_code_custom": "Of voer nieuw team in:",
        "work_form": "Werkvorm (Y)",
        "work_approach": "Werkaanpak (X)",
        "your_qualities": "Welke kwaliteiten zetten jou in je kracht om te innoveren?",
        "missed": "Welke kwaliteiten mis je bij jezelf/in je team om te innoveren?",
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
        "language": "Taal:",
        "work_form_info": "Het strategisch managementniveau omvat lange-termijnacties om richting en missie te bepalen en de relevante stakeholders te betrekken. Het tactisch niveau richt de samenwerkingsconfiguratie en processen in om het systeem te laten functioneren. Het operationeel niveau voert de dagelijkse werkzaamheden uit in projecten, programma's en processen et cetera",
        "work_approach_info": "Afstemming tussen hiërarchische duidelijkheid en middelen voor opschaling én netwerkgerichte ruimte voor experimenteren, kennisdeling en het opbouwen van draagvlak",
        "absorptive_title": "Absorptief",
        "absorptive_desc": "'Het nieuwe binnen halen'\nBenodigde kennis, mensen en andere middelen op waarde schatten, mobiliseren en doelgericht integreren",
        "adoptive_title": "Adoptief",
        "adoptive_desc": "'Toepasbaarheid en toegevoegde waarde aantonen'\nZorgen voor inzicht in wat het oplevert. Tijdens toepassen effect op scope, tijd en geld balanceren, ongeacht onzekerheden",
        "adaptive_title": "Adaptief",
        "adaptive_desc": "'Van het nieuwe, naar het nieuwe normaal'\nSignaleren wanneer \"we\" klaar zijn voor verandering en dan met kleine concrete stappen verandering doorvoeren."
    },
    "en": {
        "title": "Survey & Dashboard Innovative Capabilities",
        "sidebar_header": "📊 Survey Input",
        "team_code": "Team Code:",
        "team_code_custom": "Or enter new team:",
        "work_form": "Work Form (Y)",
        "work_approach": "Work Approach (X)",
        "your_qualities": "Which capabilities put you in your strength to innovate?",
        "missed": "Which capabilities do you miss in yourself/your team to innovate?",
        "save_button": "Save data",
        "error_code": "Team code required!",
        "success": "Success! Page refreshed.",
        "view_team": "View team results for:",
        "no_data": "No data for this team.",
        "mapping_title": "1. Individual Capabilities Mapping",
        "mapping_desc": "Circles show the average position of team members who have this capability. Hover over a circle for details.",
        "dna_title": "2. Team DNA (Expertise Overlap)",
        "dna_desc": "The colored areas show the scope of the three main quality groups within the team.",
        "admin": "⚙️ Admin",
        "admin_password": "Reset password",
        "admin_team": "Which team to delete?",
        "admin_delete": "Delete data",
        "admin_success": "Reset!",
        "quality": "Quality",
        "number": "Number",
        "language": "Language:",
        "work_form_info": "Strategic management level includes long-term actions to determine direction and mission and involve relevant stakeholders. The tactical level directs the collaboration configuration and processes to make the system function. The operational level carries out daily activities in projects, programs and processes etc",
        "work_approach_info": "Alignment between hierarchical clarity and resources for scaling and network-oriented space for experimentation, knowledge sharing and building support",
        "absorptive_title": "Absorbing",
        "absorptive_desc": "'Bringing in the new'\nAssess, mobilize and purposefully integrate required knowledge, people and other resources",
        "adoptive_title": "Adopting",
        "adoptive_desc": "'Demonstrating applicability and added value'\nEnsure insight into what it delivers. During application balance effect on scope, time and money, regardless of uncertainties",
        "adaptive_title": "Adapting",
        "adaptive_desc": "'From the new to the new normal'\nDetect when \"we\" are ready for change and implement it step by step with small concrete actions"
    }
}

# --- 1. CONFIGURATIE ---
QUALITEITEN = {
    "1.1": {"naam": "Actoren mobiliseren", "naam_en": "Mobilizing actors", "uitleg": "Vermogen om actoren in andere (delen van de) organisatie(s) te mobiliseren en/of te coördineren", "uitleg_en": "Ability to mobilize and/or coordinate actors in other (parts of) organization(s)", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.2": {"naam": "Kennis integreren", "naam_en": "Integrating knowledge", "uitleg": "Vermogen om impliciete en expliciete kennis en andere competenties te integreren", "uitleg_en": "Ability to integrate implicit and explicit knowledge and other competencies", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.3": {"naam": "Successen benadrukken", "naam_en": "Emphasizing successes", "uitleg": "Vermogen om kleine successen te benadrukken om consensus te bereiken", "uitleg_en": "Ability to emphasize small successes to reach consensus", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.4": {"naam": "Ambities concreet maken", "naam_en": "Making ambitions concrete", "uitleg": "Vermogen om de dialoog aan te gaan over concrete realisatie van ambities", "uitleg_en": "Ability to engage in dialogue about concrete realization of ambitions", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "1.5": {"naam": "Context specifiek framen", "naam_en": "Framing context-specific", "uitleg": "Vermogen om innovatie te verwoorden in een passende (sociale, bestuurlijke en/of persoonlijke) context", "uitleg_en": "Ability to express innovation in an appropriate (social, administrative and/or personal) context", "groep": "Absorptief", "kleur": "rgba(255, 165, 0, 0.8)"},
    "2.1": {"naam": "Waarde verifiëren in specifieke situatie", "naam_en": "Verifying value in specific situation", "uitleg": "Vermogen om de effecten en eigenschappen (waarde) van innovatie in een specifieke pilot inzichtelijk te maken en/of te verifiëren", "uitleg_en": "Ability to clarify and/or verify the effects and properties (value) of innovation in a specific pilot", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.2": {"naam": "Waarde verifiëren in contexten", "naam_en": "Verifying value in contexts", "uitleg": "Vermogen om de effecten en eigenschappen (waarde) van innovatie in meerdere (geografische) contexten inzichtelijk te maken en/of te verifiëren", "uitleg_en": "Ability to clarify and/or verify the effects and properties (value) of innovation in multiple (geographic) contexts", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.3": {"naam": "Beheersbaarheid testen", "naam_en": "Testing manageability", "uitleg": "Vermogen om de beheersbaarheid van (soms botsende) krachten te testen: scope, functionele prestaties (kwaliteit), kosten en tijd", "uitleg_en": "Ability to test the manageability of (sometimes conflicting) forces: scope, functional performance (quality), costs and time", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.4": {"naam": "Overzicht houden", "naam_en": "Maintaining overview", "uitleg": "In staat zijn om overzicht te houden over ontwikkelingen, de gevolgen van beslissingen te voorspellen en zich aan te passen in geval van onvoorziene omstandigheden", "uitleg_en": "Ability to maintain overview of developments, predict consequences of decisions and adapt in case of unforeseen circumstances", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.5": {"naam": "Creëer momentum in ecosysteem", "naam_en": "Creating ecosystem momentum", "uitleg": "Vermogen om steun en momentum in het ecosysteem te creëren/gebruiken", "uitleg_en": "Ability to create/use support and momentum in the ecosystem", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.6": {"naam": "Leren van de common lessons learned", "naam_en": "Learning from lessons learned", "uitleg": "Vermogen om bij het implementeren van innovaties te leren van eerder geleerde lessen door anderen", "uitleg_en": "Ability to learn from previously learned lessons by others when implementing innovations", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "2.7": {"naam": "Iteratief leren", "naam_en": "Iterative learning", "uitleg": "Vermogen om diverse innovaties te implementeren en te leren van lessen van anderen", "uitleg_en": "Ability to implement diverse innovations and learn from lessons of others", "groep": "Adoptief", "kleur": "rgba(100, 149, 237, 0.8)"},
    "3.1": {"naam": "Coördineren met of de organisatie er klaar voor is", "naam_en": "Coordinating organizational readiness", "uitleg": "Vermogen om het starten met aanpassen af te stemmen op in hoeverre de organisatie er klaar voor is", "uitleg_en": "Ability to align the start of adaptation with the degree to which the organization is ready", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.2": {"naam": "Aanpassen met kleine concrete stappen", "naam_en": "Adapting with small concrete steps", "uitleg": "Vermogen om organisatorische routines, cultuur en/of structuren met kleine concrete stappen aan te passen", "uitleg_en": "Ability to adapt organizational routines, culture and/or structures with small concrete steps", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.3": {"naam": "Ondersteunend beleid maken", "naam_en": "Creating supporting policy", "uitleg": "Vermogen om ondersteunend beleid op te stellen om ongewenste effecten te voorkomen", "uitleg_en": "Ability to establish supporting policy to prevent unwanted effects", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.4": {"naam": "Level playing field borgen", "naam_en": "Securing level playing field", "uitleg": "Vermogen om een 'level-playing-field' in de markt te borgen", "uitleg_en": "Ability to secure a 'level-playing-field' in the market", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.5": {"naam": "Lange termijn waarde bepalen", "naam_en": "Determining long-term value", "uitleg": "Vermogen om waarde toe te kennen op strategisch niveau op lange termijn", "uitleg_en": "Ability to assign value at strategic level in the long term", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"},
    "3.6": {"naam": "Markt uitdagen", "naam_en": "Challenging the market", "uitleg": "Vermogen om de markt uit te dagen", "uitleg_en": "Ability to challenge the market", "groep": "Adaptief", "kleur": "rgba(255, 215, 0, 0.8)"}
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

def get_quality_name(q_id, lang="nl"):
    """Get the quality name in the correct language"""
    if q_id in QUALITEITEN:
        return QUALITEITEN[q_id].get("naam_en" if lang == "en" else "naam", q_id)
    return q_id

def get_quality_description(q_id, lang="nl"):
    """Get the quality description in the correct language"""
    if q_id in QUALITEITEN:
        return QUALITEITEN[q_id].get("uitleg_en" if lang == "en" else "uitleg", "")
    return ""

DATA_FILE = "survey_data.json"

# --- 2. DATA FUNCTIES ---
def init_data():
    if not os.path.exists(DATA_FILE):
        start_data = [
            # --- INNO-2026 (23 mensen - groot team) ---
            {"team": "INNO-2026", "y": 1, "x": 3, "bezit": ["1.1", "2.4", "3.2"], "gemist": ["3.5"]},
            {"team": "INNO-2026", "y": 7, "x": 3, "bezit": ["1.1", "1.4", "3.5"], "gemist": ["2.4", "3.5"]},
            {"team": "INNO-2026", "y": 4, "x": 5, "bezit": ["2.1", "2.4", "3.5"], "gemist": ["3.5"]},
            {"team": "INNO-2026", "y": 6, "x": 2, "bezit": ["1.2", "1.3"], "gemist": ["2.1"]},
            {"team": "INNO-2026", "y": 5, "x": 4, "bezit": ["3.1", "3.3", "1.5"], "gemist": ["2.6"]},
            {"team": "INNO-2026", "y": 2, "x": 6, "bezit": ["2.2", "2.3", "2.7"], "gemist": ["1.1"]},
            {"team": "INNO-2026", "y": 3, "x": 5, "bezit": ["1.4", "2.5", "3.4"], "gemist": ["3.5"]},
            {"team": "INNO-2026", "y": 4, "x": 4, "bezit": ["1.1", "3.2"], "gemist": ["2.4"]},
            {"team": "INNO-2026", "y": 7, "x": 7, "bezit": ["3.5", "1.5"], "gemist": ["1.2"]},
            {"team": "INNO-2026", "y": 1, "x": 1, "bezit": ["2.6"], "gemist": ["3.3"]},
            {"team": "INNO-2026", "y": 5, "x": 3, "bezit": ["1.1", "1.3", "2.1"], "gemist": ["3.5"]},
            {"team": "INNO-2026", "y": 6, "x": 4, "bezit": ["3.1", "3.5"], "gemist": ["2.7"]},
            {"team": "INNO-2026", "y": 4, "x": 6, "bezit": ["2.4", "2.5"], "gemist": ["1.1"]},
            {"team": "INNO-2026", "y": 3, "x": 2, "bezit": ["1.2", "3.4"], "gemist": ["3.5"]},
            {"team": "INNO-2026", "y": 2, "x": 3, "bezit": ["2.1", "2.2"], "gemist": ["1.4"]},
            {"team": "INNO-2026", "y": 5, "x": 5, "bezit": ["1.1", "3.3"], "gemist": ["2.4"]},
            {"team": "INNO-2026", "y": 4, "x": 4, "bezit": ["2.7", "3.5"], "gemist": ["1.5"]},
            {"team": "INNO-2026", "y": 6, "x": 6, "bezit": ["1.4", "2.4"], "gemist": ["3.5"]},
            {"team": "INNO-2026", "y": 7, "x": 2, "bezit": ["3.1", "3.2"], "gemist": ["2.5"]},
            {"team": "INNO-2026", "y": 3, "x": 7, "bezit": ["1.5", "2.6"], "gemist": ["3.5"]},
            {"team": "INNO-2026", "y": 2, "x": 4, "bezit": ["1.1", "2.3"], "gemist": ["3.4"]},
            {"team": "INNO-2026", "y": 4, "x": 5, "bezit": ["3.5", "2.4"], "gemist": ["1.1"]},
            {"team": "INNO-2026", "y": 5, "x": 3, "bezit": ["1.3", "2.1", "3.1"], "gemist": ["3.5"]},

            # --- STARTUP-2026 (4 mensen - klein team) ---
            {"team": "STARTUP-2026", "y": 6, "x": 6, "bezit": ["1.1", "1.4", "2.1"], "gemist": ["3.5"]},
            {"team": "STARTUP-2026", "y": 5, "x": 5, "bezit": ["2.4", "3.2", "3.5"], "gemist": ["1.2"]},
            {"team": "STARTUP-2026", "y": 7, "x": 4, "bezit": ["1.5", "2.7"], "gemist": ["3.1"]},
            {"team": "STARTUP-2026", "y": 4, "x": 7, "bezit": ["3.3", "3.4"], "gemist": ["2.6"]},

            # --- PROJECT-2026 (8 mensen - middelmatig team) ---
            {"team": "PROJECT-2026", "y": 3, "x": 4, "bezit": ["1.1", "2.4", "3.2"], "gemist": ["3.5"]},
            {"team": "PROJECT-2026", "y": 5, "x": 3, "bezit": ["1.3", "1.5", "2.1"], "gemist": ["2.7"]},
            {"team": "PROJECT-2026", "y": 4, "x": 5, "bezit": ["2.2", "2.5", "3.4"], "gemist": ["1.4"]},
            {"team": "PROJECT-2026", "y": 6, "x": 2, "bezit": ["1.2", "3.1"], "gemist": ["3.5"]},
            {"team": "PROJECT-2026", "y": 2, "x": 6, "bezit": ["2.3", "2.6"], "gemist": ["1.1"]},
            {"team": "PROJECT-2026", "y": 7, "x": 4, "bezit": ["3.3", "3.5"], "gemist": ["2.1"]},
            {"team": "PROJECT-2026", "y": 4, "x": 3, "bezit": ["1.1", "2.4"], "gemist": ["3.3"]},
            {"team": "PROJECT-2026", "y": 5, "x": 5, "bezit": ["1.4", "2.7", "3.1"], "gemist": ["1.3"]},

            # --- CONSULT-2026 (6 mensen - middelmatig team) ---
            {"team": "CONSULT-2026", "y": 4, "x": 4, "bezit": ["1.1", "3.2"], "gemist": ["2.4"]},
            {"team": "CONSULT-2026", "y": 5, "x": 3, "bezit": ["1.3", "2.1", "3.5"], "gemist": ["1.5"]},
            {"team": "CONSULT-2026", "y": 3, "x": 5, "bezit": ["2.4", "2.5"], "gemist": ["3.1"]},
            {"team": "CONSULT-2026", "y": 6, "x": 2, "bezit": ["1.2", "3.4"], "gemist": ["2.7"]},
            {"team": "CONSULT-2026", "y": 2, "x": 6, "bezit": ["2.2", "2.6"], "gemist": ["1.4"]},
            {"team": "CONSULT-2026", "y": 7, "x": 4, "bezit": ["1.5", "3.3"], "gemist": ["2.1"]},

            # --- CORP-2026 (18 mensen - groot team) ---
            {"team": "CORP-2026", "y": 1, "x": 2, "bezit": ["2.6", "3.1"], "gemist": ["1.1"]},
            {"team": "CORP-2026", "y": 3, "x": 3, "bezit": ["1.1", "2.4", "3.2"], "gemist": ["3.5"]},
            {"team": "CORP-2026", "y": 5, "x": 4, "bezit": ["1.3", "1.5", "2.1"], "gemist": ["2.7"]},
            {"team": "CORP-2026", "y": 4, "x": 5, "bezit": ["2.2", "2.5", "3.4"], "gemist": ["1.4"]},
            {"team": "CORP-2026", "y": 6, "x": 3, "bezit": ["1.2", "3.1", "3.5"], "gemist": ["2.1"]},
            {"team": "CORP-2026", "y": 2, "x": 6, "bezit": ["2.3", "2.6"], "gemist": ["3.3"]},
            {"team": "CORP-2026", "y": 7, "x": 4, "bezit": ["3.3", "1.4"], "gemist": ["2.5"]},
            {"team": "CORP-2026", "y": 4, "x": 2, "bezit": ["1.1", "3.2"], "gemist": ["2.4"]},
            {"team": "CORP-2026", "y": 5, "x": 5, "bezit": ["2.4", "2.7", "3.5"], "gemist": ["1.3"]},
            {"team": "CORP-2026", "y": 3, "x": 7, "bezit": ["1.5", "2.5"], "gemist": ["3.2"]},
            {"team": "CORP-2026", "y": 6, "x": 4, "bezit": ["3.1", "3.4"], "gemist": ["1.1"]},
            {"team": "CORP-2026", "y": 2, "x": 3, "bezit": ["2.1", "2.2"], "gemist": ["3.5"]},
            {"team": "CORP-2026", "y": 4, "x": 6, "bezit": ["1.4", "2.3"], "gemist": ["1.5"]},
            {"team": "CORP-2026", "y": 7, "x": 5, "bezit": ["3.3", "3.5"], "gemist": ["2.2"]},
            {"team": "CORP-2026", "y": 1, "x": 4, "bezit": ["2.6", "3.2"], "gemist": ["1.2"]},
            {"team": "CORP-2026", "y": 5, "x": 2, "bezit": ["1.2", "1.3"], "gemist": ["3.4"]},
            {"team": "CORP-2026", "y": 3, "x": 5, "bezit": ["2.4", "2.7"], "gemist": ["1.4"]},
            {"team": "CORP-2026", "y": 6, "x": 7, "bezit": ["1.5", "3.3"], "gemist": ["2.1"]}
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
    
    /* Slider styling - oranje kleur */
    .stSlider [data-baseweb="slider"] [data-baseweb="slider-track"] {
        background-color: #ff7f0e !important;
    }
    
    .stSlider [data-baseweb="slider"] [data-baseweb="slider-progress"] {
        background-color: #ff7f0e !important;
    }
    
    .stSlider [data-baseweb="slider"] [data-baseweb="slider-thumb"] {
        background-color: #ff7f0e !important;
        border-color: #ff7f0e !important;
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
        
        # Werkvorm met tooltip
        work_form_help = t('work_form_info')
        st.markdown(f"""
        <div title="{work_form_help.replace('"', '&quot;')}" style="cursor: help; border-bottom: 1px dotted #1f77b4;">
            <label style="color: #1f77b4; font-weight: bold;">{t('work_form')}</label>
        </div>
        """, unsafe_allow_html=True)
        y_val = st.select_slider(t("work_form"), options=range(1, 8), format_func=lambda x: get_werkvorm_labels()[x-1], label_visibility="collapsed")
        
        # Werkaanpak met tooltip
        work_approach_help = t('work_approach_info')
        st.markdown(f"""
        <div title="{work_approach_help.replace('"', '&quot;')}" style="cursor: help; border-bottom: 1px dotted #1f77b4;">
            <label style="color: #1f77b4; font-weight: bold;">{t('work_approach')}</label>
        </div>
        """, unsafe_allow_html=True)
        x_val = st.select_slider(t("work_approach"), options=range(1, 8), format_func=lambda x: get_werkaanpak_labels()[x-1], label_visibility="collapsed")
        
        q_list = [f"{k}: {v['naam']}" for k,v in QUALITEITEN.items()]
        
        # Label met hulptekst
        st.markdown(f"""
        <div style='border-bottom: 2px dotted #ff7f0e; padding-bottom: 5px; margin-bottom: 10px;'>
            <label style="color: #1f77b4; font-weight: bold;">{t('your_qualities')}</label>
            <div style='font-size: 11px; color: #666; margin-top: 5px;'>💡 Selecteer kwaliteiten - klik op de items hieronder voor beschrijving</div>
        </div>
        """, unsafe_allow_html=True)
        
        bezit = st.multiselect(t("your_qualities"), q_list, label_visibility="collapsed")
        
        # Toon beschrijvingen van gekozen "bezit" items
        if bezit:
            st.markdown("<div style='background-color: #fff9e6; border-left: 4px solid #ff7f0e; padding: 10px; border-radius: 4px; margin-bottom: 15px;'>", unsafe_allow_html=True)
            for item in bezit:
                q_id = item.split(":")[0]
                desc = get_quality_description(q_id, st.session_state.get("language", "nl"))
                st.markdown(f"""
                <div style='margin-bottom: 8px;'>
                    <span style="font-weight: bold; color: #ff7f0e;">✓ {item}</span><br>
                    <span style="font-size: 11px; color: #555; margin-left: 15px;">{desc}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Label voor gemist
        st.markdown(f"""
        <div style='border-bottom: 2px dotted #1f77b4; padding-bottom: 5px; margin-bottom: 10px; margin-top: 15px;'>
            <label style="color: #1f77b4; font-weight: bold;">{t('missed')}</label>
            <div style='font-size: 11px; color: #666; margin-top: 5px;'>💡 Selecteer kwaliteiten - klik op de items hieronder voor beschrijving</div>
        </div>
        """, unsafe_allow_html=True)
        
        gemist = st.multiselect(t("missed"), q_list, label_visibility="collapsed")
        
        # Toon beschrijvingen van gekozen "gemist" items
        if gemist:
            st.markdown("<div style='background-color: #e6f2ff; border-left: 4px solid #1f77b4; padding: 10px; border-radius: 4px; margin-bottom: 15px;'>", unsafe_allow_html=True)
            for item in gemist:
                q_id = item.split(":")[0]
                desc = get_quality_description(q_id, st.session_state.get("language", "nl"))
                st.markdown(f"""
                <div style='margin-bottom: 8px;'>
                    <span style="font-weight: bold; color: #1f77b4;">✓ {item}</span><br>
                    <span style="font-size: 11px; color: #555; margin-left: 15px;">{desc}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        if st.form_submit_button(t("save_button")):
            if not team_code:
                st.error(t("error_code"))
            else:
                d = load_data()
                d.append({"team": team_code, "x": x_val, "y": y_val, 
                          "bezit": [s.split(":")[0] for s in bezit],
                          "gemist": [s.split(":")[0] for s in gemist]})
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
    bezit_counts = {}
    gemist_counts = {}

    for r in team_responses:
        for q in r['bezit']: bezit_counts[q] = bezit_counts.get(q, 0) + 1
        for q in r['gemist']: gemist_counts[q] = gemist_counts.get(q, 0) + 1

    # Top 3 per categorie
    top3_bezit = sorted(bezit_counts.items(), key=lambda x: x[1], reverse=True)[:3] if bezit_counts else []
    top3_gemist = sorted(gemist_counts.items(), key=lambda x: x[1], reverse=True)[:3] if gemist_counts else []
    top3_bezit_ids = [q[0] for q in top3_bezit]
    top3_gemist_ids = [q[0] for q in top3_gemist]

    for q_id, info in QUALITEITEN.items():
        relevant = [r for r in team_responses if q_id in r['bezit']]
        if relevant:
            avg_x = sum(r['x'] for r in relevant) / len(relevant)
            avg_y = sum(r['y'] for r in relevant) / len(relevant)
            qual_stats.append({"id": q_id, "naam": info['naam'], "groep": info['groep'],
                               "x": avg_x, "y": avg_y, "count": len(relevant), "kleur": info['kleur'], "uitleg": info.get('uitleg', '')})
            all_points_per_group[info['groep']].append([avg_x, avg_y])

    df = apply_jitter(pd.DataFrame(qual_stats))

    # --- GRAFIEK 1: MAPPING ---
    st.subheader(t("mapping_title"))
    st.write(t("mapping_desc"))
    
    # LEGENDA SECTIE - UITGEBREID
    st.markdown("""
    <div style="border: 2px solid #1f77b4; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f8f9fa;">
        <h3 style="color: #1f77b4; margin-top: 0; margin-bottom: 20px;">📋 Legenda & Uitleg</h3>
    """, unsafe_allow_html=True)
    
    # Legenda - Groepen met expandables
    st.markdown("<h4 style='color: #1f77b4; margin-bottom: 10px;'>Kwaliteitengroepen:</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.expander(f"🟠 {t('absorptive_title')}"):
            st.write(t('absorptive_desc').replace('\\n', '\n'))
    with col2:
        with st.expander(f"🔵 {t('adoptive_title')}"):
            st.write(t('adoptive_desc').replace('\\n', '\n'))
    with col3:
        with st.expander(f"🟡 {t('adaptive_title')}"):
            st.write(t('adaptive_desc').replace('\\n', '\n'))
    
    # Legenda - Markering voorbeelden met betere contextualisering
    st.markdown("<h4 style='color: #1f77b4; margin-top: 20px; margin-bottom: 10px;'>Cirkelmarkeringen in de grafiek:</h4>", unsafe_allow_html=True)
    col_leg1, col_leg2 = st.columns(2)
    with col_leg1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; background-color: #fff9e6; padding: 12px; border-radius: 6px; border-left: 4px solid #ff7f0e;">
            <svg width="60" height="60">
                <circle cx="30" cy="30" r="14" fill="rgba(255, 165, 0, 0.8)" stroke="none" />
                <text x="30" y="36" text-anchor="middle" font-size="11" fill="white" font-weight="bold">1.1</text>
            </svg>
            <div>
                <span><strong>Meest gemist</strong></span><br>
                <span style="font-size: 11px; color: #666;">Deze kwaliteit wordt door het meeste aantal teamleden gemist</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_leg2:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 15px; background-color: #e6f2ff; padding: 12px; border-radius: 6px; border-left: 4px solid #1f77b4;">
            <svg width="60" height="60">
                <circle cx="30" cy="30" r="14" fill="rgba(255, 165, 0, 0.8)" stroke="black" stroke-width="4" />
                <text x="30" y="36" text-anchor="middle" font-size="11" fill="white" font-weight="bold">1.1</text>
            </svg>
            <div>
                <span><strong>Meest gebruikt</strong></span><br>
                <span style="font-size: 11px; color: #666;">Deze kwaliteit wordt door het meeste aantal teamleden gebruikt</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Info over cirkelgrootte
    st.markdown("""
    <div style="background-color: #f0f0f0; padding: 12px; border-radius: 6px; margin-top: 15px; border-left: 4px solid #666;">
        <span style="font-size: 12px; color: #333;">
            <strong>Cirkelgrootte:</strong> Hoe groter de cirkel, hoe meer teamleden deze kwaliteit bezitten. 
            <strong>Positie:</strong> De cirkel staat op de doorsnee positie van alle teamleden die deze kwaliteit hebben.
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    fig1 = go.Figure()
    for _, row in df.iterrows():
        is_top3_bezit = row['id'] in top3_bezit_ids
        is_top3_gemist = row['id'] in top3_gemist_ids
        lang = st.session_state.get('language', 'nl')
        desc = get_quality_description(row['id'], lang)
        fig1.add_trace(go.Scatter(
            x=[row['x']], y=[row['y']], mode='markers+text',
            marker=dict(size=row['count']*15 + 10, color=row['kleur'], line=dict(width=4 if is_top3_bezit else 0, color='black')),
            text=[row['id']], textfont=dict(color='white' if is_top3_gemist else 'black', size=11, family="Arial Black"),
            name=row['groep'], hovertemplate=f"<b>{t('quality')} {row['id']}</b><br>{get_quality_name(row['id'], lang)}<br>{desc}<br>{t('number')}: {row['count']}<extra></extra>"
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