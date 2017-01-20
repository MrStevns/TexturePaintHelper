"""
Texture Paint Helper
Copyright (C) 2017 Oliver Larsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

bl_info = {
    'name': 'TexturePaintHelper',
    'author': 'Oliver Larsen aka. CandyFace',
    'version': (0, 1, 6),
    'blender': (2, 78, 0),
    'location': 'Texture_Paint > Press W > Pie menu',
    'description': 'A texture pie right at your finger tips!',
    'warning': '',
    "wiki_url" : "",
    "tracker_url" : "",
    'support': 'COMMUNITY',
    'category': 'Paint'}

if "bpy" in locals():
    import imp
    unregister()
    imp.reload(TexturePaintHelper)
    imp.reload(ImportBrushes)
else:
    import bpy
    from . import TexturePaintHelper
    from . import ImportBrushes

default_keybind = 'W'

addon_keymaps = []
def register():
    bpy.utils.register_module(__name__)
    bpy.app.handlers.load_post.append(ImportBrushes.eraseBrush)
    
    wm = bpy.context.window_manager

    def kmi_props_setattr(kmi_props, attr, value):
        try:
            setattr(kmi_props, attr, value)
        except AttributeError:
            print("Warning: property '%s' not found in keymap item '%s'" %
                  (attr, kmi_props.__class__.__name__))
        except Exception as e:
            print("Warning: %r" % e)

    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    kmi = km.keymap_items.new("wm.call_menu_pie", default_keybind, 'PRESS', ctrl=False, shift=False)
    kmi.properties.name = "paint.image_paint"

    kmi = km.keymap_items.new("paint.pencil_brush", 'P', 'PRESS', ctrl=False, shift=False)
    kmi = km.keymap_items.new("paint.erase_brush", 'E', 'PRESS', ctrl=False, shift=False)
    kmi = km.keymap_items.new("wm.radial_control", 'F', 'PRESS', ctrl=False, shift=False)
    kmi_props_setattr(kmi.properties, 'data_path_primary', 'tool_settings.image_paint.brush.radius')
    kmi_props_setattr(kmi.properties, 'rotation_path', 'tool_settings.image_paint.brush.mask_texture_slot.angle')
    kmi_props_setattr(kmi.properties, 'color_path', 'tool_settings.image_paint.brush.cursor_color_add')
    kmi_props_setattr(kmi.properties, 'fill_color_path', 'tool_settings.image_paint.brush.color')
    kmi_props_setattr(kmi.properties, 'zoom_path', 'space_data.zoom')

    addon_keymaps.append(km)

def unregister():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    # clear the list
    addon_keymaps.clear()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
