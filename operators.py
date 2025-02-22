import bpy
from pathlib import Path
from bpy.types import Operator
from bpy.props import (StringProperty,IntProperty,BoolProperty,CollectionProperty)
from . nodeshandler import NodeHandler
from . propertygroups import LinerItem
from . functions import *

ndh = NodeHandler()

class SubOperatorPoll():
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hasattr(texture_importer(), "textures")


class NODE_OT_stm_add_substance_texture(SubOperatorPoll,Operator):
    bl_idname = "node.stm_add_item"
    bl_label = "Add Texture"

    def execute(self, context):
        add_panel_lines()
        return {'FINISHED'}


class NODE_OT_stm_del_substance_texture(SubOperatorPoll,Operator):
    bl_idname = "node.stm_remove_item"
    bl_label = "Remove Texture"

    def execute(self, context):
        del_panel_line()
        return {'FINISHED'}


class NODE_OT_stm_reset_substance_textures(SubOperatorPoll,Operator):
    bl_idname = "node.stm_reset_substance_textures"
    bl_label = "Reset textures names"
    bl_description = "Resets the textures lines to a default set of values.\
                    \n (Color, Roughness, Metallic, Normal)"

    def execute(self, context):
        initialize_defaults()
        return {'FINISHED'}


class NODE_OT_stm_move_line(Operator):
    bl_idname = "node.stm_move_line"
    bl_label = "Rearrange lines order"
    bl_description = "Move lines up or down"
    bl_options = {'INTERNAL', 'UNDO'}

    down : BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return hasattr(texture_importer(), "textures") and len(lines())

    def execute(self,context):
        index = texture_index()
        new_index = (index -1+2*int(self.down))%len(lines())
        lines().move(index, new_index)
        texture_importer().texture_index = new_index
        return {'FINISHED'}


class NODE_OT_stm_fill_names(SubOperatorPoll,Operator):
    bl_idname = "node.stm_fill_names"
    bl_label = "Synch line names with files"
    bl_description = 'Rename panel lines from keywords detected in the texture files'

    def execute(self, context):
        synch_names()
        return {'FINISHED'}


class BasePanel():
    bl_options = {"REGISTER", "UNDO",'PRESET'}

    @classmethod
    def poll(cls, context):
        try:
            return get_a_mat() and props()
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            return False

    lines_count: IntProperty(get=get_lines_count,set=set_lines_count)
    cb_include_ngroups: BoolProperty(get=get_cb_include_ngroups,set=set_cb_include_ngroups)
    cb_clear_nodes: BoolProperty(get=get_cb_clear_nodes,set=set_cb_clear_nodes)
    cb_target: StringProperty(get=get_cb_target,set=set_cb_target)
    cb_tweak_levels: BoolProperty(get=get_cb_tweak_levels,set=set_cb_tweak_levels)
    cb_mode_opengl: BoolProperty(get=get_cb_mode_opengl,set=set_cb_mode_opengl)
    cb_usr_dir: StringProperty(get=get_cb_usr_dir,set=set_cb_usr_dir)
    cb_skip_normals: BoolProperty(get=get_cb_skip_normals,set=set_cb_skip_normals)
    cb_replace_shader: BoolProperty(get=get_cb_replace_shader,set=set_cb_replace_shader)
    cb_shaders_list: StringProperty(get=get_cb_shaders_list,set=set_cb_shaders_list)
    cb_separators_list: StringProperty(get=get_cb_separators_list,set=set_cb_separators_list)
    cb_lines_from_files: BoolProperty(get=get_cb_lines_from_files,set=set_cb_lines_from_files)
    cb_advanced_mode: BoolProperty(get=get_cb_advanced_mode,set=set_cb_advanced_mode)
    cb_only_active_mat: BoolProperty(get=get_cb_only_active_mat,set=set_cb_only_active_mat)
    cb_assign_images: BoolProperty(get=get_cb_assign_images,set=set_cb_assign_images)
    cb_setup_nodes: BoolProperty(get=get_cb_setup_nodes,set=set_cb_setup_nodes)
    cb_dup_mat_compatible: BoolProperty(get=get_cb_dup_mat_compatible,set=set_cb_dup_mat_compatible)
    liners: CollectionProperty(type=LinerItem)


class NODE_OT_stm_smooth_operator(BasePanel,Operator):
    bl_idname = "node.stm_smooth_operator"
    bl_label = "Label me..."
    bl_description = "Describe me"

    def execute(self, context):
        if not len(get_target_mats(context))>0:
            ShowMessageBox("No valid target material found, check Target selector",
                            'FAKE_USER_ON')
            return {'CANCELLED'}
        if props().setup_nodes:
            self.report({'INFO'}, ("\n").join(ndh.report_content))
            ndh.handle_nodes(True)
            ShowMessageBox("Check Shader nodes panel",
                            "Nodes created",
                            'FAKE_USER_ON')
        if props().assign_images:
            ndh.handle_nodes()
            self.report({'INFO'}, ("\n").join(ndh.report_content))
            img_count = len([l for l in ndh.report_content if "assigned" in l])
            ShowMessageBox(f"{img_count} matching images loaded",
                            "Images assigned to respective nodes",
                            'FAKE_USER_ON')

        """
        for i in range (2):
            ndh.handle_nodes(not i)
            self.report({'INFO'},("\n").join(ndh.report_content) )
        """
        return {'FINISHED'}

    def invoke(self, context, event):
        mat = get_a_mat()
        if not mat:
            ShowMessageBox(f"No valid material found",
                            'FAKE_USER_ON')
            return {'CANCELLED'}
        ndh.mat = bpy.context.window_manager['current_mat'] = mat
        refresh_props(props(),bpy.context)
        self.liners.clear()
        for line in lines():
            l = self.liners.add()
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(props(), 'usr_dir',text="Textures folder:")
        draw_panel(self,context)
        if len(lines()) > 1 :
            draw_options(self,context)


class IMPORT_OT_stm_window(BasePanel,Operator):
    bl_idname = "import.stm_window"
    bl_label = "Import Textures"
    bl_description = "Open a substance textures importer panel"

    def execute(self, context):
        for i in range (2):
            ndh.handle_nodes(not i)
            self.report({'INFO'},("\n").join(ndh.report_content))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        space = context.space_data
        params = space.params
        #required for the 'Map names from files' option <- maybe make it a button-like feature instead of full auto
        if props().usr_dir != params.directory.decode('utf-8'):
            props().usr_dir = params.directory.decode('utf-8')
        draw_panel(self,context)
        if len(lines()) > 1 :
            draw_options(self,context)
