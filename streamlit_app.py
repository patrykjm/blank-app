import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3  # na start, potem zamienisz na DynamoDB

# Połączenie z DB
conn = sqlite3.connect('recenzje.db', check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS recenzje (
    id INTEGER PRIMARY KEY,
    data TEXT,
    restauracja TEXT,
    smak INTEGER,
    porcja INTEGER,
    cena_ok INTEGER,
    obsluga INTEGER,
    czystosc INTEGER,
    komentarz TEXT
)""")

st.title("🍔 Szybka Recenzja Jedzenia")
st.markdown("### Zajęło Ci to **15 sekund** – dzięki!")

with st.form("recenzja"):
    restauracja = st.text_input("Nazwa lokalu / stolik", placeholder="Kebab u Ahmeda #3")
    
    col1, col2 = st.columns(2)
    with col1:
        smak = st.checkbox("Czy jedzenie **smakowało**? 😋")
        porcja = st.checkbox("Czy **porcja była duża**? 🍽️")
        cena_ok = st.checkbox("Czy **cena vs jakość OK**? 💰")
    with col2:
        obsluga = st.checkbox("Czy **obsługa była dobra**? 👌")
        czystosc = st.checkbox("Czy **lokal był czysty**? ✨")
    
    komentarz = st.text_area("Komentarz (opcjonalnie)", placeholder="Pyszny kebab, ale sos za ostry 🔥")
    
    submitted = st.form_submit_button("✅ Wyślij recenzję", type="primary")
    
    if submitted:
        nowa_recenzja = {
            "data": datetime.now().isoformat(),
            "restauracja": restauracja or "Anonim",
            "smak": int(smak),
            "porcja": int(porcja),
            "cena_ok": int(cena_ok),
            "obsluga": int(obsluga),
            "czystosc": int(czystosc),
            "komentarz": komentarz
        }
        pd.DataFrame([nowa_recenzja]).to_sql('recenzje', conn, if_exists='append', index=False)
        st.success("Dzięki! Recenzja zapisana 🎉")
        st.balloons()

# Dashboard (widoczny tylko dla Ciebie / admina)
st.subheader("📊 Twoje recenzje")
df = pd.read_sql("SELECT * FROM recenzje ORDER BY data DESC", conn)
st.dataframe(df, use_container_width=True)

# Proste statystyki
if not df.empty:
    st.metric("Średni % 'tak' dla smaku", f"{df['smak'].mean()*100:.0f}%")
    st.bar_chart(df[['smak', 'porcja', 'cena_ok', 'obsluga', 'czystosc']].mean())