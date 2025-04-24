# Customizable-Linux-Sleep-Scheduler

A customizable Linux sleep monitoring application that provides a new and intelligent way to manage your system’s sleep behavior — helping you keep important work running without interruptions.

This tool **prevents your computer from going to sleep** when:
- **Whitelisted applications are running**
- **CPU or RAM usage is above your defined thresholds**

And it **automatically puts your system to sleep** when:
- **You’re inactive**
- **Resource usage is low**
- **No important (whitelisted) apps are active**

It's ideal for developers, researchers, or anyone who needs their system to stay awake when running critical tasks — all while saving power when idle.

## Features

- Real-time CPU and RAM usage graph (via `matplotlib`)
- Whitelist specific apps to prevent sleep
- Adjustable idle time and resource thresholds
- Compatible with Linux
- **Includes a `run.sh` script** for one-step startup

## Installation

```bash
git clone https://github.com/Divte-Singh/Customize-Linux-Sleep-Scheduler
cd Customize-Linux-Sleep-Scheduler
pip install -r requirements.txt
chmod +x run.sh        # give execute permission
./run.sh               # start the sleep monitor
