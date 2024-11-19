import os
import sys
import subprocess
from pathlib import Path


def create_executable():
    # Chemins
    script_path = Path(__file__).resolve().parent

    # Dépendances à installer
    dependencies = ["customtkinter", "yt-dlp", "pyyaml", "spotdl"]

    # Installer les dépendances
    subprocess.run(["python", "-m", "pip", "install"] + dependencies)

    # Commande PyInstaller
    pyinstaller_cmd = [
        "python",
        "-m",
        "pyinstaller",
        "--onefile",  # Tout en un fichier
        "--windowed",  # Sans console
        "--add-data",
        f"{script_path}/config:config",  # Inclure le dossier config
        "--name",
        "PyDownloader",
        "main.pyw",  # Votre script principal
    ]

    subprocess.run(pyinstaller_cmd)


if __name__ == "__main__":
    create_executable()
