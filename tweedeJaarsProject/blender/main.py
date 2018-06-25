# run in commandline by: 
# $ ../blender.exe models/mq-9-reaper.blend --python main.py -- 600
# the 150 is optional and specifies how many images you want from the program
# this amount includes the different backgrounds
import sys, os, argparse
import addon_utils
import bpy, math, bpy_extras
from math import pi, ceil
from mathutils import Vector, Matrix

# globals the user can change
try:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]
    pictures = int(argv[0])
    if pictures > 100000:
        exit("Please enter a picture amount under 100000.")
    elif pictures <= 0:
        exit("Picture amount must be positive")
except ValueError:
    pictures = 500

# dronetype = sys.argv[2]
# dronetype = dronetype.replace(".blend","").replace("models/","").upper()
# voor op de server moet deze
dronetype = sys.argv[2]
dronetype = dronetype.replace(".blend","").replace("static\\models\\","").upper()

# globals backgrounds
bpy.context.scene.render.image_settings.file_format = 'JPEG'
base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
background_directorys = []
for image in os.listdir(os.path.join(base_dir, "blender/static", "background_images").replace("\\", "/")):
    background_directorys.append(os.path.join(base_dir, "blender/static", "background_images", image).replace("\\", "/"))

bounding_box_image = os.path.join(base_dir, "blender/static", "bounding_box_image", "black.jpg").replace("\\", "/")
bounding_box_amount = [round(pictures/(len(background_directorys)+1)), 0]

# divide by backgrounds/model locations/rotations/sun_locations/scales
internal_amount = ceil(pictures / ((len(background_directorys)+1) * 5 * 3 * 5)) + 1
camera = 'Camera.001'
model = 'drone_group'
light_type = 'LAMP'

def scale_model(item):
    rv = 0.4
    bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.object.select_by_type(type='MESH')
    #bpy.data.objects['black'].select = False
    for ob in bpy.context.selected_objects:
        ob.location = (0,0,0)
    bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0,0,0))
    bpy.context.active_object.name = item

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    #bpy.data.objects['black'].select = False
    scn = bpy.context.scene
    for ob in bpy.context.selected_objects:
        scn.objects.active = scn.objects[ob.name]
        bpy.data.objects[ob.name].parent = bpy.data.objects[item]
    ob = bpy.context.scene.objects[item]
    ob.rotation_euler = (90*(math.pi/180), 180*(math.pi/180), -90*(math.pi/180))
    bpy.ops.object.select_all(action='DESELECT')   
    scene = bpy.context.scene
    currentCameraObj = bpy.data.objects[camera]

    scene.camera = currentCameraObj
    
    scene.update()
    bpy.context.scene.camera = currentCameraObj
    for ob in bpy.data.objects[model].children:
        ob.select = True
    bpy.ops.view3d.camera_to_view_selected()
    bpy.ops.transform.resize(value=(rv, rv, rv))

# removes the present cameras
def remove_cameras(item):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if 'camera' in ob.name.lower():
            ob.select = True
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type=item)
    bpy.ops.object.delete()

# Adding empty to add object constraint for camera
def add_empty():
    o = bpy.data.objects.new("empty", None)
    bpy.context.scene.objects.link(o)
    o.empty_draw_size = 2
    o.empty_draw_type = 'PLAIN_AXES'

# Adds camera point to empty and deletes contraint after
def add_camera():
    context = bpy.context
    bpy.ops.object.camera_add(view_align=False,
                              location=[4, 0, 3],
                              rotation=[0.5*pi, -0.25*pi, pi])
    cam = context.object
    cam.name = camera
    ttc = bpy.data.objects[camera].constraints.new(type='TRACK_TO')
    ttc.target = bpy.data.objects['empty']
    ttc.track_axis = 'TRACK_NEGATIVE_Z'
    ttc.up_axis = 'UP_Y'
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[camera].select = True
    bpy.ops.object.visual_transform_apply()
    bpy.data.objects[camera].constraints.remove(ttc)

# Add background
def add_background(background_loc):
    bpy.ops.import_image.to_plane(
        files=[{'name': os.path.basename(background_loc)}],
        directory = os.path.dirname(background_loc))
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[os.path.basename(background_loc).replace(".jpg", "")].select = True
    bpy.ops.transform.resize(value=(1.5, 1.5, 1.5))
    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
    bpy.context.object.active_material.use_shadeless = True

    ttc = bpy.data.objects[os.path.basename(background_loc).replace(".jpg", "")].constraints.new(type='TRACK_TO')
    ttc.target = bpy.data.objects[camera]
    ttc.track_axis = 'TRACK_Z'
    ttc.up_axis = 'UP_Y'
    bpy.ops.object.visual_transform_apply()
    context = bpy.context
    obj = context.active_object 
    obj.location = (-1.6, 0.0, -1.1)

