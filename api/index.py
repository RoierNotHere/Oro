from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
            url = "https://tradingeconomics.com/commodities"
            res = scraper.get(url, timeout=10)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                fila = soup.find('tr', {'data-symbol': 'XAUUSD:CUR'})
                
                if fila:
                    precio_raw = fila.find('td', id='p').text.strip().replace(',', '')
                    precio_onza = float(precio_raw)
                    
                    # Cálculo exacto por gramo
                    precio_gramo = round(precio_onza / 31.1034768, 2)
                    
                    payload = {
                        "material": "Oro (Gramos)",
                        "precio": f"{precio_gramo} USD",
                        "precio_onza_ref": f"{precio_onza} USD",
                        "status": "success"
                    }
                    status_code = 200
                else:
                    payload = {"error": "No se encontró el precio en la fuente"}
                    status_code = 404
            else:
                payload = {"error": f"Error del sitio origen: {res.status_code}"}
                status_code = res.status_code

        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return
