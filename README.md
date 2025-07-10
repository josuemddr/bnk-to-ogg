# BNK to OGG Converter 🎵

![Python](https://img.shields.io/badge/python-v3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## Descripción

Este script en **Python** convierte archivos `.bnk` a `.ogg` para que puedas escucharlos fácilmente. Ideal para extraer audio de juegos o proyectos que usan este formato.

Integra varias herramientas potentes:  
- [bnk extractor](https://github.com/eXpl0it3r/bnkextr/releases/download/2.0/bnkextr.exe)  
- [ww2ogg](https://github.com/hcs64/ww2ogg/releases/download/0.24/ww2ogg024.zip)  
- [revorb](https://github.com/ItsBranK/ReVorb/releases/download/v1.0/ReVorb.exe)  
- [ffprobe](https://ffmpeg.org/download.html)  

Además, incluye opciones útiles como:  
- Eliminar los archivos `.wem` originales luego de la conversión.  
- Detectar y eliminar archivos `.ogg` corruptos usando `ffprobe`.  
- Descarga automática de dependencias si no se encuentran instaladas.

---

## Instalación

```bash
git clone https://github.com/tu_usuario/bnk-to-ogg.git
cd bnk-to-ogg
pip install -r requirements.txt
