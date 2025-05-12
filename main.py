# Final Pi-Tuner Main Code
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
        self.geometry("600x600")
        ctk.set_appearance_mode("dark")

        self.temp = ctk.CTkLabel(self, text="Temp: -- °C")
        self.temp.pack(pady=5)

        self.clock = ctk.CTkLabel(self, text="Clock: -- MHz")
        self.clock.pack(pady=5)

        self.volt = ctk.CTkLabel(self, text="Voltage: -- V")
        self.volt.pack(pady=5)

        # Clock Slider
        ctk.CTkLabel(self, text="CPU Clock (MHz)").pack()
        self.clock_slider = ctk.CTkSlider(self, from_=600, to=2500, command=self.update_clock_label)
        self.clock_slider.set(1500)
        self.clock_slider.pack()
        self.clock_val = ctk.CTkLabel(self, text="1500 MHz")
        self.clock_val.pack()

        # Voltage Slider
        ctk.CTkLabel(self, text="Over Voltage (0 to 6)").pack()
        self.volt_slider = ctk.CTkSlider(self, from_=0, to=6, number_of_steps=6, command=self.update_volt_label)
        self.volt_slider.set(0)
        self.volt_slider.pack()
        self.volt_val = ctk.CTkLabel(self, text="0")
        self.volt_val.pack()

        # Fan Control
        ctk.CTkLabel(self, text="Fan Speed (%)").pack()
        self.fan_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.update_fan_label)
        self.fan_slider.set(100)
        self.fan_slider.pack()
        self.fan_val = ctk.CTkLabel(self, text="100 %")
        self.fan_val.pack()

        # Profile Tools
        self.profile_entry = ctk.CTkEntry(self, placeholder_text="Profile Name")
        self.profile_entry.pack(pady=5)

        self.save_btn = ctk.CTkButton(self, text="Save Profile", command=self.save_current)
        self.save_btn.pack(pady=5)

        self.apply_btn = ctk.CTkButton(self, text="Apply Settings", command=self.apply_all)
        self.apply_btn.pack(pady=5)

        self.reset_btn = ctk.CTkButton(self, text="Restore Default", command=self.restore_default)
        self.reset_btn.pack(pady=5)

        self.profile_menu = ctk.CTkOptionMenu(self, values=["None"], command=self.load_profile)
        self.profile_menu.pack(pady=10)
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
