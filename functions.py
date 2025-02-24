import bpy
from pathlib import Path
from os.path import commonprefix

def props():
    return getattr(bpy.context.preferences.addons[__package__].preferences, "props", None)

def stm_mat():
    return bpy.context.window_manager.get('current_mat','')

def stm_nodes():
    return stm_mat().node_tree.nodes

def node_links():
    return getattr(bpy.context.preferences.addons[__package__].preferences, "node_links", None)

def shader_links():
    return getattr(bpy.context.preferences.addons[__package__].preferences, "shader_links", None)

def texture_importer():
    return getattr(bpy.context.preferences.addons[__package__].preferences, "maps", None)

def texture_index():
    return getattr(texture_importer(), "texture_index", None)

def lines():
    return getattr(texture_importer(), "textures", None)

def p_lines():
    return [line for line in lines() if line.line_on]

def line_index(line):
    for i,liner in enumerate(lines()) :
        if liner == line:
            return i
    return None

def mat_name_cleaner(mat_name):
        return mat_name.split(".0")[0] if props().dup_mat_compatible else mat_name

def get_shaders_list_eve():
    shaders_list = [
        ('ShaderNodeVolumePrincipled', 'Principled Volume', ''),
        ('ShaderNodeVolumeScatter', 'Volume Scatter', ''),
        ('ShaderNodeVolumeAbsorption', 'Volume Absorption', ''),
        ('ShaderNodeEmission', 'Emission', ''),
        ('ShaderNodeBsdfDiffuse', 'Diffuse BSDF', ''),
        ('ShaderNodeBsdfGlass', 'Glass BSDF', ''),
        ('ShaderNodeBsdfGlossy', 'Glossy BSDF', ''),
        ('ShaderNodeBsdfRefraction', 'Refraction BSDF', ''),
        ('ShaderNodeSubsurfaceScattering', 'Subsurface Scattering BSSRDF', ''),
        ('ShaderNodeEeveeSpecular', 'Specular BSDF', ''),
        ('ShaderNodeBsdfTranslucent', 'Translucent BSDF', ''),
        ('ShaderNodeBsdfTransparent', 'Transparent BSDF', ''),
        ('ShaderNodeBsdfPrincipled', 'Principled BSDF', ''),
    ]
    if props().include_ngroups:
        for i in node_links():
            shaders_list.append((i.nodetype, i.nodetype, ''), )
    shaders_list.reverse()
    return shaders_list

def get_shaders_list():
    if getattr(bpy.context,'scene',None):
        if getattr(bpy.context.scene.render,'engine','BLENDER_EEVEE_NEXT') == 'BLENDER_EEVEE_NEXT' :
            return get_shaders_list_eve()
        if bpy.context.scene.render.engine == 'CYCLES' :
            return get_shaders_list_cycles()
    return get_shaders_list_eve()

def make_clean_channels(line):
    line.channels.socket.clear()
    for i in range(3):
        item = line.channels.socket.add()
        item.name = "RGB"[i]
        item.line_name = line.name
        item['input_sockets'] = 0

def initialize_defaults():
    lines().clear()
    maps = ["Color","Metallic","Roughness","Normal"]
    for i in range(4):
        item = lines().add()
        item.name = f"{maps[i]}"
        make_clean_channels(item)
        default_sockets(item)

def safe_refresh(context=None):
    #wish = {line.name: (line['input_sockets'],[ch['input_sockets'] for ch in line.channels.socket]) for line in lines()}
    clean_input_sockets()
    refresh_shader_links()
    #get_wish(wish)

