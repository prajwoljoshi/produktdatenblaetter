import os
import io
import re
import datetime
from pathlib import Path
from utils import resource_path

def generate_emico_pdf(basic_info, base_specs, technical_specs, drawing_data, clean_links, lang, save_folder=None):

    import requests
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image,
        CondPageBreak,
    )
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader

    # === Save folder logic ===
    if save_folder is None:
        save_folder = Path.home() / "Downloads"
    else:
        save_folder = Path(save_folder).expanduser().resolve()

    os.makedirs(save_folder, exist_ok=True)
        # Filename suffix based on language
    filename_labels = {
        "de": "datenblatt_de",
        "en": "product-sheet_en",
        "fr": "fiche-technique_fr",
        "es": "hoja-tecnica_es",
        "it": "scheda-tecnica_it"
    }

    suffix = filename_labels.get(lang, "datenblatt_de")

    output_filename = os.path.join(
        save_folder,
        f"{basic_info.get('artikelnummer', 'emico_product')}_{suffix}.pdf"
    )

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=3 * cm,
        bottomMargin=2 * cm,
    )

    PAGE_WIDTH, PAGE_HEIGHT = A4
    story = []

    # === Styles ===
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CustomTitle", fontSize=20, leading=22, spaceAfter=3, alignment=1, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="CustomHeading", fontSize=14, leading=18, spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="CustomBodyText", fontSize=11, leading=14, alignment=4))

    # ============================================================
    #  FOOTER — CLEAN, FINAL, VERSION A
    # ============================================================
    def draw_header_footer(canvas_obj, doc_obj):

        # -----------------------------------------------------------------
        # LOGO
        # -----------------------------------------------------------------
        logo_path = resource_path("assets/emicologo.png")
        if os.path.exists(logo_path):
            logo_width, logo_height = 6.4 * cm, 2.6 * cm
            x_pos = (PAGE_WIDTH - logo_width) / 2
            y_pos = PAGE_HEIGHT - logo_height - 0.5 * cm
            canvas_obj.drawImage(
                logo_path,
                x_pos,
                y_pos,
                logo_width,
                logo_height,
                preserveAspectRatio=True,
                mask="auto",
            )

        page_num = canvas_obj.getPageNumber()
        last_page = doc.page

        # -----------------------------------------------------------------
        # CLEAN PRODUCT NAME (remove measurements)
        def clean_product_name(name: str) -> str:
            if not name:
                return ""

            # Remove parentheses and their contents
            name = re.sub(r"\([^)]*\)", "", name)

            # Remove dimension formats like 20x30, 5 x 10
            name = re.sub(r"\b\d+\s*[xX]\s*\d+\b", "", name)

            # Remove units like 20mm, 30 cm, 5 inch
            name = re.sub(r"\b\d+\s*(mm|cm|inch|in)\b", "", name, flags=re.I)

            # Remove standalone numbers
            name = re.sub(r"\b\d+\b", "", name)

            # Remove all punctuation including / - _ . ; : , etc
            name = re.sub(r"[^\w\s]", " ", name)

            # Collapse multiple spaces
            name = re.sub(r"\s+", " ", name)

            return name.strip()



        y_base = 1.0 * cm  # baseline for company info

        # -----------------------------------------------------------------
        # COMPANY INFO (existing logic)
        # -----------------------------------------------------------------
        if lang == 'en':
            footer_html = (
                "syskomp gehmeyr GmbH – Business Unit emico • "
                "Max-Planck-Straße 1 • 92224 Amberg • "
                "Phone: +49 9621 67545-0 • "
                '<a href="mailto:sales@emico.com">sales@emico.com</a> • '
                '<a href="https://www.emico.com/en-DE">www.emico.com/en-DE</a>'
            )
        elif lang == 'fr':
            footer_html = (
                "syskomp gehmeyr GmbH – Division emico • "
                "Max-Planck-Straße 1 • 92224 Amberg • "
                "Tél.: +49 9621 67545-0 • "
                '<a href="mailto:sales@emico.com">sales@emico.com</a> • '
                '<a href="https://www.emico.com/fr-DE">www.emico.com/fr-DE</a>'
            )
        elif lang == 'es':
            footer_html = (
                "syskomp gehmeyr GmbH – Unidad de Negocio emico • "
                "Max-Planck-Straße 1 • 92224 Amberg • "
                "Tel.: +49 9621 67545-0 • "
                '<a href="mailto:sales@emico.com">sales@emico.com</a> • '
                '<a href="https://www.emico.com/es-DE">www.emico.com/es-DE</a>'
            )
        elif lang == 'it':
            footer_html = (
                "syskomp gehmeyr GmbH – Divisione emico • "
                "Via Gerolamo Fracastoro 3 • 37010 Cavaion Veronese • "
                "Tel.: +39 045 7235605 • "
                '<a href="mailto:info@emico.it">info@emico.it</a> • '
                '<a href="https://www.emico.com/it-DE">www.emico.com/it-DE</a>'
            )
        else:
            footer_html = (
                "syskomp gehmeyr GmbH – Geschäftsbereich emico • "
                "Max-Planck-Straße 1 • 92224 Amberg • "
                "Tel.: +49 9621 67545-0 • "
                '<a href="mailto:sales@emico.com">sales@emico.com</a> • '
                '<a href="https://www.emico.com">www.emico.com</a>'
            )

        footer_style = ParagraphStyle("Footer", fontName="Helvetica", fontSize=6, alignment=1)
        p_company = Paragraph(footer_html, footer_style)
        w_company, h_company = p_company.wrap(PAGE_WIDTH - 5 * cm, 2 * cm)
        p_company.drawOn(canvas_obj, 2.5 * cm, y_base)

        # -----------------------------------------------------------------
        # DATENBLATT | Product | Version
        # -----------------------------------------------------------------
        datasheet_labels = {
            "de": "DATENBLATT",
            "en": "DATASHEET",
            "fr": "FICHE TECHNIQUE",
            "es": "HOJA TÉCNICA",
            "it": "SCHEDA TECNICA",
        }
        datasheet_word = datasheet_labels.get(lang, "DATENBLATT")

        product_name = clean_product_name(basic_info.get("product_name", ""))
        version_str = datetime.datetime.now().strftime("%m/%Y")

        header_text = f"{datasheet_word} | {product_name} | Version {version_str}"

        header_style = ParagraphStyle("FooterHeader", fontName="Helvetica", fontSize=7.5, alignment=1)
        p_header = Paragraph(header_text, header_style)
        w_head, h_head = p_header.wrap(PAGE_WIDTH - 5 * cm, 1 * cm)
        y_header = y_base + h_company + 1
        p_header.drawOn(canvas_obj, 2.5 * cm, y_header)

        # -----------------------------------------------------------------
        # LINE ABOVE DATENBLATT
        # -----------------------------------------------------------------
        y_line = y_header + h_head + 4
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(2.5 * cm, y_line, PAGE_WIDTH - 2.5 * cm, y_line)

        # -----------------------------------------------------------------
        # DISCLAIMER (last page only)
        # -----------------------------------------------------------------
        if page_num == last_page:
            disclaimer_texts = {
                "de": "Die Angaben in diesem Dokument erfolgen nach bestem Wissen, jedoch ohne Gewähr. Änderungen und Irrtümer sind vorbehalten.",
                "en": "The information in this document is provided to the best of our knowledge, but without guarantee. Changes and errors reserved.",
                "fr": "Les informations contenues dans ce document sont fournies au mieux de nos connaissances, mais sans garantie.",
                "es": "La información de este documento se proporciona según nuestro leal saber y entender, pero sin garantía.",
                "it": "Le informazioni contenute in questo documento sono fornite al meglio delle nostre conoscenze, ma senza garanzia."
            }

            disc_style = ParagraphStyle("Disc", fontName="Helvetica-Oblique", fontSize=7.5, alignment=1, textColor=colors.darkgrey)
            p_disc = Paragraph(disclaimer_texts.get(lang, disclaimer_texts["de"]), disc_style)
            w_disc, h_disc = p_disc.wrap(PAGE_WIDTH - 5 * cm, 2 * cm)
            p_disc.drawOn(canvas_obj, 2.5 * cm, y_line + h_disc - 12)
        # PAGE NUMBER
        page_labels = {
            "de": ("Seite", "von"),
            "en": ("Page", "of"),
            "fr": ("Page", "sur"),
            "es": ("Página", "de"),
            "it": ("Pagina", "di"),
        }

        label_page, label_of = page_labels.get(lang, ("Seite", "von"))

        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawRightString(
            PAGE_WIDTH - 2.5 * cm,
            0.8 * cm,
            f"{label_page} {page_num} {label_of} {last_page}",
        )

    # === Title ===
    title = basic_info.get("product_name", "Produktname unbekannt")
    story.append(Paragraph(f"<b>{title}</b>", styles["CustomTitle"]))
    story.append(Spacer(1, 0))

    # === Artikelnummer ===
    artikelnummer = basic_info.get("artikelnummer", "–")

    # --- language-based label dictionary ---
    artikel_labels = {
        "de": "Artikelnummer",
        "en": "Article Number",
        "fr": "Numéro d’article",
        "es": "Número de artículo",
        "it": "Numero articolo"
    }

    # --- choose label based on lang ---
    label = artikel_labels.get(lang, "Artikelnummer")  # default German if missing

    # --- add to story ---
    story.append(
        Paragraph(
            f"{label}: {artikelnummer}",
            ParagraphStyle(
                name="ArtikelnummerCentered",
                parent=styles["CustomBodyText"],
                alignment=1,  # center
            ),
        )
    )
    story.append(Spacer(1, 8))

    # === Helper to download and resize images ===
    def make_resized_image(img_url, max_width, max_height):
        try:
            resp = requests.get(img_url)
            img = ImageReader(io.BytesIO(resp.content))
            iw, ih = img.getSize()
            aspect = ih / iw
            if iw > max_width:
                iw = max_width
                ih = iw * aspect
            if ih > max_height:
                ih = max_height
                iw = ih / aspect
            img_obj = Image(io.BytesIO(resp.content), width=iw, height=ih)
            img_obj.hAlign = "CENTER"
            return img_obj
        except Exception as e:
            print(f"Error loading image {img_url}: {e}")
            return None

    # === Product images ===
    img_links = [l for l in clean_links if not re.search(r"_zg(?:_\d+)?\.(jpg|png)$", l, re.I)]

    img_links = img_links[:3]

    if img_links:
        max_total_width = PAGE_WIDTH - 5 * cm
        max_image_height = PAGE_HEIGHT / 6

        def load_resized_images(urls, target_width):
            imgs = []
            for link in urls:
                try:
                    resp = requests.get(link)
                    img = ImageReader(io.BytesIO(resp.content))
                    iw, ih = img.getSize()
                    aspect = ih / iw
                    width = target_width
                    height = width * aspect
                    if height > max_image_height:
                        height = max_image_height
                        width = height / aspect
                    img_obj = Image(io.BytesIO(resp.content), width=width, height=height)
                    img_obj.hAlign = "CENTER"
                    imgs.append(img_obj)
                except Exception as e:
                    print(f"Error loading image {link}: {e}")
            return imgs

        num_imgs = len(img_links)

    if num_imgs <= 3:
        target_width = (max_total_width / num_imgs) - 1 * cm
        imgs = load_resized_images(img_links, target_width)

        if imgs:
            # Create a 1-row table of images
            table = Table([imgs], hAlign="CENTER", spaceBefore=6, spaceAfter=6)

            # ✅ Real gaps only BETWEEN the images (not at edges)
            style_commands = [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]

            gap_size = 30  # points → roughly 7mm real visible space

            # Apply right padding to all but the last image
            for col in range(num_imgs - 1):
                style_commands.append(("RIGHTPADDING", (col, 0), (col, 0), gap_size))

            # No extra padding after the last image
            style_commands.append(("RIGHTPADDING", (num_imgs - 1, 0), (num_imgs - 1, 0), 0))

            table.setStyle(TableStyle(style_commands))
            story.append(table)
            story.append(Spacer(1, 12))


    # === Technische Daten ===
    technische_daten = {**base_specs, **technical_specs}

    if technische_daten:
        
        # Language-based translations for "Technical Data"
        technical_data_labels = {
            "de": "Technische Daten",
            "en": "Technical Data",
            "fr": "Données techniques",
            "es": "Datos técnicos",
            "it": "Dati tecnici"
        }

        # Pick correct translation based on lang variable
        tech_label = technical_data_labels.get(lang, "Technische Daten")

        # Add heading paragraph (same layout, just translated)
        story.append(
            Paragraph(f"<b>{tech_label}</b>", styles["CustomHeading"])
        )

        # language-based table header labels
        table_headers = {
            "de": ("Attribut", "Wert"),
            "en": ("Attribute", "Value"),
            "fr": ("Attribut", "Valeur"),
            "es": ("Atributo", "Valor"),
            "it": ("Attributo", "Valore")
        }

        # choose the correct pair based on lang
        attr_label, value_label = table_headers.get(lang, ("Attribut", "Wert"))

        # build the data table (same logic as before)
        data = [[attr_label, value_label]] + [[k, v] for k, v in technische_daten.items()]

        table = Table(
            data,
            colWidths=[(PAGE_WIDTH - 5 * cm) / 2, (PAGE_WIDTH - 5 * cm) / 2],
            hAlign="CENTER",
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 12))

    # === Beschreibung ===
    beschreibung = basic_info.get("beschreibung", "")

    if beschreibung.strip() and beschreibung.strip() != '<p></p>':
        # Replace <br> with <br/> for ReportLab compatibility
        beschreibung = beschreibung.replace("<br>", "<br/>")
        # Remove outer <p> tags, since ReportLab handles its own paragraphing
        beschreibung = beschreibung.replace("<p>", "").replace("</p>", "")
        
        # language-based translations for "Description"
        description_labels = {
            "de": "Beschreibung",
            "en": "Description",
            "fr": "Description",
            "es": "Descripción",
            "it": "Descrizione"
        }

        # pick the correct translation based on lang
        desc_label = description_labels.get(lang, "Beschreibung")

        # add heading to story (same ReportLab layout logic)
        story.append(
            Paragraph(f"<b>{desc_label}</b>", styles["CustomHeading"])
        )

        story.append(Paragraph(beschreibung, styles["CustomBodyText"]))



    story.append(CondPageBreak(PAGE_HEIGHT / 2))

    # === Zeichnung und Maßtabelle ===
    # language-based translations for "Drawing and Dimension Table"
    drawing_labels = {
        "de": "Zeichnung und Maßtabelle",
        "en": "Drawing and Dimension Table",
        "fr": "Dessin et tableau des dimensions",
        "es": "Dibujo y tabla de dimensiones",
        "it": "Disegno e tabella delle dimensioni"
    }

    # choose correct translation based on lang
    drawing_label = drawing_labels.get(lang, "Zeichnung und Maßtabelle")

    # add heading to story
    story.append(
        Paragraph(f"<b>{drawing_label}</b>", styles["CustomHeading"])
    )
    zg_links = [l for l in clean_links if re.search(r"_zg(?:_\d+)?\.(jpg|png)$", l, re.I)]
    if zg_links:
        zg_img = make_resized_image(zg_links[0], PAGE_WIDTH - 5 * cm, PAGE_HEIGHT / 5)
        if zg_img:
            story.append(zg_img)
            story.append(Spacer(1, 12))

    if drawing_data:
        data2 = [[attr_label, value_label]] + [[k, v] for k, v in drawing_data.items()]
        table2 = Table(
            data2,
            colWidths=[(PAGE_WIDTH - 5 * cm) / 2, (PAGE_WIDTH - 5 * cm) / 2],
            hAlign="CENTER",
        )
        table2.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ]
            )
        )
        story.append(table2)
        story.append(Spacer(1, 12))

    # === QR Code Section (aligned horizontally) ===

    # Example: choose QR path based on language

    if lang == 'en':
        qr_path = resource_path("assets/emico_qr_en.png")
    elif lang == 'fr':
        qr_path = resource_path("assets/emico_qr_fr.png")
    elif lang == 'it':
        qr_path = resource_path("assets/emico_qr_it.png")
    elif lang == 'es':
        qr_path = resource_path("assets/emico_qr_es.png")
    else:
        qr_path = resource_path("assets/emico_qr.png")

    if os.path.exists(qr_path):
        story.append(Spacer(1, 6))
        qr_img = Image(qr_path, width=3.5 * cm, height=3.5 * cm)
        qr_img.hAlign = "LEFT"
