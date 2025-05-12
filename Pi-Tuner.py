import os
import json
import time
import threading
import subprocess
import customtkinter as ctk
from tkinter import messagebox

PROFILE_FILE = "pi5_profiles.json"
CONFIG_PATH = "/boot/firmware/config.txt"

# Utility Functions
def get_temp():
    try:
        out = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return float(out.split("=")[1].split("'")[0])
    except:
        return 0.0

def get_clock():
    try:
        out = subprocess.check_output(["vcgencmd", "measure_clock", "arm"]).decode()
        return int(out.strip().split("=")[1]) / 1_000_000
    except:
        return 0.0

def get_voltage():
    try:
        out = subprocess.check_output(["vcgencmd", "measure_volts"]).decode()
        return float(out.split("=")[1].replace("V", ""))
    except:
        return 0.0

# Real Fan Control via GPIO18 (PWM)
def set_fan_pwm(percent):
    duty = int((percent / 100.0) * 1023)
    os.system(f"gpio -g mode 18 pwm && gpio -g pwm 18 {duty}")

# Config File Updates
def apply_voltage_clock(clock, overvolt):
    with open(CONFIG_PATH, "r") as f:
        lines = f.readlines()
    lines = [line for line in lines if not any(x in line for x in ["arm_freq=", "over_voltage=", "force_turbo="])]
    lines.append(f"force_turbo=1\n")
    lines.append(f"arm_freq={clock}\n")
    lines.append(f"over_voltage={overvolt}\n")
    with open(CONFIG_PATH, "w") as f:
        f.writelines(lines)
    subprocess.run(["vcgencmd", "measure_volts"])  # force reread

def save_profile(name, clock, volt, fan):
    try:
        with open(PROFILE_FILE, "r") as f:
            profiles = json.load(f)
    except:
        profiles = {}
    profiles[name] = {"clock": clock, "voltage": volt, "fan": fan}
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

def load_profiles():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return {}

# GUI Class
class PiTuner(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pi-Tuner")
        self.geometry("700x600")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Stat Labels
        self.temp = ctk.CTkLabel(self, text="Temp: -- °C")
        self.temp.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.clock = ctk.CTkLabel(self, text="Clock: -- MHz")
        self.clock.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.volt = ctk.CTkLabel(self, text="Voltage: -- V")
        self.volt.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        # Sliders Section
        slider_frame = ctk.CTkFrame(self)
        slider_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")
        slider_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(slider_frame, text="CPU Clock (MHz)").grid(row=0, column=0, sticky="w")
        self.clock_slider = ctk.CTkSlider(slider_frame, from_=600, to=2500, command=self.update_clock_label)
        self.clock_slider.set(1500)
        self.clock_slider.grid(row=0, column=1, sticky="ew")
        self.clock_val = ctk.CTkLabel(slider_frame, text="1500 MHz")
        self.clock_val.grid(row=0, column=2, padx=10)

        ctk.CTkLabel(slider_frame, text="Over Voltage (0 to 6)").grid(row=1, column=0, sticky="w")
        self.volt_slider = ctk.CTkSlider(slider_frame, from_=0, to=6, number_of_steps=6, command=self.update_volt_label)
        self.volt_slider.set(0)
        self.volt_slider.grid(row=1, column=1, sticky="ew")
        self.volt_val = ctk.CTkLabel(slider_frame, text="0")
        self.volt_val.grid(row=1, column=2, padx=10)

        ctk.CTkLabel(slider_frame, text="Fan Speed (%)").grid(row=2, column=0, sticky="w")
        self.fan_slider = ctk.CTkSlider(slider_frame, from_=0, to=100, command=self.update_fan_label)
        self.fan_slider.set(100)
        self.fan_slider.grid(row=2, column=1, sticky="ew")
        self.fan_val = ctk.CTkLabel(slider_frame, text="100 %")
        self.fan_val.grid(row=2, column=2, padx=10)

        # Controls Section
        controls = ctk.CTkFrame(self)
        controls.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")

        self.profile_entry = ctk.CTkEntry(controls, placeholder_text="Profile Name")
        self.profile_entry.grid(row=0, column=0, padx=5, pady=5)

        self.save_btn = ctk.CTkButton(controls, text="Save Profile", command=self.save_current)
        self.save_btn.grid(row=0, column=1, padx=5, pady=5)

        self.profile_menu = ctk.CTkOptionMenu(controls, values=["None"], command=self.load_profile)
        self.profile_menu.grid(row=0, column=2, padx=5, pady=5)

        self.apply_btn = ctk.CTkButton(controls, text="Apply Settings", command=self.apply_all)
        self.apply_btn.grid(row=1, column=0, padx=5, pady=5)

        self.reset_btn = ctk.CTkButton(controls, text="Restore Default", command=self.restore_default)
        self.reset_btn.grid(row=1, column=1, padx=5, pady=5)

        self.refresh_profiles()

        self.update_thread = threading.Thread(target=self.update_stats, daemon=True)
        self.update_thread.start()

    def update_stats(self):
        while True:
            self.temp.configure(text=f"Temp: {get_temp():.1f} °C")
            self.clock.configure(text=f"Clock: {get_clock():.0f} MHz")
            self.volt.configure(text=f"Voltage: {get_voltage():.2f} V")
            time.sleep(2)

    def update_clock_label(self, val):
        self.clock_val.configure(text=f"{int(val)} MHz")

    def update_volt_label(self, val):
        self.volt_val.configure(text=f"{int(val)}")

    def update_fan_label(self, val):
        self.fan_val.configure(text=f"{int(val)} %")

    def save_current(self):
        name = self.profile_entry.get()
        if name:
            save_profile(name, int(self.clock_slider.get()), int(self.volt_slider.get()), int(self.fan_slider.get()))
            self.refresh_profiles()
            messagebox.showinfo("Saved", f"Profile '{name}' saved.")

    def refresh_profiles(self):
        profiles = load_profiles()
        self.profile_menu.configure(values=["None"] + list(profiles.keys()))

    def load_profile(self, name):
        profiles = load_profiles()
        if name in profiles:
            data = profiles[name]
            self.clock_slider.set(data["clock"])
            self.volt_slider.set(data["voltage"])
            self.fan_slider.set(data["fan"])

    def apply_all(self):
        clk = int(self.clock_slider.get())
        ov = int(self.volt_slider.get())
        fan = int(self.fan_slider.get())
        os.system(f"sudo cpufreq-set -u {clk}MHz")
        apply_voltage_clock(clk, ov)
        set_fan_pwm(fan)
        messagebox.showinfo("Applied", "Settings applied.")

    def restore_default(self):
        self.clock_slider.set(1500)
        self.volt_slider.set(0)
        self.fan_slider.set(100)
        self.apply_all()

if __name__ == "__main__":
    app = PiTuner()
    app.mainloop()
