from pathlib import Path
import yaml
import customtkinter
from yt_dlp import YoutubeDL
import subprocess
import re
import os
import logging
from typing import Dict, Union, Optional


def default_settings_write(path):
    try:
        os.makedirs(str(path / "config"), exist_ok=True)
        os.makedirs(str(path / "output"), exist_ok=True)
        
        data = {
            "outtmpl": str(path / "output/%(title)s.%(ext)s"),
            "format": "137+140"
        }
        
        config_path = str(path / "config/params.yml")
        with open(config_path, "w", encoding="utf-8") as params:
            yaml.dump(data, params, default_flow_style=False)
        
        return data
    
    except Exception as e:
        logging.error(f"Erreur lors de l'écriture de la configuration : {e}")
        return {"outtmpl": str(path / "output/%(title)s.%(ext)s"), "format": "137+140"}

def settings_load(path):
    config_path = path / "config/params.yml"
    
    try:
        with open(str(config_path), "r", encoding="utf-8") as params_file:
            data = yaml.safe_load(params_file) or {}
        
        # Vérifications et corrections si données incomplètes
        if not data.get("outtmpl"):
            data["outtmpl"] = str(path / "output/%(title)s.%(ext)s")
        
        if not data.get("format"):
            data["format"] = "137+140"
        
        output_dir = os.path.dirname(data["outtmpl"])
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        return data
    
    except (FileNotFoundError, PermissionError):
        return default_settings_write(path)
    except Exception as e:
        logging.error(f"Erreur configuration : {e}")
        return default_settings_write(path)

