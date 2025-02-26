from bpy.types import Panel
from . functions import get_a_mat

class NODE_PT_stm_nodes_panel(Panel):
    bl_idname = "NODE_PT_stm_nodes_panel"
    bl_label = "Substance Texture Importer"
    bl_context = "material"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "STM"

    @classmethod
    def poll(cls, context):
        try:
            return get_a_mat() and context.preferences.addons[__package__].preferences.display_in_editor
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            return False

    def draw(self, context):
        self.layout.operator("node.stm_surfacing_setup",text="Show importer...")

class MATERIAL_PT_stm_material_panel(Panel):
    bl_label = "Substance Texture Importer"
    bl_idname = "MATERIAL_PT_stm_material_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        try:
            return context.active_object and context.active_object.active_material and context.preferences.addons[__package__].preferences.display_in_properties
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            return False

    def draw(self, context):
        self.layout.operator("node.stm_surfacing_setup",text="Show importer...")
