import dataset
import os


dir_path = os.path.dirname(os.path.realpath(__file__))
db = dataset.connect('sqlite:///'+dir_path+'/database.db')

table = db['edgeList']

edgeList = []
rangeNum = range(1, 10, 1)


for edge in rangeNum:
    edgeName = 'edge-'+str(edge)
    edgeIp = '192.168.20.10' + str(edge)

    edgeDict = {}
    edgeDict['edgeName'] = edgeName
    edgeDict['edgeIp'] = edgeIp
    edgeDict['vCenter'] = '192.168.20.59'
    edgeDict['lastHeartBeat'] = 0

    edgeList.append(edgeDict)

for edge in edgeList:
    print(edge)

    table.upsert(dict(edgeName=edge['edgeName'], edgeIp=edge['edgeIp'], vCenter=edge['vCenter'] , lastHeartBeat=edge['lastHeartBeat']   ), ['edgeName', 'edgeIp'])

