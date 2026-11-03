import os
 
# Extensiones de archivo que queremos exportar (código fuente, configuración, etc.)
EXTENSIONES = ('.py', '.json', '.txt', '.md', '.html', '.css', '.ui', '.ini', '.yaml', '.yml')
 
# Carpetas que queremos ignorar
IGNORAR = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode', 'build', 'dist', 'logs', 'analysis_logs'}
 
def exportar(ruta_raiz, archivo_salida='proyecto_exportado.txt'):
    with open(archivo_salida, 'w', encoding='utf-8') as out:
        for raiz, dirs, archivos in os.walk(ruta_raiz):
            # Filtrar carpetas ignoradas
            dirs[:] = [d for d in dirs if d not in IGNORAR]
            
            for archivo in archivos:
                if archivo.endswith(EXTENSIONES):
                    ruta_completa = os.path.join(raiz, archivo)
                    ruta_relativa = os.path.relpath(ruta_completa, ruta_raiz)
                    
                    out.write(f"\n{'='*80}\n")
                    out.write(f"ARCHIVO: {ruta_relativa}\n")
                    out.write(f"{'='*80}\n\n")
                    
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8') as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"[ERROR AL LEER: {e}]\n")
                    out.write("\n")
 
    print(f"✅ Proyecto exportado a: {archivo_salida}")
 
if __name__ == "__main__":
    exportar('.')
 