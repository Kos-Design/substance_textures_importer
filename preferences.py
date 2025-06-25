import bpy
from bpy.props import (StringProperty, IntProperty, BoolProperty,IntVectorProperty,
                       BoolVectorProperty, PointerProperty, CollectionProperty,EnumProperty)
from bpy.types import (PropertyGroup, UIList,AddonPreferences)
from . propertygroups import (StmProps, NodesLinks, ShaderLinks, StmChannelSocket,StmShaders,
                               StmChannelSockets,StmPanelLines, StmPanelLiner, StmNodes)
from . functions import icon_name

class NODE_UL_stm_list(UIList):
    """
    Same behaviour as normal UI list but allows the triggering
    of an update function when item names are modified in UI Panel,
    whereas normal UI lists do not!
    --could be a candidate for a bugreport--
    """
    bl_idname = "NODE_UL_stm_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            layout.prop(item, "name", text="", emboss=False,
                        icon=f"{icon_name(index)}")


class StmAddonPreferences(AddonPreferences):
    bl_idname = __package__ if __package__ else __name__

    maps: bpy.props.PointerProperty(type=StmPanelLiner)
    node_links: CollectionProperty(type=NodesLinks)
    shader_links: CollectionProperty(type=ShaderLinks)
    display_in_editor: BoolProperty(
                        default=True,
                        description="Uncheck this option to hide the Extension panel\
                                     from the Shader Nodes Editor Sidebar. \
                                    \n It will remain available in the File menu\
                                     > Import > Substance Texturesand and via \
                                    \n F3 Search > Import Surfacing Textures")
    display_in_properties: BoolProperty(
                        default=False,
                        description="Check this option to show the Extension panel\
                                     in the Material Properties Panel. \
                                    \n It will remain available in the File menu\
                                     > Import > Substance Textures and via \
                                    \n F3 Search > Import Surfacing Textures")
    debug_results: BoolProperty(
                        default=True,
                        description="Show extension activity in Blender console")
    props: bpy.props.PointerProperty(type=StmProps)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self.props, 'usr_dir',text="Textures folder:")
        row = layout.row()
        row.operator('node.stm_surfacing_setup',text="Show Substance Texture Importer Panel")
        row = layout.row()
        row.label(text="Separator used for multi-sockets: ")
        row.split(factor=10)
        row.prop(self.props,'separators_list',text="")
        layout.prop(self,'display_in_editor',text="Display shortcut button in Shader Nodes Editor.")
        layout.prop(self,'display_in_properties',text="Display shortcut button in Material Properties.")
        layout.prop(self,'debug_results',text="Show output messages in console.")
