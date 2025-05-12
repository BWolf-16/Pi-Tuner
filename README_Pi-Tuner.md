
# Pi-Tuner ⚙️🐾

**Pi-Tuner** is a sleek system tuning and monitoring tool for **Raspberry Pi 5**, inspired by MSI Afterburner. It lets you keep an eye on temps, clocks, voltages — and adjust them with style! Save your favorite setups as profiles and swap them on the fly.  

## Features ✨

- **Live Monitoring** 📊
  - 🌡️ CPU Temperature
  - ⚡ Clock Speed (MHz)
  - 🔋 Voltage (V)
  - 🌀 Fan Speed (% — simulated unless hardware is available)

- **Manual Tuning** 🎛️
  - 🔧 Adjust CPU Clock Frequency
  - 🪫 Adjust Voltage (Visual Only)
  - 🌀 Adjust Fan Speed (Visual Only)

- **Profile Manager** 💾
  - 📁 Save & Load custom profiles
  - 🔄 Apply or Reset settings with one click

## Requirements 📦

Make sure these are installed:
```bash
sudo apt update
sudo apt install cpufrequtils libraspberrypi-bin
pip install customtkinter
```

## How to Run ▶️

```bash
python3 pi_tuner.py
```

## Notes 📝

- Fan and voltage control are **simulated** unless your setup supports I2C, GPIO, or kernel drivers.
- Profiles are saved in `pi5_profiles.json`.

## Screenshot 🖼️

_Coming soon..._

---

Made with love for **Master** by your loyal demon kitty.  
**Meow~** 🖤🐱‍👤
