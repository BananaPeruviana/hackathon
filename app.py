import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ==========================================
# DIZIONARIO TRADUZIONI
# ==========================================
TRANSLATIONS = {
    "Italiano": {
        "file_not_found": "File {0} non trovato! Inseriscilo nella cartella.",
        "work_status": "Stato Lavoro",
        "rows_completed": "Righe completate: {0} su {1}",
        "rem_budget": "Budget residuo",
        "budget_info": "Budget iniziale: {0} € | Spesa approvata: {1} €",
        "all_done": "Hai analizzato o superato tutti i casi disponibili!",
        "go_back_last": "⬅️ Torna indietro per rivedere l'ultimo caso",
        "eval_case": "Valutazione Caso #{0}",
        "eval_warning": "Valuta attentamente i dati del nucleo familiare prima di consultare il parere dell'algoritmo.",
        "info_title": "1. Informazioni Chiave Famiglia",
        "members": "Membri Famiglia",
        "dep_level": "Livello Dipendenza",
        "female_head": "Capofamiglia Donna?",
        "sole_caregiver": "Caregiver Unico?",
        "yes": "Sì",
        "no": "No",
        "na": "N/D",
        "dup_reg": "Registrazione Duplicata (-500 pt)",
        "incomp_intent": "Intenzioni Incompatibili col Programma (-500 pt)",
        "irreg_asylum": "Stato Procedura Asilo Irregolare (-500 pt)",
        "red_flag_alert": "**ATTENZIONE - BLOCCHI AMMINISTRATIVI RILEVATI:**\n\n",
        "vuln_profile": "2. Profilo di Vulnerabilità",
        "global_median": "Mediana Globale",
        "curr_case": "Caso Corrente",
        "cost_dist": "2.1 Distribuzione dei fondi necessari per il salvataggio (Dati Esterni)",
        "cost_dist_name": "Distribuzione fondi necessari per il salvataggio",
        "curr_record_val": "Record Attuale ({0}€)",
        "curr_record": "Record Corrente",
        "cost_x": "Fondi necessari per il salvataggio (Raggruppati ogni 100 €)",
        "cost_y": "Numero di Record",
        "col_not_found": "Colonna '{0}' non trovata nel file {1}. Modifica il nome nel codice.",
        "ai_model": "3. Modello di Intelligenza Artificiale",
        "reasoning": "**Motivazione (Reasoning Engine)**",
        "reasoning_text_1": "La famiglia presenta un punteggio demografico di {0:.1f} e un punteggio di necessità pari a {1:.1f}. ",
        "reasoning_text_high": "I dati indicano una forte pressione sui meccanismi di sussistenza. Si raccomanda prioritizzazione.",
        "reasoning_text_low": "Rispetto al pool attuale, le vulnerabilità risultano moderate o coperte da altre reti di supporto.",
        "decision": "**Decisione (Answer Engine)**",
        "final_score": "Punteggio Finale (FinalScore)",
        "vuln_band": "Fascia Vulnerabilità",
        "rec_incl": "**RACCOMANDAZIONE: INCLUSIONE (EligibilityTarget)**",
        "rec_excl": "**RACCOMANDAZIONE: ESCLUSIONE (EligibilityTarget)**",
        "final_decision": "4. Decisione Finale Operatore",
        "prev": "⬅️ Precedente",
        "skip_prev": "⏮️ Precedente (da valutare)",
        "skip_next": "⏭ Prossimo (da valutare)",
        "next": "Prossimo ➡",
        "approve_reject": "Vuoi approvare o rifiutare questa richiesta?",
        "approve": "Approva",
        "reject": "Rifiuta",
        "motivate": "Motiva la tua scelta (Obbligatorio):",
        "motivate_ph": "Inserisci qui il motivo per cui hai approvato o rifiutato questo caso...",
        "save_next": "Salva Decisione e Vai al Prossimo da Valutare",
        "warn_missing": "⚠️ Attenzione: devi selezionare 'Approva' o 'Rifiuta' e inserire una motivazione per poter procedere."
    },
    "English": {
        "file_not_found": "File {0} not found! Please place it in the folder.",
        "work_status": "Work Status",
        "rows_completed": "Completed rows: {0} of {1}",
        "rem_budget": "Remaining Budget",
        "budget_info": "Initial Budget: {0} € | Approved Expenditure: {1} €",
        "all_done": "You have analyzed or surpassed all available cases!",
        "go_back_last": "⬅️ Go back to review the last case",
        "eval_case": "Case Evaluation #{0}",
        "eval_warning": "Carefully evaluate the household data before consulting the algorithm's opinion.",
        "info_title": "1. Key Family Information",
        "members": "Family Members",
        "dep_level": "Dependency Level",
        "female_head": "Female Head of Household?",
        "sole_caregiver": "Sole Caregiver?",
        "yes": "Yes",
        "no": "No",
        "na": "N/A",
        "dup_reg": "Duplicate Registration (-500 pt)",
        "incomp_intent": "Intentions Incompatible with Program (-500 pt)",
        "irreg_asylum": "Irregular Asylum Procedure Status (-500 pt)",
        "red_flag_alert": "**ATTENTION - ADMINISTRATIVE BLOCKS DETECTED:**\n\n",
        "vuln_profile": "2. Vulnerability Profile",
        "global_median": "Global Median",
        "curr_case": "Current Case",
        "cost_dist": "2.1 Distribution of funds needed for rescue (External Data)",
        "cost_dist_name": "Distribution of funds needed for rescue",
        "curr_record_val": "Current Record ({0}€)",
        "curr_record": "Current Record",
        "cost_x": "Funds needed for rescue (Grouped every 100 €)",
        "cost_y": "Number of Records",
        "col_not_found": "Column '{0}' not found in file {1}. Modify the name in the code.",
        "ai_model": "3. Artificial Intelligence Model",
        "reasoning": "**Motivation (Reasoning Engine)**",
        "reasoning_text_1": "The family has a demographic score of {0:.1f} and a needs score of {1:.1f}. ",
        "reasoning_text_high": "The data indicates strong pressure on livelihood mechanisms. Prioritization is recommended.",
        "reasoning_text_low": "Compared to the current pool, vulnerabilities are moderate or covered by other support networks.",
        "decision": "**Decision (Answer Engine)**",
        "final_score": "Final Score (FinalScore)",
        "vuln_band": "Vulnerability Band",
        "rec_incl": "**RECOMMENDATION: INCLUSION (EligibilityTarget)**",
        "rec_excl": "**RECOMMENDATION: EXCLUSION (EligibilityTarget)**",
        "final_decision": "4. Final Operator Decision",
        "prev": "⬅️ Previous",
        "skip_prev": "⏮️ Previous (to evaluate)",
        "skip_next": "⏭️ Next (to evaluate)",
        "next": "Next ➡️",
        "approve_reject": "Do you want to approve or reject this request?",
        "approve": "Approve",
        "reject": "Reject",
        "motivate": "Motivate your choice (Required):",
        "motivate_ph": "Insert here the reason why you approved or rejected this case...",
        "save_next": "Save Decision and Go to Next to Evaluate",
        "warn_missing": "⚠️ Warning: you must select 'Approve' or 'Reject' and enter a motivation to proceed."
    },
    "Français": {
        "file_not_found": "Fichier {0} introuvable ! Veuillez le placer dans le dossier.",
        "work_status": "Statut du travail",
        "rows_completed": "Lignes complétées : {0} sur {1}",
        "rem_budget": "Budget restant",
        "budget_info": "Budget initial : {0} € | Dépenses approuvées : {1} €",
        "all_done": "Vous avez analysé ou dépassé tous les cas disponibles !",
        "go_back_last": "⬅️ Retour pour revoir le dernier cas",
        "eval_case": "Évaluation du cas #{0}",
        "eval_warning": "Évaluez attentivement les données du ménage avant de consulter l'avis de l'algorithme.",
        "info_title": "1. Informations clés de la famille",
        "members": "Membres de la famille",
        "dep_level": "Niveau de dépendance",
        "female_head": "Femme chef de famille ?",
        "sole_caregiver": "Seul soignant ?",
        "yes": "Oui",
        "no": "Non",
        "na": "N/D",
        "dup_reg": "Inscription en double (-500 pt)",
        "incomp_intent": "Intentions incompatibles avec le programme (-500 pt)",
        "irreg_asylum": "Statut de procédure d'asile irrégulier (-500 pt)",
        "red_flag_alert": "**ATTENTION - BLOCAGES ADMINISTRATIVOS DÉTECTÉS :**\n\n",
        "vuln_profile": "2. Profil de vulnérabilité",
        "global_median": "Médiane globale",
        "curr_case": "Cas actuel",
        "cost_dist": "2.1 Distribution des fonds nécessaires au sauvetage (Données externes)",
        "cost_dist_name": "Distribution des fonds nécessaires au sauvetage",
        "curr_record_val": "Enregistrement actuel ({0}€)",
        "curr_record": "Enregistrement actuel",
        "cost_x": "Fonds nécessaires au sauvetage (Regroupés par 100 €)",
        "cost_y": "Nombre d'enregistrements",
        "col_not_found": "Colonne '{0}' introuvable dans le fichier {1}. Modifiez le nom dans le code.",
        "ai_model": "3. Modèle d'Intelligence Artificielle",
        "reasoning": "**Motivation (Reasoning Engine)**",
        "reasoning_text_1": "La famille a un score démographique de {0:.1f} et un score de besoins de {1:.1f}. ",
        "reasoning_text_high": "Les données indiquent une forte pression sur les mécanismes de subsistance. Une priorisation est recommandée.",
        "reasoning_text_low": "Par rapport au groupe actuel, les vulnérabilités sont modérées ou couverte par d'autres réseaux de soutien.",
        "decision": "**Décision (Answer Engine)**",
        "final_score": "Score final (FinalScore)",
        "vuln_band": "Niveau de vulnérabilité",
        "rec_incl": "**RECOMMANDATION : INCLUSION (EligibilityTarget)**",
        "rec_excl": "**RECOMMANDATION : EXCLUSION (EligibilityTarget)**",
        "final_decision": "4. Décision finale de l'opérateur",
        "prev": "⬅ Précédent",
        "skip_prev": "⏮️ Précédent (à évaluer)",
        "skip_next": "⏭️ Prochain (à évaluer)",
        "next": "Suivant ➡️",
        "approve_reject": "Voulez-vous approuver ou rejeter cette demande ?",
        "approve": "Approuver",
        "reject": "Rejeter",
        "motivate": "Motivez votre choix (Obligatoire) :",
        "motivate_ph": "Insérez ici la raison pour laquelle vous avez approuvé ou rejeté ce cas...",
        "save_next": "Enregistrer la décision et passer au suivant à évaluer",
        "warn_missing": "⚠️ Attention : vous devez sélectionner 'Approuver' ou 'Rejeter' et saisir un motif pour continuer."
    },
    "Español": {
        "file_not_found": "¡Archivo {0} no encontrado! Colóquelo en la carpeta.",
        "work_status": "Estado de Trabajo",
        "rows_completed": "Filas completadas: {0} de {1}",
        "rem_budget": "Presupuesto restante",
        "budget_info": "Presupuesto inicial: {0} € | Gasto aprobado: {1} €",
        "all_done": "¡Has analizado o superado todos los casos disponibles!",
        "go_back_last": "⬅️ Volver para revisar el último caso",
        "eval_case": "Evaluación del caso #{0}",
        "eval_warning": "Evalúe cuidadosamente los datos del hogar antes de consultar la opinión del algoritmo.",
        "info_title": "1. Información Clave de la Familia",
        "members": "Miembros de la familia",
        "dep_level": "Nivel de dependencia",
        "female_head": "¿Mujer cabeza de familia?",
        "sole_caregiver": "¿Cuidador único?",
        "yes": "Sí",
        "no": "No",
        "na": "N/D",
        "dup_reg": "Registro duplicado (-500 pt)",
        "incomp_intent": "Intenciones Incompatibles con el Programa (-500 pt)",
        "irreg_asylum": "Estado de Procedimiento de Asilo Irregular (-500 pt)",
        "red_flag_alert": "**ATENCIÓN - BLOQUEOS ADMINISTRATIVOS DETECTADOS:**\n\n",
        "vuln_profile": "2. Perfil de Vulnerabilidad",
        "global_median": "Mediana global",
        "curr_case": "Caso actual",
        "cost_dist": "2.1 Distribución de los fondos necesarios para el rescate (Datos Externos)",
        "cost_dist_name": "Distribución de los fondos necesarios para el rescate",
        "curr_record_val": "Registro Actual ({0}€)",
        "curr_record": "Registro actual",
        "cost_x": "Fondos necesarios para el rescate (Agrupados cada 100 €)",
        "cost_y": "Número de Registros",
        "col_not_found": "Columna '{0}' no encontrada en el archivo {1}. Modifique el nombre en el código.",
        "ai_model": "3. Modelo de Inteligencia Artificial",
        "reasoning": "**Motivación (Reasoning Engine)**",
        "reasoning_text_1": "La familia tiene una puntuación demográfica de {0:.1f} y una puntuación de necesidad de {1:.1f}. ",
        "reasoning_text_high": "Los datos indican una fuerte presión sobre los mecanismos de subsistencia. Se recomienda priorización.",
        "reasoning_text_low": "En comparación con el grupo actual, las vulnerabilidades son moderadas o están cubiertas por otras redes de apoyo.",
        "decision": "**Decisión (Answer Engine)**",
        "final_score": "Puntuación Final (FinalScore)",
        "vuln_band": "Nivel de Vulnerabilidad",
        "rec_incl": "**RECOMENDACIÓN: INCLUSIÓN (EligibilityTarget)**",
        "rec_excl": "**RECOMENDACIÓN: EXCLUSIÓN (EligibilityTarget)**",
        "final_decision": "4. Decisión Final del Operador",
        "prev": "⬅️ Anterior",
        "skip_prev": "⏮️ Anterior (a evaluar)",
        "skip_next": "⏭️ Siguiente (a evaluar)",
        "next": "Siguiente ➡️",
        "approve_reject": "¿Desea aprobar o rechazar esta solicitud?",
        "approve": "Aprobar",
        "reject": "Rechazar",
        "motivate": "Motive su elección (Obligatorio):",
        "motivate_ph": "Inserte aquí la razón por la que aprobó o rechazó este caso...",
        "save_next": "Guardar Decisión e ir al siguiente a evaluar",
        "warn_missing": "⚠️ Atención: debe seleccionar 'Aprobar' o 'Rechazar' e ingresar un motivo para continuar."
    }
}

