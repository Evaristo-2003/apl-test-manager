#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de inicio para APL Test Manager"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Crear directorio de logs si no existe
Path("logs").mkdir(exist_ok=True)

# Importar y ejecutar la aplicación
from app import main

if __name__ == "__main__":
    # Ejecutar desde app.py
    from app import main
    main()