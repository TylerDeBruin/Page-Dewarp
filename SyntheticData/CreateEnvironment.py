import mathutils
import math
import random
import os
import csv
import bpy
import bmesh

def add_jagged_edges(plane, edge_displace_strength=0.05, edge_noise_scale=10.0):

    bpy.context.view_layer.objects.active = plane

    # === Subdivide first
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(plane.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=50, use_grid_fill=True)
    bmesh.update_edit_mesh(plane.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # === Create vertex group for boundary only
    vg = plane.vertex_groups.new(name="EdgeOnly")
    bm = bmesh.new()
    bm.from_mesh(plane.data)

    boundary_verts = set()
    for edge in bm.edges:
        if len(edge.link_faces) == 1:  # border edge
            boundary_verts.add(edge.verts[0].index)
            boundary_verts.add(edge.verts[1].index)

    bm.free()

    for i, v in enumerate(plane.data.vertices):
        if i in boundary_verts:
            vg.add([i], 1.0, 'REPLACE')

    # === Add noise texture
    tex = bpy.data.textures.new(name=f"TearTex_{random.randint(0, 9999)}", type='CLOUDS')
    tex.noise_scale = edge_noise_scale
    tex.noise_depth = 1
    tex.intensity = 1.0

    # === Add Displace modifier for jagged edges
    mod = plane.modifiers.new(name="JaggedEdge", type='DISPLACE')
    mod.texture = tex
    mod.texture_coords = 'LOCAL'
    mod.strength = edge_displace_strength
    mod.vertex_group = vg.name
    mod.direction = 'NORMAL'

def add_3d_paper_noise(plane, strength=0.25, noise_scale=2.0):
    bpy.context.view_layer.objects.active = plane

    # Subdivide for deformation
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=50)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create new texture
    texture = bpy.data.textures.new(name=f"CreaseTex_{random.randint(0,9999)}", type='CLOUDS')
    texture.noise_scale = noise_scale
    texture.noise_depth = 2
    texture.intensity = 1.0
    texture.noise_type = 'HARD_NOISE'

    # Create empty object to randomize displacement coordinates
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(
        random.uniform(-10, 10),
        random.uniform(-10, 10),
        random.uniform(-10, 10)
    ))
    empty = bpy.context.object
    empty.name = f"NoiseSeed_{random.randint(0,9999)}"

    # Displace modifier
    displace = plane.modifiers.new(name="PaperWarp", type='DISPLACE')
    displace.texture = texture
    displace.texture_coords = 'OBJECT'
    displace.texture_coords_object = empty
    displace.strength = strength * random.uniform(0.8, 1.2)
    displace.mid_level = 0.5 + random.uniform(-0.1, 0.1)
    