FILE_NAME = "S8.synthetic_cashy_sample.csv"
FILE_ESTERNI = "DatiEsterni.csv"

# Funzione per trovare la prossima riga non valutata
def get_next_uncompleted(df, current_idx):
    for idx in range(current_idx + 1, len(df)):
        if pd.isna(df.at[idx, 'Decisione_Operatore']):
            return idx
    for idx in range(0, current_idx):
        if pd.isna(df.at[idx, 'Decisione_Operatore']):
            return idx
    return len(df)

# Funzione per trovare la riga precedente non valutata
def get_prev_uncompleted(df, current_idx):
    for idx in range(current_idx - 1, -1, -1):
        if pd.isna(df.at[idx, 'Decisione_Operatore']):
            return idx
    for idx in range(len(df) - 1, current_idx, -1):
        if pd.isna(df.at[idx, 'Decisione_Operatore']):
            return idx
    return len(df)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Revisore AI - UNHCR Cash Assistance", 
    page_icon="🌍",
    layout="wide"
)

# --- INIEZIONE CSS (STILE UNHCR AGGIORNATO PER LEGGIBILITÀ) ---
unhcr_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');

    /* Font globale */
    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif !important;
    }
    
    /* Sfondo pagina principale chiaro e testo scuro garantito */
    .stApp {
        background-color: #F4F6F9 !important;
    }
    
    /* Forza il testo scuro ovunque (per evitare bianco su bianco) */
    p, span, div, label {
        color: #333333 !important; 
    }

    /* Colore sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E0E0E0 !important;
    }

    /* Rimuove/corregge l'header nero fisso di Streamlit */
    header[data-testid="stHeader"] {
        background-color: transparent !important; /* Rende invisibile la barra nera */
        position: absolute !important; 
    }

    /* Colori dei titoli - Blue UNHCR */
    h1, h2, h3, h4, h5, h6 {
        color: #0072BC !important; 
        font-weight: 700 !important;
    }
    
    /* Forza testo chiaro all'interno del banner blu, sovrascrivendo la regola generica */
    .unhcr-banner {
        background-color: #0072BC;
        padding: 15px 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-size: 24px;
        font-weight: 900;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    }
    .unhcr-banner, .unhcr-banner * {
        color: #FFFFFF !important;
    }

    /* Metriche */
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] > div {
        color: #0072BC !important;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] > div {
        color: #555555 !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }

    /* Container e Form per raggruppare visivamente */
    [data-testid="stForm"], .stDataFrame {
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 8px !important;
        border: 1px solid #E5E5E5 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }

    /* Text Areas pulite */
    .stTextArea textarea {
        border: 1px solid #CCCCCC !important;
        border-radius: 4px !important;
        background-color: #FFFFFF !important;
        color: #333333 !important; /* Testo input scuro */
    }
    .stTextArea textarea:focus {
        border-color: #0072BC !important;
        box-shadow: 0 0 0 1px #0072BC !important;
    }
    .stTextArea label, .stTextArea label p {
        color: #333333 !important;
    }

    /* Pulsanti Secondari (Stile Outline pulito, testo scuro/blu su sfondo bianco) */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #0072BC !important;
        border: 1px solid #0072BC !important;
        border-radius: 4px !important;
        transition: all 0.2s ease !important;
        font-weight: 600 !important;
    }
    
    div.stButton > button p {
       color: #0072BC !important; 
    }

    div.stButton > button:hover {
        background-color: #0072BC !important;
    }
    
    div.stButton > button:hover p {
        color: #FFFFFF !important;
    }

    /* Pulsante Primario (Es. Submit form) */
    div[data-testid="stFormSubmitButton"] > button, 
    button[kind="primary"] {
        background-color: #0072BC !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        padding: 0.5rem 1rem !important;
    }
    
    div[data-testid="stFormSubmitButton"] > button p, 
    button[kind="primary"] p {
        color: #FFFFFF !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover,
    button[kind="primary"]:hover {
        background-color: #00558C !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* Stile messaggi di alert e info (sfondi chiari, testo visibile) */
    .stAlert {
        border-radius: 4px !important;
        border-left: 5px solid !important;
        color: #333333 !important;
    }
    .stAlert p {
        color: #333333 !important;
    }

    /* Radio buttons accenti blu */
    .stRadio > div {
        accent-color: #0072BC !important;
    }
    .stRadio label, .stRadio p {
         color: #333333 !important;
    }

    hr {
        border-color: #DDDDDD !important;
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
    }
    
    /* Nascondere menu default Streamlit */
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    [data-testid="stAppDeployButton"] {display:none !important;}
</style>
"""
st.markdown(unhcr_css, unsafe_allow_html=True)

# Inizializza lingua in session_state
if 'lang' not in st.session_state:
    st.session_state.lang = "Italiano"

# Recupera subito il dizionario lingua corrente
t = TRANSLATIONS[st.session_state.lang]

# --- CARICAMENTO DATI ---
def load_data():
    if not os.path.exists(FILE_NAME):
        st.error(t["file_not_found"].format(FILE_NAME))
        return None
    
    df = pd.read_csv(FILE_NAME)
    for col in ['Decisione_Operatore', 'Motivazione_Operatore']:
        if col not in df.columns:
            df[col] = None
    return df

@st.cache_data
def load_dati_esterni():
    if not os.path.exists(FILE_ESTERNI):
        return None
    return pd.read_csv(FILE_ESTERNI, sep=';')

if 'df' not in st.session_state:
    st.session_state.df = load_data()
    if st.session_state.df is not None:
        categorie_radar = [
            'Demographics.HH.Head', 'Demographics.Language', 'Demographics.Profiles', 'Demographics.Documentation',
            'Needs_and_Coping.BasicNeeds', 'Needs_and_Coping.Housing', 'Needs_and_Coping.Neg.mechanism', 'Needs_and_Coping.Dependency'
        ]
        mediane_radar = []
        for cat in categorie_radar:
            mediana = st.session_state.df[cat].median()
            mediane_radar.append(mediana if pd.notna(mediana) else 1.0)
        mediane_radar.append(mediane_radar[0]) 
        st.session_state.mediane_radar = mediane_radar
        
        da_analizzare = st.session_state.df[st.session_state.df['Decisione_Operatore'].isnull()]
        st.session_state.current_index = da_analizzare.index[0] if not da_analizzare.empty else len(st.session_state.df)

if st.session_state.df is None:
    st.stop()

df = st.session_state.df
df_esterni = load_dati_esterni()
indice = st.session_state.current_index

budget_totale = None
budget_residuo = None
spesa_approvata = 0
if df_esterni is not None and {'Budget', 'Costo'}.issubset(df_esterni.columns):
    valori_budget = pd.to_numeric(df_esterni['Budget'], errors='coerce').dropna()
    if not valori_budget.empty:
        budget_totale = valori_budget.iloc[0]
        approvati = df['Decisione_Operatore'] == 'Approva'
        costi = pd.to_numeric(df_esterni['Costo'], errors='coerce')
        spesa_approvata = costi.reindex(df.index[approvati]).sum()
        budget_residuo = budget_totale - spesa_approvata

# --- BARRA LATERALE ---
with st.sidebar:
    # Selettore Lingua
    st.header("🌐 Language / Lingua")
    lingua_scelta = st.selectbox(
        "Seleziona / Select:",
        options=["Italiano", "English", "Français", "Español"],
        index=["Italiano", "English", "Français", "Español"].index(st.session_state.lang)
    )
    if lingua_scelta != st.session_state.lang:
        st.session_state.lang = lingua_scelta
        st.rerun()
        
    st.divider()

    st.header(t["work_status"])
    st.write(t["rows_completed"].format(df['Decisione_Operatore'].notna().sum(), len(df)))
    st.progress(df['Decisione_Operatore'].notna().sum() / len(df) if len(df) > 0 else 0)

    if budget_residuo is not None:
        st.metric(t["rem_budget"], f"{budget_residuo:,.2f} €")
        st.caption(t["budget_info"].format(f"{budget_totale:,.2f}", f"{spesa_approvata:,.2f}"))
    
    st.write("---")

if indice >= len(df):
    st.success(t["all_done"])
    
    if st.button(t["go_back_last"]):
        st.session_state.current_index = len(df) - 1
        st.rerun()

    colonne_finali = [c for c in ['Elegibilidad', 'Decisione_Operatore', 'Motivazione_Operatore'] if c in df.columns]
    st.dataframe(df[colonne_finali])
    st.stop()

riga = df.iloc[indice]

# ==========================================
# HEADER E TITOLO
# ==========================================
st.markdown("""
<div class="unhcr-banner">
    🌍 UNHCR | Cash Assistance - AI Reviewer
</div>
""", unsafe_allow_html=True)

st.title(t["eval_case"].format(indice + 1))
st.write(t["eval_warning"])

# ==========================================
# SEZIONE 1: I FATTI OGGETTIVI
# ==========================================
st.subheader(t["info_title"])
col1, col2, col3, col4 = st.columns(4)
col1.metric(t["members"], riga['NumIntegrantes'])
col2.metric(t["dep_level"], riga['dependencyCategory'])

val_female = t["yes"] if riga['FemaleHeadedHousehold'] == 'jefatura_femenina' else (t["na"] if pd.isna(riga['FemaleHeadedHousehold']) else t["no"])
val_caregiver = t["yes"] if riga['CuidadorSolo'] == 'si' else (t["na"] if pd.isna(riga['CuidadorSolo']) else t["no"])

col3.metric(t["female_head"], val_female)
col4.metric(t["sole_caregiver"], val_caregiver)

red_flags = []
if riga['ScoreDuplicidad'] < 0: red_flags.append(t["dup_reg"])
if riga['ScoreIntenciones'] < 0: red_flags.append(t["incomp_intent"])
if riga['ScoreCOMAR_PIL'] < 0: red_flags.append(t["irreg_asylum"])

if red_flags:
    st.error(t["red_flag_alert"] + "\n".join([f"- {f}" for f in red_flags]))

st.subheader(t["vuln_profile"])
categorie_radar = [
    'Demographics.HH.Head', 'Demographics.Language', 'Demographics.Profiles', 'Demographics.Documentation',
    'Needs_and_Coping.BasicNeeds', 'Needs_and_Coping.Housing', 'Needs_and_Coping.Neg.mechanism', 'Needs_and_Coping.Dependency'
]
valori_radar = [riga[cat] if pd.notna(riga[cat]) else 1.0 for cat in categorie_radar]
valori_radar.append(valori_radar[0])
etichette_radar = [c.replace('_', ' ').replace('.', '\n') for c in categorie_radar]
etichette_radar.append(etichette_radar[0])

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
  r=st.session_state.mediane_radar,
  theta=etichette_radar,
  fill='toself',
  fillcolor='rgba(169, 169, 169, 0.3)',
  line_color='#888888',
  name=t["global_median"]
))

fig.add_trace(go.Scatterpolar(
  r=valori_radar,
  theta=etichette_radar,
  fill='toself',
  fillcolor='rgba(0, 114, 188, 0.4)', # UNHCR Blue trasparente
  line_color='#0072BC',
  name=t["curr_case"]
))

fig.update_layout(
  polar=dict(
      radialaxis=dict(visible=True, range=[0, 3.5], color="#888888", tickfont=dict(color="#333333")),
      angularaxis=dict(color="#333333", tickfont=dict(color="#333333"))
  ),
  showlegend=True,
  height=400,
  margin=dict(l=40, r=40, t=20, b=20),
  paper_bgcolor='rgba(0,0,0,0)',
  plot_bgcolor='rgba(0,0,0,0)',
  font=dict(color="#333333")
)
# AGGIUNTO theme=None per evitare che il tema di default di Streamlit sovrascriva i colori (testo bianco)
st.plotly_chart(fig, use_container_width=True, theme=None) 

if df_esterni is not None:
    st.subheader(t["cost_dist"])
    colonna_costo = 'Costo' 
    
    if colonna_costo in df_esterni.columns:
        df_esterni['Costo_Binned'] = (df_esterni[colonna_costo] // 100) * 100
        distribuzione = df_esterni['Costo_Binned'].value_counts().sort_index().reset_index()
        distribuzione.columns = ['Scaglione_Costo', 'Numero_Record']
        
        fig_costi = go.Figure()
        fig_costi.add_trace(go.Scatter(
            x=distribuzione['Scaglione_Costo'],
            y=distribuzione['Numero_Record'],
            mode='lines+markers',
            name=t["cost_dist_name"],
            line=dict(color='#0072BC', width=2), # UNHCR Blue
            marker=dict(size=6)
        ))
        
        if indice < len(df_esterni):
            costo_corrente = df_esterni.iloc[indice][colonna_costo]
            costo_binned_corrente = (costo_corrente // 100) * 100
            
            if costo_binned_corrente in distribuzione['Scaglione_Costo'].values:
                y_corrente = distribuzione[distribuzione['Scaglione_Costo'] == costo_binned_corrente]['Numero_Record'].values[0]
            else:
                y_corrente = 0
            
            fig_costi.add_vline(
                x=costo_binned_corrente, 
                line_dash="dash", 
                line_color="red", 
                annotation_text=t["curr_record_val"].format(costo_corrente),
                annotation_position="top right"
            )
            
            fig_costi.add_trace(go.Scatter(
                x=[costo_binned_corrente],
                y=[y_corrente],
                mode='markers',
                name=t["curr_record"],
                marker=dict(color='#E02D2D', size=14, symbol='circle', line=dict(color='white', width=2))
            ))

        fig_costi.update_layout(
            xaxis_title=t["cost_x"],
            yaxis_title=t["cost_y"],
            showlegend=True,
            height=350,
            margin=dict(l=40, r=40, t=30, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#333333")
        )
        # AGGIUNTO theme=None per evitare che il tema di default di Streamlit sovrascriva i colori (testo bianco)
        st.plotly_chart(fig_costi, use_container_width=True, theme=None) 
    else:
        st.warning(t["col_not_found"].format(colonna_costo, FILE_ESTERNI))

st.divider()

# ==========================================
# SEZIONE 2: LA VALUTAZIONE DELL'AI
# ==========================================
st.subheader(t["ai_model"])
col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.info(t["reasoning"])
    testo_ragionamento = t["reasoning_text_1"].format(riga['Demographics_Score'], riga['NeedsandCoping_Score'])
    if riga['FinalScore'] > 40:
        testo_ragionamento += t["reasoning_text_high"]
    else:
        testo_ragionamento += t["reasoning_text_low"]
    st.write(f"*{testo_ragionamento}*")

with col_ai2:
    st.info(t["decision"])
    st.metric(t["final_score"], round(riga['FinalScore'], 2))
    st.metric(t["vuln_band"], riga['Vulnerability_Category'])
    if riga['EligibilityTarget'] == 'INCLUSION':
        st.success(t["rec_incl"])
    else:
        st.error(t["rec_excl"])

st.divider()

# ==========================================
# SEZIONE 3: NAVIGAZIONE E DECISIONE
# ==========================================
st.subheader(t["final_decision"])

col_prev, col_skip_prev, col_skip_next, col_next = st.columns(4)

with col_prev:
    if st.button(t["prev"], disabled=(indice == 0), use_container_width=True):
        st.session_state.current_index -= 1
        st.rerun()

with col_skip_prev:
    if st.button(t["skip_prev"], use_container_width=True):
        st.session_state.current_index = get_prev_uncompleted(df, indice)
        st.rerun()

with col_skip_next:
    if st.button(t["skip_next"], use_container_width=True):
        st.session_state.current_index = get_next_uncompleted(df, indice)
        st.rerun()

with col_next:
    if st.button(t["next"], disabled=(indice >= len(df) - 1), use_container_width=True):
        st.session_state.current_index += 1
        st.rerun()

st.write("---")

val_decisione_esistente = df.at[indice, 'Decisione_Operatore']
val_motivazione_esistente = df.at[indice, 'Motivazione_Operatore']

idx_decisione = None
if val_decisione_esistente == "Approva":
    idx_decisione = 0
elif val_decisione_esistente == "Rifiuta":
    idx_decisione = 1

testo_motivazione = val_motivazione_esistente if pd.notna(val_motivazione_esistente) else ""

with st.form(key=f"form_{indice}"):
    
    decisione_ui = st.radio(
        t["approve_reject"],
        options=[t["approve"], t["reject"]], 
        index=idx_decisione, 
        horizontal=True
    )
    
    motivazione = st.text_area(
        t["motivate"],
        value=testo_motivazione,
        placeholder=t["motivate_ph"]
    )
    
    submit_button = st.form_submit_button(label=t["save_next"], type="primary")
    
    if submit_button:
        if decisione_ui is None or not motivazione.strip():
            st.warning(t["warn_missing"])
        else:
            # Riconverti sempre il valore tradotto nel valore standard per i dati ("Approva"/"Rifiuta")
            decisione_val = "Approva" if decisione_ui == t["approve"] else "Rifiuta"
            
            st.session_state.df.at[indice, 'Decisione_Operatore'] = decisione_val
            st.session_state.df.at[indice, 'Motivazione_Operatore'] = motivazione.strip()
            
            st.session_state.df.to_csv(FILE_NAME, index=False)
            st.cache_data.clear()
            
            st.session_state.current_index = get_next_uncompleted(st.session_state.df, indice)
            st.rerun()
