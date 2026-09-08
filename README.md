==================================================
APL TEST MANAGER v2.0 - INSTRUCCIONES DE INSTALACIÓN
==================================================

1. INSTALAR PYTHON
   - Descargar: https://python.org/downloads
   - MARCAR "Add Python to PATH"

2. INSTALAR GIT
   - Descargar: https://git-scm.com/download/win

3. CLONAR REPOSITORIO
   git clone https://github.com/Evaristo-2003/apl-test-manager.git
   cd apl-test-manager

4. INSTALAR DEPENDENCIAS
   pip install -r requirements.txt

5. EJECUTAR
   python app.py

==================================================
SOLUCIÓN DE PROBLEMAS
==================================================

ERROR: pip no se reconoce
  python -m ensurepip --upgrade

ERROR: PySide6 no se instala
  pip install PySide6==6.4.0

ERROR: No module named 'core'
  cd C:\ruta\donde\esta\apl-test-manager
  python app.py

==================================================
COMANDOS ÚTILES
==================================================

Subir cambios a GitHub:
  git add .
  git commit -m "Descripción"
  git push

Traer cambios de GitHub:
  git pull

==================================================