class App(customtkinter.CTk):
    def __init__(self, path: Path, params):
        """
        Initialiser l'application avec les paramètres donnés.
        
        Args:
            path (Path): Chemin racine de l'application
            params (Dict): Paramètres de configuration
        """
        super().__init__()
        self.path = path
        self.params = params
        
        self.onlyaudio = False
        self.use_spotify = False
        
        self._setup_window()
        self._create_widgets()
    
    def _setup_window(self):
        """Configuration de la fenêtre principale"""
        self.title("pydownloader (wip)")
        self.geometry("400x200")
        self.resizable(False, False)
        
        for i in range(2):
            self.rowconfigure(index=i, weight=1)
            self.columnconfigure(index=i, weight=1)

    def set_audio(self):
        """
        Basculer entre le téléchargement audio et vidéo.
        Modifie les paramètres de yt-dlp en conséquence.
        """
        self.onlyaudio = not self.onlyaudio
        
        if self.onlyaudio:
            self.params["format"] = "bestaudio/best"
            self.params["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
            # Mettre à jour visuellement la checkbox
            self.audioCheckbox.select()
        else:
            self.params["format"] = "137+140"
            self.params.pop("postprocessors", None)
            self.audioCheckbox.deselect()

    def set_spotdl(self):
        """
        Basculer l'utilisation de SpotDL pour le téléchargement.
        Désactive l'extraction audio standard si SpotDL est activé.
        """
        self.use_spotify = not self.use_spotify
        
        if self.use_spotify:
            # Désactiver l'extraction audio standard
            if self.onlyaudio:
                self.set_audio()
            
            self.spotdlCheckbox.select()
        else:
            self.spotdlCheckbox.deselect()
    def downloader(self):
        """
        Gérer le téléchargement de contenu audio ou vidéo.
        Supporte YouTube, Spotify, et recherche générique.
        """
        input_link = self.input.get().strip()
        if not input_link:
            return

        self.btn.configure(text="downloading...", state="disabled")
        
        self.after(100, self._download_process, input_link)
    def _download_process(self, input_link):
        """
        Processus de téléchargement avec gestion des différents cas.
        """
        try:
            if input_link.startswith("https://open.spotify.com/") or self.use_spotify:
                subprocess.run(["python", "-m", "spotdl", input_link], check=True)
            
            else:
                download_params = self.params.copy()
                
                try:
                    YoutubeDL(download_params).download([input_link])
                
                except Exception:
                    YoutubeDL(download_params).download([f"ytsearch1:{input_link}"])

        except Exception as e:
            logging.error(f"Erreur de téléchargement : {e}")
            self.text.configure(text=f"Erreur : {str(e)}")

        finally:
            self.btn.configure(text="download", state="normal")
            self.input.delete(0, 'end')  # Effacer le champ de saisie
            
            try:
                self.open_explorer(config=False)
            except Exception:
                pass
                
    def _create_widgets(self):
        """Créer tous les widgets de l'interface"""
        # Frame pour les labels
        self.labelframe = customtkinter.CTkFrame(master=self, fg_color="gray14")
        self.labelframe.columnconfigure(index=0, weight=1)
        self.labelframe.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Frame principale de la grille
        self.gridframe = customtkinter.CTkFrame(master=self)
        self.gridframe.columnconfigure(index=0, weight=1)
        self.gridframe.columnconfigure(index=1, weight=1)
        self.gridframe.grid(row=1, column=0, columnspan=2, sticky="news")

        # Frame pour les checkboxes
        self.checkframe = customtkinter.CTkFrame(
            master=self.gridframe, fg_color="gray17"
        )
        self.checkframe.columnconfigure(index=0, weight=1)
        self.checkframe.columnconfigure(index=1, weight=1)
        self.checkframe.grid(row=2, column=0, columnspan=1, pady=20)

        # Label principal
        self.text = customtkinter.CTkLabel(
            master=self.labelframe, text="download any video/song..."
        )
        self.text.grid(row=0, column=0, columnspan=2)

        # Champ de saisie
        self.input = customtkinter.CTkEntry(
            master=self.gridframe, placeholder_text="link"
        )
        self.input.grid(row=1, column=0, sticky="ew", padx="20")
        self.input.focus_set()

        # Bouton de téléchargement
        self.btn = customtkinter.CTkButton(
            master=self.gridframe, text="download", command=self.downloader
        )
        self.btn.grid(row=1, column=1, padx=20)

        # Bouton configuration
        self.check2 = customtkinter.CTkButton(
            master=self.gridframe,
            fg_color="gray14",
            hover_color="gray20",
            text="open config folder",
            command=self.open_explorer,
        )
        self.check2.grid(row=2, column=1, pady=20, padx=20)

        # Checkbox audio
        self.audioCheckbox = customtkinter.CTkCheckBox(
            master=self.checkframe,
            corner_radius=16,
            text="extract\naudio",
            command=self.set_audio,
        )
        self.audioCheckbox.grid(row=0, column=1, padx=10)

        # Checkbox Spotify
        self.spotdlCheckbox = customtkinter.CTkCheckBox(
            master=self.checkframe,
            corner_radius=16,
            text="use spotdl\n(only audio)",
            command=self.set_spotdl,
        )
        self.spotdlCheckbox.grid(row=0, column=2, padx=10)    

    def open_explorer(self, config: bool = True):
        """
        Ouvrir l'explorateur de fichiers avec un gestionnaire d'erreurs.
        
        Args:
            config (bool): Ouvrir le dossier de configuration ou de sortie
        """
        explorers = ["thunar", "explorer", "xdg-open"]
        emplacement = str(self.path / "config" if config else 
                        re.split(r"[\\/]+", self.params["outtmpl"])[:-1])
        
        for explorer in explorers:
            try:
                subprocess.run([explorer, emplacement])
                return
            except Exception as e:
                logging.debug(f"Échec avec {explorer}: {e}")
        

def main():
    """Point d'entrée principal de l'application"""
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s: %(message)s')
    
    path = Path(__file__).resolve().parent
    params = settings_load(path)
    
    app = App(path, params)
    customtkinter.set_appearance_mode("dark")
    
    try:
        app.mainloop()
    except Exception as e:
        logging.error(f"Erreur fatale : {e}")

if __name__ == "__main__":
    main()
