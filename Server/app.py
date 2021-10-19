from flask import Flask, render_template, request, redirect,url_for
from flask_assets import Bundle, Environment

import dataset
import os
import urllib3
import configparser
import time
import subprocess

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL

from tools import tasks

from VMwareClient import VMWareClient

urllib3.disable_warnings()


app = Flask(__name__)
app.secret_key = "super secret key"

env = Environment(app)
js = Bundle('https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js', 'https://code.jquery.com/ui/1.12.1/jquery-ui.js' ,'js/clarity-icons.min.js', 'js/clarity-icons-api.js',
            'js/clarity-icons-element.js', 'js/custom-elements.min.js', 'js/backup.js')
env.register('js_all', js)

css = Bundle('css/modal.css', 'css/clarity-ui.min.css', 'css/clarity-icons.min.css')
env.register('css_all', css)

dir_path = os.path.dirname(os.path.realpath(__file__))



# Configuration
config = configparser.ConfigParser()
config.sections()

config.read('config.ini')

VCO_FQDN = config['DEFAULT']['VCO_FQDN']
VCO_USERNAME = config['DEFAULT']['VCO_USERNAME']
VCO_PASSWORD = config['DEFAULT']['VCO_PASSWORD']
VCO_ENTERPRISE = config['DEFAULT'].getboolean('VCO_ENTERPRISE')



# db = dataset.connect('sqlite:///tmp/database.db')

print('=================')
print(dir_path)




@app.route('/')
def listEdgeCompute():

    db = dataset.connect('sqlite:///' + dir_path + '/database.db')

    table = db['edgeList']
    edges = table.all()

    return render_template('enterprises.html', table=edges)


@app.route('/enterprise/<int:enterpriseId>')

def listEdges(enterpriseId):

    if VCO_ENTERPRISE:
        resp = vcoClient.call_api("enterprise/getEnterpriseEdgeList",{})

    else:
        resp = vcoClient.call_api("enterprise/getEnterpriseEdgeList", {
            "enterpriseId": enterpriseId,
        })



    table = db['edgeList']
    for edge in resp:
        table.upsert(dict(enterpriseId=enterpriseId, edgeId=edge['id'], edgeName=edge['name']), ['enterpriseId', 'edgeId'])


    if VCO_ENTERPRISE:
        profileResp = vcoClient.call_api("enterprise/getEnterpriseConfigurationsPolicies", {})

    else:
        profileResp = vcoClient.call_api("enterprise/getEnterpriseConfigurationsPolicies", {
            "enterpriseId": enterpriseId,
        })


    table = db['profileList']
    for profile in profileResp:
        table.upsert(dict(enterpriseId=enterpriseId, profileId=profile['id'], profileName=profile['name']), ['enterpriseId', 'profileId'])

    table = db['enterpriseList']
    enterprise = table.find_one(enterpriseId=enterpriseId)

    if enterprise == None:
        enterprise = {}
        enterprise['name'] = 'Enterprise'

    return render_template('edges.html', profiles=profileResp, enterpriseId=enterpriseId, table=resp, enterprise=enterprise)



@app.route('/edge/heartbeat', methods=[ 'POST'])
def edgeHeartBeat():
    db = dataset.connect('sqlite:///' + dir_path + '/database.db')

    data = request.json
    edgeIp = data['ipAddress']
    table = db['edgeList']
    edge = table.find_one(edgeIp=edgeIp)
    print(edge['edgeName'], edge['edgeIp'] + ' ' + 'found')

    timestamp = int(time.time())
    edge['lastHeartBeat'] = timestamp
    registeredVc = edge['registeredVc']
    print(registeredVc)
    if not registeredVc:
        print('Registering ' + edgeIp + ' to vc')
        vcenter_ip = edge['vCenter']
        vcenter_username = 'administrator@vsphere.local'
        vcenter_password = os.environ['vcenter_password']

        esxi_host_ip = edgeIp
        esxi_host_username = 'root'
        esxi_host_password = os.environ['esxi_host_password']

        datacenter_name = 'Datacenter'
        cluster_name = 'EdgeCluster'

        vmware_client = VMWareClient(vcenter_ip, vcenter_username, vcenter_password)
        vmware_client.add_host_to_vc(esxi_host_ip, esxi_host_username, esxi_host_password, datacenter_name,
                                     cluster_name)

        edge['registeredVc'] = True
        table.upsert(edge, ['edgeName', 'edgeIp'])

    table.upsert(edge, ['edgeName', 'edgeIp'])

    return 'Done'
    # return render_template('profileBackups.html', profileName=profile['profileName'], enterprise=enterprise, backups=list(backups), modules=modules, enterpriseId=enterpriseId, profileId=profileId)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
