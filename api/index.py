from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://www.inversoro.es/precio-del-oro/en-tiempo-real/gramos/USD/#show-chart"
        
        try:
            # Creamos el scraper e imbricamos headers reales de navegador
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Referer': 'https://www.google.com/'
            }
            
            res = scraper.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Buscamos el elemento con el selector especifico
                elem_precio = soup.find('span', {'name': 'current_price_field'})
                
                if elem_precio:
                    precio_texto = elem_precio.text.replace('\xa0', ' ').strip()
                    
                    payload = {
                        "material": "Oro (Gramos)",
                        "precio": precio_texto,
                        "status": "success"
                    }
                    status_code = 200
                else:
                    payload = {"error": "No se encontró la etiqueta con el precio en el HTML"}
                    status_code = 404
            else:
                payload = {"error": f"Error del sitio origen: {res.status_code}"}
                status_code = res.status_code

        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        # Respuesta para Vercel
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return
