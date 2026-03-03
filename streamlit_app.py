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

# === NAJSTABILNIEJSZA WERSJA USUWANIA ===
st.divider()
st.subheader("📜 Historia Twoich recenzji")

df = pd.read_sql_query("""
    SELECT id, data, restauracja, smak, porcja, cena_ok, obsluga, czystosc, komentarz 
    FROM recenzje 
    ORDER BY data DESC
""", conn)

if df.empty:
    st.info("Jeszcze nie masz żadnych recenzji. Dodaj pierwszą powyżej! 🍔")
else:
    for _, row in df.iterrows():
        with st.container(border=True):   # ładna ramka wokół każdej recenzji
            col1, col2 = st.columns([6, 1])
            
            with col1:
                st.markdown(f"**{row['data'][:16]}** — **{row['restauracja']}**")
                st.write(f"Smakowało: **{'✅ Tak' if row['smak'] else '❌ Nie'}** | "
                         f"Duża porcja: **{'✅ Tak' if row['porcja'] else '❌ Nie'}** | "
                         f"Cena OK: **{'✅ Tak' if row['cena_ok'] else '❌ Nie'}**")
                st.write(f"Obsługa: **{'✅ Tak' if row['obsluga'] else '❌ Nie'}** | "
                         f"Czystość: **{'✅ Tak' if row['czystosc'] else '❌ Nie'}**")
                if row['komentarz']:
                    st.caption(f"Komentarz: {row['komentarz']}")
            
            with col2:
                if st.button("🗑 Usuń", key=f"delete_{row['id']}", type="secondary"):
                    try:
                        conn.execute("DELETE FROM recenzje WHERE id = ?", (row['id'],))
                        conn.commit()
                        st.success(f"Usunięto recenzję z {row['data'][:10]}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Błąd: {e}")
                        conn.rollback()

    # Dodatkowa statystyka na dole
    st.caption(f"Łącznie recenzji: **{len(df)}**")