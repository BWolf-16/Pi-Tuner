
import os
import subprocess
import json
import time
import threading
import customtkinter as ctk
from tkinter import messagebox

PROFILE_PATH = "pi5_profiles.json"

def read_temperature():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return float(output.split('=')[1].split("'")[0])
    except:
        return 0.0

def read_clock():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_clock", "arm"]).decode()
        return int(output.strip().split('=')[1]) / 1_000_000
    except:
        return 0.0

def read_voltage():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_volts"]).decode()
        return float(output.split('=')[1].replace("V", ""))
    except:
        return 0.0

def read_fan_speed():
    return 50  # Simulated

def apply_settings(clock=None, voltage=None, fan=None):
    if clock:
        os.system(f"sudo cpufreq-set -u {clock}MHz")
    # Real fan/voltage control would require hardware-specific tools

def save_profile(name, clock, voltage, fan):
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            profiles = json.load(f)
    else:
        profiles = {}
    profiles[name] = {"clock": clock, "voltage": voltage, "fan": fan}
    with open(PROFILE_PATH, "w") as f:
        json.dump(profiles, f, indent=4)

def load_profiles():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return {}

class Pi5MonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pi-Tuner")
        self.geometry("600x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.temp_label = ctk.CTkLabel(self, text="Temp: -- °C")
        self.temp_label.pack(pady=10)

        self.clock_label = ctk.CTkLabel(self, text="Clock: -- MHz")
        self.clock_label.pack(pady=10)

        self.volt_label = ctk.CTkLabel(self, text="Voltage: -- V")
        self.volt_label.pack(pady=10)

        self.fan_label = ctk.CTkLabel(self, text="Fan Speed: -- %")
        self.fan_label.pack(pady=10)

        ctk.CTkLabel(self, text="Clock (MHz)").pack()
        self.clock_slider = ctk.CTkSlider(self, from_=100, to=2500, command=self.update_clock_value)
        self.clock_slider.set(1500)
        self.clock_slider.pack()
        self.clock_val = ctk.CTkLabel(self, text="1500 MHz")
        self.clock_val.pack()

        ctk.CTkLabel(self, text="Voltage (V)").pack()
        self.voltage_slider = ctk.CTkSlider(self, from_=0.8, to=1.4, command=self.update_voltage_value)
        self.voltage_slider.set(1.1)
        self.voltage_slider.pack()
        self.volt_val = ctk.CTkLabel(self, text="1.10 V")
        self.volt_val.pack()

        ctk.CTkLabel(self, text="Fan Speed (%)").pack()
        self.fan_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.update_fan_value)
        self.fan_slider.set(50)
        self.fan_slider.pack()
        self.fan_val = ctk.CTkLabel(self, text="50 %")
        self.fan_val.pack()

        self.profile_entry = ctk.CTkEntry(self, placeholder_text="Profile Name")
        self.profile_entry.pack(pady=5)

        self.save_button = ctk.CTkButton(self, text="Save Profile", command=self.save_profile_action)
        self.save_button.pack(pady=5)

        self.apply_button = ctk.CTkButton(self, text="Apply Settings", command=self.apply_current)
        self.apply_button.pack(pady=5)

        self.reset_button = ctk.CTkButton(self, text="Reset", command=self.reset_sliders)
        self.reset_button.pack(pady=5)

        self.profile_menu = ctk.CTkOptionMenu(self, values=["None"], command=self.load_selected_profile)
        self.profile_menu.pack(pady=10)

        self.update_profiles()
        self.update_stats()
        self.polling_thread = threading.Thread(target=self.live_update, daemon=True)
        self.polling_thread.start()

    def update_stats(self):
        temp = read_temperature()
        clock = read_clock()
        volt = read_voltage()
        fan = read_fan_speed()
        self.temp_label.configure(text=f"Temp: {temp:.1f} °C")
        self.clock_label.configure(text=f"Clock: {clock:.0f} MHz")
        self.volt_label.configure(text=f"Voltage: {volt:.2f} V")
        self.fan_label.configure(text=f"Fan Speed: {fan} %")

    def live_update(self):
        while True:
            self.update_stats()
            time.sleep(2)

    def update_clock_value(self, value):
        self.clock_val.configure(text=f"{int(value)} MHz")

    def update_voltage_value(self, value):
        self.volt_val.configure(text=f"{value:.2f} V")

    def update_fan_value(self, value):
        self.fan_val.configure(text=f"{int(value)} %")

    def save_profile_action(self):
        name = self.profile_entry.get()
        if not name:
            messagebox.showwarning("Error", "Profile name is empty.")
            return
        clock = int(self.clock_slider.get())
        voltage = round(self.voltage_slider.get(), 2)
        fan = int(self.fan_slider.get())
        save_profile(name, clock, voltage, fan)
        self.update_profiles()
        messagebox.showinfo("Saved", f"Profile '{name}' saved.")

    def update_profiles(self):
        profiles = load_profiles()
        self.profile_menu.configure(values=["None"] + list(profiles.keys()))

    def load_selected_profile(self, name):
        profiles = load_profiles()
        if name in profiles:
            profile = profiles[name]
            self.clock_slider.set(profile["clock"])
            self.voltage_slider.set(profile["voltage"])
            self.fan_slider.set(profile["fan"])

    def apply_current(self):
        clock = int(self.clock_slider.get())
        voltage = round(self.voltage_slider.get(), 2)
        fan = int(self.fan_slider.get())
        apply_settings(clock, voltage, fan)
        messagebox.showinfo("Applied", f"Settings applied: {clock} MHz, {voltage} V, {fan}% fan")

    def reset_sliders(self):
        self.clock_slider.set(1500)
        self.voltage_slider.set(1.1)
        self.fan_slider.set(50)
        messagebox.showinfo("Reset", "Sliders reset to default.")

app = Pi5MonitorApp()
app.mainloop()
