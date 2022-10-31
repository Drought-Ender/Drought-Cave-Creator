import os
import shutil
import settings
from wwlib.fs_helpers import *
from wwlib.bti import BTIFile
from wwlib.yaz0 import Yaz0
from wwlib.rarc import RARC
from wwlib.dol import DOL
from wwlib.rel import REL, RELRelocation, RELRelocationType
from wwlib.gcm import GCM
from wwlib.jpc import JPC


def import_bti_by_data(data):
    return BTIFile(data)

def read_bti(bti_path):
    with open(bti_path, "rb") as f:
      data = BytesIO(f.read())
    
    import_bti_by_data(data).render().save(bti_path+".png")

def import_rarc_by_path(rarc_path):
    with open(rarc_path, "rb") as f:
      data = BytesIO(f.read())
    
    
    return import_rarc_by_data(data)
  
def import_rarc_by_data(data):
    rarc = RARC()
    rarc.read(data)
    
    return rarc
    

def extract_all_files_from_rarc_folder_by_path(path, folder_path):
    rarc = import_rarc_by_path(path)
    root_node = rarc.nodes[0]
    node = root_node
    rarc.extract_node_to_disk(node, folder_path)

def decompress_yaz0_by_paths(comp_path, decomp_path):
    with open(comp_path, "rb") as f:
      comp_data = BytesIO(f.read())
    decomp_data = Yaz0.decompress(comp_data)
    with open(decomp_path, "wb") as f:
        decomp_data.seek(0)
        f.write(decomp_data.read())

def prep_cavgen_unit(unit_path, end):
    os.mkdir(end)
    decompress_yaz0_by_paths(f"{unit_path}/arc.szs", f"{end}/arc.arc")
    decompress_yaz0_by_paths(f"{unit_path}/texts.szs", f"{end}/texts.arc")
    extract_all_files_from_rarc_folder_by_path(f"{end}/arc.arc", f"{end}/arc.d/")
    extract_all_files_from_rarc_folder_by_path(f"{end}/texts.arc", f"{end}/texts.d/")
    read_bti(f"{end}/arc.d/texture.bti")
    os.remove(f"{end}/texts.arc")
    os.remove(f"{end}/arc.arc")
    os.remove(f"{end}/arc.d/view.bmd")
    os.remove(f"{end}/arc.d/texture.bti")

def run_cavegen_setup():
    if os.path.exists("./CaveGen-master/files/droughtCaveEditor/arc/"):
        shutil.rmtree("./CaveGen-master/files/droughtCaveEditor/arc/")
    os.mkdir("./CaveGen-master/files/droughtCaveEditor/arc/")
    for subdir, dirs, files in os.walk(f"{settings.settings.unit_path}"):
        for dir in dirs:
            dir_name = dir.split()[-1]
            prep_cavgen_unit(f"{settings.settings.unit_path}{dir_name}/", f"./CaveGen-master/files/droughtCaveEditor/arc/{dir_name}")
