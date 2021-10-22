import subprocess
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect, SmartConnectNoSSL
import atexit
import os

from tools import tasks


def get_ssl_thumbprint(host_ip):
    p1 = subprocess.Popen(('echo', '-n'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(('openssl', 's_client', '-connect', '{0}:443'.format(host_ip)), stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p3 = subprocess.Popen(('openssl', 'x509', '-noout', '-fingerprint', '-sha1'), stdin=p2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p3.stdout.read()
    ssl_thumbprint = out.split(b'=')[-1].strip()
    return ssl_thumbprint.decode("utf-8")


class VMWareClient:
    def __init__(self, host, user, password, port=443, insecure=True):
        if insecure:
            self._service_instance = SmartConnectNoSSL(host=host, user=user, pwd=password, port=port)
        else:
            self._service_instance = SmartConnect(host=host, user=user, pwd=password, port=port)
        self._host = host
        self._user = user
        self._password = password
        atexit.register(Disconnect, self._service_instance)
        self._content = self._service_instance.RetrieveContent()

    def get_obj(self, content, vimtype, name=None):
        return [item for item in content.viewManager.CreateContainerView(
            content.rootFolder, [vimtype], recursive=True).view]


    def find_cluster(self, name):

        cluster_obj = None
        for cluster_obj in self.get_obj(self._content, vim.ComputeResource, name):
            if cluster_obj.name == name:
                return cluster_obj


    def find_datacenter(self, name):
        # A list comprehension of all the root folder's first tier children...
        datacenters = [entity for entity in self._content.rootFolder.childEntity
                       if hasattr(entity, 'vmFolder')]

        dcVal = None
        for dc in datacenters:
            if dc.name == name:
                dcVal = dc
                return dcVal


    def create_datacenter(self, name):
        folder = self._content.rootFolder
        return folder.CreateDatacenter(name=name)

    def create_cluster(self, name, datacenter):
        host_folder = datacenter.hostFolder
        cluster_spec = vim.cluster.ConfigSpecEx()
        return host_folder.CreateClusterEx(name=name, spec=cluster_spec)

    def add_host_to_vc(self, host_ip, host_username, host_password, datacenter_name, cluster_name):
        host_connect_spec = vim.host.ConnectSpec()
        host_connect_spec.hostName = host_ip
        host_connect_spec.userName = host_username
        host_connect_spec.password = host_password
        host_connect_spec.force = True
        host_connect_spec.sslThumbprint = get_ssl_thumbprint(host_ip)
        datacenter = self.find_datacenter(datacenter_name)
        cluster = self.find_cluster(cluster_name)
        if not cluster:
            cluster = self.create_cluster(cluster_name, datacenter)

        add_host_task = cluster.AddHost(spec=host_connect_spec, asConnected=True)
        tasks.wait_for_tasks(self._service_instance, [add_host_task])



if __name__ == '__main__':
    vcenter_ip = os.environ['vCenter']
    vcenter_username = 'administrator@vsphere.local'
    vcenter_password = os.environ['vcenter_password']

    datacenter_name = 'Datacenter'
    cluster_name = 'EdgeCluster-2'

    vmware_client = VMWareClient(vcenter_ip, vcenter_username, vcenter_password)
    datacenter = vmware_client.find_datacenter('Datacenter')
    # A list comprehension of all the root folder's first tier children...


    cluster = vmware_client.find_cluster('Edge-1')
    if not cluster:
        vmware_client.create_cluster(cluster_name, datacenter)