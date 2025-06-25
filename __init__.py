import bpy

bl_info = {
    "name": "Substance Textures Importer",
    "author": "Cosmin Planchon",
    "version": (0, 7, 1),
    "blender": (4, 2, 0),
    "location": "File > Import > Substance Textures",
    "description": "Import & autoassign images from Substance or similar 3D painting tools",
    "warning": "",
    "wiki_url": "https://github.com/Kos-Design/substance_textures_importer/blob/main/readme.rst",
    "tracker_url": "https://github.com/Kos-Design/substance_textures_importer/issues",
    "category": "Node"}

from . functions import menu_func

from . propertygroups import ( StringItem,LinerItem,ShaderLinks, NodesLinks, StmProps)

from . operators import ( NODE_OT_stm_reset_substance_textures,NODE_OT_stm_del_substance_texture,
                          NODE_OT_stm_move_line,NODE_OT_stm_add_substance_texture,
                          NODE_OT_stm_surfacing_setup,NODE_OT_stm_fill_names,IMPORT_OT_stm_window)

from . panels import ( NODE_PT_stm_nodes_panel,MATERIAL_PT_stm_material_panel )

from . preferences import (StmAddonPreferences, StmPanelLiner, NODE_UL_stm_list, StmPanelLines,
                            StmChannelSocket, StmChannelSockets,StmShaders, StmNodes,)

classes = (
    LinerItem,
    StringItem,
    StmProps,
    NodesLinks,
    ShaderLinks,
    StmShaders,
    StmNodes,
    NODE_OT_stm_surfacing_setup,
    NODE_OT_stm_fill_names,
    NODE_OT_stm_add_substance_texture,
    NODE_OT_stm_del_substance_texture,
    NODE_PT_stm_nodes_panel,
    StmChannelSocket,
    StmChannelSockets,
    StmPanelLines,
    StmPanelLiner,
    StmAddonPreferences,
    NODE_UL_stm_list,
    IMPORT_OT_stm_window,
    NODE_OT_stm_reset_substance_textures,
    MATERIAL_PT_stm_material_panel,
    NODE_OT_stm_move_line
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)

def unregister():
    from bpy.utils import unregister_class
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == '__main__':
    register()
