import bpy
import os
from bpy.types import Menu, UnifiedPaintSettings
from bpy.props import IntProperty
from mathutils import Vector
from bpy.app.handlers import persistent

@persistent
def eraseBrush(self):

	brushIconPath = os.path.join(os.path.dirname(__file__), "icons/")
	brushes = bpy.data.brushes
	# get a list of erase alpha brushes
	erase_brushes = [b for b in brushes
        	if b.use_paint_image and b.blend == 'ERASE_ALPHA']
	if len(erase_brushes):
    	# always choose the first
		use_brush = erase_brushes[0]
	else:
		# Create brush and set its properties
		use_brush = bpy.data.brushes.new('EraseBrush')
		use_brush.blend = 'ERASE_ALPHA'
		use_brush.use_custom_icon = True
		use_brush.icon_filepath = brushIconPath + "erase_brush.png"
		use_brush.use_pressure_strength = False
		use_brush.strength = 1.0

class importBrushes(bpy.types.Operator):
	bl_label = "Add erase brush to brush collection"
	bl_idname = "paint.import_brushes"

	def execute(self,context):
		eraseBrush()
