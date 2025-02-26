import bpy
from bpy.props import ( StringProperty,IntProperty,BoolProperty,
                        IntVectorProperty,BoolVectorProperty,
                        EnumProperty,CollectionProperty,PointerProperty)
from bpy.types import PropertyGroup
from . functions import (include_ngroups_up,clear_nodes_up,target_list_cb,target_list_up,
                        usr_dir_up,get_liners_bools,set_liners_vals,get_liners_name,
                        set_liners_name,set_liners_bools,get_liners_vals,
                        replace_shader_up,shaders_list_cb,shaders_list_up,separators_cb,
                        advanced_mode_up,only_active_mat_up, enum_sockets_cb,
                        auto_mode_up, ch_sockets_up, enum_sockets_up, manual_up,
                        split_rgb_up, line_on_up, get_name_up,set_name_up,
                        get_line_bools,set_line_bools,get_line_vals,set_line_vals)

class StringItem(PropertyGroup):

    name: StringProperty(
        name="sock",
        default=""
    )


class LinerItem(PropertyGroup):
    liners_id: IntProperty()
    liners_bools: BoolVectorProperty(get=get_liners_bools,set=set_liners_bools,size=4)
    liners_vals: IntVectorProperty(get=get_liners_vals,set=set_liners_vals,size=4)
    liners_name: StringProperty(get=get_liners_name,set=set_liners_name)


class ShaderLinks(PropertyGroup):

    ID: IntProperty(
        name="ID",
        default=0
    )
    name: StringProperty(
        name="named",
        default="Principled BSDF"
    )
    shadertype: StringProperty(
        name="internal name",
        default='ShaderNodeBsdfPrincipled'
    )
    in_sockets : CollectionProperty(type=StringItem)


class NodesLinks(PropertyGroup):

    ID: IntProperty(
        name="ID",
        default=0
    )
    name: StringProperty(
        name="named",
        default="Unknown name"
    )
    nodetype: StringProperty(
        name="internal name",
        default="{'0':''}"
    )
    in_sockets : CollectionProperty(type=StringItem)


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


class StmProps(PropertyGroup):

    include_ngroups: BoolProperty(
        name="Enable or Disable",
        description=" Append your own Nodegroups in the 'Replace Shader' list above \
                    \n\
                    \n Allows to use Custom Shader nodes\
                    \n Custom NodeGroups must have a valid Surface Shader output socket \
                    \n and at least one input socket to appear in the list \
                    \n (Experimental !!!)",
        default=False,
        update=include_ngroups_up
    )
    clear_nodes: BoolProperty(
        name="Enable or Disable",
        description=" Clear existing nodes \
                     \n Removes all nodes from the material shader \
                     \n before setting up the nodes trees",
        default=True,
        update=clear_nodes_up
    )
    target: EnumProperty(
        name="Target ",
        description=" Objects or materials affected by the operations ",
        items=target_list_cb,
        update=target_list_up
    )
    tweak_levels: BoolProperty(
        name="Enable or Disable",
        description=" Attach RGB Curves and Color Ramps nodes\
                        \n\
                        \n Inserts a RGB Curve if the Texture map type is RGB \
                        \n or a Color ramp if the texture map type is Black & White\
                        \n between the Image texture node and the Shader Input Socket\
                        \n during Nodes Trees setup",
        default=False
    )
    mode_opengl: BoolProperty(
        name="OpenGL Normals",
        description=" Disable to use DirectX™ normal map format instead of OpenGL.\
                        \n\
                        \n When this option is disabled, the script inverts the Y channel\
                        \n of the normal map to match blender format by adding a RGBCurve\
                        \n node with the green channel curve inverted before a normal map\
                        \n is plugged during Nodes Trees setup",
        default=True
    )

    usr_dir: StringProperty(
        name="",
        description="Folder containing the Textures Images to be imported",
        subtype="DIR_PATH",
        default=bpy.utils.extension_path_user(f'{__package__}', create=True),
        update=usr_dir_up
    )

    in_sockets : CollectionProperty(type=StringItem)
    img_files: CollectionProperty(type=StringItem)

    skip_normals: BoolProperty(
        name="Skip normal map detection",
        description=" Skip Normal maps and Height maps detection.\
                            \n\
                            \n Usually the script inserts a Normal map converter node \
                            \n or a Bump map converter node according to the texture maps name.\
                            \n Tick to link the texture map directly",
        default=False
    )
    replace_shader: BoolProperty(
        description=" Enable to replace the Material Shader with the one in the list \
                       \n\
                       \n (Enabled by default if 'Apply to all' is activated)",
        default=True,
        update=replace_shader_up
    )
    shaders_list: EnumProperty(
        name="shaders_list:",
        description=" Base Shader node selector \
                        \n Used to select a replacement for the current Shader node\
                        \n if 'Replace Shader' is enabled or if no valid Shader node is detected.",

        items=shaders_list_cb,
        update=shaders_list_up
    )
    separators_list: EnumProperty(
        name="separators_list:",
        description=" Selector for the separator used to detect multi-sockets.\
                        \n If your texture map name contains multiple keywords like\
                        \n material_bump,metallic,ambient.exr , material_bump-metallic-ambient.exr\
                        \n or material_bump;metallic;ambient.exr etc. \
                        \n Adjust this to fit the separator character between your maps keywords.",

        items=separators_cb,
    )
    advanced_mode: BoolProperty(
        description=" Allows Manual setup of the Maps filenames, \
                    \n  (Tick the checkbox between Map Name and Sockets \
                                        to enable manual file selection)",
        default=False,
        update=advanced_mode_up
    )
    only_active_mat: BoolProperty(
        description=" Apply on active material only, \
                        \n  (By default the script iterates through all materials\
                        \n  presents in the Material Slots.)\
                        \n Enable this to only use the active Material Slot.",
        default=False,
        update=only_active_mat_up
    )
    assign_images: BoolProperty(
        description=" Assign the images found in usr_dir to the corresponding nodes.\
                        \n The nodes should already be created for this to work. \
                        \n (Enable 'Setup Nodes' to create them at the same time)",
        default=True,
    )
    setup_nodes: BoolProperty(
        description=" Creates a (pseudo) PBR nodetree to load images textures",
        default=True,
    )
    dup_mat_compatible: BoolProperty(
        description=" Process duplicated materials names like the originals, \
                        \n  Use this to treat materials with suffix .001\
                        \n  as the original ones (ignores the .00x suffix)",
        default=True
    )

