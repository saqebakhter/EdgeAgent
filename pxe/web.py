# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from getmac import get_mac_address

hostName = "0.0.0.0"
serverPort = 8090


class db_dict():
    def __init__(self):
        self.db = {
            "00:11:22:33:44:55": {
                "bootproto": "static",
                "bootdevice": "vmnic0",
                "ipaddr": "10.115.37.207",
                "netmask": "255.255.255.0",
                "gateway": "10.115.37.253",
                "dns": ["10.115.37.201", "10.20.145.1", "10.33.4.1"],
                "hostname": "nested-esxi5",
                "license": ""
            },
            "00:50:56:ba:97:21": {
                "bootproto": "static",
                "bootdevice": "vmnic0",
                "ipaddr": "192.168.20.200",
                "netmask": "255.255.255.0",
                "gateway": "192.168.20.1",
                "dns": ["192.168.20.70"],
                "hostname": "esxi-1a",
                "license": ""
            },
            "00:50:56:ba:97:22": {
                "bootproto": "static",
                "bootdevice": "vmnic0",
                "ipaddr": "192.168.20.201",
                "netmask": "255.255.255.0",
                "gateway": "192.168.20.1",
                "dns": ["192.168.20.70"],
                "hostname": "esxi-1b",
                "license": ""
            },
            "00:50:56:ba:97:23": {
                "bootproto": "static",
                "bootdevice": "vmnic0",
                "ipaddr": "192.168.20.202",
                "netmask": "255.255.255.0",
                "gateway": "192.168.20.1",
                "dns": ["192.168.20.70"],
                "hostname": "esxi-2a",
                "license": ""
            },
            "00:50:56:ba:97:24": {
                "bootproto": "static",
                "bootdevice": "vmnic0",
                "ipaddr": "192.168.20.203",
                "netmask": "255.255.255.0",
                "gateway": "192.168.20.1",
                "dns": ["192.168.20.70"],
                "hostname": "esxi-2b",
                "license": ""
            },

        }

    def lookup(self, mac):
        if mac not in self.db:
            return self.db["00:11:22:33:44:55"]
        return self.db[mac]


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Base on the URL we respond
        if self.path == "/getks":
            ks = self.__get_ks()
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

    def __get_ks(self):
        client_addr = self.client_address[0]
        client_mac = get_mac_address(ip=client_addr)
        db = db_dict()
        db_out = db.lookup(client_mac)
        print(client_addr)
        print(client_mac)
        if db_out is None:
            # To-do, probably return 404 Not Found
            pass
        db_out["dns1"] = db_out["dns"][0]

        # Build the network config line based on the address type
        network_config = "network --bootproto={bootproto} --device={bootdevice}".format(**db_out)
        if db_out["bootproto"] == "static":
            network_config += " --ip={ipaddr} --netmask={netmask} --gateway={gateway} --nameserver={dns1} --hostname={hostname} --addvmportgroup=0".format(
                **db_out)

        # Build the additional network config needed as part of firstboot
        post_network_config = ""
        if len(db_out["dns"]) > 1:
            for dns in db_out["dns"][1:]:
                post_network_config += "esxcli network ip dns server add -s %s\n" % dns

        ks = '''        
            #
            # Sample scripted installation file
            #

            # Accept the VMware End User License Agreement
            vmaccepteula

            # Set the root password for the DCUI and Tech Support Mode
            rootpw VeloCloud123$

            # Install on the first local disk available on machine
            clearpart --alldrives --overwritevmfs
            install --firstdisk --overwritevmfs
        ''' + "\n" + network_config + "\n" + '''

            # Reboot ESXi host
            reboot

            # A sample post-install script
            %firstboot --interpreter=busybox 
            esxcli system maintenanceMode set -e true
            esxcli system settings advanced set -o /UserVars/SuppressShellWarning -i 1
            vim-cmd hostsvc/enable_ssh
            vim-cmd hostsvc/start_ssh
            
            esxcli software acceptance set --level CommunitySupported
            wget 'http://192.168.20.71/getVIB' -O /tmp/edgeagent.zip
            esxcli software vib install -d /tmp/edgeagent.zip -f

        ''' + "\n" + post_network_config + "\n"
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

