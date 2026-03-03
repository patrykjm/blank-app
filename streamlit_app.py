import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
from datetime import datetime, timedelta

# ================== HASŁO (ZAHASHOWANE) ==================
# ←←← Wklej tutaj cały hash z bcrypt-generator.com
PASSWORD_HASH = b'$2b$12$$2a$12$FIF6xjXSRIsDsmj4AFzHqOPRWqNOyXAmlZXk6KDY/WHiB4CgvQUui$...'

# ================== LOGOWANIE ==================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Prywatny Dziennik Jedzenia")
    st.markdown("**Tylko Ty masz dostęp** – podaj hasło")

    password = st.text_input("Hasło", type="password", placeholder="Wpisz hasło...")

    if st.button("🔑 Zaloguj się", type="primary", use_container_width=True):
        if bcrypt.checkpw(password.encode('utf-8'), PASSWORD_HASH):
            st.session_state.logged_in = True
            st.success("✅ Zalogowano pomyślnie!")
            st.rerun()
        else:
            st.error("❌ Nieprawidłowe hasło!")
    st.stop()   # zatrzymuje dalsze wykonywanie

# ================== GŁÓWNA APLIKACJA (po zalogowaniu) ==================
st.title("🍔 Mój prywatny dziennik jedzenia")
st.markdown("Wszystko jest prywatne i tylko Ty to widzisz.")

# Przycisk wylogowania w sidebarze
if st.sidebar.button("🚪 Wyloguj się"):
    st.session_state.logged_in = False
    st.rerun()

# Połączenie z bazą
conn = sqlite3.connect('recenzje.db', check_same_thread=False)

# === FORMULARZ DODAWANIA RECENZJI (Twój poprzedni kod) ===
with st.form("recenzja"):
    restauracja = st.text_input("Nazwa lokalu", placeholder="Kebab u Ahmeda #3")
    
    col1, col2 = st.columns(2)
    with col1:
        smak = st.checkbox("Czy jedzenie **smakowało**? 😋")
        porcja = st.checkbox("Czy **porcja była duża**? 🍽️")
        cena_ok = st.checkbox("Czy **cena vs jakość OK**? 💰")
    with col2:
        obsluga = st.checkbox("Czy **obsługa była dobra**? 👌")
        czystosc = st.checkbox("Czy **lokal był czysty**? ✨")
    
    komentarz = st.text_area("Komentarz (opcjonalnie)")
    
    submitted = st.form_submit_button("✅ Zapisz recenzję", type="primary")
    
    if submitted:
        nowa = {
            "data": datetime.now().isoformat(),
            "restauracja": restauracja or "Anonim",
            "smak": int(smak),
            "porcja": int(porcja),
            "cena_ok": int(cena_ok),
            "obsluga": int(obsluga),
            "czystosc": int(czystosc),
            "komentarz": komentarz
        }
        pd.DataFrame([nowa]).to_sql('recenzje', conn, if_exists='append', index=False)
        st.success("Recenzja zapisana! 🎉")
        st.rerun()

# === DASHBOARD Z USUWANIEM (ostatnia działająca wersja) ===
st.divider()
st.subheader("📜 Historia Twoich recenzji")

df = pd.read_sql_query("""
    SELECT id, data, restauracja, smak, porcja, cena_ok, obsluga, czystosc, komentarz 
    FROM recenzje 
    ORDER BY data DESC
""", conn)

if df.empty:
    st.info("Jeszcze nie masz recenzji – dodaj pierwszą powyżej!")
else:
    for _, row in df.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{row['data'][:16]}** — **{row['restauracja']}**")
                st.write(f"Smak: **{'✅ Tak' if row['smak'] else '❌ Nie'}** | "
                         f"Porcja: **{'✅ Tak' if row['porcja'] else '❌ Nie'}** | "
                         f"Cena: **{'✅ Tak' if row['cena_ok'] else '❌ Nie'}**")
                st.write(f"Obsługa: **{'✅ Tak' if row['obsluga'] else '❌ Nie'}** | "
                         f"Czystość: **{'✅ Tak' if row['czystosc'] else '❌ Nie'}**")
                if row['komentarz']:
                    st.caption(f"Komentarz: {row['komentarz']}")
            with col2:
                if st.button("🗑 Usuń", key=f"del_{row['id']}"):
                    conn.execute("DELETE FROM recenzje WHERE id = ?", (row['id'],))
                    conn.commit()
                    st.success("Usunięto!")
                    st.rerun()

st.caption(f"Łącznie recenzji: **{len(df)}**")