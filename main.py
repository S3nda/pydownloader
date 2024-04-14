from pathlib import Path
import yaml
import customtkinter
from yt_dlp import YoutubeDL
import subprocess
import re


def default_settings_write(path):
    print(f"writing default config! at {path}")
    data = {"outtmpl": str(path / "output/%(title)s.%(ext)s"), "format": "137+140"}
    try:
        with open(str(path / "config/params.yml"), "a+", encoding="utf-8") as params:
            yaml.dump(data, params, default_flow_style=False)
    except Exception as e:
        print(e)
        return 1


def settings_load(path) -> dict:
    try:
        with open(str(path / "config/params.yml"), "r+", encoding="utf-8") as params:
            data = yaml.safe_load(params)
            return data
    except FileNotFoundError:
        if default_settings_write(path) != 1:
            return settings_load(path)
        else:
            raise Exception("please make a config folder")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(str(path / "config/icon.ico"))
        self.onlyaudio = False
        self.use_spotify = False
        self.title("pydownloader (wip)")
        self.geometry("400x200")
        self.resizable(False, False)

        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=1)
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)

        self.labelframe = customtkinter.CTkFrame(master=self, fg_color="gray14")
        self.labelframe.columnconfigure(index=0, weight=1)
        self.labelframe.rowconfigure(index=0, weight=1)
        self.labelframe.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.gridframe = customtkinter.CTkFrame(master=self)
        self.gridframe.columnconfigure(index=0, weight=1)
        self.gridframe.columnconfigure(index=1, weight=1)
        self.gridframe.rowconfigure(index=0, weight=1)
        self.gridframe.rowconfigure(index=1, weight=1)
        self.gridframe.grid(row=1, column=0, columnspan=2, sticky="news")

        self.checkframe = customtkinter.CTkFrame(
            master=self.gridframe, fg_color="gray17"
        )
        self.checkframe.columnconfigure(index=0, weight=1)
        self.checkframe.columnconfigure(index=1, weight=1)
        self.checkframe.grid(row=2, column=0, columnspan=1, pady=20)

        self.btn = customtkinter.CTkButton(
            master=self.gridframe, text="download", command=self.downloader
        )
        self.btn.grid(row=1, column=1, padx=20)

        self.input = customtkinter.CTkEntry(
            master=self.gridframe, placeholder_text="link"
        )
        self.input.grid(row=1, column=0, sticky="ew", padx="20")
        self.input.focus_set()

        self.text = customtkinter.CTkLabel(
            master=self.labelframe, text="download any video/song..."
        )
        self.text.grid(row=0, column=0, columnspan=2)

        # config button
        self.check2 = customtkinter.CTkButton(
            master=self.gridframe,
            fg_color="gray14",
            hover_color="gray20",
            text="open config folder",
            command=self.open_explorer,
        )
        self.check2.grid(row=2, column=1, pady=20, padx=20)

        self.audioCheckbox = customtkinter.CTkCheckBox(
            master=self.checkframe,
            corner_radius=16,
            text="extract\naudio",
            command=self.set_audio,
        )
        self.audioCheckbox.grid(row=0, column=1, padx=10)

        self.spotdlCheckbox = customtkinter.CTkCheckBox(
            master=self.checkframe,
            corner_radius=16,
            text="use spotdl\n(only audio)",
            command=self.set_spotdl,
        )
        self.spotdlCheckbox.grid(row=0, column=2, padx=10)

    def open_explorer(self, explorer_list=["thunar", "explorer"], config: bool = True):
        if config:
            emplacement = str(path / "config")
        else:
            emplacement = re.split(r"[\\/]+", params["outtmpl"])
            emplacement = "\\".join(emplacement[:-1])

        for i in explorer_list:
            try:
                subprocess.run([i, emplacement])
                return
            except:
                print("failed opening the dir !")
                pass

    def downloader(self):
        input = self.input.get().strip()
        if not input:
            return
        self.btn.configure(text="downloading...")
        self.after(1000, self.download_process, input)

    def download_process(self, input):
        try:
            if input.startswith("https://open.spotify.com/") or self.use_spotify:
                subprocess.run(["python", "-m", "spotdl", input])
            else:
                YoutubeDL(params.copy()).download([input])
        except Exception as e:
            print("Error during download:", e)
            if not self.use_spotify:
                YoutubeDL(params.copy()).download(["ytsearch1:" + input])

        finally:
            self.btn.configure(text="download")
            self.open_explorer(config=False)

    def set_audio(self):
        self.onlyaudio = not self.onlyaudio
        if self.onlyaudio:
            params["format"] = "bestaudio/best"
            params["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        else:
            params["format"] = "137+140"
            del params["postprocessors"]

    def set_spotdl(self):
        self.use_spotify = not self.use_spotify


if __name__ == "__main__":
    global path
    global params

    path = Path(__file__).resolve().parent
    params = settings_load(path)

    app = App()
    customtkinter.set_default_color_theme(str(path / "config/gui.json"))
    customtkinter.set_appearance_mode("dark")
    app.mainloop()
