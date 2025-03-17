import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import time
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="Il Casino GSOM", page_icon="🎰", layout="wide")

# Inizializzazione delle variabili di stato della sessione
if 'saldo' not in st.session_state:
    st.session_state.saldo = 1000
if 'storico_partite' not in st.session_state:
    st.session_state.storico_partite = pd.DataFrame(columns=['Timestamp', 'Gioco', 'Scommessa', 'Importo', 'Risultato', 'Vincita'])
if 'gioco_selezionato' not in st.session_state:
    st.session_state.gioco_selezionato = None
if 'mostra_statistiche' not in st.session_state:
    st.session_state.mostra_statistiche = False

# Funzione per aggiornare lo storico delle partite
def aggiorna_storico(gioco, scommessa, importo, risultato, vincita):
    nuova_partita = pd.DataFrame({
        'Timestamp': [datetime.now()],
        'Gioco': [gioco],
        'Scommessa': [scommessa],
        'Importo': [importo],
        'Risultato': [risultato],
        'Vincita': [vincita]
    })
    st.session_state.storico_partite = pd.concat([st.session_state.storico_partite, nuova_partita], ignore_index=True)
    st.session_state.saldo += vincita

# Funzioni per la Roulette
def estrai_numero_roulette():
    return random.randint(0, 36)

def calcola_vincita_roulette(numero_estratto, scommessa, importo):
    risultato = str(numero_estratto)
    vincita = -importo  # Di default, perdi l'importo scommesso
    
    # Controlla il tipo di scommessa e calcola la vincita
    if scommessa == "rosso" and numero_estratto in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
        vincita = importo  # Vincita 1:1
    elif scommessa == "nero" and numero_estratto in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]:
        vincita = importo  # Vincita 1:1
    elif scommessa == "pari" and numero_estratto % 2 == 0 and numero_estratto != 0:
        vincita = importo  # Vincita 1:1
    elif scommessa == "dispari" and numero_estratto % 2 == 1:
        vincita = importo  # Vincita 1:1
    elif scommessa == "1-18" and 1 <= numero_estratto <= 18:
        vincita = importo  # Vincita 1:1
    elif scommessa == "19-36" and 19 <= numero_estratto <= 36:
        vincita = importo  # Vincita 1:1
    elif scommessa == "1a dozzina" and 1 <= numero_estratto <= 12:
        vincita = importo * 2  # Vincita 2:1
    elif scommessa == "2a dozzina" and 13 <= numero_estratto <= 24:
        vincita = importo * 2  # Vincita 2:1
    elif scommessa == "3a dozzina" and 25 <= numero_estratto <= 36:
        vincita = importo * 2  # Vincita 2:1
    elif scommessa.isdigit() and int(scommessa) == numero_estratto:
        vincita = importo * 35  # Vincita 35:1
    
    return risultato, vincita

def gioca_roulette():
    st.subheader("🎡 Roulette")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write(f"Saldo attuale: €{st.session_state.saldo}")
        importo = st.number_input("Importo della scommessa (€)", min_value=1, max_value=st.session_state.saldo, value=10)
        
        opzioni_scommessa = [
            "rosso", "nero", "pari", "dispari", "1-18", "19-36",
            "1a dozzina", "2a dozzina", "3a dozzina"
        ] + [str(i) for i in range(0, 37)]
        
        scommessa = st.selectbox("Scegli su cosa scommettere", opzioni_scommessa)
        
        if st.button("Gira la Ruota"):
            with st.spinner("La ruota gira..."):
                time.sleep(1)  # Aggiunge suspense
                numero_estratto = estrai_numero_roulette()
                risultato, vincita = calcola_vincita_roulette(numero_estratto, scommessa, importo)
                
                # Aggiorna lo storico
                aggiorna_storico("Roulette", scommessa, importo, risultato, vincita)
                
                # Mostra il risultato
                st.success(f"Numero estratto: {risultato}")
                if vincita > 0:
                    st.balloons()
                    st.success(f"Hai vinto €{vincita}! Nuovo saldo: €{st.session_state.saldo}")
                else:
                    st.error(f"Hai perso €{abs(vincita)}. Nuovo saldo: €{st.session_state.saldo}")

