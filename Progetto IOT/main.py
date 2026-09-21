import math
import math
import matplotlib.pyplot as plt

def prompt_float(prompt_text, default_value):
    """Chiede un valore all'utente; se premuto invio, usa il valore predefinito."""
    user_val = input(f"{prompt_text} [Default: {default_value}]: ").strip()
    if not user_val:
        return float(default_value)
    return float(user_val)

def prompt_int(prompt_text, default_value):
    user_val = input(f"{prompt_text} [Default: {default_value}]: ").strip()
    if not user_val:
        return int(default_value)
    return int(user_val)

def genera_grafici(
    energia_usata_kwh, energia_surplus_kwh,
    ricavo_btc, capex, opex, profitto,
    btc_mined, salvage, btc_price
):
    """Genera i tre grafici basati sui risultati dei calcoli."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("GRAFICI DEI RISULTATI", fontsize=13, fontweight='bold')

    # --- 1. Grafico a Torta: Efficienza ed Energia ---
    labels_pie = ['Energia Utilizzata', 'Surplus Inutilizzato']
    sizes_pie = [energia_usata_kwh, max(0, energia_surplus_kwh)]
    colors_pie = ['#2ecc71', '#e74c3c']
    
    ax1.pie(sizes_pie, labels=labels_pie, autopct='%1.1f%%', colors=colors_pie, startangle=140)
    ax1.set_title("Utilizzo Energia Rinnovabile", fontweight='bold')

    # --- 2. Grafico a Barre: Flussi Economici ($M) ---
    v_ricavo = ricavo_btc / 1e6
    v_capex = capex / 1e6
    v_opex = opex / 1e6
    v_profit = profitto / 1e6
    
    categories = ['Ricavi BTC', 'CAPEX', 'OPEX', 'Netto']
    values = [v_ricavo, v_capex, v_opex, v_profit]
    colors_bar = ['#3498db', '#e67e22', '#9b59b6', '#2ecc71' if v_profit >= 0 else '#e74c3c']
    
    bars = ax2.bar(categories, values, color=colors_bar)
    ax2.set_ylabel("Milioni di USD ($M)")
    ax2.set_title("Breakdown Finanziario ($M)", fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0, yval,
            f"${yval:.2f}M",
            ha='center', va='bottom' if yval >= 0 else 'top', fontsize=9
        )

    # --- 3. Grafico a Linee: Sensibilità al Prezzo Bitcoin ---
    prezzi_simulati = [20000, 30000, 40000, 50000, 60000, 80000, 100000]
    if btc_price not in prezzi_simulati:
        prezzi_simulati.append(btc_price)
        prezzi_simulati.sort()
        
    profitti_simulati = [(btc_mined * p + salvage - capex - opex) / 1e6 for p in prezzi_simulati]
    
    ax3.plot(prezzi_simulati, profitti_simulati, marker='o', color='#f39c12', linewidth=2, label="Profitto Netto")
    
    # Linea tratteggiata di Break-Even con label aggiunta per la legenda
    ax3.axhline(0, color='red', linestyle='--', alpha=0.7, label="Break-Even (Pareggio)")
    
    # Evidenzia il punto con il prezzo inserito dall'utente
    ax3.plot(btc_price, v_profit, marker='*', color='red', markersize=12, label=f"Tuo Input (${btc_price:,.0f})")
    
    ax3.set_xlabel("Prezzo Bitcoin ($)")
    ax3.set_ylabel("Profitto Netto ($M)")
    ax3.set_title("Sensibilità Prezzo Bitcoin", fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend()

    plt.tight_layout()
    plt.show()


def main():
    print("=" * 65)
    print("   CALCOLATORE ESPERIMENTALE PROFITTO BITCOIN MINING + RINNOVABILI")
    print("   (Premi INVIO per confermare il valore di default consigliato)")
    print("=" * 65)

    # --- DATI DELL'IMPIANTO RINNOVABILE ---
    print("\n--- 1. SPECIFICHE IMPIANTO RINNOVABILE ---")
    tipo_impianto = input("Tipo di impianto (solar/wind) [Default: solar]: ").strip().lower() or "solar"
    capacità_impianto = prompt_float("Capacità nominale impianto (MW)", 250.0)
    durata_fase_pre_commerciale = prompt_float("Durata fase pre-commerciale (Ore, es. 4380 = 6 mesi, 8760 = 1 anno)", 8760.0)
    energia_tot_generata_kwh = prompt_float("Energia totale generata dall'impianto (kWh) per la durata del progetto", capacità_impianto * 1000 * durata_fase_pre_commerciale * 0.50)

    # --- DATI HARDWARE E COSTI INIZIALI (CAPEX) ---
    print("\n--- 2. HARDWARE MINING E COSTI INIZIALI ---")
    n_miners = prompt_int("Numero di ASIC Miner installati", 3528)
    costo_miner = prompt_float("Costo unitario singolo Miner ($)", 3395.0)
    consumo_miner_kw = prompt_float("Consumo di potenza medio singolo Miner (kW)", 3.25)
    potenza_hash_miner= prompt_float("Hashing power singolo Miner (TH/s)", 100.0)

    print("\n--- 3. SISTEMA DI RAFFREDDAMENTO AUSILIARIO ---")
    costo_pompa_calore = prompt_float("Costo unitario pompa di calore ($)", 300000.0)
    capacità_pompa_calor_kw = prompt_float("Capacità massima singola pompa di calore (kW)", 1000.0)
    cop = prompt_float("COP Pompa di calore (Coefficient of Performance)", 1.5)
    hf = prompt_float("Fattore di trasmissione calore (hf)", 0.38)

    # --- PARAMETRI DI MERCATO BITCOIN ---
    print("\n--- 4. MERCATO BITCOIN ---")
    btc_price = prompt_float("Prezzo medio stimato Bitcoin ($)", 47000.0)
    difficulty = prompt_float("Difficoltà media di rete (in Triliardi, es. 35 = 35e12)", 35.0)
    block_reward = prompt_float("Premio per blocco estratto (BTC)", 6.25)

    # --- CALCOLI FISICI ED ECONOMICI ---
    
    # Potenza totale richiesta dalla piattaforma di mining e raffreddamento (kW)
    potenza_miner_totale_kw = n_miners * consumo_miner_kw

    #I miner trasformano l'elettricità in calore. 
    #La quota di calore che deve essere rimossa attivamente dalle pompe è la potenza termica: potenza_miner_totale_kw*hf 
    potenza_pompe_kw = potenza_miner_totale_kw* (hf / cop)

    potenza_totale_mining_kw = potenza_miner_totale_kw + potenza_pompe_kw
    if potenza_pompe_kw > 0:
        numero_pompe = math.ceil(potenza_pompe_kw / capacità_pompa_calor_kw) 
    else:
        numero_pompe = 0

    # Costi iniziali
    costo_iniziale_miners = n_miners * costo_miner
    costo_iniziale_pompe = numero_pompe * costo_pompa_calore
    costo_totale_iniziale = costo_iniziale_miners + costo_iniziale_pompe

    # Utilizzo energetico effettivo
    energia_totale_richiesta_kwh = potenza_totale_mining_kw * durata_fase_pre_commerciale
    if energia_totale_richiesta_kwh > 0:
        energia_utilizzata_kwh = min(energia_tot_generata_kwh, energia_totale_richiesta_kwh)
        active_ratio = energia_utilizzata_kwh / energia_totale_richiesta_kwh
    else:
        energia_utilizzata_kwh = 0.0
        active_ratio = 0.0
        
    energia_surplus_kwh = energia_tot_generata_kwh - energia_utilizzata_kwh

    # Bitcoin Estratti e Ricavi
    effective_hashrate = (n_miners * potenza_hash_miner) * active_ratio
    periodo_fase_pre_commerciale_s = durata_fase_pre_commerciale * 3600.0
    
    # Hashrate (in TH/s) e Difficoltà (in Triliardi) si elidono a vicenda
    btc_mined = (effective_hashrate * periodo_fase_pre_commerciale_s * block_reward) / (difficulty * (2**32))
    total_revenue_btc = btc_mined * btc_price

    vendita_pompe = 0.242 * costo_iniziale_pompe  # 24.2% valore residuo pompe di calore
    total_salvage = vendita_pompe

    # Costi Operativi 
    if potenza_totale_mining_kw > 0:
        energia_pompe_kwh = energia_utilizzata_kwh * (potenza_pompe_kw / potenza_totale_mining_kw)
        opfachp = 0.00207
    else:
        energia_pompe_kwh = 0.0
        opfachp = 0.0

    costo_operativo_pompe = energia_pompe_kwh * opfachp

    if tipo_impianto == "solar":
        opfac_renew = 22.64
    else:
        opfac_renew = 43.0

    costo_operativo_impianto = (capacità_impianto * 1000.0) * opfac_renew * (durata_fase_pre_commerciale / 8760.0)
    costo_operativo_totale = costo_operativo_pompe + costo_operativo_impianto

    # PROFITTO NETTO FINALE
    profitto_totale = total_revenue_btc + total_salvage - costo_totale_iniziale - costo_operativo_totale

    print("\n" + "=" * 65)
    print("                    REPORT DEI RISULTATI")
    print("=" * 65)
    print(f" Impianto: {capacità_impianto:.1f} MW ({tipo_impianto.upper()}) | Durata: {durata_fase_pre_commerciale:.0f} ore")
    print(f" Configurazione: {n_miners} Miner + {numero_pompe} Pompe di calore")
    print(f" Energia utilizzata (P_UTL)  : {energia_utilizzata_kwh:,.0f} kWh su {energia_tot_generata_kwh:,.0f} kWh generati")
    print(f" Tasso di utilizzo della farm: {active_ratio * 100:.2f}%")
    print(f" Energia sprecata (P_SURPLUS): {energia_surplus_kwh:,.0f} kWh ({(energia_surplus_kwh / energia_tot_generata_kwh) * 100:.2f}%)")
    print("-" * 65)
    print(f" [+] Bitcoin Estratti Totali : {btc_mined:.4f} BTC")
    print(f" [+] Ricavo Lordo Bitcoin    : ${total_revenue_btc:,.2f}")
    print(f" [+] Valore Vendita Pompe    : ${total_salvage:,.2f}")
    print(f" [-] Costi Iniziali          : ${costo_totale_iniziale:,.2f}  (Miner: ${costo_iniziale_miners:,.2f}, HP: ${costo_iniziale_pompe:,.2f})")
    print(f" [-] Costi Operativi         : ${costo_operativo_totale:,.2f}")
    print("-" * 65)
    
    if profitto_totale >= 0:
        print(f" PROFITTO NETTO FINALE  : +${profitto_totale:,.2f}  (PROGETTO REDDITIZIO)")
    else:
        print(f" PROFITTO NETTO FINALE  : -${abs(profitto_totale):,.2f}  (PROGETTO IN PERDITA)")
    print("=" * 65)

    genera_grafici(
        energia_usata_kwh=energia_utilizzata_kwh,
        energia_surplus_kwh=energia_surplus_kwh,
        ricavo_btc=total_revenue_btc,
        capex=costo_totale_iniziale,
        opex=costo_operativo_totale,
        profitto=profitto_totale,
        btc_mined=btc_mined,
        salvage=total_salvage,
        btc_price=btc_price
    )

if __name__ == "__main__":
    main()