import bpy, http, threading, pprint, types, os
import socketserver
from mathutils import Euler
from bpy.props import * 
from bpy.types import Operator
from .websocket_server import websocket_server 

bl_info = {
    "name": "Remote 3D Navigation ",
    "author": "Laxminarayan Kamath <kamathln@gmail.com>",
    "version": (1, 2),
    "blender": (2, 57, 0),
    "location": "View3D > Tool Shelf > 3D Remote",
    "description": "Navigate the Camera & 3D View from any html5 capable device with accelerometer",
    "warning": "Uses Multi-Threading! Toy add-on!! Do Not use on production blender!",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}


rpcserver_localvars=types.ModuleType('main').__dict__
rpcserver_globalvars=globals()
rpcserver = None
tcpserver = None
wstserver = None
commands = {}

def rotate_view(x_angle,y_angle,z_angle):
    x_angle = float(x_angle)
    y_angle = float(y_angle)
    z_angle = float(z_angle)
    try:
        for view in rpcserver_localvars['views2control']:
           view.region_3d.view_rotation.rotate(Euler((x_angle,y_angle,z_angle)))
        return True
    except Exception as E:
        return pprint.pformat(E)

def move_view(x_distance,y_distance,z_distance):
    x_distance = float(x_distance)
    y_distance = float(y_distance)
    z_distance = float(z_distance)
    
    print ('distances {0}_{1}_{2}'.format(x_distance, y_distance, z_distance))
    try:
        for view in rpcserver_localvars['views2control']:
           view.region_3d.view_location += view.region_3d.view_location.__class__((x_distance, y_distance, z_distance))
           #view.region_3d.view_location.x+=x_distance
           #view.region_3d.view_location.y+=y_distance
           #view.region_3d.view_location.z+=z_distance
        return True
    except Exception as E:
        return pprint.pformat(E)
def move_camera(x_distance,y_distance,z_distance):
    x_distance = float(x_distance)
    y_distance = float(y_distance)
    z_distance = float(z_distance)
    try:
        for view in rpcserver_localvars['views2control']:
            view.camera.location+=view.camera.location.__class__((x_distance,y_distance,z_distance))
        return True
    except Exception as E:
        return pprint.pformat(E)
    
def rotate_camera(x_angle,y_angle,z_angle):
    x_angle = float(x_angle)
    y_angle = float(y_angle)
    z_angle = float(z_angle)
    try:
        for view in rpcserver_localvars['views2control']:
           view.camera.rotation_euler.x+=x_angle
           view.camera.rotation_euler.y+=y_angle
           view.camera.rotation_euler.z+=z_angle
        return True
    except Exception as E:
        return pprint.pformat(E)

def rotateabsolute_camera(x_angle,y_angle,z_angle):
    x_angle = float(x_angle)
    y_angle = float(y_angle)
    z_angle = float(z_angle)
    try:
        for view in rpcserver_localvars['views2control']:
           view.camera.rotation_euler = view.camera.rotation_euler.__class__((x_angle,y_angle,z_angle))
        return True
    except Exception as E:
        return pprint.pformat(E)

def move_selection(x_distance,y_distance,z_distance):
    x_distance = float(x_distance)
    y_distance = float(y_distance)
    z_distance = float(z_distance)
    try:
        for scene in rpcserver_localvars['scenes2control']:
           scene.objects.active.location+=scene.objects.active.location.__class__(x_distance,y_distance,z_distance)
        return True
    except Exception as E:
        return pprint.pformat(E)
    

def rotate_selection(x_angle,y_angle,z_angle):
    x_angle = float(x_angle)
    y_angle = float(y_angle)
    z_angle = float(z_angle)
    try:
        for scene in rpcserver_localvars['scenes2control']:
            scene.objects.active.rotation_euler.x+=x_angle
            scene.objects.active.rotation_euler.y+=y_angle
            scene.objects.active.rotation_euler.z+=z_angle
        return True
    except Exception as E:
        return pprint.pformat(E)

def rotateabsolute_selection(x_angle,y_angle,z_angle):
    x_angle = float(x_angle)
    y_angle = float(y_angle)
    z_angle = float(z_angle)
    try:
        for scene in rpcserver_localvars['scenes2control']:
           scene.objects.active.rotation_euler = scene.objects.active.rotation_euler.__class__((x_angle,y_angle,z_angle))
        return True
    except Exception as E:
        return pprint.pformat(E)


def handle_wscmdline(client,cmdline):
    if (str(cmdline) == 'PING'):
        wstserver.send_message(client,'PONG')
    else:
        handle_cmdline(cmdline)
