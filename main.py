import threading
from utils import extract_language
from pathlib import Path
# === Background preloading to improve perceived startup ===
def preload_dependencies():
    try:
        import requests
        import bs4
        import reportlab
    except Exception:
        pass

# Run preload in background
threading.Thread(target=preload_dependencies, daemon=True).start()


def get_emico_data(url):
    """Scrape an Emico product page and return all relevant data."""
    import requests
    from bs4 import BeautifulSoup
    import re
    lang = extract_language(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    def get_images_links(soup):
        pattern = r"https://intellishop\.sirv\.com/[^\s\"'>]+"
        links = re.findall(pattern, response.text)
        clean_links = []
        for link in set(links):
            if ".jpg" in link.lower():
                link = link[: link.lower().find(".jpg") + 4]
            elif ".png" in link.lower():
                link = link[: link.lower().find(".png") + 4]
            clean_links.append(link)
        return list(set(clean_links))

    clean_links = get_images_links(soup)
    print(clean_links)
    def get_basic_info(soup):
        product_info = {}
        info_section = soup.select_one("div.col-lg-6.col-xl-8.ps-lg-4.ps-xl-5")
        if info_section:
            # --- product name ---
            name_tag = info_section.select_one("h1")
            if name_tag:
                product_info["product_name"] = name_tag.get_text(strip=True)
            # --- define regexes for each language ---
            if lang == 'de':
                artikel_regex = r"Artikel[-\s]?Nr\.\s*([0-9]+)"
                alt_artikel_regex = r"Alte\s+Artikelnummer:\s*([0-9]+)"
            elif lang == 'en':
                artikel_regex = r"Part\s*no\.?\s*([0-9]+)"
                alt_artikel_regex = r"Old\s*(item|part)\s*(number|no\.?):\s*([0-9]+)"
            elif lang == 'es':
                artikel_regex = r"N[º°]?\s*de\s*pieza\s*([0-9]+)"
                alt_artikel_regex = r"N[úu]mero\s+de\s+art[ií]culo\s+antiguo:\s*([0-9]+)"
            elif lang == 'fr':
                artikel_regex = r"No\.\s*d['’]article\s*([0-9]+)"
                alt_artikel_regex = r"ancien\s+num[ée]ro\s+d['’]article:\s*([0-9]+)"
            elif lang == 'it':
                artikel_regex = r"Articolo\s*n\.?\s*([0-9]+)"
                alt_artikel_regex = r"vecchio\s+numero\s+d['’]articolo:\s*([0-9]+)"
            else:
                # strict: don't proceed if unsupported
                raise ValueError(f"Unsupported language: {lang}")

            # --- artikel tag ---
            artikel_tag = info_section.find(
                "p",
                string=re.compile("|".join(["Artikel", "Part", "pieza", "article", "Articolo"]), re.I)
            )

            if artikel_tag:
                text = artikel_tag.get_text(strip=True)

                match = re.search(artikel_regex, text)
                if match:
                    product_info["artikelnummer"] = match.groups()[-1]  # works for both single/multiple groups

                match_alt = re.search(alt_artikel_regex, text)
                if match_alt:
                    product_info["alte_artikelnummer"] = match_alt.groups()[-1]

            # --- description ---
            desc_tag = info_section.select_one("div.is-detail-page__description p")
            if desc_tag:
                product_info["beschreibung"] = str(desc_tag)

        return product_info

    basic_info = get_basic_info(soup)

    def extract_specs(group_id):
        container = soup.select_one("div.container.my-3")
        specs = {}
        if not container:
            return specs
        group = container.select_one(f"div#{group_id}")
        if group:
            for row in group.select("div.row.is-flex-table__row"):
                cols = row.select("div")
                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True)
                    key = key[0].upper() + key[1:]
                    value = cols[1].get_text(strip=True)
                    specs[key] = value
        return specs

    base_specs = extract_specs("group-2")
    technical_specs = extract_specs("group-3")
    drawing_data = extract_specs("group-6")

    return basic_info, base_specs, technical_specs, drawing_data, clean_links, lang


# === Standalone Run Mode ===
if __name__ == "__main__":
    from pdf_generator import generate_emico_pdf

    print("🔹 Emico PDF Generator (Standalone Mode)")
    test_url = input("Enter Emico product URL: ").strip()

    if not test_url:
        print("❌ No URL entered.")
    else:
        print("⏳ Scraping product data...")
        try:
            basic_info, base_specs, technical_specs, drawing_data, clean_links,lang = get_emico_data(test_url)
            print(f"✅ Data fetched for: {basic_info.get('product_name', 'Unknown Product')}")
            print("🧾 Generating PDF...")
            save_path = input("Enter folder to save PDF (leave empty for default Downloads): ").strip()
            if not save_path:
                save_path = Path(r"G:\6Artikel\Datenblätter(Produkte)")

            generate_emico_pdf(
                basic_info,
                base_specs,
                technical_specs,
                drawing_data,
                clean_links,
                lang,
                save_folder=save_path
            )
            print("✅ PDF successfully created!")
        except Exception as e:
            print(f"❌ Error: {e}")
