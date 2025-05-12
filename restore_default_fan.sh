#!/bin/bash
CONFIG_FILE="/boot/firmware/config.txt"

# Remove fan and clock overrides
sudo sed -i '/dtparam=fan_/d' $CONFIG_FILE
sudo sed -i '/force_turbo/d' $CONFIG_FILE
sudo sed -i '/arm_freq/d' $CONFIG_FILE
sudo sed -i '/over_voltage/d' $CONFIG_FILE

# Reset firmware fan control defaults
echo "dtparam=fan_temp0=55" | sudo tee -a $CONFIG_FILE
echo "dtparam=fan_temp1=60" | sudo tee -a $CONFIG_FILE
echo "dtparam=fan_temp2=65" | sudo tee -a $CONFIG_FILE
echo "dtparam=fan_temp3=70" | sudo tee -a $CONFIG_FILE

echo "✅ Defaults restored. Reboot required to take effect."