# language-based translations for the QR code text
        qr_texts = {
            "de": (
                "Scannen Sie den QR-Code, um weitere Artikel in dieser Kategorie zu entdecken.<br/><br/>"
                "Für eine individuelle Beratung freuen wir uns über Ihre E-Mail "
                "an <a href='mailto:sales@emico.com'>sales@emico.com</a> "
                "oder telefonisch unter +49 9621 67545-0."
            ),
            "en": (
                "Scan the QR code to discover more items in this category.<br/><br/>"
                "For personalized advice, feel free to contact us by email at "
                "<a href='mailto:sales@emico.com'>sales@emico.com</a> "
                "or by phone at +49 9621 67545-0."
            ),
            "fr": (
                "Scannez le code QR pour découvrir d'autres articles dans cette catégorie.<br/><br/>"
                "Pour un conseil personnalisé, contactez-nous par e-mail à "
                "<a href='mailto:sales@emico.com'>sales@emico.com</a> "
                "ou par téléphone au +49 9621 67545-0."
            ),
            "es": (
                "Escanee el código QR para descubrir más artículos en esta categoría.<br/><br/>"
                "Para recibir asesoramiento personalizado, puede escribirnos a "
                "<a href='mailto:sales@emico.com'>sales@emico.com</a> "
                "o llamarnos al +49 9621 67545-0."
            ),
            "it": (
                "Scansiona il codice QR per scoprire altri articoli in questa categoria.<br/><br/>"
                "Per una consulenza personalizzata, contattaci via e-mail a "
                "<a href='mailto:info@emico.it'>info@emico.it</a> "
                "oppure telefonicamente al +39 045 7235605."
            )
        }

        # choose correct text based on lang
        qr_text = qr_texts.get(lang, qr_texts["de"])

        qr_para = Paragraph(qr_text, styles["CustomBodyText"])

        # box around text only
        qr_text_box = Table(
            [[qr_para]],
            colWidths=[PAGE_WIDTH - 5 * cm - 4 * cm],
            hAlign="LEFT",
        )
        qr_text_box.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        # align QR and text horizontally
        qr_table = Table(
            [[qr_img, qr_text_box]],
            colWidths=[4 * cm, PAGE_WIDTH - 5 * cm - 4 * cm],
            hAlign="CENTER",
        )
        qr_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(qr_table)
        story.append(Spacer(1, 20))

    def on_first_page(canvas_obj, doc_obj):
        draw_header_footer(canvas_obj, doc_obj)

    def on_later_pages(canvas_obj, doc_obj):
        draw_header_footer(canvas_obj, doc_obj)

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f"✅ PDF successfully created: {output_filename}")
