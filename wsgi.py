"""
WSGI CONFIGURATION PARA PYTHONANYWHERE
======================================
Este archivo conecta PythonAnywhere con la aplicación Cyber Smash Arena.
En la pestaña 'Web' de PythonAnywhere:
1. Haz clic en el enlace del 'WSGI configuration file'.
2. Pega el contenido de este archivo o añade las siguientes líneas.
"""

import sys
import os

# Ajusta la ruta de tu proyecto en PythonAnywhere si es necesario
# Por ejemplo: /home/tuusuario/a
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importa la aplicación WSGI / Flask desde app.py
from app import application
