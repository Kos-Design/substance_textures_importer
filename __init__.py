bl_info = {
    "name": "Substance Textures Importer",
    "author": "Cosmin Planchon",
    "version": (0, 6, 1),
    "blender": (4, 2, 0),
    "location": "Shader editor > Sidebar > STM",
    "description": "Import & autoassign images from Substance Painter or similar 3D painting tools",
    "warning": "",
    "wiki_url": "https://github.com/Kos-Design/substance_textures_importer/blob/main/readme.rst",
    "tracker_url": "https://github.com/Kos-Design/substance_textures_importer/issues",
    "category": "Node"}

import bpy

from . propertygroups import ( StringItem,LinerItem,ShaderLinks, NodesLinks, StmProps)

from . operators import ( NODE_OT_stm_reset_substance_textures,
                          NODE_OT_stm_move_line,NODE_OT_stm_add_substance_texture,NODE_OT_stm_del_substance_texture,
                          NODE_OT_stm_smooth_operator,NODE_OT_stm_fill_names,IMPORT_OT_stm_window)

from . panels import ( NODE_PT_stm_importpanel )

from . preferences import (StmAddonPreferences, StmPanelLiner, NODE_UL_stm_list, StmPanelLines,
                            StmChannelSocket, StmChannelSockets,StmShaders, StmNodes,)

from . functions import init_prefs,menu_func

classes = (
    LinerItem,
    StringItem,
    StmProps,
    NodesLinks,
    ShaderLinks,
    StmShaders,
    StmNodes,
    NODE_OT_stm_smooth_operator,
    NODE_OT_stm_fill_names,
    NODE_OT_stm_add_substance_texture,
    NODE_OT_stm_del_substance_texture,
    NODE_PT_stm_importpanel,
    StmChannelSocket,
    StmChannelSockets,
    StmPanelLines,
    StmPanelLiner,
    StmAddonPreferences,
    NODE_UL_stm_list,
    IMPORT_OT_stm_window,
    NODE_OT_stm_reset_substance_textures,
    NODE_OT_stm_move_line
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    init_prefs()
    bpy.types.TOPBAR_MT_file_import.append(menu_func)

def unregister():
    from bpy.utils import unregister_class
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == '__main__':
    register()