def get_shaders_list_cycles():
    shaders_list = [
        ('ShaderNodeBsdfHairPrincipled', 'Principled-Hair BSDF', ''),
        ('ShaderNodeVolumePrincipled', 'Principled Volume', ''),
        ('ShaderNodeVolumeScatter', 'Volume Scatter', ''),
        ('ShaderNodeVolumeAbsorption', 'Volume Absorption', ''),
        ('ShaderNodeEmission', 'Emission', ''),
        ('ShaderNodeBsdfDiffuse', 'Diffuse BSDF', ''),
        ('ShaderNodeBsdfGlass', 'Glass BSDF', ''),
        ('ShaderNodeBsdfGlossy', 'Glossy BSDF', ''),
        ('ShaderNodeBsdfRefraction', 'Refraction BSDF', ''),
        ('ShaderNodeSubsurfaceScattering', 'Subsurface Scattering BSSRDF', ''),
        ('ShaderNodeBsdfToon', 'Toon BSDF', ''),
        ('ShaderNodeBsdfTranslucent', 'Translucent BSDF', ''),
        ('ShaderNodeBsdfTransparent', 'Transparent BSDF', ''),
        ('ShaderNodeBsdfHair', 'Hair BSDF', ''),
        ('ShaderNodeBsdfSheen', 'Sheen BSDF', ''),
        ('ShaderNodeBsdfPrincipled', 'Principled BSDF', ''),
    ]
    if props().include_ngroups:
        for i in node_links():
            shaders_list.append((i.nodetype, i.nodetype, ''), )
    shaders_list.reverse()
    return shaders_list

def set_nodes_groups():
    ng = bpy.data.node_groups
    node_links().clear()
    mat_tmp = bpy.data.materials.new(name="tmp_mat")
    mat_tmp.use_nodes = True
    for nd in ng:
        nw = mat_tmp.node_tree.nodes.new('ShaderNodeGroup')
        nw.node_tree = nd
        if len(nw.inputs) + len(nw.outputs) > 0:
            new_link = node_links().add()
            new_link.name = nd.name
            new_link.label = nd.name
            new_link.nodetype = nd.name
            for sk in [n.name for n in nw.inputs if n.type != "SHADER"]:
                si = new_link.in_sockets.add()
                si.name = sk
    mat_tmp.node_tree.nodes.clear()
    bpy.data.materials.remove(mat_tmp)

def del_panel_line():
    if 0 <= texture_index() < len(lines()):
        lines().remove(texture_index())
        texture_importer().texture_index = max(0, texture_index() - 1)

def add_panel_lines():
    texture = lines().add()
    texture.name = get_available_name()
    texture_importer().texture_index = len(lines()) - 1
    make_clean_channels(texture)

def adjust_lines_count(difference):
    method = del_panel_line if difference < 0 else add_panel_lines
    for _i in range(abs(difference)):
        method()

def get_available_name():
    new_index = 0
    new_name = "Custom map 1"
    while new_name in [item.name for item in lines()]:
        new_index += 1
        new_name = f"Custom map {new_index}"
    return new_name

def refresh_shader_links():
    shader_links().clear()
    mat_tmp = bpy.data.materials.new(name="tmp_mat")
    mat_tmp.use_nodes = True
    for shader_enum in get_shaders_list_eve():
        node_type = str(shader_enum[0])
        if node_type is not None and node_type != '0' :
            if node_type in bpy.data.node_groups.keys():
                new_node = mat_tmp.node_tree.nodes.new(type='ShaderNodeGroup')
                new_node.node_tree = bpy.data.node_groups[str(shader_enum[1])]
            else:
                new_node = mat_tmp.node_tree.nodes.new(type=node_type)
            new_shader_link = shader_links().add()
            new_shader_link.name = str(shader_enum[1])
            new_shader_link.shadertype = node_type
            for sk in [i for i in new_node.inputs.keys() if not i == 'Weight']:
                si = new_shader_link.in_sockets.add()
                si.name = sk

    for shader_enum in get_shaders_list_cycles():
        node_type = str(shader_enum[0])
        if node_type is not None and node_type != '0' :
            if node_type in bpy.data.node_groups.keys():
                new_node = mat_tmp.node_tree.nodes.new(type='ShaderNodeGroup')
                new_node.node_tree = bpy.data.node_groups[str(shader_enum[1])]
            else:
                new_node = mat_tmp.node_tree.nodes.new(type=node_type)
            new_shader_link = shader_links().add()
            new_shader_link.name = str(shader_enum[1])
            new_shader_link.shadertype = node_type
            for sk in [i for i in new_node.inputs.keys() if not i == 'Weight']:
                si = new_shader_link.in_sockets.add()
                si.name = sk

    mat_tmp.node_tree.nodes.clear()
    bpy.data.materials.remove(mat_tmp)

def refresh_inputs():
    clean_input_sockets()
    if props().include_ngroups:
        node_links().clear()
        set_nodes_groups()
    refresh_shader_links()

