import bpy
from pathlib import Path
from bpy.types import Operator
from bpy.props import StringProperty,BoolProperty
from . propertieshandler import PropertiesHandler,props,texture_importer,texture_index,lines
from . nodeshandler import NodeHandler
from . panels import draw_panel,NODE_PT_stm_options

propper = PropertiesHandler()
ndh = NodeHandler()

def menu_func(self, context):
    self.layout.operator("import.stm_window", text="Substance Textures...")

def ShowMessageBox(message="", title="Message", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def get_directory(self):
    #props().usr_dir = self.get("directory",'')
    return self.get("directory",'')

def set_directory(self,value):
    self["directory"] = value
    props().usr_dir = self["directory"]

class SubOperatorPoll():
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hasattr(texture_importer(), "textures")


class OperatorPoll():

    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            return len(ndh.get_target_mats(context))>0
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            return False


class NODE_OT_stm_add_substance_texture(SubOperatorPoll,Operator):
    bl_idname = "node.stm_add_item"
    bl_label = "Add Texture"

    def execute(self, context):
        propper.add_panel_lines()
        return {'FINISHED'}


class NODE_OT_stm_del_substance_texture(SubOperatorPoll,Operator):
    bl_idname = "node.stm_remove_item"
    bl_label = "Remove Texture"

    def execute(self, context):
        propper.del_panel_line()
        return {'FINISHED'}


class NODE_OT_stm_reset_substance_textures(SubOperatorPoll,Operator):
    bl_idname = "node.stm_reset_substance_textures"
    bl_label = "Reset textures names"
    bl_description = "Resets the textures lines to a default set of values.\
                    \n (Color, Roughness, Metallic, Normal)"

    def execute(self, context):
        propper.initialize_defaults()
        return {'FINISHED'}


class NODE_OT_stm_make_nodes(OperatorPoll,Operator):
    bl_idname = "node.stm_make_nodes"
    bl_label = "Only Setup Nodes"
    bl_description = "Setup empty Texture Nodes"

    def execute(self, context):
        self.report({'INFO'}, ("\n").join(ndh.report_content))
        ndh.handle_nodes(True)
        ShowMessageBox("Check Shader nodes panel",
                         "Nodes created",
                         'FAKE_USER_ON')
        return {'FINISHED'}


class NODE_OT_stm_assign_nodes(OperatorPoll,Operator):
    bl_idname = "node.stm_assign_nodes"
    bl_label = "Only Assign Images"
    bl_description = "import maps for all selected objects"

    def execute(self, context):
        ndh.handle_nodes()
        self.report({'INFO'}, ("\n").join(ndh.report_content))
        img_count = len([l for l in ndh.report_content if "assigned" in l])
        ShowMessageBox(f"{img_count} matching images loaded",
                         "Images assigned to respective nodes",
                         'FAKE_USER_ON')
        return {'FINISHED'}


class NODE_OT_stm_import_textures(OperatorPoll,Operator):
    bl_idname = "node.stm_import_textures"
    bl_label = "Import Substance Maps"
    bl_description = "Import texture maps for active object"

    def execute(self,context):
        for i in range (2):
            ndh.handle_nodes(not i)
            self.report({'INFO'},("\n").join(ndh.report_content) )
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


class NODE_OT_stm_add_preset(SubOperatorPoll,Operator):
    bl_idname = 'node.stm_add_preset'
    bl_label = 'Add A preset'
    bl_description = 'Add preset'

    def execute(self, context):
        preset_name = props().custom_preset_name
        if not preset_name:
            self.report({'ERROR'}, "Preset name cannot be empty")
            return {'CANCELLED'}
        p_file = Path(NODE_OT_stm_presets_dialog.p_dir).joinpath(preset_name)
        filer = f"{p_file}{'.py' if 'py' not in p_file.suffix else ''}"
        with open(filer, "w", encoding="utf-8") as w:
            w.write(str(propper.fill_settings()))
            self.report({'INFO'}, f"Added preset: {preset_name}")
            return {'FINISHED'}
        return {'CANCELLED'}


class NODE_OT_stm_presets_dialog(SubOperatorPoll,Operator):
    bl_idname = "node.stm_presets_dialog"
    bl_label = "STM Presets..."
    bl_description = 'Open preset panel'

    p_dir = Path(bpy.utils.extension_path_user(f'{__package__}',path="stm_presets", create=True))
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=200)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.label(text="Presets:")
        layout.separator()
        if self.p_dir.exists():
            files = sorted(self.p_dir.glob("*.py"))
            for file in files:
                row = layout.split(factor=0.85, align=True)
                op = row.operator("node.stm_execute_preset", text=file.stem,emboss=False)
                op.preset_file = str(file)
                del_op = row.operator("node.stm_delete_preset", text="", icon="REMOVE",emboss=False)
                del_op.preset_file = str(file)
        else:
            layout.label(text="No presets found")
        layout.separator()
        row = layout.split(factor=0.85, align=True)
        row.prop(props(), "custom_preset_name", text="")
        row.operator("node.stm_add_preset", text="", icon="ADD")


