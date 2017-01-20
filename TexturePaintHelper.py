import bpy
import os
from bpy.types import Menu, UnifiedPaintSettings
from bpy.props import IntProperty

class EraseBrush(bpy.types.Operator):
    bl_label = "Select erase brush"
    bl_idname = "paint.erase_brush"
    
    def execute(self, context):

        brushInUse = context.tool_settings.image_paint.brush
        if brushInUse == bpy.data.brushes["TexDraw"]:
            use_brush = bpy.data.brushes["EraseBrush"]
        else:
            use_brush = bpy.data.brushes["TexDraw"]

        context.tool_settings.image_paint.brush = use_brush
        return {'FINISHED'}

class PencilBrush(bpy.types.Operator):
    bl_label = "Pencil Brush"
    bl_idname = "paint.pencil_brush"

    def execute(self,context):
        pencilBrush = bpy.data.brushes["TexDraw"]
        context.tool_settings.image_paint.brush = pencilBrush
        return {'FINISHED'}

class brushMods(bpy.types.Operator):
    bl_label = "Radial brush update"
    bl_idname = "brush.radial_radius"
    n = 0
    stepper = 0.005
    val1 = 0
    val2 = 0
    val3 = 0
    valMidX = 0
    init = True

    def brush_radiusSetAA(self, context):
        toolsettings = bpy.context.tool_settings 
        mode = bpy.context.mode
        if mode == 'PAINT_TEXTURE' or aType == 'IMAGE_EDITOR':
            brush = toolsettings.image_paint.brush
        if mode == 'SCULPT':
           brush = toolsettings.sculpt.brush
        if mode == 'PAINT_WEIGHT':
            brush = toolsettings.weight_paint.brush
        if mode == 'PAINT_VERTEX':
            brush = toolsettings.vertex_paint.brush  
        uniPaintSettings = context.tool_settings.unified_paint_settings
        
        bpy.ops.brush.curve_preset(shape='LINE')
        decrementer = brushMods.n
        radius = brush.radius
        valTopYn = brushMods.val2
        stepper = brushMods.stepper
        valTopXn = brushMods.val1
        valMidXn = brushMods.valMidX
        init = brushMods.init

        decrementer = radius +2.5

        if decrementer < radius - 50:
            decrementer = decrementer + 0.5

        #We only care about AA when hardness is above 90%
        if brush.hardness > 90:
            valTopX = float(radius/decrementer)
            valMidY = 1.3 - valTopX 
            if valTopYn < 0.5:
                valTopYn = 0.95
        else:
            valTopX = valTopXn 
            valTopY = valTopYn
            valMidY = valTopYn - 0.030

        valMidX = valTopX + stepper + 0.030
        if valTopX < 0.990:
            if valMidX >= valTopX + 0.030:
                valMidXn = valTopX + 0.030
            else:
                valMidXn = valMidX

            if valMidX > 0.99:
                valMidXn = 0.998
        else:
            valMidY = 0
            valMidX = 1.0
            valMidXn = 1.0
            valTopX = 0.999
            valTopYn = 1.0
            stepper = 0

        #TODO: add new brush for water painting
        ####
        
        bpy.data.brushes[brush.name].curve.curves[0].points.new(valTopX, valTopYn)
        bpy.data.brushes[brush.name].curve.curves[0].points.new(valMidXn, valMidY)
        bpy.data.brushes[brush.name].curve.update()

        uniPaintSettings.size = radius
        brushMods.valMidX = valMidX

    bpy.types.Brush.radius = bpy.props.IntProperty(
    name = 'Adjust AA relative to brush size',
    subtype = 'PIXEL', min = 1, max = 500, 
    default = 50,
    description = 'adjusts Anti aliasing based on the size of the brush',
    update = brush_radiusSetAA
    )

    def brush_hardness_updater(self,context):
        aType = bpy.context.area.type
        toolsettings = bpy.context.tool_settings 
        mode = bpy.context.mode
        brushMods.brush_radiusSetAA(self, context)
        if mode == 'PAINT_TEXTURE' or aType == 'IMAGE_EDITOR':
            brush = toolsettings.image_paint.brush
        if mode == 'SCULPT':
           brush = toolsettings.sculpt.brush
        if mode == 'PAINT_WEIGHT':
            brush = toolsettings.weight_paint.brush
        if mode == 'PAINT_VERTEX':
            brush = toolsettings.vertex_paint.brush    

        hardness = brush.hardness + 100
        valTopX = float(hardness/200)
        valTopY = float(hardness/200)
        valMidX = valTopX + 0.030
        valMidY = valTopY - 0.030

        if valTopX < 0.40 and valTopY < 0.40:
            valTopX = 0.40
            valTopY = 0.40
            valMidX = 0.40 + 0.050
            valMidY = 0.40
            valMidY = valTopY - 0.050
        if valTopX > 0.9020:
            valTopX = 0.9020
            valMidX = valTopX + 0.050
        if valTopY >= 1.0:
            valTopY = 1.0
        bpy.ops.brush.curve_preset(shape='LINE')
        bpy.data.brushes[brush.name].curve.curves[0].points.new(valTopX, valTopY)
        bpy.data.brushes[brush.name].curve.curves[0].points.new(valMidX, valMidY)
        bpy.data.brushes[brush.name].curve.update()

        brushMods.val1 = valTopX
        brushMods.val2 = valTopY
    
    bpy.types.Brush.hardness = bpy.props.IntProperty(
    name = 'Brush Hardness',
    subtype = 'PERCENTAGE', min = 0, max = 100,
    default = 100,
    description = 'Changes the softness of the brush via the brush curve',
    update= brush_hardness_updater
    )