def check_special_keywords(term):
    if props().separators_list in term:
        return ""
    #no spaces
    matcher = { "Color":["color","col","colore","colour","couleur", "basecolor",
                            "emit", "emission", "albedo"],
                "Ambient Occlusion":["ambientocclusion","ambientocclusion","ambient",
                                        "occlusion","ao","ambocc","ambient_occlusion"],
                "Displacement":["relief","displacement","displace","displace_map"],
                "Disp Vect":["dispvect","dispvector","disp_vector","vector_disp",
                                "vectordisplacement","displacementvector",
                                "displacement_vector", "vector_displacement"],
                "Normal":["normal","normalmap","normalmap", "norm", "tangent"],
                "bump":["bump","bumpmap","bump map", "height","heightmap","weight","weight map"]
                }
    for k,v in matcher.items():
        if find_in_sockets(term.strip(),v):
            return k
    return ""

def synch_names():
    liners = []
    props().img_files.clear()
    exts = set(bpy.path.extensions_image)
    dir_content = [x.name for x in Path(props().usr_dir).glob('*.*') if x.suffix.lower() in exts]
    if len(dir_content) :
        for img in dir_content:
            i = props().img_files.add()
            i.name = img
        if mat_name_cleaner(stm_mat().name) in [i.name for i in props().img_files]:
            mat_related = [Path(_img).stem.lower() for _img in dir_content if mat_name_cleaner(stm_mat().name) in _img]
            prefix = commonprefix(mat_related)
            suffix = commonprefix([s[::-1] for s in mat_related])
            liners = sorted(list({i.replace(prefix,"").replace(suffix[::-1],"") for i in mat_related}))
    if len(liners) > 1 :
        adjust_lines_count(len(liners)-len(lines()))
        for i,l in enumerate(lines()) :
            l.name = liners[i]

def guess_sockets():
    for line in p_lines():
        default_sockets(line)

def get_wish(wish):
    for name, value in wish.items():
        try:
            lines()[name]['input_sockets'] = value[0]
        except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
            lines()[name]['input_sockets'] = 0
        for i,ch in enumerate(lines()[name].channels.socket):
            try:
                ch['input_sockets'] = value[1][i]
            except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
                ch['input_sockets'] = 0

def menu_func(self, context):
    self.layout.operator("import.stm_window", text="Substance Textures...")

