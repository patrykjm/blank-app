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

# === DASHBOARD Z OPCJĄ USUWANIA ===
st.divider()
st.subheader("📜 Historia Twoich recenzji")

# Pobieramy dane z kolumną ID (potrzebne do usuwania)
df = pd.read_sql_query("""
    SELECT id, data, restauracja, smak, porcja, cena_ok, obsluga, czystosc, komentarz 
    FROM recenzje 
    ORDER BY data DESC
""", conn)

if df.empty:
    st.info("Jeszcze nie masz żadnych recenzji. Dodaj pierwszą powyżej! 🍔")
else:
    # Dodajemy kolumnę checkbox do zaznaczania
    df_display = df.copy()
    df_display['🗑 Usuń?'] = False   # nowa kolumna z checkboxami

    # Edytowalna tabela (można zaznaczać wiele wpisów naraz)
    edited_df = st.data_editor(
        df_display,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "data": st.column_config.TextColumn("Data", disabled=True),
            "restauracja": st.column_config.TextColumn("Lokal", disabled=True),
            "smak": st.column_config.CheckboxColumn("Smakowało?", disabled=True),
            "porcja": st.column_config.CheckboxColumn("Duża porcja?", disabled=True),
            "cena_ok": st.column_config.CheckboxColumn("Cena OK?", disabled=True),
            "obsluga": st.column_config.CheckboxColumn("Obsługa OK?", disabled=True),
            "czystosc": st.column_config.CheckboxColumn("Czysto?", disabled=True),
            "komentarz": st.column_config.TextColumn("Komentarz", disabled=True),
            "🗑 Usuń?": st.column_config.CheckboxColumn(
                "Zaznacz do usunięcia",
                help="Zaznacz recenzje, które chcesz usunąć",
                default=False,
            ),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
    )

    # Przycisk usuwania z potwierdzeniem
    if st.button("🗑 Usuń zaznaczone recenzje", type="primary"):
        # Pobieramy ID zaznaczonych wierszy
        ids_to_delete = edited_df[edited_df['🗑 Usuń?'] == True]['id'].tolist()
        
        if not ids_to_delete:
            st.warning("Nie zaznaczyłeś żadnej recenzji do usunięcia.")
        else:
            # Potwierdzenie
            st.warning(f"Na pewno chcesz usunąć **{len(ids_to_delete)}** recenzji? Tej operacji nie da się cofnąć!")
            col_yes, col_no = st.columns(2)
            if col_yes.button("Tak, usuń na zawsze", type="primary"):
                with st.spinner("Usuwam..."):
                    for rec_id in ids_to_delete:
                        conn.execute("DELETE FROM recenzje WHERE id = ?", (rec_id,))
                    conn.commit()
                st.success(f"Usunięto {len(ids_to_delete)} recenzji!")
                st.rerun()   # odświeża stronę automatycznie
            if col_no.button("Nie, anuluj"):
                st.info("Usuwanie anulowane.")

# Proste statystyki
if not df.empty:
    st.metric("Średni % 'tak' dla smaku", f"{df['smak'].mean()*100:.0f}%")
    st.bar_chart(df[['smak', 'porcja', 'cena_ok', 'obsluga', 'czystosc']].mean())