class TexturePaintHelper(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Texture paint"
    bl_idname = "paint.image_paint"

    @staticmethod
    def paint_settings(context):
        toolsettings = context.tool_settings

        if context.vertex_paint_object:
            return toolsettings.vertex_paint
        elif context.weight_paint_object:
            return toolsettings.weight_paint
        elif context.image_paint_object:
            if (toolsettings.image_paint and toolsettings.image_paint.detect_data()):
                return toolsettings.image_paint

            return None
        return None
      
    @staticmethod
    def unified_paint_settings(parent, context):
        ups = context.tool_settings.unified_paint_settings
        parent.label(text="Unified Settings:")
        row = parent.row()
        row.prop(ups, "use_unified_size", text="Size")
        row.prop(ups, "use_unified_strength", text="Strength")
        if context.weight_paint_object:
            parent.prop(ups, "use_unified_weight", text="Weight")
        elif context.vertex_paint_object or context.image_paint_object:
            parent.prop(ups, "use_unified_color", text="Color")
        else:
            parent.prop(ups, "use_unified_color", text="Color")

    @staticmethod
    def prop_unified_size(parent, context, brush, prop_name, icon='NONE', text="", slider=False):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_size else brush
        parent.prop(ptr, prop_name, icon=icon, text=text, slider=slider)

    @staticmethod
    def prop_unified_strength(parent, context, brush, prop_name, icon='NONE', text="", slider=False):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_strength else brush
        parent.prop(ptr, prop_name, icon=icon, text=text, slider=slider)

    @staticmethod
    def prop_unified_weight(parent, context, brush, prop_name, icon='NONE', text="", slider=False):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_weight else brush
        parent.prop(ptr, prop_name, icon=icon, text=text, slider=slider)

    @staticmethod
    def prop_unified_color(parent, context, brush, prop_name, text=""):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_color else brush
        parent.prop(ptr, prop_name, text=text)

    @staticmethod
    def prop_unified_color_picker(parent, context, brush, prop_name, value_slider=True):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_color else brush
        parent.template_color_picker(ptr, prop_name, value_slider=value_slider)

    def brush_texpaint_common(self, layout, context, brush, settings, projpaint=False):
        capabilities = brush.image_paint_capabilities

        pie = layout.menu_pie()
        col = layout.menu_pie()
        group = pie.box()
        
        toolsettings = context.tool_settings
        ipaint = toolsettings.image_paint
        if not context.particle_edit_object:
            obj = context.active_object
            if obj:
                mat = obj.active_material
                toolsettings = context.tool_settings.image_paint
                if mat:
                    if toolsettings.missing_stencil:
                        group.operator("image.new", text="New").gen_context = 'PAINT_STENCIL'
                    elif toolsettings.missing_uvs:
                        group.operator("paint.add_simple_uvs")
                    else:
                        group.template_ID_preview(settings, "brush", new="brush.add", rows=3, cols=8)
                else:
                    print('no materials')
                    if toolsettings.missing_uvs:
                        group.operator("paint.add_simple_uvs")

                    group.operator_menu_enum("paint.add_texture_paint_slot", "type", text="Add Paint Slot")
            else:
                print('no object')

            group2 = group.box().column(align=True).row(align=True)
            group2.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
            group2.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
            group2.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
            group2.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
            group2.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
            group2.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'
            
            group2.separator()
            group2.prop(ipaint, "use_symmetry_x", text="X      ", icon_value=100)
            group2.prop(ipaint, "use_symmetry_y", text="Y      ", icon_value=100)
            group2.prop(ipaint, "use_symmetry_z", text="Z      ", icon_value=100)
        
        if brush.image_tool in {'DRAW', 'FILL'}:
            if brush.blend not in {'ERASE_ALPHA', 'ADD_ALPHA'}:
                if not brush.use_gradient:
                    self.prop_unified_color_picker(group, context, brush, "color", value_slider=True)
                else:
                    group.template_color_ramp(brush, "gradient", expand=True)
                
        elif brush.image_tool == 'SOFTEN':
            group.prop(brush, "sharp_threshold")
            group.prop(brush, "direction", expand=False)
            if not projpaint:
                group.prop(brush, "blur_kernel_radius")
            group.prop(brush, "blur_mode")
        elif brush.image_tool == 'MASK':
            group.prop(brush, "weight", text="Mask Value", slider=True)
            group.label("Stencil Image")
            group.template_ID(ipaint, "stencil_image")

        elif brush.image_tool == 'CLONE':
            if projpaint:
                if settings.mode == 'MATERIAL':
                    group.prop(settings, "use_clone_layer", text="Clone from paint slot")
                elif settings.mode == 'IMAGE':
                    group.prop(settings, "use_clone_layer", text="Clone from image/UV map")

                if settings.use_clone_layer:
                    ob = context.active_object

                    if settings.mode == 'MATERIAL':
                        if len(ob.material_slots) > 1:
                            group.label("Materials")
                            group.template_list("MATERIAL_UL_matslots", "",
                                              ob, "material_slots",
                                              ob, "active_material_index", rows=2)

                        mat = ob.active_material
                        if mat:
                            group.label("Source Clone Slot")
                            group.template_list("TEXTURE_UL_texpaintslots", "",
                                              mat, "texture_paint_images",
                                              mat, "paint_clone_slot", rows=2)

                    elif settings.mode == 'IMAGE':
                        mesh = ob.data

                        clone_text = mesh.uv_texture_clone.name if mesh.uv_texture_clone else ""
                        col.label("Source Clone Image")
                        col.template_ID(settings, "clone_image")
                        col.label("Source Clone UV Map")
                        col.menu("VIEW3D_MT_tools_projectpaint_clone", text=clone_text, translate=False)
            else:
                col.prop(brush, "clone_image", text="Image")
                col.prop(brush, "clone_alpha", text="Alpha")

        row = pie.row()
        group = pie.row(align=True).box().row(align=True)
        
        pie = pie.row()
        
        obj = context.active_object
        if obj:
            mat = obj.active_material
            context.tool_settings.image_paint
            if mat and not toolsettings.missing_stencil:
                if settings.palette:
                        
                        col.separator()
                        col.box().template_palette(settings, "palette", color=True)
                        if brush.use_gradient:

                            if brush.image_tool == 'DRAW':
                                group.prop(brush, "gradient_stroke_mode", text="Mode")
                                if brush.gradient_stroke_mode in {'SPACING_REPEAT', 'SPACING_CLAMP'}:
                                    group.prop(brush, "grad_spacing")
                            elif brush.image_tool == 'FILL':
                                group.prop(brush, "gradient_fill_mode")
                        else:
                            self.prop_unified_color(group, context, brush, "color", text="")
                            if brush.image_tool == 'FILL' and not projpaint:
                                col.prop(brush, "fill_threshold")
                            else:
                                self.prop_unified_color(group, context, brush, "secondary_color", text="")
                                group.separator()
                                group.operator("paint.brush_colors_flip", icon='FILE_REFRESH', text="flip")
    
                else:
                        if brush.use_gradient:
                            if brush.image_tool == 'DRAW':
                                group.prop(brush, "gradient_stroke_mode", text="Mode")
                                if brush.gradient_stroke_mode in {'SPACING_REPEAT', 'SPACING_CLAMP'}:
                                    group.prop(brush, "grad_spacing")
                            elif brush.image_tool == 'FILL':
                                group.prop(brush, "gradient_fill_mode")
                            if brush.image_tool != 'FILL':
                                #group.label("Background Color")
                                self.prop_unified_color(group, context, brush, "secondary_color", text="")
                                group.separator()
                        else:
                            self.prop_unified_color(group, context, brush, "color", text="")
                            if brush.image_tool == 'FILL' and not projpaint:
                                col.prop(brush, "fill_threshold")
                            else:
                                self.prop_unified_color(group, context, brush, "secondary_color", text="")
                                group.operator("paint.brush_colors_flip", icon='FILE_REFRESH', text="flip")
                                group.separator()
    
        
        if capabilities.has_space_attenuation:
            group.prop(brush, "use_space_attenuation", toggle=True, icon_only=True)
    
        self.prop_unified_strength(group, context, brush, "strength", text="Strength")
        self.prop_unified_strength(group, context, brush, "use_pressure_strength")
        
        if capabilities.has_radius:
            self.prop_unified_size(group, context, brush, "use_pressure_size")
            
        group.separator()
        group.prop(brush, "radius", slider=True, text="Radius")
        group.prop(brush, "hardness")

        col.separator()

        col = layout.column()
 
        group = pie.box().column()
        obj = context.active_object
        if obj:
            mat = obj.active_material
            context.tool_settings.image_paint
            if mat and not toolsettings.missing_stencil:
                group.box().template_ID(settings, "palette", new="palette.new")
        
        group.separator()
        if brush.image_tool in {'DRAW', 'FILL'}:
            group.prop(brush, "blend", text="Blend")

        # use_accumulate
        if capabilities.has_accumulate:
            group.prop(brush, "use_accumulate")

        if projpaint:
            group.prop(brush, "use_alpha")
            group.prop(brush, "use_gradient")

        if mat:
            group.label("Available Paint Slots")
            group.template_list("TEXTURE_UL_texpaintslots", "",
                          mat, "texture_paint_images",
                          mat, "paint_active_slot", rows=2)
            group.operator_menu_enum("paint.add_texture_paint_slot", "type", text="Add Paint Slot")
        
        userpref = context.user_preferences
        system = userpref.system
        group.prop(system, "use_mipmaps") 

    def draw(self, context):
        layout = self.layout
        
        toolsettings = context.tool_settings
        settings = self.paint_settings(context)
        brush = context.tool_settings.image_paint.brush
        ipaint = toolsettings.image_paint
      
        # Makes radius a tad bigger
        pie = layout.menu_pie()
        prefs = bpy.context.user_preferences
        prefs.view.pie_menu_radius = 160

        self.brush_texpaint_common( layout, context, brush, settings, True)
