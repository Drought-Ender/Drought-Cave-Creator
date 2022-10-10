import copy

class Colors:
    def __init__(self, r:int, g:int, b:int, a:int):
        self.red = r
        self.green = g
        self.blue = b
        self.alpha = a


class Fog:
    def __init__(self, start:float, end:float):
        self.start = start
        self.end = end

class FogLight:
    def __init__(self, color:Colors, fog_parms:Fog):
        self.color = color
        self.fog_parms = fog_parms

class SpotLight:
    def __init__(self, color:Colors, cutoff:float):
        self.color = color
        self.cutoff = cutoff

class lightParameter:
    def __init__(self, move_dist:float, main:SpotLight, sub:SpotLight, specular:Colors, ambient:Colors, fog:FogLight, shadow:Colors):
        self.move_dist = move_dist
        self.main = main
        self.sub = sub
        self.specular = specular
        self.ambient = ambient
        self.fog = fog
        self.shadow = shadow

class LightCommon:
    def __init__(self, version:str, light_type:int):
        self.version = version
        self.light_type = light_type

class LightFile:
    def __init__(self, common:LightCommon, normal:lightParameter, orb:lightParameter):
        self.common = common
        self.normal = normal
        self.orb = orb

#

def read_light(light):
    common = read_common(light)
    orb = read_params(light, 10)
    normal = orb if len(light) < 100 else read_params(light, 94)
    return LightFile(common, normal, orb)

def read_common(light):
    light_ver = str(light[8])
    comment_start = light_ver.index("#")
    light_ver = light_ver[2:comment_start].strip()
    light_ver = light_ver.split(" ")[0].strip(" \\\n\t\r\btnrb")
    light_type = str(light[9])
    comment_start = light_type.index("#")
    light_type = light_type[2:comment_start].strip()
    light_type = int(light_type.split(" ")[0].strip(" \\\n\t\r\btnrb"))
    return LightCommon(light_ver, light_type)

def read_params(light, start_index):
    move_dist = read_comment_line(light[start_index + 8], float)
    main = read_spotlight(light, start_index + 14)
    sub = read_spotlight(light, start_index + 28)
    specular = read_color(light, start_index + 43)
    ambient = read_color(light, start_index + 52)
    fog = read_fog(light, start_index + 60)
    shadow = read_color(light, start_index + 76)
    return lightParameter(move_dist, main, sub, specular, ambient, fog, shadow)

def read_comment_line(line, get_type):
    line = str(line)
    comment_start = line.find("#")
    line = line[2:comment_start].strip()
    line = line.split(" ")
    return get_type(line[2])

def read_color(light, start_index):
    r = read_comment_line(light[start_index + 2], int)
    g = read_comment_line(light[start_index + 3], int)
    b = read_comment_line(light[start_index + 4], int)
    a = read_comment_line(light[start_index + 5], int)
    return Colors(r, g, b, a)

def read_fog(light, start_index):
    colors = read_color(light, start_index + 1)
    fog_start = read_comment_line(light[start_index + 11], float)
    fog_end = read_comment_line(light[start_index + 12], float)
    return FogLight(colors, Fog(fog_start, fog_end))

def read_spotlight(light, start_index):
    colors = read_color(light, start_index + 1)
    spot = read_comment_line(light[start_index + 11], float)
    return SpotLight(colors, spot)


def export_light(light:LightFile):
    export_string = [
        "############################################### \n",
        "#\n",
        "# Game Light Mgr Setting\n"
        "#\n",
        "############################################### \n",
        "#=============================================== \n",
        "#\t共通設定 \n"
        "#=============================================== \n"
        f"{light.common.version} \t# バージョン\n",
        f"{light.common.light_type}\t# タイプ \n"]
    for light_param in (light.orb, light.normal):
        export_string += [
            "#=============================================== \n",
            "#\tスポットタイプ設定 \n",
            "#=============================================== \n",
            "#----------------------------------------------- \n",
            "# パラメタ \n",
            "#----------------------------------------------- \n",
            "# MoveParms\n",
            "{\n",
            f"\t{{f000}} 4 {light_param.move_dist:.6f} \t# 光源までの距離\n",
            "\t{_eof} \n",
            "}\n",
            "#----------------------------------------------- \n",
            "#　ライト設定 \n",
            "#----------------------------------------------- \n",
            "# メインライト \n"] + export_spot(light_param.main) + [
            "# サブライト \n"] + export_spot(light_param.sub) + [
            "# スペキュラライト \n"] + export_color(light_param.specular) + [
            "# アンビエントライト \n"] + export_color(light_param.ambient) + [
            "# フォグ \n"] + export_fog(light_param.fog) + [
            "# 影 \n"] + export_color(light_param.shadow)
    return export_string


def export_spot(spotlight:SpotLight):
    return export_color(spotlight.color) + [
        "# SpotParms\n",
        "{\n",
        f"\t{{f000}} 4 {spotlight.cutoff:.6f} \t# カットオフ\n",
        "\t{_eof} \n",
        "}\n"
        ]

def export_color(color:Colors):
    return [
        "# ColorParms\n",
        "{\n",
        f"\t{{u800}} 4 {color.red} \t# 赤\n",
        f"\t{{u801}} 4 {color.green} \t# 緑\n",
        f"\t{{u802}} 4 {color.blue} \t# 青\n",
        f"\t{{u803}} 4 {color.alpha} \t# アルファ\n",
        "\t{_eof} \n",
        "}\n"]

def export_fog(foglight:FogLight):
    return export_color(foglight.color) + [
        "# GameFogParms\n",
        "{\n",
        f"\t{{f000}} 4 {foglight.fog_parms.start:.6f} \t# 開始z値\n",
        f"\t{{f001}} 4 {foglight.fog_parms.end:.6f} \t# 終了z値\n",
        "\t{_eof} \n",
        "}\n"
        ]

DEFAULT_COLORS = Colors(0, 0, 0, 255)
DEFAULT_SPOTLIGHT = SpotLight(copy.copy(DEFAULT_COLORS), 30.0)
DEFAULT_FOG = Fog(1000.0, 10000.0)
DEFAULT_FOGLIGHT = FogLight(copy.copy(DEFAULT_COLORS), copy.copy(DEFAULT_FOG))
DEFAULT_NOORB = lightParameter(1500.0,
    copy.copy(DEFAULT_SPOTLIGHT),
    copy.copy(DEFAULT_SPOTLIGHT),
    copy.copy(DEFAULT_COLORS),
    copy.copy(DEFAULT_COLORS),
    copy.copy(DEFAULT_FOGLIGHT),
    copy.copy(DEFAULT_COLORS)
    )
DEFAULT_ORB = lightParameter(500.0,
    copy.copy(DEFAULT_SPOTLIGHT),
    copy.copy(DEFAULT_SPOTLIGHT),
    copy.copy(DEFAULT_COLORS),
    copy.copy(DEFAULT_COLORS),
    copy.copy(DEFAULT_FOGLIGHT),
    copy.copy(DEFAULT_COLORS)
    )
DEFAULT_LIGHTCOMMON = LightCommon("{0001}", 1)
DEFAULT_LIGHT = LightFile(copy.copy(DEFAULT_LIGHTCOMMON), copy.copy(DEFAULT_NOORB), copy.copy(DEFAULT_ORB))

