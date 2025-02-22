import bpy
from bpy.props import (StringProperty, IntProperty, BoolProperty,IntVectorProperty,BoolVectorProperty,
                        PointerProperty, CollectionProperty,EnumProperty)
from bpy.types import (PropertyGroup, UIList,AddonPreferences)

from . functions import (lines, enum_sockets_cb, auto_mode_up, ch_sockets_up, enum_sockets_up, manual_up,
                                split_rgb_up, line_on_up, draw_panel,draw_options,get_name_up,set_name_up,
                                get_line_bools,set_line_bools,get_line_vals,set_line_vals)

from . propertygroups import (StmProps, NodesLinks, ShaderLinks)


class StmChannelSocket(PropertyGroup):
    input_sockets: EnumProperty(
        name="Input socket",
        description="Target shader input sockets for this texture node.\
                    \n Selected automaticaly if -Detect target socket- is enabled",
        items=enum_sockets_cb,
        update=ch_sockets_up
    )
    line_name: StringProperty(
        name="Color",
        description="name of the line owning this instance",
        default="Select a name"
    )


class StmChannelSockets(PropertyGroup):
    socket: CollectionProperty(type=StmChannelSocket)


class StmPanelLines(PropertyGroup):
    name: StringProperty(
        name="name",
        description="Keyword identifier of the texture map to import",
        get=get_name_up,
        set=set_name_up
    )
    line_id: IntProperty()

    line_bools: BoolVectorProperty(get=get_line_bools,set=set_line_bools,size=4)
    line_vals: IntVectorProperty(get=get_line_vals,set=set_line_vals,size=4)

    channels: PointerProperty(type=StmChannelSockets)

    file_name: StringProperty(
        name="File",
        subtype='FILE_PATH',
        description="Complete filepath of the texture map",
        default="Select a file"
    )
    auto_mode: BoolProperty(
        name="Detect target socket",
        description="Auto detect target shader socket",
        default=True,
        update=auto_mode_up
    )
    input_sockets: EnumProperty(
        name="",
        description="Target shader input sockets for this texture node.\
                    \n Selected automaticaly if Autodetect sockets is enabled",
        items=enum_sockets_cb,
        update=enum_sockets_up
    )
    file_is_real: BoolProperty(
        description="Associated file exists",
        default=False
    )
    manual: BoolProperty(
        name='Overwrite file name',
        description="Manual mode switch",
        default=False,
        update=manual_up
    )
    line_on: BoolProperty(
        name="Active",
        description="Enable/Disable line",
        default=True,
        update=line_on_up
    )
    split_rgb: BoolProperty(
        name="Split rgb channels",
        description="Split the RGB channels of the target image \
                        to plug them into individual sockets",
        default=False,
        update=split_rgb_up
    )


class StmPanelLiner(PropertyGroup):
    textures: CollectionProperty(type=StmPanelLines)
    texture_index: IntProperty(default=0)


class StmNodes(PropertyGroup):
    node_links: CollectionProperty(type=NodesLinks)
    node_index: IntProperty(default=0)


class StmShaders(PropertyGroup):
    shader_links: CollectionProperty(type=ShaderLinks)
    shader_index: IntProperty(default=0)


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
                        icon=f"SEQUENCE_COLOR_0{((index+3)%9+1)}")


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
                                     > Import > Substance Textures")
    props: bpy.props.PointerProperty(type=StmProps)

    def draw(self, context):
        layout = self.layout
        layout.prop(self.props, 'usr_dir',text="Textures folder:")
        draw_panel(self,context)
        draw_options(self,context)
        row = layout.row()
        row.label(text="Separator used for multi-sockets: ")
        row.split(factor=10)
        row.prop(self.props,'separators_list',text="")
        layout.prop(self,'display_in_editor',text="Display Panel in Shader Nodes Editor")
