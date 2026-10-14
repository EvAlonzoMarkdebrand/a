# GUÍA DE PUBLICACIÓN EN PYTHONANYWHERE PARA JUGADORES ONLINE
## CYBER SMASH ARENA

Esta guía te explica paso a paso cómo subir y activar el servidor de multijugador online en **PythonAnywhere** de forma 100% gratuita para que cualquier amigo pueda jugar contigo por internet.

---

### PASO 1: Crear una cuenta gratuita en PythonAnywhere
1. Ve a [https://www.pythonanywhere.com](https://www.pythonanywhere.com).
2. Haz clic en **Pricing & Sign Up** y elige la opción **Create a Beginner Account** (gratuita).
3. Tu nombre de usuario determinará tu URL pública:
   - Ejemplo: si tu usuario es `evergame`, tu URL será:
     `https://evergame.pythonanywhere.com`

---

### PASO 2: Subir los archivos del proyecto a PythonAnywhere
Puedes subir los archivos desde la pestaña **Files** o usando la consola Bash de PythonAnywhere:

#### Opción Rápida (Consola Bash en PythonAnywhere):
1. En el Dashboard de PythonAnywhere, abre una consola **Bash**.
2. Clona o sube tu carpeta:
   ```bash
   git clone <URL_DE_TU_REPOSITORIO> a
   # O crea la carpeta
   mkdir -p a
   ```
3. Si los subes manualmente desde la pestaña **Files**:
   - Sube `app.py` y `wsgi.py` en `/home/tuusuario/a/`.
   - Crea las subcarpetas `templates/` y `static/` y sube `templates/index.html`, `static/style.css` y `static/game.js`.

---

### PASO 3: Configurar la Web App en PythonAnywhere
1. En el menú superior de PythonAnywhere, ve a la pestaña **Web**.
2. Haz clic en **Add a new web app**.
3. Selecciona **Manual configuration** (o Flask) y elige **Python 3.10** o **Python 3.11**.
4. Una vez creada la web app, en la sección **Code**:
   - **Source code**: pon la ruta de tu proyecto, por ejemplo:
     `/home/tuusuario/a`
   - **Working directory**:
     `/home/tuusuario/a`
5. En la sección **WSGI configuration file**:
   - Haz clic en el enlace (se abrirá un editor con un archivo que termina en `_wsgi.py`).
   - Borra todo su contenido y pega lo siguiente:
     ```python
     import sys
     import os

     # Reemplaza 'tuusuario' por tu nombre de usuario real en PythonAnywhere:
     path = '/home/tuusuario/a'
     if path not in sys.path:
         sys.path.insert(0, path)

     from app import application
     ```
   - Haz clic en el botón verde **Save** arriba a la derecha.

---

### PASO 4: Recargar el Servidor
1. Vuelve a la pestaña **Web**.
2. Haz clic en el botón verde grande: **Reload tuusuario.pythonanywhere.com**.
3. ¡Listo! Abre tu navegador y visita:
   `https://tuusuario.pythonanywhere.com`
   - Verás la interfaz web de Cyber Smash Arena con el estado **ONLINE** en verde.

---

### PASO 5: Conectarse desde el juego de Python (Pygame)
1. Abre tu juego de escritorio:
   ```bash
   python gemini-code-1791990527364.py
   ```
2. En el menú principal, haz clic en **MULTIJUGADOR ONLINE (PythonAnywhere)**.
3. Introduce la URL de tu servidor:
   `https://tuusuario.pythonanywhere.com`
   *(También puedes probarlo en local usando `http://127.0.0.1:5000` si ejecutas `python app.py` en tu PC)*.
4. Un jugador hace clic en **CREAR SALA** y recibirá un código de 4 dígitos (ejemplo: `CYBER-4892`).
5. El segundo jugador introduce ese código y hace clic en **UNIRSE**.
6. Ambos eligen su personaje, pulsan **LISTO**, ¡y la partida online comenzará a 60 FPS!
