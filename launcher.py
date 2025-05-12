import os
import subprocess
import urllib.request
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import zipfile
import shutil
import sys

REPO_URL = "https://github.com/BWolf-16/Pi-Tuner-/archive/refs/heads/main.zip"
LAUNCH_PATH = "Pi-Tuner-/main/main.py"
LOCAL_ZIP = "pi_tuner_latest.zip"
EXTRACT_DIR = "pi_tuner_update"

DISCLAIMER = (
    "⚠️ Warning ⚠️\n\n"
    "This tool will download and update the Pi-Tuner system from GitHub, including this launcher.\n"
    "Use at your own risk. Improper tuning (especially voltage/fan control) could result in unstable operation or damage.\n"
    "You accept full responsibility for any consequences."
)

class Launcher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pi-Tuner Launcher")
        self.geometry("500x400")
        ctk.set_appearance_mode("dark")

        self.label = ctk.CTkLabel(self, text=DISCLAIMER, wraplength=480, justify="left")
        self.label.pack(pady=20)

        self.accept_btn = ctk.CTkButton(self, text="Accept & Launch", command=self.update_and_run)
        self.accept_btn.pack(pady=10)

        self.quit_btn = ctk.CTkButton(self, text="Cancel", command=self.destroy)
        self.quit_btn.pack(pady=10)

    def update_and_run(self):
        try:
            self.label.configure(text="Downloading latest version...")
            urllib.request.urlretrieve(REPO_URL, LOCAL_ZIP)

            if os.path.exists(EXTRACT_DIR):
                shutil.rmtree(EXTRACT_DIR)

            with zipfile.ZipFile(LOCAL_ZIP, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)

            os.remove(LOCAL_ZIP)

            full_main_path = os.path.join(EXTRACT_DIR, LAUNCH_PATH)
            if os.path.exists(full_main_path):
                self.label.configure(text="Launching Pi-Tuner...")
                subprocess.Popen(["python3", full_main_path])
                self.destroy()
            else:
                messagebox.showerror("Error", "Main Pi-Tuner file not found after update.")
        except Exception as e:
            messagebox.showerror("Update Failed", str(e))

if __name__ == '__main__':
    app = Launcher()
    app.mainloop()