# add a source of light
def add_sun(sun_loc_nr, item):
    locations = [[-2.0, 3.5, 2.75], [-3.0, 0.0, 1.5], [1.8, -2.0, 1.1], [-0.4, -0.1, 8], [2.3,-1.75,-1]]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type=item)
    bpy.ops.object.delete()
    bpy.ops.object.lamp_add(type='POINT', radius = 1, view_align= False, location = locations[sun_loc_nr])

# scales the main model in a percentage
def scale(x):
   bpy.ops.object.select_all(action='DESELECT')
   bpy.data.objects[model].select = True
   bpy.ops.transform.resize(value=(x, x, x)) 

# changes the background, input the new directory and the old name
def change_background(new_direc, old_name):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[old_name].select = True
    bpy.ops.object.delete()
    add_background(new_direc)   

# loops through the different backgrounds and depending on the amount of pictures
# you gave, makes an amount of rotated pictures on 5 locations on the image
# and writes those images to the file 'frames' in the Blender folder
def main():
    bpy.ops.object.select_all(action='DESELECT')
    ob = bpy.context.scene.objects[model]
    rotate_by = round(360/internal_amount)
    start_angle = 90
    ob.rotation_euler = (90*(math.pi/180), 180*(math.pi/180), -90*(math.pi/180))
    
    # bounding_box = [bounding_box_amount[0],bounding_box_amount[1]+counter]
    # loop over the backgrounds in the background folder, the first loop is for the bounding box pictures
    for z in range(len(background_directorys) + 1):
        counter = 0
        if z == 0:
            bpy.ops.object.select_all(action='DESELECT')
            for item in bpy.data.materials:
                item.use_shadeless = True
        elif z == 1:
            bpy.ops.object.select_all(action='DESELECT')
            for item in bpy.data.materials:
                item.use_shadeless = False
            change_background(background_directorys[z-1], "black")
        elif z >= 2:
            change_background(background_directorys[z-1], os.path.basename(background_directorys[z-2]).replace(".jpg", ""))

        # loop over the 5 sun locations
        for i in range(5):
            add_sun(i, light_type)

            # loop over the different model locations
            for y in range(5):
                model_locations = [(0, 0, 0), (0, 0.15, 0), (0, 0, 0.05), (0, -0.15, 0), (0.05, 0, 0)]
                ob.location = model_locations[y]
                for x in range(1, internal_amount):
                    counter += 1
                    angle = (start_angle * (math.pi/180)) + (x*-1) * (rotate_by * (math.pi/180))
                    ob.rotation_euler = (angle, 0, 0)
                    bpy.context.scene.camera = bpy.data.objects[camera]
                    if z == 0:
                        bpy.context.scene.render.filepath = os.path.join(base_dir, "Blender", "frames", "B_%s_FRAME_%d.jpg" % (dronetype, counter))
                    else:
                        bpy.context.scene.render.filepath = os.path.join(base_dir, "images", "B_%s_FRAME_%d_%d.jpg" % (dronetype, z, counter))
                    bpy.ops.render.render(write_still=True, use_viewport=True)

                for x in range(1, internal_amount):
                    counter += 1
                    angle = (start_angle * (math.pi/180)) + (x*-1) * (rotate_by * (math.pi/180))
                    ob.rotation_euler = (0, angle, 0)
                    bpy.context.scene.camera = bpy.data.objects[camera]
                    if z == 0:
                        bpy.context.scene.render.filepath = os.path.join(base_dir, "Blender", "frames", "B_%s_FRAME_%d.jpg" % (dronetype, counter))
                    else:
                        bpy.context.scene.render.filepath =os.path.join(base_dir, "images", "B_%s_FRAME_%d_%d.jpg" % (dronetype, z, counter))
                    bpy.ops.render.render(write_still=True, use_viewport=True)

                for x in range(1, internal_amount):
                    counter += 1
                    angle = (start_angle * (math.pi/180)) + (x*-1) * (rotate_by * (math.pi/180))
                    ob.rotation_euler = (0, 0, angle)
                    bpy.context.scene.camera = bpy.data.objects[camera]
                    if z == 0:
                        bpy.context.scene.render.filepath = os.path.join(base_dir, "Blender", "frames", "B_%s_FRAME_%d.jpg" % (dronetype, counter))
                    else:
                        bpy.context.scene.render.filepath = os.path.join(base_dir, "images", "B_%s_FRAME_%d_%d.jpg" % (dronetype, z, counter))
                    bpy.ops.render.render(write_still=True, use_viewport=True)

def setup():
    remove_cameras('CAMERA')
    add_empty()
    add_camera()
    scale_model(model)
    add_background(bounding_box_image)
    add_sun(0, light_type)

if __name__ == '__main__':
    setup()
    main()