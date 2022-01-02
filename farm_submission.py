import urllib2,urllib,json, random
import maya.cmds as cmds
def request(method,url,d=None):
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    if d:
        data = d
    else:
        data = None
    request = urllib2.Request(url, data=data)
    request.add_header("Content-Type", 'application/json')
    request.get_method = lambda: method
    try:
        connection = opener.open(request)
        print (connection)
    except Exception as e:
        print(e)
        return 'failed: ' + str(e)
    if connection.code == 200:
        data = connection.read()
        print (data)
        return [data,connection.code]
    else:
        return 'failed to connect deadline'

def submit_to_deadline(scene,frame,output,config):
    JobInfo = {
        "Name": 'test',
        #"User": "pav-33",
        "Frames": frame,
        "Comment": "",
        "Department": "",
        "Pool": config['pool'],
        "Priority": config['priority'],
        "Plugin": "MayaBatch",
        "OutputDirectory0": output,
        "BatchName":config['batch_name']
    }

    PluginInfo = {
        "ProjectPath": cmds.workspace(q=True, rd=True),
        "SceneFile": scene,
        "OutputFilePath": output,
        "Version": config['maya_version'],
        "RenderSetupIncludeLights":"1",
        "UseLegacyRenderLayers":"0",
        "StrictErrorChecking":"True",
        "Renderer":"File"
    }


    aux = []
    idOnly = False
    body = '{"JobInfo":' + json.dumps(JobInfo) + ',"PluginInfo":' + json.dumps(
        PluginInfo) + ',"AuxFiles":' + json.dumps(aux)
    if idOnly:
        body += ',"IdOnly":true'
    body += '}'
    deadlineUrl = config['dealineurl'] + 'api/jobs'
    r = request("POST",url=deadlineUrl, d=body)
    return r