class NODE_OT_stm_delete_preset(SubOperatorPoll,Operator):
    bl_idname = "node.stm_delete_preset"
    bl_label = "Delete Custom Preset"
    bl_description = 'Delete preset'

    preset_file: StringProperty()

    def execute(self, context):
        preset_path = Path(self.preset_file)
        if preset_path.exists():
            preset_path.unlink()
            props()['preset_enum']= 0
            self.report({'INFO'}, f"Deleted preset: {preset_path.name}")
        else:
            self.report({'ERROR'}, "Preset not found")
        return {'FINISHED'}


class NODE_OT_stm_execute_preset(SubOperatorPoll,Operator):
    bl_idname = "node.stm_execute_preset"
    bl_label = "Execute a Python Preset"
    bl_description = 'Select preset'

    preset_file: StringProperty()

    def execute(self, context):
        if not self.preset_file:
            self.report({'ERROR'}, "Preset name cannot be empty")
            return {'CANCELLED'}
        filer = f"{Path(NODE_OT_stm_presets_dialog.p_dir).joinpath(self.preset_file)}"
        if filer in [p[0] for p in propper.get_preset_list()]:
            print("reading preset")
            props().preset_enum = filer
            return {'FINISHED'}
        return {'CANCELLED'}


class NODE_OT_add_preset_popup(SubOperatorPoll,Operator):
    bl_idname = "node.add_preset_popup"
    bl_label = "Add Preset..."
    bl_description = "Add a new preset"

    preset_name: StringProperty(name="Preset Name")

    def execute(self, context):
        if not self.preset_name:
            self.report({'ERROR'}, "Preset name cannot be empty")
            return {'CANCELLED'}
        p_file = Path(NODE_OT_stm_presets_dialog.p_dir).joinpath(self.preset_name)
        filer = f"{p_file}{'.py' if 'py' not in p_file.suffix else ''}"
        with open(filer, "w", encoding="utf-8") as w:
            w.write(str(propper.fill_settings()))
        props().preset_enum = filer
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")


class NODE_OT_stm_fill_names(SubOperatorPoll,Operator):
    bl_idname = "node.stm_fill_names"
    bl_label = "Synch line names with files"
    bl_description = 'Rename panel lines from keywords detected in the texture files'

    def execute(self, context):
        propper.synch_names()
        return {'FINISHED'}

"""
def set_settings(self,val):
    props().stm_all = val

def get_settings(self):
    return f"{propper.fill_settings()}"
"""

class IMPORT_OT_stm_window(Operator):
    bl_idname = "import.stm_window"
    bl_label = "Import Textures"
    bl_description = "Open a substance textures importer panel"
    bl_options = {"REGISTER", "UNDO"}

    #settings : StringProperty(get=get_settings,set=set_settings)
    directory: StringProperty(subtype="DIR_PATH",get=get_directory,set=set_directory)
    op: BoolProperty(name="Options", default=True)
    p_dir = NODE_OT_stm_presets_dialog.p_dir

    @classmethod
    def poll(cls, context):
        try:
            return len(bpy.data.materials) > 0 and props()
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            return False

    def execute(self, context):
        for i in range (2):
            ndh.handle_nodes(not i)
            self.report({'INFO'},("\n").join(ndh.report_content))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        if self.p_dir.exists():
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            split = row.split(factor=0.85, align=True)
            split.prop(props(), "preset_enum", text="")
            buttons_row = split.row(align=True)
            buttons_row.operator("node.add_preset_popup", text="", icon="ADD")
            del_op = buttons_row.operator("node.stm_delete_preset", text="", icon="REMOVE")
            del_op.preset_file = props().preset_enum

        row = layout.row()
        row.prop(props(), "target")
        draw_panel(self,context)
        row = layout.row()
        row.alignment = 'LEFT'
        row.prop(props(), "advanced_mode", text="Manual Mode ", )
        row = layout.row()
        row.operator("node.stm_assign_nodes",text="Assign Images")
        row.separator()
        row.operator("node.stm_make_nodes",text="Setup Nodes")
        row = layout.row(align = True)
        row.alignment = 'LEFT'
        row.prop(self, "op", icon="TRIA_DOWN" if self.op else "TRIA_RIGHT", emboss=False)
        if self.op:
            NODE_PT_stm_options.draw(self, context)