def handle_cmdline(cmdline):
#    space = bytes(' ','ascii')
    print (cmdline)
        
    try:
        if (cmdline):
            params = str(cmdline).strip().split(' ')
            command=params.pop(0)
            commands[command](*params)
    except KeyError:
        print ("Warning: Unimplemented command called : {0}".format(command))
    except Exception as e:
        pprint.pprint (e)
    
    
class TCPCommandHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            cmdline = self.rfile.readline()
            if (cmdline):
                handle_cmdline(cmdline)
            else:
                break

class ServerThread(threading.Thread):
    def __init__(self,server):
        super(ServerThread,self).__init__()
        self.server = server
        self.rpcserver_localvars = rpcserver_localvars
        self.rpcserver_globalvars = rpcserver_globalvars
    def run(self):
        self.server.serve_forever()

class VIEW3D_PT_RemotePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Remote Nav"
    
    def draw(self, context):
        self.layout.prop(context.window_manager,'view_subscribed_to_remote')
        self.layout.prop(context.scene,'scene_subscribed_to_remote')



def get_view_subscription(self):
    global rpcserver_localvars
    return bpy.context.area.spaces[0] in rpcserver_localvars['views2control']

def set_view_subscription(self,value):
    global rpcserver_localvars
    if value and not get_view_subscription(self):
        rpcserver_localvars['views2control'].append(bpy.context.area.spaces[0])
    if not value and get_view_subscription(self):
        rpcserver_localvars['views2control'].remove(bpy.context.area.spaces[0])

def get_scene_subscription(self):
    global rpcserver_localvars
    return bpy.context.scene in rpcserver_localvars['scenes2control']

def set_scene_subscription(self,value):
    global rpcserver_localvars
    if value and not get_scene_subscription(self):
        rpcserver_localvars['scenes2control'].append(bpy.context.scene)
    if not value and get_scene_subscription(self):
        rpcserver_localvars['scenes2control'].remove(bpy.context.scene)


def register():
    global rpcserver
    global tcpserver 
    global wstserver
    global rpcserver_localvars 
    global rpcserver_globalvars
    global commands
    commands[b'rotateabsolute_camera'] = rotateabsolute_camera
    commands[b'rotate_camera'] = rotate_camera
    commands[b'move_camera'] = move_camera
    commands[b'rotate_view'] = rotate_view
    commands[b'move_view'] = move_view
    commands['rotateabsolute_camera'] = rotateabsolute_camera
    commands['rotate_camera'] = rotate_camera
    commands['rotate_selection'] = rotate_selection
    commands['move_camera'] = move_camera
    commands['rotate_view'] = rotate_view
    commands['move_view'] = move_view
    def debug(*args):
        print (args)
    commands['debug'] = debug
    bpy.types.WindowManager.view_subscribed_to_remote = BoolProperty(
                            name="Control View and camera",
                            description="Subscribe current view to the remote", 
                            default=0,
                            subtype="UNSIGNED", 
                            get = get_view_subscription,
                            set = set_view_subscription) 

    bpy.types.Scene.scene_subscribed_to_remote = BoolProperty(
                            name="Control Selection ",
                            description="Subscribe current view to the remote", 
                            default=0,
                            subtype="UNSIGNED", 
                            get = get_scene_subscription,
                            set = set_scene_subscription) 

    bpy.utils.register_module(__name__)
    if (not rpcserver):
        os.chdir(os.path.dirname(__file__))
        rpcserver = http.server.HTTPServer(('0.0.0.0',9000), http.server.SimpleHTTPRequestHandler)
        tcpserver = socketserver.ThreadingTCPServer(('0.0.0.0',9002),TCPCommandHandler)
        wstserver = websocket_server.WebsocketServer(9001,'0.0.0.0')
        wstserver.set_fn_message_received(lambda client,server,message: handle_wscmdline(client,message))

        rpcserver_globalvars=globals()
        rpcserver_localvars['views2control']=[]
        rpcserver_localvars['scenes2control']=[]

        rpcserver_thread=ServerThread(rpcserver)
        rpcserver_thread.daemon = False
        rpcserver_thread.start()

        tcpserver_thread=ServerThread(tcpserver)
        tcpserver_thread.daemon = False
        tcpserver_thread.start()

        wstserver_thread=ServerThread(wstserver)
        wstserver_thread.daemon = False
        wstserver_thread.start()

def unregister():
    print("stopping rpcserver")
    global rpcserver
    global tcpserver
    rpcserver.socket.close()
    rpcserver.shutdown()
    tcpserver.socket.close()
    tcpserver.server_close()
    bpy.utils.unregister_module(__name__)
