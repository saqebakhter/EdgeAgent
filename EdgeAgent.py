import os
import logging
import sys, time
from daemon3x import daemon
import subprocess
from urllib import request, parse
import json

logFile = '/tmp/EdgeAgent.log'
EdgeRegistrar = 'http://mockbin.org/bin/c890afbc-2e85-4c89-92ab-e606ce9e8f33'
logging.basicConfig(filename=logFile,level=logging.DEBUG)


class MyDaemon(daemon):
    def getVMKIp(self):
        logging.debug('get vmkip')
        process = subprocess.Popen(['/bin/esxcli --debug --formatter=json network ip interface ipv4 get'],
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        logging.debug(stdout)
        parsedList = json.loads(stdout)
        for interface in parsedList:
            if interface['Name'] == 'vmk0':
                return interface['IPv4Address']

    def run(self):
        while True:
            timestamp = int(time.time())
            vmk0Ip = self.getVMKIp()
            logging.debug('Edge Agent is running now ' + str(timestamp) + ' : ' + vmk0Ip)
            payload = {'ipAddress': vmk0Ip}
            encoded_data = json.dumps(payload).encode('utf-8')

            req = request.Request(EdgeRegistrar, data=encoded_data)
            resp = request.urlopen(req)

            time.sleep(30)



if __name__ == "__main__":
    daemon = MyDaemon('/tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print ("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print ("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