def ShowMessageBox(message="", title="Message", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def get_linked_node(_socket):
    if _socket and _socket.is_linked:
        return _socket.links[0].from_node
    return None

def node_finder(node):
    if not node:
        return None
    if node.type in {"MIX_SHADER", "ADD_SHADER"}:
        return node_finder(get_linked_node(node.inputs[1])) or \
                node_finder(get_linked_node(node.inputs[2]))
    if node.type in "SEPARATE_COLOR":
        return None
    if node.type in "GROUP" and not props().include_ngroups:
        return None
    return node

def get_output_node():
    if not stm_nodes():
        return None
    out_nodes = [n for n in stm_nodes() if n.type in "OUTPUT_MATERIAL"]
    for node in out_nodes:
        if node.is_active_output:
            return node
    return None

def get_shader_node():
    shader_node = None
    output_node = get_output_node()
    if output_node :
        shader_node = node_finder(get_linked_node(output_node.inputs["Surface"]))
    return shader_node


def get_target_mats(context):
        mat_list = []
        validtypes = ['SURFACE', 'CURVE', 'META', 'MESH']
        match props().target:
            case "selected_objects":
                if len(context.view_layer.objects):
                    mat_list = list({mat.material for obj in context.view_layer.objects.selected if obj.type in validtypes for mat in obj.material_slots if mat.material is not None and not mat.material.is_grease_pencil})
            case "all_visible":
                if len(context.view_layer.objects):
                    mat_list = list({mat.material for obj in context.view_layer.objects if obj.visible_get() and obj.type in validtypes for mat in obj.material_slots if mat.material is not None and not mat.material.is_grease_pencil})
            case "all_objects":
                if len(bpy.data.objects):
                    mat_list = list({mat.material for obj in bpy.data.objects if obj.type in validtypes for mat in obj.material_slots if mat.material is not None and not mat.material.is_grease_pencil})
            case "all_materials":
                mat_list = [mat for mat in bpy.data.materials if not mat.is_grease_pencil]
            case "active_obj":
                obj = context.view_layer.objects.active if context.view_layer.objects.active in list(context.view_layer.objects.selected) else None
                if obj and obj.type in validtypes:
                    mat_list = list({mat.material for mat in obj.material_slots if mat.material is not None and not mat.material.is_grease_pencil})
        return mat_list

def get_a_mat():
    mat = bpy.context.object.active_material if not bpy.context.object.active_material.is_grease_pencil else None
    if not mat:
        mat = get_target_mats()[0] or [mat for mat in bpy.data.materials if not mat.is_grease_pencil][0] if [mat for mat in bpy.data.materials if not mat.is_grease_pencil] else None
    return mat

def clean_input_sockets():
    #required to avoid warning errors
    for line in lines():
        line['input_sockets'] = 0
        for ch in line.channels.socket:
            ch['input_sockets'] = 0

def get_shader_inputs():
    shd = get_shader_node()
    if shd and shd.inputs:
        return shd.inputs.keys()
    return None

def get_hard_sockets():
        return [ "Base Color", "Metallic","Roughness","IOR", "Alpha",
                "Normal", "Diffuse Roughness", "Subsurface Weight", "Subsurface Radius",
                "Subsurface Scale", "Subsurface IOR","Subsurface Anisotropy","Specular IOR Level",
                "Specular Tint","Anisotropic", "Anisotropic Rotation", "Tangent",
                "Transmission Weight", "Coat Weight","Coat Roughness","Coat IOR", "Coat Tint",
                "Coat Normal","Sheen Weight", "Sheen Roughness","Sheen Tint", "Emission Color",
                "Emission Strength", "Thin Film Thickness", "Thin Film IOR" ]

def set_enum_sockets_items():
    rawdata = []
    if not props().replace_shader:
        rawdata = get_shader_inputs()
    else:
        selectedshader = props().shaders_list
        shaders = [sh.in_sockets for sh in shader_links() if sh.shadertype in selectedshader]
        if len(shaders) > 0:
            rawdata = [sk.name for sk in shaders[0]]
        customs = [sh.in_sockets for sh in node_links() if sh.nodetype in selectedshader]
        if props().include_ngroups and len(customs) > 0:
            rawdata = [sk.name for sk in customs[0]]
        if not len(rawdata) > 0 :
            rawdata = get_hard_sockets()
    if not rawdata:
        clean_input_sockets()
        rawdata = [sh.name for sh in props().in_sockets]
    else:
        rawdata.append('Ambient Occlusion')
    props().in_sockets.clear()
    for sk in rawdata:
        si = props().in_sockets.add()
        si.name = sk

def format_enum(rawdata):
    default = ('no_socket', '-- Unmatched Socket --', '')
    if rawdata == []:
        return [default]
    dispitem = [('Disp Vector', 'Disp Vector', ''), ('Displacement', 'Displacement', '')]
    items = [(item, item, '') for item in rawdata]
    items.extend(dispitem)
    items.reverse()
    items.append(default)
    items.reverse()
    return items

def get_sockets_enum_items():
    if len(props().in_sockets) == 0:
        set_enum_sockets_items()
    return format_enum([sh.name for sh in props().in_sockets])

def sicks():
    return [sc[0] for sc in get_sockets_enum_items()]

def find_in_sockets(term,target_list=None):
        if term in "":
            return None
        if not target_list:
            target_list = sicks()
        for sock in target_list:
            match = term.replace(" ", "").lower() in sock.replace(" ", "").lower()
            if match:
                return sock
        return None

def detect_multi_socket(line):
        splitted = line.name.split(props().separators_list)
        if not len(splitted) > 1 :
            line['split_rgb'] = False
            return False
        line['split_rgb'] = True
        if len(splitted) != 3 :
            for i in range(3-len(splitted)):
                splitted.append("no_socket")
        for i,_sock in enumerate(splitted):
            if i > 2:
                return False
            sock = find_in_sockets(_sock)
            if not sock:
                sock = check_special_keywords(_sock)
                if not sock:
                    sock = sicks()[0]
                if sock in "bump" :
                    sock = 'Normal'
            if (sock in sicks() and line.auto_mode) or (not line.auto_mode and sock in 'no_socket'):
                line.channels.socket[i]['input_sockets'] = sicks().index(sock)
        return True

def default_sockets(line):
        if not line.auto_mode :
            return
        if detect_multi_socket(line):
            return
        sock = find_in_sockets(line.name)
        if not sock:
            sock = check_special_keywords(line.name)
            if not sock:
                sock = sicks()[0]
            if "bump" in sock:
                sock = 'Normal'
        if sock in sicks():
            line['input_sockets'] = sicks().index(sock)

def find_file(line):
    if line.manual:
        return line.file_name
    mat_name = mat_name_cleaner(bpy.context.window_manager.get('current_mat','').name)
    if len(props().img_files) > 0 :
        dir_content = [i.name for i in props().img_files]
        lower_dir_content = [v.lower() for v in dir_content]
        map_name = line.name
        for map_file in lower_dir_content:
            if mat_name.lower() in map_file and map_name.lower() in map_file:
                return str(Path(props().usr_dir).joinpath(Path(dir_content[lower_dir_content.index(map_file)])))
    return ""


def detect_a_map(line):
    line.file_name = find_file(line)
    default_sockets(line)
    line.file_is_real = False
    if line.file_name != "" :
        line.file_is_real = Path(line.file_name).exists() and Path(line.file_name).is_file()

def detect_relevant_maps():
    for line in p_lines():
        detect_a_map(line)

def get_lines_count(self):
    self.liners.clear()
    for i,line in enumerate(lines()):
        l = self.liners.add()
        l.liners_id = i
        l.liners_name = line.name
    return len(lines())

def set_lines_count(self,val):
    lines().clear()
    for i in range(val):
        l = lines().add()
        make_clean_channels(l)

def set_cb_include_ngroups(self,val):
    props()['include_ngroups'] = val

def get_cb_include_ngroups(self):
    return props().include_ngroups

def set_cb_clear_nodes(self,val):
    props()['clear_nodes'] = val

def get_cb_clear_nodes(self):
    return props().clear_nodes

def set_cb_target(self,val):
    props()['target'] = val

def get_cb_target(self):
    return props().target

def set_cb_tweak_levels(self,val):
    props()['tweak_levels'] = val

def get_cb_tweak_levels(self):
    return props().tweak_levels

def set_cb_mode_opengl(self,val):
    props()['mode_opengl'] = val

def get_cb_mode_opengl(self):
    return props().mode_opengl

def set_cb_usr_dir(self,val):
    props()['usr_dir'] = val

def get_cb_usr_dir(self):
    return props().usr_dir

def set_cb_skip_normals(self,val):
    props()['skip_normals'] = val

def get_cb_skip_normals(self):
    return props().skip_normals

def set_cb_replace_shader(self,val):
    props()['replace_shader'] = val

def get_cb_replace_shader(self):
    return props().replace_shader

def set_cb_shaders_list(self,val):
    props()['shaders_list'] = val

def get_cb_shaders_list(self):
    return props().shaders_list

def set_cb_separators_list(self,val):
    props()['separators_list'] = val

def get_cb_separators_list(self):
    return props().separators_list

def set_cb_lines_from_files(self,val):
    props()['lines_from_files'] = val

def get_cb_lines_from_files(self):
    return props().lines_from_files

def set_cb_advanced_mode(self,val):
    props()['advanced_mode'] = val

def get_cb_advanced_mode(self):
    return props().advanced_mode

def set_cb_only_active_mat(self,val):
    props()['only_active_mat'] = val

def get_cb_only_active_mat(self):
    return props().only_active_mat

def set_cb_assign_images(self,val):
    props()['assign_images'] = val

def get_cb_assign_images(self):
    return props().assign_images

def set_cb_setup_nodes(self,val):
    props()['setup_nodes'] = val

def get_cb_setup_nodes(self):
    return props().setup_nodes

def set_cb_dup_mat_compatible(self,val):
    props()['dup_mat_compatible'] = val

def get_cb_dup_mat_compatible(self):
    return props().dup_mat_compatible

def draw_panel(self,context):
    layout = self.layout
    row = layout.row()
    row.prop(props(), "target")
    row = layout.row()
    row.template_list(
        "NODE_UL_stm_list", "Textures",
        texture_importer(), "textures",
        texture_importer(), "texture_index",
        type="GRID",
        columns=1,
        rows=6,
    )
    button_col = row.column(align=True)
    button_col.operator("node.stm_add_item", icon="ADD", text="")
    button_col.operator("node.stm_remove_item", icon="REMOVE", text="")
    button_col.separator(factor=.5)
    button_col.operator("node.stm_move_line", icon="TRIA_UP", text="").down= False
    button_col.operator("node.stm_move_line", icon="TRIA_DOWN", text="").down= True
    button_col.separator(factor=.5)
    button_col.operator("node.stm_fill_names", icon="SETTINGS", text="")
    button_col.separator(factor=2)
    button_col.operator("node.stm_reset_substance_textures", icon="MEMORY", text="")
    if lines() and texture_index() < len(lines()):
        item = lines()[texture_index()]
        layout.prop(item, "line_on")
        sub_layout = layout.column()
        sub_layout.enabled = item.line_on
        sub_layout.prop(item, "auto_mode")
        sub_sub_layout = layout.column()
        sub_sub_layout.enabled = not item.auto_mode
        sub_sub_layout.prop(item, "split_rgb")
        if item.split_rgb:
            if item.channels.socket :
                sl = sub_sub_layout.column()
                sl.enabled = not item.auto_mode and item.line_on
                for i,sk in enumerate(item.channels.socket):
                    sl.prop(sk, "input_sockets",text=sk.name,icon=f"SEQUENCE_COLOR_0{((i*3)%9+1)}")
        if props().advanced_mode :
            sub_sub_layout = sub_layout.column()
            sub_sub_layout.prop(item, "manual")
            if item.manual :
                sub_sub_sub_layout = sub_sub_layout.column()
                sub_sub_sub_layout.prop(item, "file_name")
        if not item.split_rgb:
            sub_layout_2 = layout.column()
            sub_layout_2.enabled = not item.auto_mode and item.line_on
            sub_layout_2.prop(item, "input_sockets")


def get_name_up(self):
    return self.get("name","")

def set_name_up(self, value):
    self["name"] = value
    for ch in self.channels.socket:
        ch['line_name'] = value
    try:
        if (self.auto_mode and not self.manual) or self.split_rgb:
            default_sockets(self)
            if self.split_rgb :
                ch_sockets_up(self,bpy.context)
            elif self.auto_mode:
                enum_sockets_up(self,bpy.context)
    except AttributeError:
        pass

def get_line_bools(self):
    return [self.line_on,self.auto_mode,self.split_rgb,self.manual]

def set_line_bools(self, value):
    [self['line_on'],self['auto_mode'],self['split_rgb'],self['manual']] = self["line_bools"] = value

def get_line_vals(self):
    return [self['input_sockets']] + [ch['input_sockets'] for ch in self.channels.socket]

def set_line_vals(self, value):
    self['input_sockets'], self.channels.socket[0]['input_sockets'], self.channels.socket[1]['input_sockets'], self.channels.socket[2]['input_sockets'] = value

def init_prefs(self):
    prefs = bpy.context.preferences.addons[__package__].preferences
    if len(prefs.shader_links) == 0:
        prefs.shader_links.add()
    if len(prefs.maps.textures) == 0:
        maps = ["Color","Metallic","Roughness","Normal"]
        for i in range(4):
            item = prefs.maps.textures.add()
            item.name = f"{maps[i]}"
            item['input_sockets'] = i+2 +(int(not i%3)*2)*int(bool(i))
            make_clean_channels(item)
    refresh_props(props(),bpy.context)
    self.liners.clear()
    for line in lines():
        l = self.liners.add()

def line_on_up(self, context):
    default_sockets(self)
    safe_refresh()

def target_list_cb(self,context):
    targets = [('selected_objects', 'Selected Objects materials', '',0),
                ('all_visible', 'All visible Objects materials', '',1),
                ('all_objects', 'All Objects materials', '',2),
                ('all_materials', 'All scene materials', '',3),
                ('active_obj', 'Only Active Object in selection', '',4),
            ]
    return targets

def target_list_up(self,context):
    match self.target:
        case "selected_objects":
            set_operator_description("selected objects materials.")
        case "all_visible":
            set_operator_description("all visible objects materials.")
        case "all_objects":
            set_operator_description("all objects materials in the current viewlayer.")
        case "all_materials":
            set_operator_description("all the materials in the blend.")
            self.only_active_mat = False
        case "active_obj":
            pass

def set_operator_description(target):
    """
    bpy.types.NODE_OT_stm_import_textures.bl_description = "Setup nodes and load textures\
                                                            \n maps on " + target
    bpy.types.NODE_OT_stm_make_nodes.bl_description = "Setup Nodes on " + target
    bpy.types.NODE_OT_stm_assign_nodes.bl_description = "Load textures maps on " + target
    liste = [
        bpy.types.NODE_OT_stm_import_textures,
        bpy.types.NODE_OT_stm_make_nodes,
        bpy.types.NODE_OT_stm_assign_nodes
    ]
    for cls in liste:
        laclasse = cls
        unregister_class(cls)
        register_class(laclasse)
    """

def split_rgb_up(self,context):
    if not (len(self.channels.socket) and len(self.channels.socket) == 3):
        make_clean_channels(self)
    if self.auto_mode:
        default_sockets(self)
    ch_sockets_up(self,context) if self.split_rgb else enum_sockets_up(self,context)

def include_ngroups_up(self, context):
    if props().include_ngroups:
        set_nodes_groups()
    else:
        node_links().clear()
    set_enum_sockets_items()
    safe_refresh()
    guess_sockets()

def enum_sockets_cb(self, context):
    inp_list = None
    try:
        inp_list = get_sockets_enum_items()
    except (TypeError,NameError,KeyError,ValueError,AttributeError,OverflowError):
        if not inp_list or len(inp_list) < 5:
            return [('no_socket','-- Unmatched Socket --',''),('Base Color','Base Color',''),
                    ('Metallic','Metallic',''),('Roughness','Roughness',''),
                    ('IOR','IOR',''),('Alpha','Alpha',''),('Normal','Normal',''),
                    ('Diffuse Roughness','Diffuse Roughness',''),
                    ('Subsurface Weight','Subsurface Weight',''),
                    ('Subsurface Radius','Subsurface Radius',''),
                    ('Subsurface Scale','Subsurface Scale',''),
                    ('Subsurface IOR','Subsurface IOR',''),
                    ('Subsurface Anisotropy','Subsurface Anisotropy',''),
                    ('Specular IOR Level','Specular IOR Level',''),
                    ('Specular Tint','Specular Tint',''),('Anisotropic','Anisotropic',''),
                    ('Anisotropic Rotation','Anisotropic Rotation',''),('Tangent','Tangent',''),
                    ('Transmission Weight','Transmission Weight',''),
                    ('Coat Weight','Coat Weight',''),('Coat Roughness','Coat Roughness',''),
                    ('Coat IOR','Coat IOR',''),('Coat Tint','Coat Tint',''),
                    ('Coat Normal','Coat Normal',''),('Sheen Weight','Sheen Weight',''),
                    ('Sheen Roughness','Sheen Roughness',''),('Sheen Tint','Sheen Tint',''),
                    ('Emission Color','Emission Color',''),
                    ('Emission Strength','Emission Strength',''),
                    ('Thin Film Thickness','Thin Film Thickness',''),
                    ('Thin Film IOR','Thin Film IOR',''),
                    ('Disp Vector','Disp Vector',''),('Displacement','Displacement',''),
                    ('Ambient Occlusion','Ambient Occlusion',''),]
    return inp_list

def enum_sockets_up(self, context):
    if self.input_sockets not in sicks():
        self['input_sockets'] = 0
        return
    for line in p_lines():
        if line.split_rgb:
            for sk in line.channels.socket:
                if sk.input_sockets in self.input_sockets and not 'no_socket' in self.input_sockets and not sk.line_name in self.name:
                    sk['input_sockets'] = 0
                    line.auto_mode = False
        elif line.input_sockets in self.input_sockets and not 'no_socket' in self.input_sockets and not line == self:
            line['input_sockets'] = 0
            line.auto_mode = False

def ch_sockets_up(self, context):
    if not self.input_sockets in sicks():
        self['input_sockets'] = 0
        return
    for line in p_lines():
        if line.split_rgb:
            for sk in line.channels.socket:
                if sk.input_sockets in self.input_sockets and not 'no_socket' in self.input_sockets and not self == sk and not sk.line_name in line.name:
                    sk['input_sockets'] = 0
                    line.auto_mode = False
        elif line.input_sockets in self.input_sockets and not 'no_socket' in self.input_sockets and not self.line_name in line.name:
            line['input_sockets'] = 0
            line.auto_mode = False

def shaders_list_cb(self, context):
    return get_shaders_list()
    #else:
    #    return [('ShaderNodeBsdfPrincipled', 'Principled BSDF', '')]

def shaders_list_up(self, context):
    #forces rebuilding the sockets list
    self.replace_shader = not self.replace_shader
    self.replace_shader = not self.replace_shader

    context.view_layer.update()

def manual_up(self, context):
    if self.manual:
        props().target = 'active_obj'
        props().only_active_mat = True
    else:
        detect_a_map(self)

def advanced_mode_up(self, context):
    safe_refresh()
    if not self.advanced_mode:
        for line in lines():
            line.manual = False

def usr_dir_up(self, context):
    if self.lines_from_files:
        synch_names()
    self.dir_content = ""
    if not Path(self.usr_dir).is_dir():
        self.usr_dir = str(Path(self.usr_dir).parent)
        if not Path(self.usr_dir).is_dir():
            self.usr_dir = Path(bpy.utils.extension_path_user(f'{__package__}', create=True))
    exts = set(bpy.path.extensions_image)
    dir_content = [x.name for x in Path(self.usr_dir).glob('*.*') if x.suffix.lower() in exts]
    if len(dir_content) :
        for img in dir_content:
            i = props().img_files.add()
            i.name = img
    if self.include_ngroups:
        node_links().clear()
        include_ngroups_up(self,context)
    guess_sockets()

    context.view_layer.update()

def dup_mat_compatible_up(self,context):
    detect_relevant_maps()

def clear_nodes_up(self, context):
    if self.clear_nodes:
        self.replace_shader = True

def auto_mode_up(self,context):
    if self.auto_mode:
        default_sockets(self)

def only_active_mat_up(self, context):
    if "all_materials" in self.target and self.only_active_mat:
        self.target = "selected_objects"
    safe_refresh()

def refresh_props(self,context):
    set_enum_sockets_items()
    if self.include_ngroups:
        node_links().clear()
        include_ngroups_up(self,context)
    safe_refresh()
    guess_sockets()

def replace_shader_up(self, context):
    refresh_props(self,context)

def separators_cb(self,context):
    return [("_","_","(underscore)"),("-","-","(minus sign)"),(",",",","(comma)"),(";",";","(semicolon)"),(".",".","(dot)"),("+","+","(plus sign)"),("&","&","(ampersand)")]

def get_liners_name(self):
    return lines()[self.liners_id].name

def set_liners_name(self,val):
    lines()[self.liners_id]['name'] = val

def get_liners_vals(self):
    return lines()[self.liners_id].line_vals

def set_liners_vals(self,val):
    lines()[self.liners_id].line_vals = val

def get_liners_bools(self):
    return lines()[self.liners_id].line_bools

def set_liners_bools(self,val):
    lines()[self.liners_id].line_bools = val

def draw_options(self,context):
    layout = self.layout
    row = layout.row()
    row.alignment = 'LEFT'
    row.prop(props(), "advanced_mode", text="Manual Mode ", )
    row = layout.row()
    col = row.column(align = True)
    row = col.row(align = True)
    row.prop(props(), "replace_shader", text="Replace Shader",)
    row = row.split()
    if props().replace_shader :
        row.prop(props(), "shaders_list", text="")
    row = layout.row()
    row.prop(props(), "skip_normals", )
    row = layout.row()
    row.prop(props(), "mode_opengl", )
    row = layout.row()
    row.prop(props(), "include_ngroups", text="Enable Custom Shaders", )
    row = layout.row()
    row.prop(props(), "clear_nodes", text="Clear nodes from material", )
    row = layout.row()
    row.prop(props(), "tweak_levels", text="Attach Curves and Ramps ", )
    row = layout.row()
    row.prop(props(), "only_active_mat", text="Only active Material",)
    row = layout.row()
    row.prop(props(), "dup_mat_compatible", text="Duplicated material compatibility",)
    row = layout.row()
    row.prop(props(), "lines_from_files", text="Map names from files",)
    row = layout.row()
    row.prop(props(), "setup_nodes", text="Setup Nodes",)
    row = layout.row()
    row.prop(props(), "assign_images", text="Assign Images",)
    row = layout.row()
    row.separator()
