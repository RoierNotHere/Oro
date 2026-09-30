from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://www.inversoro.es/precio-del-oro/en-tiempo-real/gramos/USD/#show-chart"
        
        try:
            # Creamos el scraper imitando un navegador estándar
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
            res = scraper.get(url, timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Buscamos la etiqueta por el atributo name y data-currency
                # <span name="current_price_field" data-currency="default">133,67 $</span>
                elem_precio = soup.find('span', {'name': 'current_price_field'})
                
                if elem_precio:
                    # Limpiamos los espacios duros/raros (&nbsp; / \xa0)
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
                payload = {"error": f"Error de conexión: {res.status_code}"}
                status_code = res.status_code

        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        # Respuesta JSON para Vercel
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return
