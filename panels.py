import bpy
from bpy.types import Panel
from . functions import draw_options,draw_panel

class TexImporterPanel():
    bl_context = "material"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "STM"

    @classmethod
    def poll(cls, context):
        try:
            return context.preferences.addons[__package__].preferences.display_in_editor
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            return False

class NODE_PT_stm_importpanel(TexImporterPanel, Panel):
    bl_idname = "NODE_PT_stm_importpanel"
    bl_label = "Substance Texture Importer"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("node.stm_smooth_operator",text="Show importer panel")

