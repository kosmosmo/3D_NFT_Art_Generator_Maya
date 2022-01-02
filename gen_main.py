import os,json,bisect,random,subprocess
import maya.cmds as cmds


def open_folder( folder):
    subprocess.Popen('explorer "{}"'.format(folder.replace('/', '\\')))


def write_to_json( path, data):
    with open(path, 'w+') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def load_json( path):
    f = open(path, "r")
    return json.loads(f.read())


def create_layer_map_json():
    layers_map = {}
    layers = get_root()
    trait_types = cmds.listRelatives( layers, children=True ,f=True)
    for tt in trait_types:
        type_name = tt.split('|')[-1]
        layers_map[type_name] = {
            "attributes":{
                "00_no_trait": {
                    "trait_weight": 1.0
                }
            }
        }
        traits = cmds.listRelatives( tt, children=True,f=True )
        for t in traits:
            trait_name = t.split('|')[-1]
            layers_map[type_name][ "attributes"][trait_name] = {"trait_weight": 1.0}
    return layers_map

def get_weight(attributes):
    population = []
    weight = []
    for key,val in attributes.items():
        population.append(key)
        weight.append(val['trait_weight'])
    return [population,weight]

def generate_trait_map(layers_map_json,total_art):
    with open(layers_map_json, 'r') as f:
        layers_map = json.load(f)
    trait_map = {}
    visited = set()
    i = 0
    while i < total_art:
        print ('generating number ' + str(i))
        temp = {}
        atts = ''
        for key,val in layers_map.items():
            population, weights = get_weight(val['attributes'])
            random_pick =random_choices(population=population, weights=weights)
            if random_pick == '00_no_trait':
                random_pick = ''
            temp[key] = random_pick
            atts += key + ':' +  temp[key]+ ','
        if atts not in visited:
            visited.add(atts)
            trait_map[i] = temp
            i += 1
    return trait_map

def random_choices(population,weights):
    added_weight = []
    temp = 0
    for w in weights:
        temp += w
        added_weight.append(temp)
    random_num = random.uniform(0, added_weight[-1])
    index = bisect.bisect(added_weight, random_num)
    return population[index]

def get_root():
    layers = cmds.ls('layers')
    if len(layers) != 1:
        layers = cmds.ls(sl=True)
        if len(layers) != 1:
            return None
    return layers[0]

def get_all_trait(layers_map):
    traits = []
    trait_types = []
    root = get_root()
    for key,val in layers_map.items():
        trait = root+'|'+key
        traits.append(trait)
        for k,v in val['attributes'].items():
            if k == "00_no_trait":
                continue
            trait_types.append(trait+'|'+k)
    return [traits,trait_types]

def set_trait_key(traits,trait_types,frame):
    for item in traits:
        cmds.setAttr(item+'.v', 1)
        cmds.setKeyframe(item+'.v',t=frame)
    for item in trait_types:
        cmds.setAttr(item+'.v', 0)
        cmds.setKeyframe(item+'.v',t=frame)

def set_keys(trait_map,layer_map,frame_range):
    root = get_root()
    all_trait = get_all_trait(layer_map)
    traits = all_trait[0]
    trait_types = all_trait[1]
    for key,val in trait_map.items():
        set_trait_key(traits,trait_types,key)
        for k,v in val.items():
            full_name = '{}|{}|{}'.format(root,k,v)
            if not v:
                cmds.setAttr(root + '|' + k+'.v',0)
                cmds.setKeyframe(root + '|' + k,t=key)
            else:
                cmds.setAttr(full_name+'.v', 1)
                cmds.setKeyframe(full_name, t=key)

def clear_keys(layer_map):
    all_trait = get_all_trait(layer_map)
    traits = all_trait[0]
    trait_types = all_trait[1]
    for item in traits:
        cmds.cutKey( item)
    for item in trait_types:
        cmds.cutKey(item)