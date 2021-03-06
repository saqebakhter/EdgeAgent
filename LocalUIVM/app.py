from flask import Flask, render_template, request, redirect,url_for
from flask_assets import Bundle, Environment
from flask import send_file

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



# db = dataset.connect('sqlite:///tmp/database.db')

print('=================')
print(dir_path)




@app.route('/')
def getIndex():

    data = {}
    data['currentVMK0'] = '192.168.20.1'
    return render_template('networking.html', table=data)

@app.route('/sdwan')
def getSDWANIndex():

    data = {}
    data['currentStatus'] = 'Not Deployed'
    return render_template('sdwan.html', table=data)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
