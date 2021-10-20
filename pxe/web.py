# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from getmac import get_mac_address

hostName = "0.0.0.0"
serverPort = 8090

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Base on the URL we respond
        if self.path == "/getks":
            ks = self.get_ks()
            self.send_response(200)
            self.send_header("Content-type", "text")
            self.end_headers()
            self.wfile.write(bytes(ks, "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>ERROR</title></head>", "utf-8"))
            self.wfile.write(bytes("<p>Path: %s not found</p>" % self.path, "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<p></p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

    def get_ks(self):
        client_addr = self.client_address[0]
        client_mac = get_mac_address(ip=client_addr)
        print(client_addr)
        print(client_mac) 
        ks = '''        
#
# Sample scripted installation file
#

# Accept the VMware End User License Agreement
vmaccepteula

# Set the root password for the DCUI and Tech Support Mode
rootpw VeloCloud123$

# Install on the first local disk available on machine
install --firstdisk --overwritevmfs

# Set the network to DHCP on the first network adapter
network --bootproto=dhcp --device=vmnic0

# A sample post-install script
%post --interpreter=python --ignorefailure=true
import time
stampFile = open('/finished.stamp', mode='w')
stampFile.write( time.asctime() )
        '''
        return ks

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

