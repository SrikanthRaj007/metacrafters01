import bpy
import json
import bmesh

def create_edge(location, width, height, thickness, name):
    # Create a new mesh and object
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Create a bmesh to hold the edges
    bm = bmesh.new()

    # Define the four corners of the rectangle
    p1 = bm.verts.new((location[0] - width / 2, location[1] - height / 2, 0))  # Bottom left
    p2 = bm.verts.new((location[0] + width / 2, location[1] - height / 2, 0))  # Bottom right
    p3 = bm.verts.new((location[0] + width / 2, location[1] + height / 2, 0))  # Top right
    p4 = bm.verts.new((location[0] - width / 2, location[1] + height / 2, 0))  # Top left

    # Create the top vertices at the specified thickness
    p1_top = bm.verts.new((p1.co.x, p1.co.y, thickness))
    p2_top = bm.verts.new((p2.co.x, p2.co.y, thickness))
    p3_top = bm.verts.new((p3.co.x, p3.co.y, thickness))
    p4_top = bm.verts.new((p4.co.x, p4.co.y, thickness))

    # Create edges between the bottom corners
    bm.edges.new((p1, p2))
    bm.edges.new((p2, p3))
    bm.edges.new((p3, p4))
    bm.edges.new((p4, p1))

    # Create edges between the top corners
    bm.edges.new((p1_top, p2_top))
    bm.edges.new((p2_top, p3_top))
    bm.edges.new((p3_top, p4_top))
    bm.edges.new((p4_top, p1_top))

    # Create vertical edges connecting top and bottom corners
    bm.edges.new((p1, p1_top))
    bm.edges.new((p2, p2_top))
    bm.edges.new((p3, p3_top))
    bm.edges.new((p4, p4_top))

    # Finish the mesh and update it
    bm.to_mesh(mesh)
    bm.free()

def main():
    # Load detected objects from JSON using absolute path
    with open(r'C:\Users\SRI MADHU\Desktop\metacrafters01-main\metacrafters01-main\detected_objects.json', 'r') as f:
        detected_objects = json.load(f)

    for obj in detected_objects:
        if "box" in obj:
            box = obj["box"]
            x, y, width, height = box
            
            # Adjust for line objects if needed
            if obj["class"] == "detected line":
                continue  # Skip lines for now
            
            # Calculate location for the edge
            location = (x + width / 2.0, y + height / 2.0, 0)  # Center the edge

            thickness = 10.0  # Set the desired thickness here (increase this value for more height)
            create_edge(location, width, height, thickness, obj.get("class", "Edge"))

# Clear existing objects in the scene
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete(use_global=False)

# Run the main function
main()
