import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import os

FILE_NAME = "S8.synthetic_cashy_sample.csv"
FILE_ESTERNI = "DatiEsterni.csv"

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

@st.cache_data
def load_dati_esterni():
    if not os.path.exists(FILE_ESTERNI):
        return None
    return pd.read_csv(FILE_ESTERNI, sep=';')

if 'df' not in st.session_state:
    st.session_state.df = load_data()
    if st.session_state.df is not None:
        # Trova la prima riga non valutata
        da_analizzare = st.session_state.df[st.session_state.df['Accordo_Risposta'].isnull()]
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
        approvati = (
            df['EligibilityTarget'].eq('INCLUSION')
            & df['Accordo_Risposta'].isin(['Sì', 'Si'])
        )
        costi = pd.to_numeric(df_esterni['Costo'], errors='coerce')
        spesa_approvata = costi.reindex(df.index[approvati]).sum()
        budget_residuo = budget_totale - spesa_approvata

# --- BARRA LATERALE (DOWNLOAD) ---
with st.sidebar:
    st.header("Stato Lavoro")
    st.write(f"Righe completate: {min(indice, len(df))} su {len(df)}")
    st.progress(min(indice, len(df)) / len(df))

    if budget_residuo is not None:
        st.metric("Budget residuo", f"{budget_residuo:,.2f} €")
        st.caption(
            f"Budget iniziale: {budget_totale:,.2f} € | "
            f"Spesa approvata: {spesa_approvata:,.2f} €"
        )
    
    st.write("---")
    # Prepara il CSV per il download
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Scarica Dati Valutati",
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
  polar=dict(radialaxis=dict(visible=True, range=[0, 3.5])),
  showlegend=False,
  height=400,
  margin=dict(l=40, r=40, t=20, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 1D: GRAFICO DEI COSTI (DATI ESTERNI)
# ==========================================
if df_esterni is not None:
    st.subheader("2.1 Distribuzione dei Costi (Dati Esterni)")
    
    # MODIFICA QUI SE LA TUA COLONNA HA UN NOME DIVERSO
    colonna_costo = 'Costo' 
    
    if colonna_costo in df_esterni.columns:
        # Raggruppa i costi per scaglioni di 100 euro
        df_esterni['Costo_Binned'] = (df_esterni[colonna_costo] // 100) * 100
        
        # Conta quanti record ci sono per ogni scaglione
        distribuzione = df_esterni['Costo_Binned'].value_counts().sort_index().reset_index()
        distribuzione.columns = ['Scaglione_Costo', 'Numero_Record']
        
        fig_costi = go.Figure()
        
        # Linea generale della distribuzione
        fig_costi.add_trace(go.Scatter(
            x=distribuzione['Scaglione_Costo'],
            y=distribuzione['Numero_Record'],
            mode='lines+markers',
            name='Distribuzione Costi',
            line=dict(color='#8884d8', width=2),
            marker=dict(size=6)
        ))
        
        # Evidenzia il record in analisi (se l'indice esiste nei DatiEsterni)
        if indice < len(df_esterni):
            costo_corrente = df_esterni.iloc[indice][colonna_costo]
            costo_binned_corrente = (costo_corrente // 100) * 100
            
            # Trova l'altezza (Y) per posizionare il pallino sulla curva
            if costo_binned_corrente in distribuzione['Scaglione_Costo'].values:
                y_corrente = distribuzione[distribuzione['Scaglione_Costo'] == costo_binned_corrente]['Numero_Record'].values[0]
            else:
                y_corrente = 0
            
            # Retta verticale
            fig_costi.add_vline(
                x=costo_binned_corrente, 
                line_dash="dash", 
                line_color="red", 
                annotation_text=f"Record Attuale ({costo_corrente}€)",
                annotation_position="top right"
            )
            
            # Pallino di evidenziazione
            fig_costi.add_trace(go.Scatter(
                x=[costo_binned_corrente],
                y=[y_corrente],
                mode='markers',
                name='Record Corrente',
                marker=dict(color='red', size=14, symbol='circle', line=dict(color='white', width=2))
            ))

        fig_costi.update_layout(
            xaxis_title="Costo (Raggruppato ogni 100 €)",
            yaxis_title="Numero di Record",
            showlegend=True,
            height=350,
            margin=dict(l=40, r=40, t=30, b=30)
        )
        
        st.plotly_chart(fig_costi, use_container_width=True)
    else:
        st.warning(f" Colonna '{colonna_costo}' non trovata nel file {FILE_ESTERNI}. Modifica il nome nel codice.")
else:
    st.info(f" Il file {FILE_ESTERNI} non è presente. Se lo carichi, qui apparirà il grafico dei costi.")

st.divider()

# ==========================================
# SEZIONE 2: LA VALUTAZIONE DELL'AI
# ==========================================
st.subheader("3. Modello di Intelligenza Artificiale")
st.write("Di seguito il ragionamento e la decisione presa dall'algoritmo (Cashy-AI). Nessun *Responsible-AI statement* è mostrato per evitare pregiudizi cognitivi.")

col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.info("**Motivazione (Reasoning Engine)**")
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

with st.form(key=f"form_{indice}"):
    q_ragionamento = st.radio(
        "A) Ritieni che la **Motivazione (Reasoning)** fornita dall'AI sia coerente con i dati?",
        options=["Sì", "No"], index=None, horizontal=True
    )
    
    q_risposta = st.radio(
        "B) Condividi la **Raccomandazione Finale (Answer)** dell'AI per questo caso?",
        options=["Sì", "No"], index=None, horizontal=True
    )
    
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
            st.warning(" Devi rispondere a entrambe le domande (Sì/No) per procedere.")
        elif q_risposta == "No" and motivo_override == "Nessun disaccordo":
            st.warning(" Hai deciso di non condividere la decisione dell'AI. Devi selezionare un motivo di override dall'elenco.")
        else:
            st.session_state.df.at[indice, 'Accordo_Ragionamento'] = q_ragionamento
            st.session_state.df.at[indice, 'Accordo_Risposta'] = q_risposta
            st.session_state.df.at[indice, 'Motivo_Override'] = motivo_override if q_risposta == "No" else None
            
            st.session_state.current_index += 1
            st.rerun()
