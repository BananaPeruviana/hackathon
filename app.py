import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import os

FILE_NAME = "S8.synthetic_cashy_sample.csv"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Revisore AI - Cash Assistance", layout="wide")

# --- CARICAMENTO DATI ---
@st.cache_data
def load_data():
    if not os.path.exists(FILE_NAME):
        st.error(f"File {FILE_NAME} non trovato! Inseriscilo nella cartella.")
        return None
    
    df = pd.read_csv(FILE_NAME)
    
    # Crea le colonne per l'annotazione se non esistono
    for col in ['Accordo_Ragionamento', 'Accordo_Risposta', 'Motivo_Override']:
        if col not in df.columns:
            df[col] = None
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()
    if st.session_state.df is not None:
        # Trova la prima riga non valutata
        da_analizzare = st.session_state.df[st.session_state.df['Accordo_Risposta'].isnull()]
        st.session_state.current_index = da_analizzare.index[0] if not da_analizzare.empty else len(st.session_state.df)

if st.session_state.df is None:
    st.stop()

df = st.session_state.df
indice = st.session_state.current_index

# --- BARRA LATERALE (DOWNLOAD) ---
with st.sidebar:
    st.header("Stato Lavoro")
    st.write(f"Righe completate: {min(indice, len(df))} su {len(df)}")
    st.progress(min(indice, len(df)) / len(df))
    
    st.write("---")
    # Prepara il CSV per il download
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica Dati Valutati",
        data=csv_data,
        file_name="S8.annotato.csv",
        mime="text/csv",
        type="primary"
    )

# Se tutte le righe sono finite
if indice >= len(df):
    st.success("Hai analizzato tutti i casi disponibili!")
    st.dataframe(df[['Elegibilidad', 'Accordo_Ragionamento', 'Accordo_Risposta', 'Motivo_Override']])
    st.stop()

riga = df.iloc[indice]

# ==========================================
# SEZIONE 1: I FATTI OGGETTIVI (SENZA AI)
# ==========================================
st.title(f"Valutazione Caso #{indice + 1}")
st.write("Valuta attentamente i dati del nucleo familiare prima di consultare il parere dell'algoritmo.")

# 1A: Badge Informativi Rapidi
st.subheader("1. Informazioni Chiave Famiglia")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Membri Famiglia", riga['NumIntegrantes'])
col2.metric("Livello Dipendenza", riga['dependencyCategory'])
col3.metric("Capofamiglia Donna?", "Sì" if riga['FemaleHeadedHousehold'] == 'jefatura_femenina' else ("N/D" if pd.isna(riga['FemaleHeadedHousehold']) else "No"))
col4.metric("Caregiver Unico?", "Sì" if riga['CuidadorSolo'] == 'si' else ("N/D" if pd.isna(riga['CuidadorSolo']) else "No"))

# 1B: Red Flags (Blocchi Amministrativi)
red_flags = []
if riga['ScoreDuplicidad'] < 0: red_flags.append("Registrazione Duplicata (-500 pt)")
if riga['ScoreIntenciones'] < 0: red_flags.append("Intenzioni Incompatibili col Programma (-500 pt)")
if riga['ScoreCOMAR_PIL'] < 0: red_flags.append("Stato Procedura Asilo Irregolare (-500 pt)")

if red_flags:
    st.error("**ATTENZIONE - BLOCCHI AMMINISTRATIVI RILEVATI:**\n\n" + "\n".join([f"- {f}" for f in red_flags]))

# 1C: Grafico a Radar della Vulnerabilità
st.subheader("2. Profilo di Vulnerabilità")
categorie_radar = [
    'Demographics.HH.Head', 'Demographics.Language', 'Demographics.Profiles', 'Demographics.Documentation',
    'Needs_and_Coping.BasicNeeds', 'Needs_and_Coping.Housing', 'Needs_and_Coping.Neg.mechanism', 'Needs_and_Coping.Dependency'
]
valori_radar = [riga[cat] if pd.notna(riga[cat]) else 1.0 for cat in categorie_radar]
# Per chiudere la linea nel grafico a radar
valori_radar.append(valori_radar[0])
etichette_radar = [c.replace('_', ' ').replace('.', '\n') for c in categorie_radar]
etichette_radar.append(etichette_radar[0])

