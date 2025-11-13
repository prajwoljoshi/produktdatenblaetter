import customtkinter as ctk
import threading
from tkinter import filedialog
from pathlib import Path
from main import get_emico_data
from pdf_generator import generate_emico_pdf
from utils import resource_path

# === App setup ===
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class EmicoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Emico PDF-Generator")
        self.geometry("850x550")
        self.resizable(False, False)

        self.selected_folder = None  # vom Benutzer gewählter Ordner

        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # === Titel ===
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Emico PDF-Generator",
            font=("Segoe UI", 28, "bold"),
            text_color=("#1E1E1E", "#E5E5E5"),
        )
        self.title_label.pack(pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Erstellen Sie professionelle Produkt-PDFs direkt aus Emico-URLs.",
            font=("Segoe UI", 14),
            text_color=("#6E6E73", "#A0A0A5"),
        )
        self.subtitle_label.pack(pady=(0, 30))

        # === URL-Eingabe + Speicher-Icon nebeneinander ===
        entry_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        entry_frame.pack(pady=10)

        self.url_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="https://www.emico.com/produkt/...",
            width=460,
            height=40,
            font=("Segoe UI", 14),
            corner_radius=12,
        )
        self.url_entry.pack(side="left", padx=(0, 10))

        # === Speicherordner-Button ===
        self.folder_icon_btn = ctk.CTkButton(
            entry_frame,
            text="📂",
            width=55,
            height=40,
            font=("Segoe UI", 20),
            fg_color=("#1E90FF", "#3B9CFF"),  # helleres Emico-Blau
            hover_color=("#0070E0", "#339CFF"),
            text_color="white",
            corner_radius=10,
            command=self.select_folder,
        )
        self.folder_icon_btn.pack(side="left")

        # === PDF-Erstellen-Button ===
        self.generate_btn = ctk.CTkButton(
            self.main_frame,
            text="PDF generieren",
            fg_color=("#1E90FF", "#3B9CFF"),
            hover_color=("#0070E0", "#339CFF"),
            text_color="white",
            width=200,
            height=45,
            font=("Segoe UI", 16, "bold"),
            command=self.start_process,
        )
        self.generate_btn.pack(pady=(20, 25))

        # === Fortschrittsbalken + Status ===
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400, height=8)
        self.progress_bar.pack(pady=(10, 5))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Bereit zum Generieren 🚀",
            font=("Segoe UI", 13),
            text_color=("#3A3A3C", "#C7C7CC"),
        )
        self.status_label.pack(pady=(10, 20))

        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="© 2025 syskomp gehmeyr GmbH – Emico Division",
            font=("Segoe UI", 11),
            text_color=("#6E6E73", "#A0A0A5"),
        )
        self.footer_label.pack(side="bottom", pady=10)

    # === Ordnerauswahl (aufgerufen bei Klick auf 📂) ===
    def select_folder(self):
        folder = filedialog.askdirectory(title="Ordner zum Speichern der PDF auswählen")
        if folder:
            self.selected_folder = folder
            self.status_label.configure(
                text=f"📁 Speicherordner: {folder}", text_color="#1E90FF"
            )

    # === Startet den Prozess ===
    def start_process(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(
                text="❌ Bitte geben Sie eine gültige Produkt-URL ein.",
                text_color="#D93025",
            )
            return

        self.status_label.configure(
            text="⏳ Produktdaten werden abgerufen...", text_color="#1E90FF"
        )
        self.progress_bar.set(0)
        self.generate_btn.configure(state="disabled")
        threading.Thread(target=self.run_process, args=(url,)).start()

    # === Arbeitsthread ===
    def run_process(self, url):
        try:
            self.update_progress(0.3, "🔍 Produktdetails werden ausgelesen...")
            basic_info, base_specs, technical_specs, drawing_data, clean_links,lang = get_emico_data(url)

            # === Speicherordner behandeln ===
            try:
                if self.selected_folder is None:
                    save_folder = Path.home() / "Downloads"
                else:
                    save_folder = Path(self.selected_folder).expanduser().resolve()

                # Ordner erstellen, falls nicht vorhanden
                save_folder.mkdir(parents=True, exist_ok=True)

            except (OSError, TypeError):
                # Wenn ungültig, auf Downloads zurückgreifen
                self.update_progress(0.4, "⚠️ Ungültiger Ordner – Downloads wird verwendet.")
                save_folder = Path.home() / "Downloads"
                save_folder.mkdir(parents=True, exist_ok=True)

            self.update_progress(0.7, "🧾 PDF wird generiert...")
            generate_emico_pdf(basic_info, base_specs, technical_specs, drawing_data, clean_links,lang, save_folder)

            self.update_progress(1.0, f"✅ PDF gespeichert in: {save_folder}")
            self.status_label.configure(text_color="#34C759")

        except Exception as e:
            self.status_label.configure(
                text=f"❌ Fehler: {e}", text_color="#FF3B30"
            )

        finally:
            self.generate_btn.configure(state="normal")

    # === Fortschritt aktualisieren ===
    def update_progress(self, value, message):
        self.progress_bar.set(value)
        self.status_label.configure(text=message)
        self.update_idletasks()


if __name__ == "__main__":
    app = EmicoApp()
    app.mainloop()
