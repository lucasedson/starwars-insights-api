import os
import sys

from functions_framework import create_app

# Adiciona o diretório atual ao path para evitar erros de importação local
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Iniciando ambiente de desenvolvimento")

    app = create_app(target="star_wars_insights", source="main.py")

    app.run(host="0.0.0.0", port=8080, threaded=False)
