import shutil, os
import CaveLibrary.cave as cave, settings

this_dir = os.getcwd()

def setup_cavegen():
    if os.path.exists("./CaveGen-master/output/Output/output.png"):
        os.remove("./CaveGen-master/output/Output/output.png")
    if os.path.exists("./CaveGen-master/output/!caveinfo/output.png"):
        os.remove("./CaveGen-master/output/!caveinfo/output.png")
    keys = settings.settings
    if os.path.exists("./CaveGen-master/files/droughtCaveEditor/resulttex/itemIcons/"):
        shutil.rmtree("./CaveGen-master/files/droughtCaveEditor/resulttex/itemIcons/")
    if os.path.exists("./CaveGen-master/files/droughtCaveEditor/enemytex/tekiIcons/"):
        shutil.rmtree("./CaveGen-master/files/droughtCaveEditor/enemytex/tekiIcons/")
    shutil.copytree(f"./presets/{keys.preset}/itemIcons/", "./CaveGen-master/files/droughtCaveEditor/resulttex/itemIcons/")
    shutil.copytree(f"./presets/{keys.preset}/tekiIcons/", "./CaveGen-master/files/droughtCaveEditor/enemytex/tekiIcons/")

def run_cavegen(caveInfo:cave.CaveInfo, unitsFile:str, sublevel:int, seed:int):
    setup_cavegen()
    with open("./CaveGen-master/files/droughtCaveEditor/caveinfo/caveinfo.txt", "w",  encoding='utf-8') as f:
        f.writelines(cave.export_cave(caveInfo))
    shutil.copy(unitsFile, "./CaveGen-master/files/droughtCaveEditor/units/units.txt")
    os.chdir(f"{this_dir}/CaveGen-master")
    os.system(f"java -jar CaveGen.jar cave EC-{sublevel} -num 1 -seed {hex(seed)} -noPrint")
    os.chdir(this_dir)
    return "./CaveGen-master/output/Output/output.png"

def run_caveinfo(caveInfo:cave.CaveInfo, unitsFile:str, sublevel:int):
    setup_cavegen()
    with open("./CaveGen-master/files/droughtCaveEditor/caveinfo/caveinfo.txt", "w",  encoding='utf-8') as f:
        f.writelines(cave.export_cave(caveInfo))
    shutil.copy(unitsFile, "./CaveGen-master/files/droughtCaveEditor/units/units.txt")
    os.chdir(f"{this_dir}/CaveGen-master")
    os.system(f"java -jar CaveGen.jar cave EC-{sublevel} -caveInfoReport -noPrint -drawSpawnPoints")
    os.chdir(this_dir)
    return "./CaveGen-master/output/!caveinfo/output.png"
