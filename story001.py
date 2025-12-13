import bpy
import math
from mathutils import Vector

# =========================
# 初期化
# =========================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = 0
scene.frame_end = 450
scene.render.fps = 30

# =========================
# Light（AR想定でシンプル）
# =========================
bpy.ops.object.light_add(type='AREA', location=(5, -5, 8))
light = bpy.context.object
light.data.energy = 800
light.data.size = 5

# =========================
# Text 作成関数
# =========================
def create_letter(char, location):
    bpy.ops.object.text_add(location=location)
    txt = bpy.context.object
    txt.data.body = char
    txt.data.extrude = 0.2
    txt.data.bevel_depth = 0.02
    txt.data.align_x = 'CENTER'
    txt.data.align_y = 'CENTER'

    bpy.ops.object.convert(target='MESH')
    txt.scale = (1.2, 1.2, 1.2)
    bpy.context.view_layer.update()
    return txt

# =========================
# 文字生成
# =========================
T = create_letter("T", (0, 0, 8))
K = create_letter("K", (-4, 0, 1))
S = create_letter("S", (4, 0, 1))

K.hide_viewport = True
S.hide_viewport = True
K.hide_render = True
S.hide_render = True

# =========================
# 「起」Tが落ちる
# =========================
T.location = (0, 0, 8)
T.keyframe_insert("location", frame=0)

T.location = (0, 0, 1)
T.keyframe_insert("location", frame=60)

# 着地バウンド
T.scale = (1.4, 1.4, 0.7)
T.keyframe_insert("scale", frame=65)

T.scale = (1.2, 1.2, 1.2)
T.keyframe_insert("scale", frame=75)

# =========================
# 「承」K・S 登場して集合
# =========================
for obj in [K, S]:
    obj.hide_viewport = False
    obj.hide_render = False
    obj.keyframe_insert("hide_viewport", frame=75)
    obj.keyframe_insert("hide_render", frame=75)

K.location = (-4, 0, 1)
S.location = (4, 0, 1)
K.keyframe_insert("location", frame=75)
S.keyframe_insert("location", frame=75)

K.location = (-1.5, 0, 1)
S.location = (1.5, 0, 1)
K.keyframe_insert("location", frame=180)
S.keyframe_insert("location", frame=180)

# 軽く弾む
for obj in [T, K, S]:
    obj.scale = (1.35, 1.35, 0.8)
    obj.keyframe_insert("scale", frame=190)
    obj.scale = (1.2, 1.2, 1.2)
    obj.keyframe_insert("scale", frame=210)

# =========================
# 「転」衝突 → 吹き飛ぶ
# =========================
explode_positions = {
    T: (0, -4, 3),
    K: (-5, 2, 2.5),
    S: (5, 2, 2.5)
}

for obj, pos in explode_positions.items():
    obj.keyframe_insert("location", frame=210)
    obj.location = pos
    obj.keyframe_insert("location", frame=300)

    obj.rotation_euler = (math.radians(360), 0, 0)
    obj.keyframe_insert("rotation_euler", frame=300)

# =========================
# 「結」整列して着地
# =========================
final_positions = {
    T: (-1.5, 0, 1),
    K: (0, 0, 1),
    S: (1.5, 0, 1)
}

for obj, pos in final_positions.items():
    obj.location = pos
    obj.keyframe_insert("location", frame=420)

    obj.scale = (1.4, 1.4, 0.85)
    obj.keyframe_insert("scale", frame=430)

    obj.scale = (1.2, 1.2, 1.2)
    obj.keyframe_insert("scale", frame=450)
