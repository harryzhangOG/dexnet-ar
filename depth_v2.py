import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import trimesh
from perception import DepthImage as dpi
import pyrender
from pyrender import RenderFlags

def _create_node_from_points(points, name=None, pose=None, color=None, material=None, radius=None, n_divs=20):
    points = np.asanyarray(points)
    if points.ndim == 1:
        points = np.array([points])

    if pose is None:
        pose = np.eye(4)
    else:
        pose = pose.matrix

    # Create vertex colors if needed
    if color is not None:
        color = np.asanyarray(color, dtype=np.float)
        if color.ndim == 1 or len(color) != len(points):
            color = np.repeat(color[np.newaxis,:], len(points), axis=0)

    if radius is not None:
        poses = None
        mesh = trimesh.creation.uv_sphere(radius, [n_divs, n_divs])
        if color is not None:
            mesh.visual.vertex_colors = color[0]
        poses = np.tile(np.eye(4), (len(points), 1)).reshape(len(points),4,4)
        poses[:, :3, 3::4] = points[:,:,None]
        m = pyrender.Mesh.from_trimesh(mesh, material=material, poses=poses)
    else:
        m = pyrender.Mesh.from_points(points, colors=color)

    return pyrender.Node(mesh=m, name=name, matrix=pose)


"""
AR Kit default: Y is HEIGHT
The next few steps convert [x, z, y] to [x, y, z]
"""
def bound(x, z):
    # campbells
    # if x > -0.69 and x < -0.41 and z > -0.55 and z < -0.21:
    # small box
    if x > 0.03 and x < 0.28 and z > -0.29 and z < 0.2:
    # cereal bowl
    # if x > -0.24 and x < 0.15 and z > -0.27 and z < 0.15:
        return True
    return False
filtered = []
fin = open('campbells.txt')
for line in fin:
    string = line.split(' ')
    x = float(string[0])
    y = float(string[1])
    z = float(string[2])
    filtered.append([x, z, y])
print(filtered[0])
# shift the data points by the mean value to match the frame
temp = np.array(filtered)
xmean = np.mean(temp[:, 0])
ymean = np.mean(temp[:, 1])
zmean = np.mean(temp[:, 2])
for i in range(len(filtered)):
    filtered[i][0] -= xmean
    filtered[i][1] -= ymean
    filtered[i][2] -= zmean
print(filtered[0])
# Define a numpy array containing the converted [x, z, y]
mat = np.array(filtered)
# PYRENDER's wrapper for point cloud data: nodes
nodes = _create_node_from_points(mat, radius = 0.0005)
# nodes = pyrender.Mesh.from_points(mat)
scene = pyrender.Scene()
scene.add_node(nodes)
# scene.add(nodes)
"""
Phoxi camera intrinsics:
"_cy": 384.0,
"_cx": 511.5,
"_fy": 1122.0,
"_height": 772,
"_fx": 1122.0,
"_width": 1032,
"_skew": 0.0,
"_K": 0,
"_frame": "phoxi"
"""
camera = pyrender.IntrinsicsCamera(fx = 1122.0, fy = 1122.0, cx = 511.5, cy = 384.0)
# camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
camera_pose = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0.4], [0, 0, 0, 1]])
# s = np.sqrt(2)/2
# camera_pose = np.array([[0.0, -s,   s,   0.3],[1.0,  0.0, 0.0, 0.0],[0.0,  s,   s,   0.35],[0.0,  0.0, 0.0, 1.0],])
scene.add(camera, pose=camera_pose)
# light = pyrender.SpotLight(color=np.ones(3), intensity=3.0)
# scene.add(light, pose=camera_pose)
r = pyrender.OffscreenRenderer(1200, 1200)
flags = RenderFlags.DEPTH_ONLY
depth = r.render(scene, flags=flags)
plt.figure()
plt.axis('off')
plt.imshow(depth)
plt.show()
depthImage = dpi(depth)
filledDepth = depthImage.inpaint()
# plt.imshow(filledDepth.data, cmap = plt.cm.gray_r)
plt.imshow(filledDepth.data)
plt.show()
# np.save('campbellsNew.npy', filledDepth.data)
