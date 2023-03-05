import http.server
import socketserver
import os


filepath = "testfile1GB"
PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler
if not os.path.exists(filepath):
    open(filepath, "w").write("A" * 1024**3)
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