def create_image(image_path: str):
    # Load image
    image = bpy.data.images.load(image_path)
    image.use_fake_user = True
    image.colorspace_settings.name = 'sRGB'
    image.alpha_mode = 'STRAIGHT'
    image.use_view_as_render = True
    image.use_generated_float = True
    image.generated_width = image.size[0]
    image.generated_height = image.size[1]

    # Create a plane at origin
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    plane = bpy.context.object

    # Set plane scale to match image aspect ratio
    width, height = image.size
    aspect_ratio = width / height
    plane.scale.x = aspect_ratio
    plane.scale.y = 1.0

    # Create material
    material = bpy.data.materials.new(name="ImageMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    # Create basic shader setup with image
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    shader_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    texture_node = nodes.new(type='ShaderNodeTexImage')

    # Configure texture
    texture_node.image = image
    texture_node.interpolation = 'Closest'  # For sharpness (use 'Cubic' for smoother text if preferred)
    texture_node.extension = 'CLIP'

    # Link image directly to base color
    links.new(texture_node.outputs["Color"], shader_node.inputs["Base Color"])
    links.new(shader_node.outputs["BSDF"], output_node.inputs["Surface"])

    # Assign material to plane
    plane.data.materials.append(material)

    # OPTIONAL: Set 3D viewport to rendered view for full resolution preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'RENDERED'

    return plane




def match_camera_to_mesh_aspect(camera, mesh_obj):
    scene = bpy.context.scene
    aspect = mesh_obj.scale.x / mesh_obj.scale.y
    scene.render.resolution_y = 1080
    scene.render.resolution_x = int(aspect * scene.render.resolution_y)

    camera.data.ortho_scale = max(mesh_obj.scale.x, mesh_obj.scale.y) * 2
    
def create_camera_facing_object(target_obj, distance=1.5):
    # Add a camera
    bpy.ops.object.camera_add()
    camera = bpy.context.object

    target_location = target_obj.location
    cam_location = target_location + mathutils.Vector((0, 0, distance))
    camera.location = cam_location
    camera.rotation_euler = (0, 0, 0)

    bpy.context.scene.camera = camera

    # === Add Random Light ===
    light_types = [
    'POINT', 
    'SUN', 
    'AREA'
    ]
    light_type = random.choice(light_types)

    bpy.ops.object.light_add(type=light_type)
    light = bpy.context.object
    light.data.type = light_type

    # Random position above/around the target
    light.location = target_location + mathutils.Vector((
        random.uniform(-2, 2),
        random.uniform(-2, 2),
        random.uniform(4.0, 10.0)
    ))

    # === Randomize light energy (brightness) by type
    if light_type == 'SUN':
        light.data.energy = random.uniform(1.0, 5.0)  # sun is directional
    elif light_type == 'POINT':
        light.data.energy = random.uniform(500, 1500)
    elif light_type == 'AREA':
        light.data.energy = random.uniform(100, 1000)

    # === Random light color (soft white / warm / cool tints)
    base_colors = [
        (1.0, 1.0, 1.0),       # white
        (1.0, 0.95, 0.85),     # warm
        (0.85, 0.9, 1.0),      # cool
        (1.0, 1.0, 0.9),       # daylight
    ]
    base_color = random.choice(base_colors)
    # Slight noise around the base color
    color = tuple(min(1.0, max(0.0, c + random.uniform(-0.05, 0.05))) for c in base_color)
    light.data.color = color

    return camera

def set_viewport_to_camera(camera):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
                        space.camera = camera
                        return

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.images:
        bpy.data.images.remove(block)
    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)
    for block in bpy.data.lights:
        bpy.data.lights.remove(block)


def animate_camera_pan_from_current(
    camera,
    frames=120,
    stall_frames=10,
    move_distance=5,
    rise_amount=1,
    x_drift_range=1,
    keyframe_interval=20
):
    scene = bpy.context.scene

    # Cleanup
    camera.animation_data_clear()
    for constraint in camera.constraints:
        camera.constraints.remove(constraint)

    # Initial pose
    start_location = camera.location.copy()
    start_rotation = camera.rotation_euler.copy()

    # === Stall: always keyframe at 0 and stall_frames
    for frame in [0, stall_frames]:
        scene.frame_set(frame)
        camera.location = start_location
        camera.rotation_euler = start_rotation
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)

    # === Final destination
    x_drift = random.uniform(random.randint(-x_drift_range, 0), random.randint(0, x_drift_range))
    end_location = mathutils.Vector((
        start_location.x + x_drift,
        start_location.y - random.uniform(0.5, move_distance),
        start_location.z + random.randint(0, rise_amount)
    ))

    # === Animate motion & rotation toward (0, 0, 0)
    for frame in range(stall_frames + 1, frames + 1):
        t = (frame - stall_frames) / (frames - stall_frames)
        interpolated_loc = start_location.lerp(end_location, t)

        scene.frame_set(frame)
        camera.location = interpolated_loc

        # Always look at origin
        direction = mathutils.Vector((0, 0, 0)) - interpolated_loc
        camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

        # Keyframe only if on interval or final frame
        if (frame - stall_frames) % keyframe_interval == 0 or frame == frames:
            camera.keyframe_insert(data_path="location", frame=frame)
            camera.keyframe_insert(data_path="rotation_euler", frame=frame)


# === Utility Functions ===

