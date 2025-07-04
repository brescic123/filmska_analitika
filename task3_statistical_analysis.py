import pandas as pd

def analyze_online_store_data(file_path='online_store_data.csv'):
    """
    Vrši analizu podataka online trgovine na temelju zadatih pitanja.

    Args:
        file_path (str): Putanja do CSV datoteke sa podacima.

    Returns:
        None: Ispisuje rezultate analize na konzolu.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Uspješno učitana datoteka: {file_path}")
        print("\nPrvih 5 redova podataka:")
        print(df.head())
        print("\nInformacije o podacima:")
        df.info()
    except FileNotFoundError:
        print(f"Greška: Datoteka '{file_path}' nije pronađena. Molimo provjerite putanju.")
        return
    except Exception as e:
        print(f"Došlo je do greške prilikom učitavanja datoteke: {e}")
        return

    print("\n" + "="*50)
    print("Analiza podataka online trgovine")
    print("="*50)

    # 1. Kolika je prosječna ocjena proizvoda u online trgovini?
    if 'rating' in df.columns:
        prosjecna_ocjena = df['rating'].mean()
        print(f"\n1. Prosječna ocjena proizvoda u online trgovini: {prosjecna_ocjena:.2f}")
    else:
        print("\n1. Stupac 'rating' nije pronađen.")

    # 2. Koji je najčešći brend u online trgovini?
    if 'brand' in df.columns:
        najcesci_brend = df['brand'].mode()[0] # .mode() vraća Series, [0] uzima prvi element
        print(f"\n2. Najčešći brend u online trgovini: {najcesci_brend}")
    else:
        print("\n2. Stupac 'brand' nije pronađen.")
    # 3. Koji je najprodavaniji brend u online trgovini?
    if 'brand' in df.columns and 'quantity_sold' in df.columns:
        prodaja_po_brendu = df.groupby('brand')['quantity_sold'].sum().sort_values(ascending=False)
        najprodavaniji_brend = prodaja_po_brendu.index[0]
        print(f"\n3. Najprodavaniji brend u online trgovini: {najprodavaniji_brend} (Ukupna prodaja: {int(prodaja_po_brendu.iloc[0])})")
        print("\nTop 5 najprodavanijih brendova:")
        print(prodaja_po_brendu.head())
    else:
        print("\n3. Stupci 'brand' ili 'quantity_sold' nisu pronađeni.")
    # 4. Kolika je prosječna ocjena proizvoda po kategorijama?
    if 'category' in df.columns and 'rating' in df.columns:
        prosjecna_ocjena_po_kategoriji = df.groupby('category')['rating'].mean().sort_values(ascending=False)
        print("\n4. Prosječna ocjena proizvoda po kategorijama:")
        print(prosjecna_ocjena_po_kategoriji)
    else:
        print("\n4. Stupci 'category' ili 'rating' nisu pronađeni.")

    # 5. Kako izgleda popularnost proizvoda po bojama?
    if 'color' in df.columns and 'quantity_sold' in df.columns:
        popularnost_po_boji = df.groupby('color')['quantity_sold'].sum().sort_values(ascending=False)
        print("\n5. Popularnost proizvoda po bojama (ukupno prodanih):")
        print(popularnost_po_boji)
    else:
        print("\n5. Stupci 'color' ili 'quantity_sold' nisu pronađeni.")
    # 6. Koji su 5 najefikasnijih brendova po pitanju prodaje?
    required_cols_for_efficiency = ['brand', 'quantity_sold', 'quantity_in_stock']
    if all(col in df.columns for col in required_cols_for_efficiency):
        # Dobivanje 2 agregatne operacije
        agregirani_podaci = df.groupby('brand').agg(
            sumirane_kolicine_prodate=('quantity_sold', 'sum'),
            sumirane_kolicine_na_stanju=('quantity_in_stock', 'sum')
        ).reset_index()
    # Generiranje novih kolona
        # Broj prodatih primeraka = sumirane_kolicine_prodate
        agregirani_podaci['broj_prodanih_primjeraka'] = agregirani_podaci['sumirane_kolicine_prodate']
        # Broj_preroku_na_stanju = sumirane_kolicine_na_stanju - sumirane_kolicine_prodate (ako je > 0)
        agregirani_podaci['broj_preroku_na_stanju'] = agregirani_podaci['sumirane_kolicine_na_stanju'] - agregirani_podaci['sumirane_kolicine_prodate']
        agregirani_podaci['broj_preroku_na_stanju'] = agregirani_podaci['broj_preroku_na_stanju'].apply(lambda x: max(0, x)) # Osigurati da nije negativno        
    # Izračun efikasnosti
        # Efikasnost = (broj_prodanih_primjeraka + broj_preroku_na_stanju) / (broj_prodanih_primjeraka * broj_preroku_na_stanju)
        # Efikasnost = broj_prodanih_primjeraka / (broj_prodanih_primjeraka + broj_preroku_na_stanju)
        # Efkasnost = (broj_prodanih_primjeraka) / (broj_prodanih_primjeraka + broj_preroku_na_stanju) -> ovo je logičnije, veći udio prodanih je bolja efikasnost.
        # Formula: efikasnost = broj_prodatih_primjeraka / (broj_prodatih_primjeraka + broj_preroku_na_stanju)
        #  što znači:  `broj_prodatih_jedinica / (broj_prodatih_jedinica + broj_jedinica_na_stanju)`
        agregirani_podaci['efikasnost'] = agregirani_podaci.apply(
            lambda row: row['broj_prodanih_primjeraka'] / (row['broj_prodanih_primjeraka'] + row['broj_preroku_na_stanju'])
            if (row['broj_prodanih_primjeraka'] + row['broj_preroku_na_stanju']) > 0 else 0,
            axis=1
        )
    # Sortiranje i prikaz top 5 najefikasnijih
        najefikasniji_brendovi = agregirani_podaci.sort_values(by='efikasnost', ascending=False)
        print("\n6. Top 5 najefikasnijih brendova po pitanju prodaje:")
        print(najefikasniji_brendovi[['brand', 'efikasnost', 'broj_prodanih_primjeraka', 'broj_preroku_na_stanju']].head(5))
    else:
        print("\n6. Neki od potrebnih stupaca ('brand', 'quantity_sold', 'quantity_in_stock') za izračun efikasnosti nisu pronađeni.")

# Pozivanje funkcije za pokretanje analize
if __name__ == "__main__":
    analyze_online_store_data('online_store_data.csv')    