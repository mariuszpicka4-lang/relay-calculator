with tab1:
    st.subheader("1. Wgraj zrzut ekranu z Amazon Relay")
    uploaded_file = st.file_uploader("Dodaj screen oferty (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # Wykrywanie wgrania nowego pliku i resetowanie danych w sesji
        if "last_filename" not in st.session_state or st.session_state["last_filename"] != uploaded_file.name:
            st.session_state["last_filename"] = uploaded_file.name
            # Resetujemy pola, aby nie trzymać poprzedniej trasy
            st.session_state["truck_reg"] = ""
            st.session_state["total_km_amazon"] = 0
            st.session_state["rate_eur"] = 0.0
            st.session_state["duration_days"] = 1
            st.session_state["toll_est_eur"] = 0.0

        st.image(uploaded_file, caption="Załadowany screen bloku", use_column_width=True)
        st.success("Plik został załadowany!")
        
        # Pola formularza pobierające wartości ze stanu sesji (lub domyślne)
        col1, col2, col3 = st.columns(3)
        with col1:
            truck_reg = st.text_input("Numer rejestracyjny", value=st.session_state.get("truck_reg", "KN0783G"))
            total_km_amazon = st.number_input("Dystans z Amazona (km)", value=st.session_state.get("total_km_amazon", 2687))
        with col2:
            rate_eur = st.number_input("Stawka z Amazona (€)", value=st.session_state.get("rate_eur", 4572.59))
            duration_days = st.number_input("Czas trwania (dni)", value=st.session_state.get("duration_days", 5))
        with col3:
            toll_est_eur = st.number_input("Szacowane opłaty drogowe / UTA (€)", value=st.session_state.get("toll_est_eur", 732.50))

        st.divider()
        st.subheader("2. Odczyt z Ruptela GPS API")
        
        # Wartości domyślne / pobrane z Rupteli
        ruptela_spalanie = 23.10  # l/100km
        ruptela_km = 2922.49      # km rzeczywiste
        
        st.info(f"Pojazd: **{truck_reg}** | Średnie spalanie z CAN: **{ruptela_spalanie} l/100km** | Przebieg rzeczywisty: **{ruptela_km} km**")
        
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
