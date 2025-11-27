import pandas as pd
import requests
import re
sprache = 'de'
file = pd.ExcelFile("Importvorlage_aktuell.xlsx")
link_file = pd.ExcelFile("Mappe1.xlsx")
article_df = pd.read_excel(file, sheet_name = "neue Teilenummern")
link_df = pd.read_excel(link_file, sheet_name='url')
artikels = article_df['TeileNr']

def generate_all(artikels):
    for number in artikels[:5]:
        match = link_df.loc[link_df['Spalte1'] == str(number).strip(),'loc']
        print(number, match.iloc[0],type(match.iloc[0]))
        # If a row is found
        if match.empty:
            # Example: get a specific column, e.g. 'loc
            print(f"No loc found for {number}")


generate_all(artikels)


