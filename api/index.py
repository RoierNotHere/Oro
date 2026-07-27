from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import json
import re
import random
import time

# Lista de User-Agents reales para rotar en cada petición
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (X11; Linux x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        target_url = "https://www.inversoro.es/precio-del-oro/en-tiempo-real/gramos/USD/"
        
        # 1. Retardo aleatorio entre 1.5 y 3.5 segundos para no parecer bot
        time.sleep(random.uniform(1.5, 3.5))
        
        # 2. Construimos cabeceras completas de un navegador real
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
        try:
            # 3. Timeout de 10s para la respuesta de la petición
            res = requests.get(target_url, headers=headers, timeout=10)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, 'html.parser')
            precio_element = soup.find("span", {"name": "current_price_field"})
            
            if precio_element:
                texto_sucio = precio_element.text
                texto_con_punto = texto_sucio.replace(',', '.')
                precio_limpio = re.sub(r'[^0-9.]', '', texto_con_punto)
                status = "success"
            else:
                precio_limpio = "0.00"
                status = "No se encontro el elemento span"

        except Exception as e:
            precio_limpio = "0.00"
            status = str(e)

        # Respuesta JSON en Vercel
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps({
            "precio": precio_limpio,
            "status": status
        }).encode('utf-8'))
        return
