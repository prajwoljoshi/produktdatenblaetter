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


    # === Filename suffix ===
    filename_labels = {
        "de": "Datenblatt_de",
        "en": "Productsheet_en",
        "fr": "FicheDeDonnées_fr",
        "es": "FichaDeDatos_es",
        "it": "SchedaDati_it"
    }
    suffix = filename_labels.get(lang, "Datenblatt_de")

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
    styles.add(ParagraphStyle(name="CustomTitle",
                              fontSize=20,
                              leading=22,
                              alignment=1,
                              fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="CustomHeading",
                              fontSize=14,
                              leading=18,
                              spaceBefore=12,
                              spaceAfter=6,
                              fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="CustomBodyText",
                              fontSize=11,
                              leading=14,
                              alignment=4))

    # === Multilingual Labels ===
    datasheet_labels = {
        "de": "DATENBLATT",
        "en": "DATASHEET",
        "fr": "FICHE TECHNIQUE",
        "es": "HOJA TÉCNICA",
        "it": "SCHEDA TECNICA"
    }

    page_labels = {
        "de": ("Seite", "von"),
        "en": ("Page", "of"),
        "fr": ("Page", "sur"),
        "es": ("Página", "de"),
        "it": ("Pagina", "di"),
    }

    artikel_labels = {
        "de": "Artikelnummer",
        "en": "Article Number",
        "fr": "Numéro d’article",
        "es": "Número de artículo",
        "it": "Numero articolo"
    }

    tech_labels = {
        "de": "Technische Daten",
        "en": "Technical Data",
        "fr": "Données techniques",
        "es": "Datos técnicos",
        "it": "Dati tecnici"
    }

    table_headers = {
        "de": ("Attribut", "Wert"),
        "en": ("Attribute", "Value"),
        "fr": ("Attribut", "Valeur"),
        "es": ("Atributo", "Valor"),
        "it": ("Attributo", "Valore"),
    }

    desc_labels = {
        "de": "Beschreibung",
        "en": "Description",
        "fr": "Description",
        "es": "Descripción",
        "it": "Descrizione"
    }

    drawing_labels = {
        "de": "Zeichnung und Maßtabelle",
        "en": "Drawing and Dimension Table",
        "fr": "Dessin et tableau des dimensions",
        "es": "Dibujo y tabla de dimensiones",
        "it": "Disegno e tabella delle dimensioni"
    }

    # === Footer company lines (NO website) ===
    company_texts = {
        "de": "syskomp gehmeyr GmbH – emico • Max-Planck-Straße 1 • 92224 Amberg • Tel.: +49 9621 67545-0 • sales@emico.com",
        "en": "syskomp gehmeyr GmbH – emico • Max-Planck-Straße 1 • 92224 Amberg • Phone: +49 9621 67545-0 • sales@emico.com",
        "fr": "syskomp gehmeyr GmbH – emico • Max-Planck-Straße 1 • 92224 Amberg • Tél.: +49 9621 67545-0 • sales@emico.com",
        "es": "syskomp gehmeyr GmbH – emico • Max-Planck-Straße 1 • 92224 Amberg • Tel.: +49 9621 67545-0 • sales@emico.com",
        "it": "syskomp gehmeyr GmbH – emico • Via Gerolamo Fracastoro 3 • 37010 Cavaion Veronese • Tel.: +39 045 7235605 • info@emico.it"
    }

    # === QR text ===
    qr_texts = {
        "de": (
            "Scannen Sie den QR-Code, um weitere Artikel in dieser Kategorie zu entdecken.<br/><br/>"
            "Für eine individuelle Beratung freuen wir uns über Ihre E-Mail an "
            "<a href='mailto:sales@emico.com'>sales@emico.com</a> oder telefonisch unter +49 9621 67545-0."
        ),
        "en": (
            "Scan the QR code to discover more items in this category.<br/><br/>"
            "For personalized advice, feel free to contact us at "
            "<a href='mailto:sales@emico.com'>sales@emico.com</a> or by phone at +49 9621 67545-0."
        ),
        "fr": (
            "Scannez le code QR pour découvrir d'autres articles dans cette catégorie.<br/><br/>"
            "Pour un conseil personnalisé, contactez-nous par e-mail à "
            "<a href='mailto:sales@emico.com'>sales@emico.com</a> ou par téléphone au +49 9621 67545-0."
        ),
        "es": (
            "Escanee el código QR para descubrir más artículos en esta categoría.<br/><br/>"
            "Para recibir asesoramiento personalizado, puede escribirnos a "
            "<a href='mailto:sales@emico.com'>sales@emico.com</a> o llamarnos al +49 9621 67545-0."
        ),
        "it": (
            "Scansiona il codice QR per scoprire altri articoli in questa categoria.<br/><br/>"
            "Per una consulenza personalizzata, contattaci via e-mail a "
            "<a href='mailto:info@emico.it'>info@emico.it</a> oppure telefonicamente al +39 045 7235605."
        )
    }

    disclaimer_texts = {
        "de": "Die Angaben in diesem Dokument erfolgen nach bestem Wissen, jedoch ohne Gewähr. Änderungen und Irrtümer sind vorbehalten.",
        "en": "The information in this document is provided to the best of our knowledge, but without guarantee. Changes and errors reserved.",
        "fr": "Les informations contenues dans ce document sont fournies au mieux de nos connaissances, mais sans garantie.",
        "es": "La información de este documento se proporciona según nuestro leal saber y entender, pero sin garantía.",
        "it": "Le informazioni contenute in questo documento sono fornite al meglio delle nostre conoscenze, ma senza garanzia."
    }

    # === Clean product name helper ===
    def clean_product_name(name: str) -> str:
        if not name:
            return ""
        name = re.sub(r"\([^)]*\)", "", name)
        name = re.sub(r"\b\d+\s*[xX]\s*\d+\b", "", name)
        name = re.sub(r"\b\d+\s*(mm|cm|inch|in)\b", "", name, flags=re.I)
        name = re.sub(r"\b\d+\b", "", name)
        name = re.sub(r"[^\w\s]", " ", name)
        name = re.sub(r"\s+", " ", name)
        return name.strip()

    # =====================================================================
    # UPDATED FOOTER WITH CENTERED DIVIDER LINE + FONT SIZE 7
    # =====================================================================
    def draw_header_footer(canvas_obj, doc_obj):
        # Logo
        logo_path = resource_path("assets/emicologo.png")
        if os.path.exists(logo_path):
            canvas_obj.drawImage(
                logo_path,
                (PAGE_WIDTH - 6.4 * cm) / 2,
                PAGE_HEIGHT - 3 * cm,
                6.4 * cm,
                2.6 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )

        page_num = canvas_obj.getPageNumber()
        last_page = doc.page

        # --- Footer Header (DATENBLATT | Product | Version)
        datasheet_word = datasheet_labels.get(lang, "DATENBLATT")
        product_name = clean_product_name(basic_info.get("product_name", ""))
        version_str = datetime.datetime.now().strftime("%m/%Y")

        header_text = (
    f"{datasheet_word} | {product_name} | "
    f"Version <font color='#000000'><b>{version_str}</b></font>"
)


        p_header = Paragraph(
            header_text,
            ParagraphStyle(
                "FooterHeader",
                fontName="Helvetica",
                fontSize=7,
                alignment=1,
                textColor=colors.Color(0.2,0.2,0.2)
            )
        )
        w_head, h_head = p_header.wrap(PAGE_WIDTH - 5 * cm, 20)
        p_header.drawOn(canvas_obj, 2.5 * cm, 1.45 * cm)

        # --- COMPANY FOOTER LINE (centered)
        p_company = Paragraph(
            company_texts.get(lang, company_texts["de"]),
            ParagraphStyle(
                "FooterCompany",
                fontName="Helvetica",
                fontSize=7,
                alignment=1,
                textColor=colors.Color(0.2,0.2,0.2)
            )
        )
        w_comp, h_comp = p_company.wrap(PAGE_WIDTH - 5 * cm, 20)
        p_company.drawOn(canvas_obj, 2.5 * cm, 0.9 * cm)

        # --- DIVIDER LINE (solid black, centered)
        canvas_obj.setStrokeColor(colors.Color(0.2,0.2,0.2))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(2.5 * cm, 1.45 * cm, PAGE_WIDTH - 2.5 * cm, 1.45 * cm)

        # --- PAGE NUMBER
        label_page, label_of = page_labels.get(lang, ("Seite", "von"))
        page_text = f"{label_page} {page_num} {label_of} {last_page}"

        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawRightString(
            PAGE_WIDTH - 2.5 * cm,
            0.55 * cm,
            page_text
        )

    # === Title ===
    story.append(Paragraph(f"<b>{basic_info.get('product_name', 'Produktname unbekannt')}</b>", styles["CustomTitle"]))
    story.append(Spacer(1, 4))

    story.append(
        Paragraph(
            f"{artikel_labels.get(lang)}: {basic_info.get('artikelnummer', '–')}",
            ParagraphStyle("ArtikelnummerCentered", parent=styles["CustomBodyText"], alignment=1),
        )
    )
    story.append(Spacer(1, 10))

    # === Images ===
    def make_resized_image(url, max_width, max_height):
        try:
            content = requests.get(url).content
            img = ImageReader(io.BytesIO(content))
            iw, ih = img.getSize()
            aspect = ih / iw
            if iw > max_width:
                iw = max_width
                ih = iw * aspect
            if ih > max_height:
                ih = max_height
                iw = ih / aspect
            return Image(io.BytesIO(content), width=iw, height=ih)
        except:
            return None

    img_links = [l for l in clean_links if not re.search(r"_zg(?:_\\d+)?\\.(jpg|png)$", l, re.I)]
    img_links = img_links[:3]

    if img_links:
        max_total_width = PAGE_WIDTH - 5 * cm
        target_width = max_total_width / len(img_links) - 1 * cm
        imgs = [make_resized_image(l, target_width, PAGE_HEIGHT / 6) for l in img_links]

        table = Table([imgs], hAlign="CENTER")
        table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("RIGHTPADDING", (0, 0), (-2, 0), 30),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    # === Technical Data ===
    technische_daten = {**base_specs, **technical_specs}

    if technische_daten:
        story.append(Paragraph(f"<b>{tech_labels.get(lang)}</b>", styles["CustomHeading"]))

        attr_label, value_label = table_headers.get(lang, table_headers["de"])
        data = [[attr_label, value_label]] + [[k, v] for k, v in technische_daten.items()]

        table = Table(data,
                      colWidths=[(PAGE_WIDTH - 5 * cm) / 2] * 2,
                      hAlign="CENTER")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    # === Description ===
    beschreibung = basic_info.get("beschreibung", "").strip()
    if beschreibung and beschreibung != "<p></p>":
        beschreibung = beschreibung.replace("<br>", "<br/>").replace("<p>", "").replace("</p>", "")
        story.append(Paragraph(f"<b>{desc_labels.get(lang)}</b>", styles["CustomHeading"]))
        story.append(Paragraph(beschreibung, styles["CustomBodyText"]))
        story.append(Spacer(1, 10))

    story.append(CondPageBreak(PAGE_HEIGHT / 2))

    # === Drawing ===
    story.append(Paragraph(f"<b>{drawing_labels.get(lang)}</b>", styles["CustomHeading"]))

    zg_links = [l for l in clean_links if re.search(r"_zg(?:_\\d+)?\\.(jpg|png)$", l, re.I)]
    if zg_links:
        zg_img = make_resized_image(zg_links[0], PAGE_WIDTH - 5 * cm, PAGE_HEIGHT / 5)
        if zg_img:
            story.append(zg_img)
            story.append(Spacer(1, 12))

    if drawing_data:
        attr_label, value_label = table_headers.get(lang, table_headers["de"])
        data2 = [[attr_label, value_label]] + [[k, v] for k, v in drawing_data.items()]
        table2 = Table(data2,
                       colWidths=[(PAGE_WIDTH - 5 * cm) / 2] * 2,
                       hAlign="CENTER")
        table2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        story.append(table2)
        story.append(Spacer(1, 12))

    # === QR Code ===
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
        story.append(Spacer(1, 8))
        qr_img = Image(qr_path, width=3.5 * cm, height=3.5 * cm)
        qr_img.hAlign = "LEFT"

        qr_para = Paragraph(qr_texts.get(lang, qr_texts["de"]), styles["CustomBodyText"])

        qr_text_box = Table([[qr_para]],
                            colWidths=[PAGE_WIDTH - 5 * cm - 4 * cm],
                            hAlign="LEFT")
        qr_text_box.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        qr_table = Table([[qr_img, qr_text_box]],
                         colWidths=[4 * cm, PAGE_WIDTH - 5 * cm - 4 * cm],
                         hAlign="CENTER")
        qr_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))

        story.append(qr_table)
        story.append(Spacer(1, 2))

    story.append(
        Paragraph(
            disclaimer_texts.get(lang, disclaimer_texts["de"]),
            ParagraphStyle("Disc", fontName="Helvetica-Oblique",
                           fontSize=7.5, alignment=1, textColor=colors.darkgrey),
        )
    )

    doc.build(
        story,
        onFirstPage=lambda c, d: draw_header_footer(c, d),
        onLaterPages=lambda c, d: draw_header_footer(c, d),
    )

    print(f"✅ PDF successfully created: {output_filename}")