# Funzioni per il Blackjack
def crea_mazzo():
    semi = ['♠', '♥', '♦', '♣']
    valori = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    mazzo = []
    
    for seme in semi:
        for valore in valori:
            carta = {'valore': valore, 'seme': seme}
            mazzo.append(carta)
    
    random.shuffle(mazzo)
    return mazzo

def valore_carta(carta):
    if carta['valore'] in ['J', 'Q', 'K']:
        return 10
    elif carta['valore'] == 'A':
        return 11  # L'asso vale 11 di default (poi si può cambiare a 1 se necessario)
    else:
        return int(carta['valore'])

def calcola_punteggio(mano):
    punteggio = sum(valore_carta(carta) for carta in mano)
    
    # Se il punteggio supera 21 e ci sono assi, contiamo gli assi come 1 invece di 11
    assi = sum(1 for carta in mano if carta['valore'] == 'A')
    while punteggio > 21 and assi > 0:
        punteggio -= 10
        assi -= 1
    
    return punteggio

def mostra_carte(mano, titolo):
    carte_str = ""
    for carta in mano:
        carte_str += f"{carta['valore']}{carta['seme']} "
    
    st.write(f"{titolo}: {carte_str} (Punteggio: {calcola_punteggio(mano)})")

def gioca_blackjack():
    st.subheader("♠️ Blackjack")
    
    # Inizializza le variabili di gioco
    if 'mazzo' not in st.session_state:
        st.session_state.mazzo = crea_mazzo()
    if 'mano_giocatore' not in st.session_state:
        st.session_state.mano_giocatore = []
    if 'mano_banco' not in st.session_state:
        st.session_state.mano_banco = []
    if 'gioco_in_corso' not in st.session_state:
        st.session_state.gioco_in_corso = False
    if 'importo_scommessa' not in st.session_state:
        st.session_state.importo_scommessa = 10
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write(f"Saldo attuale: €{st.session_state.saldo}")
        
        if not st.session_state.gioco_in_corso:
            # Inizio del gioco
            importo = st.number_input("Importo della scommessa (€)", min_value=1, max_value=st.session_state.saldo, value=10)
            
            if st.button("Nuova Partita"):
                # Resetta il gioco
                st.session_state.mazzo = crea_mazzo()
                st.session_state.mano_giocatore = []
                st.session_state.mano_banco = []
                st.session_state.gioco_in_corso = True
                st.session_state.importo_scommessa = importo
                
                # Distribuisci le prime carte
                st.session_state.mano_giocatore.append(st.session_state.mazzo.pop())
                st.session_state.mano_banco.append(st.session_state.mazzo.pop())
                st.session_state.mano_giocatore.append(st.session_state.mazzo.pop())
                st.session_state.mano_banco.append(st.session_state.mazzo.pop())
        else:
            # Gioco in corso
            mostra_carte(st.session_state.mano_giocatore, "Le tue carte")
            
            # Mostra solo la prima carta del banco
            st.write(f"Carta visibile del banco: {st.session_state.mano_banco[0]['valore']}{st.session_state.mano_banco[0]['seme']}")
            
            punteggio_giocatore = calcola_punteggio(st.session_state.mano_giocatore)
            
            # Controlla se il giocatore ha un blackjack (21 con le prime due carte)
            if punteggio_giocatore == 21 and len(st.session_state.mano_giocatore) == 2:
                st.success("Blackjack! Hai 21!")
                st.session_state.gioco_in_corso = False
                
                # Mostra tutte le carte del banco
                mostra_carte(st.session_state.mano_banco, "Carte del banco")
                
                punteggio_banco = calcola_punteggio(st.session_state.mano_banco)
                
                # Se anche il banco ha un blackjack, è un pareggio
                if punteggio_banco == 21 and len(st.session_state.mano_banco) == 2:
                    st.info("Il banco ha anche un Blackjack. Pareggio!")
                    aggiorna_storico("Blackjack", "Blackjack", st.session_state.importo_scommessa, "Pareggio", 0)
                else:
                    vincita = int(st.session_state.importo_scommessa * 1.5)
                    st.success(f"Hai vinto €{vincita}!")
                    aggiorna_storico("Blackjack", "Blackjack", st.session_state.importo_scommessa, "Blackjack", vincita)
                
                if st.button("Nuova Partita", key="new_game_blackjack"):
                    st.session_state.gioco_in_corso = False
            
            elif punteggio_giocatore > 21:
                st.error("Hai sballato! Hai perso.")
                st.session_state.gioco_in_corso = False
                
                # Mostra tutte le carte del banco
                mostra_carte(st.session_state.mano_banco, "Carte del banco")
                
                aggiorna_storico("Blackjack", "Sballato", st.session_state.importo_scommessa, "Perso", -st.session_state.importo_scommessa)
                
                if st.button("Nuova Partita", key="new_game_bust"):
                    st.session_state.gioco_in_corso = False
            
            else:
                col_hit, col_stand = st.columns(2)
                
                with col_hit:
                    if st.button("Chiedi carta", key="hit"):
                        st.session_state.mano_giocatore.append(st.session_state.mazzo.pop())
                
                with col_stand:
                    if st.button("Stai", key="stand"):
                        # Il banco gioca
                        mostra_carte(st.session_state.mano_banco, "Carte del banco")
                        
                        # Il banco pesca carte finché non raggiunge almeno 17
                        while calcola_punteggio(st.session_state.mano_banco) < 17:
                            st.session_state.mano_banco.append(st.session_state.mazzo.pop())
                            mostra_carte(st.session_state.mano_banco, "Carte del banco")
                        
                        punteggio_banco = calcola_punteggio(st.session_state.mano_banco)
                        
                        # Determina il vincitore
                        if punteggio_banco > 21:
                            st.success("Il banco ha sballato! Hai vinto!")
                            aggiorna_storico("Blackjack", "Banco sballato", st.session_state.importo_scommessa, "Vinto", st.session_state.importo_scommessa)
                        elif punteggio_banco > punteggio_giocatore:
                            st.error(f"Il banco vince con {punteggio_banco} punti contro i tuoi {punteggio_giocatore}.")
                            aggiorna_storico("Blackjack", f"Perso {punteggio_giocatore} vs {punteggio_banco}", st.session_state.importo_scommessa, "Perso", -st.session_state.importo_scommessa)
                        elif punteggio_banco < punteggio_giocatore:
                            st.success(f"Hai vinto con {punteggio_giocatore} punti contro i {punteggio_banco} del banco!")
                            aggiorna_storico("Blackjack", f"Vinto {punteggio_giocatore} vs {punteggio_banco}", st.session_state.importo_scommessa, "Vinto", st.session_state.importo_scommessa)
                        else:
                            st.info(f"Pareggio a {punteggio_giocatore} punti.")
                            aggiorna_storico("Blackjack", f"Pareggio {punteggio_giocatore}", st.session_state.importo_scommessa, "Pareggio", 0)
                        
                        st.session_state.gioco_in_corso = False
                        
                        if st.button("Nuova Partita", key="new_game_after_stand"):
                            st.session_state.gioco_in_corso = False

