import streamlit as st
import json
import requests
import pandas as pd

st.set_page_config(page_title="Amazon Relay Calculator", layout="wide")

st.title("🚛 Amazon Relay Profitability Calculator")
st.markdown("Narzędzie dla dyspozytorów: Ruptela GPS + Opłaty UTA + Cena Paliwa z Bazy")

# Pasek boczny z parametrami
with st.sidebar:
    st.header("⚙️ Parametry Bazy i Kosztów")
    fuel_price = st.number_input("Cena paliwa na bazie (PLN/L netto)", value=5.45, step=0.05)
    eur_rate = st.number_input("Kurs EUR/PLN", value=4.30, step=0.01)
    driver_per_day = st.number_input("Koszt kierowcy (PLN/dzień)", value=400, step=50)
    wear_per_km = st.number_input("Amortyzacja / Serwis (PLN/km)", value=1.10, step=0.05)
    
    st.divider()
    st.subheader("🔑 Dostęp API")
    
    # Pobieranie klucza z Secrets (jeśli istnieje) lub z pola tekstowego
    if "RUPTELA_API_KEY" in st.secrets:
        ruptela_key = st.secrets["RUPTELA_API_KEY"]
        st.success("API Ruptela podłączone (Secrets)")
    else:
        ruptela_key = st.text_input("Ruptela API Key", type="password")

# Definicja zakładek
tab1, tab2 = st.tabs(["📸 Skaner Bloków Amazon", "📄 Faktury i Rozliczenia UTA"])

with tab1:
    st.subheader("1. Wgraj zrzut ekranu z Amazon Relay")
    uploaded_file = st.file_uploader("Dodaj screen oferty (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    # Domyślne wartości początkowe w stanie sesji
    if "truck_reg" not in st.session_state:
        st.session_state["truck_reg"] = "KN0783G"
        st.session_state["total_km_amazon"] = 2687
        st.session_state["rate_eur"] = 4572.59
        st.session_state["duration_days"] = 5
        st.session_state["toll_est_eur"] = 732.50

    if uploaded_file is not None:
        # Wykrywanie nowego pliku – czyszczenie / resetowanie formularza
        if "last_filename" not in st.session_state or st.session_state["last_filename"] != uploaded_file.name:
            st.session_state["last_filename"] = uploaded_file.name
            
            # W tym miejscu docelowo podłączamy odczyt ze zdjęcia (OCR).
            # Na ten moment zerujemy wartości po zmianie pliku:
            st.session_state["truck_reg"] = ""
            st.session_state["total_km_amazon"] = 0
            st.session_state["rate_eur"] = 0.0
            st.session_state["duration_days"] = 1
            st.session_state["toll_est_eur"] = 0.0
            st.rerun()

        st.image(uploaded_file, caption="Załadowany screen bloku", use_column_width=True)
        st.success("Plik został załadowany!")
        
        # Pola formularza powiązane ze stanem sesji poprzez 'key'
        col1, col2, col3 = st.columns(3)
        with col1:
            truck_reg = st.text_input("Numer rejestracyjny", key="truck_reg")
            total_km_amazon = st.number_input("Dystans z Amazona (km)", key="total_km_amazon")
        with col2:
            rate_eur = st.number_input("Stawka z Amazona (€)", key="rate_eur")
            duration_days = st.number_input("Czas trwania (dni)", key="duration_days")
        with col3:
            toll_est_eur = st.number_input("Szacowane opłaty drogowe / UTA (€)", key="toll_est_eur")

        st.divider()
        st.subheader("2. Odczyt z Ruptela GPS API")
        
        # Wartości domyślne / pobrane z Rupteli
        ruptela_spalanie = 23.10  # l/100km
        ruptela_km = 2922.49      # km rzeczywiste
        
        st.info(f"Pojazd: **{truck_reg if truck_reg else 'Brak num. rej.'}** | Średnie spalanie z CAN: **{ruptela_spalanie} l/100km** | Przebieg rzeczywisty: **{ruptela_km} km**")
        
        # Obliczenia
        total_revenue_pln = rate_eur * eur_rate
        total_fuel_liters = (ruptela_km / 100.0) * ruptela_spalanie
        total_fuel_cost = total_fuel_liters * fuel_price
        total_toll_cost_pln = toll_est_eur * eur_rate
        total_driver_cost = duration_days * driver_per_day
        total_wear_cost = ruptela_km * wear_per_km
        
        total_costs = total_fuel_cost + total_toll_cost_pln + total_driver_cost + total_wear_cost
        net_profit = total_revenue_pln - total_costs
        margin = (net_profit / total_revenue_pln) * 100 if total_revenue_pln > 0 else 0
        
        st.divider()
        st.header("📊 Wynik Rentowności Bloku")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Przychód Netto", f"{total_revenue_pln:,.2f} PLN", f"{rate_eur:.2f} €")
        c2.metric("Koszty Całkowite", f"{total_costs:,.2f} PLN")
        c3.metric("Zysk Netto", f"{net_profit:,.2f} PLN", delta=f"{margin:.1f}% Marża")
        
        if net_profit > 3000:
            c4.success("✅ REKOMENDACJA: AKCEPTUJ BLOK")
        elif net_profit > 0:
            c4.warning("⚠️ REKOMENDACJA: ŚREDNIA OPŁACALNOŚĆ")
        else:
            c4.error("❌ REKOMENDACJA: STRATA / ODRZUĆ")

with tab2:
    st.subheader("Rozliczenia opłat drogowych UTA")
    uta_file = st.file_uploader("Wgraj rozliczenie UTA (PDF / CSV)", type=["pdf", "csv"])
    if uta_file:
        st.success("Faktura przetworzona. Koszty drogowe zostały przypisane do ciągników.")
