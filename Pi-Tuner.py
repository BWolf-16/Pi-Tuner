import customtkinter as ctk
import subprocess
import json
import os
import pigpio

# Initialize pigpio for fan control
pi = pigpio.pi()
FAN_GPIO = 18

CONFIG_FILE = "pi_tuner_profiles.json"

class PiTunerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🐾 Pi-Tuner 🐾")
        self.geometry("600x700")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.cpu_freq = ctk.IntVar()
        self.voltage = ctk.IntVar()
        self.fan_speed = ctk.IntVar()
        self.auto_fan = ctk.BooleanVar()

        self.create_ui()
        self.load_profile("default")

    def create_ui(self):
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        title_label = ctk.CTkLabel(main_frame, text="🐾 Pi-Tuner 🐾", font=("Arial", 26, "bold"))
        title_label.pack(pady=10)

        monitoring_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        monitoring_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(monitoring_frame, text="📈 Real-Time Monitoring", font=("Arial", 20, "bold")).pack(pady=5)

        self.temp_label = ctk.CTkLabel(monitoring_frame, text="🌡️ Temp: -- °C")
        self.temp_label.pack()
        self.clock_label = ctk.CTkLabel(monitoring_frame, text="⚙️ CPU Clock: -- MHz")
        self.clock_label.pack()
        self.volt_label = ctk.CTkLabel(monitoring_frame, text="🔋 Voltage: -- mV")
        self.volt_label.pack()
        self.fan_label = ctk.CTkLabel(monitoring_frame, text="🌀 Fan Speed: -- %")
        self.fan_label.pack()

        control_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        control_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(control_frame, text="🎚️ Controls", font=("Arial", 20, "bold")).pack(pady=5)

        self.create_slider(control_frame, "CPU Frequency (MHz)", 600, 3000, self.cpu_freq)
        self.create_slider(control_frame, "Voltage (over_voltage)", 0, 6, self.voltage)
        self.create_slider(control_frame, "Fan Speed (%)", 0, 100, self.fan_speed)

        ctk.CTkCheckBox(control_frame, text="Auto Fan Control", variable=self.auto_fan).pack(pady=10)

        button_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        button_frame.pack(pady=15, fill="x")

        ctk.CTkButton(button_frame, text="✅ Apply", command=self.apply_settings).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(button_frame, text="🔄 Default Settings", command=self.restore_defaults).pack(side="left", expand=True, padx=5)

        profile_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        profile_frame.pack(pady=10, fill="x")

        ctk.CTkButton(profile_frame, text="💾 Save Profile", command=self.save_profile).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(profile_frame, text="📂 Load Profile", command=self.load_profile).pack(side="left", expand=True, padx=5)

        self.after(1000, self.update_monitoring)

    def create_slider(self, parent, text, min_val, max_val, variable):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=5, fill="x")
        ctk.CTkLabel(frame, text=text).pack(side="left")
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, variable=variable)
        slider.pack(side="right", fill="x", expand=True, padx=10)

    def update_monitoring(self):
        temp = subprocess.getoutput("vcgencmd measure_temp").replace("temp=", "")
        freq = subprocess.getoutput("vcgencmd measure_clock arm").split('=')[1]
        volt = subprocess.getoutput("vcgencmd measure_volts").replace("volt=", "")

        self.temp_label.configure(text=f"🌡️ Temp: {temp}")
        self.clock_label.configure(text=f"⚙️ CPU Clock: {int(freq)//1000000} MHz")
        self.volt_label.configure(text=f"🔋 Voltage: {volt}")
        self.fan_label.configure(text=f"🌀 Fan Speed: {self.fan_speed.get()} %")

        self.after(2000, self.update_monitoring)

    def apply_settings(self):
        self.set_cpu_freq()
        self.set_voltage()
        self.toggle_auto_fan()

        if self.voltage.get() > 0:
            subprocess.run(["sudo", "reboot"])

    def restore_defaults(self):
        self.cpu_freq.set(1500)
        self.voltage.set(0)
        self.fan_speed.set(50)
        self.auto_fan.set(True)
        self.apply_settings()

    def set_cpu_freq(self):
        freq = self.cpu_freq.get()
        subprocess.run(["sudo", "cpufreq-set", "-u", f"{freq}MHz"])

    def set_voltage(self):
        voltage = self.voltage.get()
        config_lines = ["over_voltage=0\n", "force_turbo=0\n"]
        if voltage > 0:
            config_lines = [f"over_voltage={voltage}\n", "force_turbo=1\n"]
        with open("/boot/firmware/config.txt", "w") as file:
            file.writelines(config_lines)

    def set_fan_speed(self):
        speed = int(self.fan_speed.get() * 255 / 100)
        pi.set_PWM_dutycycle(FAN_GPIO, speed)

    def toggle_auto_fan(self):
        if self.auto_fan.get():
            pi.set_PWM_dutycycle(FAN_GPIO, 0)
        else:
            self.set_fan_speed()

    def save_profile(self):
        profile = {"cpu_freq": self.cpu_freq.get(), "voltage": self.voltage.get(),
                   "fan_speed": self.fan_speed.get(), "auto_fan": self.auto_fan.get()}
        with open(CONFIG_FILE, "w") as file:
            json.dump(profile, file)

    def load_profile(self, profile_name=None):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                profile = json.load(file)
            self.cpu_freq.set(profile.get("cpu_freq", 1500))
            self.voltage.set(profile.get("voltage", 0))
            self.fan_speed.set(profile.get("fan_speed", 50))
            self.auto_fan.set(profile.get("auto_fan", True))
            self.apply_settings()

if __name__ == "__main__":
    app = PiTunerApp()
    app.mainloop()
