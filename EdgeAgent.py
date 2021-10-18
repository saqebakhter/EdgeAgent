import os
import logging
import sys, time
from daemon3x import daemon


logFile = '/tmp/EdgeAgent.log'

logging.basicConfig(filename=logFile,level=logging.DEBUG)


class MyDaemon(daemon):
    def run(self):
        while True:
            timestamp = int(time.time())
            logging.debug('Edge Agent is running now ' + str(timestamp))
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