def render_animation_frames(output_dir, file_prefix="render", start=0, end=120, interval=5):
    scene = bpy.context.scene
    original_path = scene.render.filepath

    os.makedirs(output_dir, exist_ok=True)

    for frame in range(start, end + 1, interval):
        scene.frame_set(frame)
        scene.render.filepath = os.path.join(output_dir, f"{file_prefix}_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)

    scene.render.filepath = original_path


def process_tif_file(image_path, output_root_dir, partial_root_start="images"):
    clear_scene()
    set_black_background()
    
    image_plane = create_image(image_path)
    add_jagged_edges(image_plane)
    add_3d_paper_noise(image_plane, strength=0.05, noise_scale=1.0)

    camera = create_camera_facing_object(image_plane)
    match_camera_to_mesh_aspect(camera, image_plane)
    set_viewport_to_camera(camera)

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.show_floor = False
                        space.overlay.show_axis_x = False
                        space.overlay.show_axis_y = False
                        space.overlay.show_cursor = False
                        space.shading.show_xray = False
                        space.overlay.show_overlays = False

    animate_camera_pan_from_current(camera)

    # === Determine relative folder structure ===
    path_parts = os.path.normpath(image_path).split(os.sep)
    try:
        idx = path_parts.index(partial_root_start)
    except ValueError:
        raise ValueError(f"'{partial_root_start}' not found in path: {image_path}")
    
    relative_subdir = os.path.join(*path_parts[idx:-1])  # skip filename, keep folders from 'images' on
    output_dir = os.path.join(output_root_dir, relative_subdir)
    
    # Strip extension and keep just filename
    file_stem = os.path.splitext(os.path.basename(image_path))[0]
    render_animation_frames(output_dir=output_dir, file_prefix=f"{file_stem}", start=0, end=120, interval=1)
    
    append_checkpoint(
        output_root_dir=output_root_dir,
        image_path=relative_subdir,
        file_stem=file_stem,
        frame_start=0,
        frame_end=120,
        frame_interval=1
    )
    


def find_and_process_tifs(input_root_dir, output_root_dir, partial_root_start="images", total=None):
    totalProcessed = 0
    checkpoint_path = get_checkpoint_path(os.path.join(input_root_dir, "render_checkpoint_log.csv"))
    checkpoint_reached = checkpoint_path is None  # If no checkpoint, start from the beginning

    for root, dirs, files in os.walk(input_root_dir):
        if not checkpoint_reached:
            # Skip until we reach the checkpoint folder
            if os.path.normpath(root).endswith(os.path.normpath(checkpoint_path)):
                checkpoint_reached = True
            else:
                continue

        for file in files:
            if file.lower().endswith('.tif'):
                image_path = os.path.join(root, file)
                process_tif_file(image_path, output_root_dir, partial_root_start)
                totalProcessed += 1

                if total is not None and totalProcessed >= total:
                    return  # Only process up to 'total' .tif files
                
def set_black_background():
    # Get the World node tree
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes

    # Set background color to black
    background_node = nodes.get("Background")
    if background_node:
        background_node.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)  # RGBA for black

def append_checkpoint(output_root_dir, image_path, file_stem, frame_start, frame_end, frame_interval):
    log_path = os.path.join(output_root_dir, "render_checkpoint_log.csv")
    
    rendered_files = [f"{file_stem}_{frame:04d}.png" for frame in range(frame_start, frame_end + 1, frame_interval)]
    line = ', '.join([image_path] + rendered_files) + '\n'
    
    with open(log_path, "a") as f:
        f.write(line)

def get_checkpoint_path(log_path):
    """Reads the last non-empty line from the CSV log and returns the first column (checkpoint path)."""
    if not os.path.exists(log_path):
        return None

    with open(log_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        lines = [row for row in reader if row]
        if not lines:
            return None
        return lines[-1][0]  # Return first column of the last line



# === Execution Parameters ===

input_root = r"D:/Public/Page-Dewarp/SyntheticData/Data/rvl_cdip_raw/images"
output_root = r"F:/SyntheticData/Output"
partial_structure_root = "images"

find_and_process_tifs(input_root, output_root, partial_structure_root)