# Funzioni di analisi statistica
def visualizza_statistiche():
    st.subheader("📊 Statistiche e Probabilità")
    
    if len(st.session_state.storico_partite) == 0:
        st.info("Gioca alcune partite per vedere le statistiche!")
        return
    
    tab1, tab2 = st.tabs(["Statistiche Generali", "Analisi Dettagliata"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Conteggio vittorie/perdite/pareggi
            risultati = st.session_state.storico_partite['Vincita'].apply(lambda x: 'Vittoria' if x > 0 else ('Pareggio' if x == 0 else 'Perdita'))
            conteggio_risultati = risultati.value_counts()
            
            # Grafico a torta dei risultati
            fig_pie = px.pie(
                values=conteggio_risultati.values,
                names=conteggio_risultati.index,
                title="Distribuzione dei Risultati",
                color=conteggio_risultati.index,
                color_discrete_map={'Vittoria': 'green', 'Perdita': 'red', 'Pareggio': 'blue'}
            )
            st.plotly_chart(fig_pie)
        
        with col2:
            # Profitto/perdita nel tempo
            df_profitto = st.session_state.storico_partite.copy()
            df_profitto['Profitto Cumulativo'] = df_profitto['Vincita'].cumsum()
            
            fig_line = px.line(
                df_profitto,
                x=df_profitto.index,
                y='Profitto Cumulativo',
                title="Andamento del Profitto nel Tempo",
                labels={'index': 'Partita', 'Profitto Cumulativo': 'Profitto (€)'},
            )
            st.plotly_chart(fig_line)
    
    with tab2:
        # Statistiche per gioco
        st.subheader("Statistiche per Gioco")
        
        giochi = st.session_state.storico_partite['Gioco'].unique()
        gioco_selezionato = st.selectbox("Seleziona un gioco", giochi)
        
        df_gioco = st.session_state.storico_partite[st.session_state.storico_partite['Gioco'] == gioco_selezionato]
        
        # Conteggio risultati per il gioco selezionato
        risultati_gioco = df_gioco['Vincita'].apply(lambda x: 'Vittoria' if x > 0 else ('Pareggio' if x == 0 else 'Perdita'))
        conteggio_risultati_gioco = risultati_gioco.value_counts().reset_index()
        conteggio_risultati_gioco.columns = ['Risultato', 'Conteggio']
        
        # Calcolo percentuali di vittoria
        totale_partite = len(df_gioco)
        vittorie = len(df_gioco[df_gioco['Vincita'] > 0])
        perdite = len(df_gioco[df_gioco['Vincita'] < 0])
        pareggi = len(df_gioco[df_gioco['Vincita'] == 0])
        
        percentuale_vittoria = (vittorie / totale_partite) * 100 if totale_partite > 0 else 0
        percentuale_perdita = (perdite / totale_partite) * 100 if totale_partite > 0 else 0
        percentuale_pareggio = (pareggi / totale_partite) * 100 if totale_partite > 0 else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Totale Partite", totale_partite)
            st.metric("Percentuale di Vittoria", f"{percentuale_vittoria:.2f}%")
            st.metric("Percentuale di Perdita", f"{percentuale_perdita:.2f}%")
            st.metric("Percentuale di Pareggio", f"{percentuale_pareggio:.2f}%")
        
        with col2:
            fig_bar = px.bar(
                conteggio_risultati_gioco,
                x='Risultato',
                y='Conteggio',
                title=f"Distribuzione dei Risultati - {gioco_selezionato}",
                color='Risultato',
                color_discrete_map={'Vittoria': 'green', 'Perdita': 'red', 'Pareggio': 'blue'}
            )
            st.plotly_chart(fig_bar)
        
        # Mostra la tabella dello storico per il gioco selezionato
        st.subheader(f"Storico Partite - {gioco_selezionato}")
        st.dataframe(df_gioco)

# Funzione principale dell'app
def main():
    st.title("🎰 Il Casino GSOM")
    
    # Mostra il saldo sempre visibile in alto
    col_saldo, col_reset, col_reset_stats = st.columns([3, 1, 1])
    with col_saldo:
        st.write(f"**Saldo attuale: €{st.session_state.saldo}**")
    with col_reset:
        if st.button("Reimposta Saldo", help="Reimposta il saldo a €1000"):
            st.session_state.saldo = 1000
    with col_reset_stats:
        if st.button("Azzera Statistiche", help="Cancella tutte le statistiche delle partite"):
            st.session_state.storico_partite = pd.DataFrame(columns=['Timestamp', 'Gioco', 'Scommessa', 'Importo', 'Risultato', 'Vincita'])
    
    # Disclaimer
    st.markdown("""
    **Benvenuto al Casino GSOM!** Qui puoi giocare a Roulette e Blackjack, 
    piazzare scommesse e analizzare le tue probabilità di vincita nel tempo.
    *Ricorda: il gioco è divertente solo quando è responsabile!*
    """)
    
    # Pulsanti di selezione del gioco nella parte superiore
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎡 ROULETTE", use_container_width=True, key="roulette_btn"):
            st.session_state.gioco_selezionato = "Roulette"
            st.session_state.mostra_statistiche = False
    
    with col2:
        if st.button("♠️ BLACKJACK", use_container_width=True, key="blackjack_btn"):
            st.session_state.gioco_selezionato = "Blackjack"
            st.session_state.mostra_statistiche = False
    
    with col3:
        if st.button("📊 STATISTICHE", use_container_width=True, key="stats_btn"):
            st.session_state.mostra_statistiche = True
            st.session_state.gioco_selezionato = None
    
    # Mostra un separatore
    st.markdown("---")
    
    # Mostra il gioco selezionato o le statistiche
    if st.session_state.mostra_statistiche:
        visualizza_statistiche()
    elif st.session_state.gioco_selezionato == "Roulette":
        gioca_roulette()
    elif st.session_state.gioco_selezionato == "Blackjack":
        gioca_blackjack()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")
        st.error("Dettagli completi dell'errore:")
        st.exception(e)
