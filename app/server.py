from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import socket
from datetime import datetime

PORT = 8080


class InventoryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            if os.path.exists("/tmp/ready"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"READY")
            else:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"NOT READY")
            return

        if self.path == "/inventory":
            pod_name = socket.gethostname()

            response = (
                f"Inventory response from Pod: {pod_name}\n"
                f"Time: {datetime.now().isoformat()}\n"
                f"Item: laptop\n"
                f"Quantity available: 25\n"
            )

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(response.encode())
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}", flush=True)


if __name__ == "__main__":
    open("/tmp/ready", "w").close()

    server = HTTPServer(("0.0.0.0", PORT), InventoryHandler)
    print("Inventory server running on port 8080", flush=True)
    server.serve_forever()