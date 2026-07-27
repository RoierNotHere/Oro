from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time
import re

# Caché global en memoria para Serverless (Vercel)
cache_oro = {
    "datos": {},
    "timestamp": 0
}

class handler(BaseHTTPRequestHandler):

    def intentar_scrape(self):
        # URL exacta para consultar el precio del oro en gramos (USD)
        url = "https://www.inversoro.es/precio-del-oro/en-tiempo-real/gramos/USD/"
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        ]

        # Instancia de cloudscraper optimizada
        scraper = cloudscraper.create_scraper(
            delay=5,
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/',
            'Sec-Fetch-Mode': 'navigate'
        }

        try:
            res = scraper.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Buscamos el selector exacto del precio: <span name="current_price_field">
                precio_element = soup.find("span", {"name": "current_price_field"})
                
                if precio_element:
                    # 1. Obtenemos el texto original (ej. "131,54\xa0$")
                    texto_sucio = precio_element.text.strip()
                    
                    # 2. Reemplazamos la coma por el punto decimal
                    texto_con_punto = texto_sucio.replace(',', '.')
                    
                    # 3. Limpiamos para dejar solo dígitos y el punto decimal
                    precio_limpio = re.sub(r'[^0-9.]', '', texto_con_punto)
                    
                    return {"precio": precio_limpio, "status": "success"}
                else:
                    return {"precio": "0.00", "status": "No se encontro el elemento span"}
            else:
                return {"precio": "0.00", "status": f"Error {res.status_code}"}

        except Exception as e:
            return {"precio": "0.00", "status": f"Error: {str(e)}"}

    def do_GET(self):
        global cache_oro
        
        ahora = time.time()
        TIEMPO_CACHE = 1800  # 30 minutos
        
        # Comprobar si la caché tiene datos válidos recientes
        if cache_oro["datos"] and (ahora - cache_oro["timestamp"] < TIEMPO_CACHE):
            resultado = cache_oro["datos"]
            fuente = "cache"
        else:
            resultado = self.intentar_scrape()
            
            # Solo guardamos en caché si la extracción fue exitosa
            if resultado.get("status") == "success":
                cache_oro["datos"] = resultado
                cache_oro["timestamp"] = ahora
            fuente = "real-time"

        # Encabezados de respuesta JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        res_json = {
            "precio": resultado.get("precio", "0.00"),
            "status": resultado.get("status", "unknown"),
            "fuente": fuente,
            "timestamp": int(ahora)
        }
        
        self.wfile.write(json.dumps(res_json).encode('utf-8'))
        return
