import bpy
from bpy.types import Operator
from bpy.props import (StringProperty,IntProperty,BoolProperty,CollectionProperty)
from . nodeshandler import NodeHandler
from . propertygroups import LinerItem
from . functions import (   ShowMessageBox, add_panel_lines, del_panel_line, draw_options,
                            get_cb_advanced_mode, get_cb_assign_images, get_cb_clear_nodes,
                            get_cb_dup_mat_compatible, get_cb_include_ngroups, get_cb_mode_opengl,
                            get_cb_only_active_mat, get_cb_replace_shader, get_cb_separators_list,
                            get_cb_setup_nodes, get_cb_shaders_list, get_cb_skip_normals,
                            get_cb_target, get_cb_tweak_levels, get_cb_usr_dir, get_lines_count,
                            get_target_mats, init_prefs, initialize_defaults, lines, props,
                            set_cb_advanced_mode, set_cb_assign_images, set_cb_clear_nodes,
                            set_cb_dup_mat_compatible, set_cb_include_ngroups, set_cb_mode_opengl,
                            set_cb_only_active_mat, set_cb_replace_shader, set_cb_separators_list,
                            set_cb_setup_nodes, set_cb_shaders_list, set_cb_skip_normals,synch_dirs,
                            set_cb_target, set_cb_tweak_levels, set_cb_usr_dir, set_lines_count,
                            synch_names, texture_importer, texture_index,draw_panel,get_a_mat
                        )

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
        synch_names(self,context)
        return {'FINISHED'}


class BasePanel():
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
    cb_advanced_mode: BoolProperty(get=get_cb_advanced_mode,set=set_cb_advanced_mode)
    cb_only_active_mat: BoolProperty(get=get_cb_only_active_mat,set=set_cb_only_active_mat)
    cb_assign_images: BoolProperty(get=get_cb_assign_images,set=set_cb_assign_images)
    cb_setup_nodes: BoolProperty(get=get_cb_setup_nodes,set=set_cb_setup_nodes)
    cb_dup_mat_compatible: BoolProperty(get=get_cb_dup_mat_compatible,set=set_cb_dup_mat_compatible)
    liners: CollectionProperty(type=LinerItem)
    show_options: BoolProperty(default=False)
    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        space = context.space_data
        if space.type in 'TOPBAR':
            props().usr_dir = self.directory

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
            if ndh.report_content :
                self.report({'INFO'}, ("\n").join(ndh.report_content))
                img_count = len([l for l in ndh.report_content if "assigned" in l])
                ShowMessageBox(f"{img_count} matching images loaded",
                                "Images assigned to respective nodes",
                                'FAKE_USER_ON')
        return {'FINISHED'}

class NODE_OT_stm_surfacing_setup(BasePanel,Operator):
    bl_idname = "node.stm_surfacing_setup"
    bl_label = "Import Surfacing Textures"
    bl_description = "Import textures created with substance \
                    or other similar 3D surfacing/painting tools"
    bl_options = {"REGISTER", "UNDO",'PRESET'}

    def invoke(self, context, event):
        if not ndh.check_mat():
            return {'CANCELLED'}
        init_prefs(self)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout.row()
        row.prop(props(), 'usr_dir',text="Folder ")
        draw_panel(self,context)
        if len(lines()) > 1 :
            draw_options(self,context)


class IMPORT_OT_stm_window(BasePanel,Operator):
    bl_idname = "import.stm_window"
    bl_label = "Substance Textures Importer Window"
    bl_description = "Open a substance textures importer window panel"
    bl_options = {"INTERNAL", "UNDO",'PRESET'}

    def invoke(self, context, event):
        self.show_options = True
        if not ndh.check_mat():
            return {'CANCELLED'}
        init_prefs(self)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        draw_panel(self,context)
        if len(lines()) > 1 :
            draw_options(self,context)
