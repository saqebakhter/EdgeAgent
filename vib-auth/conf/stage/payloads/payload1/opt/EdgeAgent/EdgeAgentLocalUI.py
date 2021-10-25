from bottle import route, run, template, request, post
import subprocess
import json


def getVMKIp():
    process = subprocess.Popen(['/bin/esxcli --debug --formatter=json network ip interface ipv4 get'],
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # logging.debug(stdout)
    parsedList = json.loads(stdout)
    for interface in parsedList:
        if interface['Name'] == 'vmk0':
            return interface['IPv4Address']

def createLocalNet():

    process = subprocess.Popen(['/bin/esxcli --debug --formatter=json network vswitch standard add  --vswitch-name=vswitch2'],
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    process = subprocess.Popen(['/bin/esxcli --debug --formatter=json network vswitch standard uplink add --uplink-name=vmnic1 --vswitch-name=vswitch2'],
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()


    process = subprocess.Popen(['/bin/esxcli --debug --formatter=json network vswitch standard portgroup add --portgroup-name=local-ui --vswitch-name=vswitch2'],
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()


    process = subprocess.Popen(['/bin/esxcli --debug --formatter=json esxcli network ip interface add --interface-name=vmk2 --portgroup-name=local-ui'],
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    process = subprocess.Popen(['/bin/esxcli --debug --formatter=json network ip interface ipv4 set --interface-name=vmk2 --ipv4=192.168.2.254 --netmask=255.255.255.0 --type=static'],
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    process = subprocess.Popen(['/bin/esxcli --debug --formatter=json network ip interface tag add -i vmk2 -t Management'],
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()



@route('/')
def index():
    ip = getVMKIp()
    return '''
        <b>Current IP: {ip}</b>
        <form action="/update" method="post">
            New IP: <input name="ip" type="text" />
            New netamask: <input name="netmask" type="text" />
            New gateway: <input name="gateway" type="text" />

            <input value="update" type="submit" />
        </form>
    
    '''.format(ip=ip)

@post('/update') # or @route('/login', method='POST')
def update():
    ip = request.forms.get('ip')
    netmask = request.forms.get('netmask')
    gateway = request.forms.get('gateway')

    cmd = 'network ip interface ipv4 set --interface-name=vmk0 --ipv4={ip} --netmask={netmask} --gateway={gateway} --type=static'.format(ip=ip, netmask=netmask, gateway=gateway)
    print(cmd)
    process = subprocess.Popen(['/bin/esxcli --debug --formatter=json '+cmd],
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print('out:  '+  str(stdout))
    print('err:  '+ str(stderr))

    return 'Completed'
createLocalNet()
run(host='0.0.0.0', port=8080)