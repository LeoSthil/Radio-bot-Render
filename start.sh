#!/usr/bin/env bash

# Actualizar paquetes e instalar ffmpeg (necesario para audio en Discord)
apt-get update && apt-get install -y ffmpeg

# Ejecutar el bot
python3 main.py
