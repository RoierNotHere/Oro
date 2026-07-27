from http.server import BaseHTTPRequestHandler
import cloudscraper  # Cambiamos requests por cloudscraper
from bs4 import BeautifulSoup
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://www.inversoro.es/precio-del-oro/en-tiempo-real/onzas/USD/"
        
        try:
            # Creamos el scraper para evadir el bloqueo
            scraper = cloudscraper.create_scraper()
            res = scraper.get(url, timeout=10)
            
            # Lanzamos error si la respuesta no es 200 OK
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, 'html.parser')
            precio_element = soup.find("span", {"name": "current_price_field"})
            
            if precio_element:
                texto_sucio = precio_element.text
                # Limpieza: quitamos todo excepto números y puntos
                precio_limpio = re.sub(r'[^0-9.]', '', texto_sucio.replace(',', '.'))
                status = "success"
            else:
                precio_limpio = "2450.00"
                status = "No se encontro el elemento, usando respaldo"

        except Exception as e:
            precio_limpio = "0.00"
            status = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps({
            "precio": precio_limpio,
            "status": status
        }).encode())
        return