fig = go.Figure(data=go.Scatterpolar(
  r=valori_radar,
  theta=etichette_radar,
  fill='toself',
  line_color='blue'
))
fig.update_layout(
  polar=dict(radialaxis=dict(visible=True, range=[1, 3.5])),
  showlegend=False,
  height=400,
  margin=dict(l=40, r=40, t=20, b=20)
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==========================================
# SEZIONE 2: LA VALUTAZIONE DELL'AI
# ==========================================
st.subheader("3. Modello di Intelligenza Artificiale")
st.write("Di seguito il ragionamento e la decisione presa dall'algoritmo (Cashy-AI). Nessun *Responsible-AI statement* è mostrato per evitare pregiudizi cognitivi.")

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.info("**Motivazione (Reasoning Engine)**")
    # Generiamo un mock-up del ragionamento basato sul punteggio, 
    # dato che il dataset sintetico fornito non contiene la vera narrativa generata dall'LLM.
    testo_ragionamento = f"La famiglia presenta un punteggio demografico di {riga['Demographics_Score']:.1f} e un punteggio di necessità pari a {riga['NeedsandCoping_Score']:.1f}. "
    if riga['FinalScore'] > 40:
        testo_ragionamento += "I dati indicano una forte pressione sui meccanismi di sussistenza. Si raccomanda prioritizzazione."
    else:
        testo_ragionamento += "Rispetto al pool attuale, le vulnerabilità risultano moderate o coperte da altre reti di supporto."
    st.write(f"*{testo_ragionamento}*")

with col_ai2:
    st.info("**Decisione (Answer Engine)**")
    st.metric("Punteggio Finale (FinalScore)", round(riga['FinalScore'], 2))
    st.metric("Fascia Vulnerabilità", riga['Vulnerability_Category'])
    if riga['EligibilityTarget'] == 'INCLUSION':
        st.success("**RACCOMANDAZIONE: INCLUSIONE (EligibilityTarget)**")
    else:
        st.error("**RACCOMANDAZIONE: ESCLUSIONE (EligibilityTarget)**")

st.divider()

# ==========================================
# SEZIONE 3: COGNITIVE FORCING & DECISIONE
# ==========================================
st.subheader("4. Decisione Finale Operatore")

# Usiamo st.form per assicurarci che l'utente debba interagire attivamente prima di proseguire
with st.form(key=f"form_{indice}"):
    q_ragionamento = st.radio(
        "A) Ritieni che la **Motivazione (Reasoning)** fornita dall'AI sia coerente con i dati?",
        options=["Sì", "No"], index=None, horizontal=True
    )
    
    q_risposta = st.radio(
        "B) Condividi la **Raccomandazione Finale (Answer)** dell'AI per questo caso?",
        options=["Sì", "No"], index=None, horizontal=True
    )
    
    # Menù a tendina visibile sempre, ma obbligatorio solo se si sceglie "No"
    motivo_override = st.selectbox(
        "Se NON condividi la decisione dell'AI, indica il motivo principale dell'override:",
        options=[
            "Nessun disaccordo",
            "Informazioni inaccurate o incorrette (Inaccurate or incorrect information)",
            "Risultato inappropriato (Not appropriate or unexpected result)",
            "Decisione ingiusta per la famiglia (Unfair or unjust decision)",
            "Blocco amministrativo ignorato dall'AI",
            "Altro"
        ]
    )
    
    submit_button = st.form_submit_button(label="Conferma Decisione e Vai al Caso Successivo", type="primary")
    
    if submit_button:
        if q_ragionamento is None or q_risposta is None:
            st.warning("⚠️ Devi rispondere a entrambe le domande (Sì/No) per procedere.")
        elif q_risposta == "No" and motivo_override == "Nessun disaccordo":
            st.warning("⚠️ Hai deciso di non condividere la decisione dell'AI. Devi selezionare un motivo di override dall'elenco.")
        else:
            # Salvataggio nello stato (session_state.df)
            st.session_state.df.at[indice, 'Accordo_Ragionamento'] = q_ragionamento
            st.session_state.df.at[indice, 'Accordo_Risposta'] = q_risposta
            st.session_state.df.at[indice, 'Motivo_Override'] = motivo_override if q_risposta == "No" else None
            
            # Avanza riga e ricarica l'app per mostrare il caso successivo
            st.session_state.current_index += 1
            st.rerun()
