from fastapi import FastAPI
from app.main import app
from pathlib import Path

def generate_russian_docs():
    docs = []
    docs.append("<h1>🚀 API Documentation</h1>")
    docs.append("<h2>📋 Все доступные эндпоинты</h2>")
    
    for route in sorted(app.routes, key=lambda x: x.path):
        if hasattr(route, "methods"):
            methods = ", ".join(route.methods)
            docs.append(f"<div class='endpoint'>")
            docs.append(f"<h3>{methods} {route.path}</h3>")
            docs.append(f"<p>Название: {route.name}</p>")
            docs.append("</div>")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>API Documentation</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .endpoint {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; }}
            h3 {{ color: #333; }}
        </style>
    </head>
    <body>
        {''.join(docs)}
    </body>
    </html>
    """
    
    with open("API_DOCUMENTATION.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ Документация создана: API_DOCUMENTATION.html")

if __name__ == "__main__":
    generate_russian_docs()
    