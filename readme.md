# ☠️This is in Beta, please use under your own responsibility☠️

I will redo everything from 0 please wait for an update :)

# Pi-Tuner 🐾

A complete, real-time tuning tool for your Raspberry Pi 5 — with true fan, clock, and voltage control. Inspired by MSI Afterburner, built to serve your system with power and style.

## Features 💡

- 📈 Real-Time Monitoring
  - 🌡️ Temperature
  - ⚙️ CPU Clock
  - 🔋 Voltage
  - 🌀 Fan Speed

- 🎚️ Manual Controls
  - Set CPU clock with `cpufreq-set`
  - Adjust voltage with `over_voltage` + `force_turbo`
  - Fan control via GPIO18 PWM (hardware-connected fan only)

- 🔁 Auto/Manual Fan Mode
  - Toggle between firmware control and manual GPIO-based control

- 💾 Profile Support
  - Save/load custom settings
  - Default profile included
  - Restore-to-default button

- ⚙️ Auto Setup
  - Edits `/boot/firmware/config.txt` as needed
  - Uses `pigpio` or GPIO tools for fan PWM
  - Applies all settings without reboot

## Installation 🛠

```bash
sudo apt update
sudo apt install cpufrequtils libraspberrypi-bin pigpio
pip install customtkinter
```

## Usage 🚀

```bash
sudo python3 pi_tuner.py
```

## Optional: Autostart with systemd

Use `pi-tuner.service` to enable boot startup.
