import configparser
import gettext
import locale
import os
import re
import subprocess
import sys
import datetime
from tkinter import messagebox

from rpp2exo.dict import mydict

R2E_VERSION = '2.09.3'
R2E_TITLE = 'RPPtoEXO v' + R2E_VERSION

if os.path.abspath(sys.argv[0]).endswith('.py'):
    TEMP_PATH = os.path.abspath('.')
else:
    TEMP_PATH = os.path.dirname(sys.executable)

CONFIG_PATH = os.path.join(os.path.dirname(sys.argv[0]), "config.ini")


class LoadFilterFileError(Exception):  # EXA読み込みエラー
    def __init__(self, message, filename=None):
        super().__init__(message)
        self.filename = filename


class ItemNotFoundError(Exception):  # 出力対象アイテム数0エラー
    pass


class TemplateNotFoundError(Exception):  # テンプレート読み込みエラー
    pass


def get_locale(language):
    """指定された言語の翻訳関数を返す"""
    return gettext.translation(
        'text',  # domain: 辞書ファイルの名前
        localedir=TEMP_PATH,  # 辞書ファイル配置ディレクトリ
        languages=[language],  # 翻訳に使用する言語
        fallback=True
    ).gettext


def replace_ordinal(num_str):
    def replace(match):
        num = int(match.group(1))
        # 10-20の間は' th'を付け、それ以外は1st, 2nd, 3rd等を処理
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th') if not (10 <= num % 100 <= 20) else 'th'
        return f"{num}{suffix}"

    return re.sub(r'(\d+)(th)', replace, num_str)


def ignore_sjis(encoding, path, chars=0):
    text = ''
    ext = os.path.splitext(path)[1]
    for c in path:
        try:
            c.encode(encoding)
            text += c
            chars += 1
            if chars >= 259 - len(ext):
                pass
        except UnicodeEncodeError:
            pass
    return text

def format_seconds(seconds):
    # 秒(REAPER管理)から、hh:mm:ss.ms(YMM4管理)に直す
    delta = datetime.timedelta(seconds=seconds)
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = delta.microseconds
    return "{:02d}:{:02d}:{:02d}.{:06d}".format(hours, minutes, seconds, microseconds)

def read_cfg():
    try:
        # 設定ファイルの読み込み
        config_ini = configparser.ConfigParser()
        config_ini.read(CONFIG_PATH, encoding='utf-8')

        # システムロケールの読込み
        default_lang = 'ja'
        if locale.getencoding() == 'cp936':
            default_lang = 'zh'

        # 欠損値を補完
        for default, option, section in [
            ('', 'RPPDir', 'Directory'),  # RPPの保存ディレクトリ
            ('', 'EXODir', 'Directory'),  # EXOの保存ディレクトリ
            ('', 'SrcDir', 'Directory'),  # 素材の保存ディレクトリ
            ('', 'AlsDir', 'Directory'),  # エイリアスの保存ディレクトリ
            ('0', 'is_ccw', 'Param'),     # 左右・上下反転時に反時計回りにするかどうか 0/1
            ('0', 'same_pitch_option', 'Param'),  # 同音程で反転を変更するオプションを表示するか 0/1
            ('0', 'patch_exists', 'Param'),  # patch.aulが存在するか 0/1
            ('0', 'use_roundup','Param'),  # 四捨五入処理を切り上げとするか 0/1
            ('0', 'use_ymm4', 'Param'),   # YMM4を使うかどうか 0/1
            ('', 'ymm4path', 'Param'),    # YMM4の実行ファイルパス
            ('RPPtoEXO', 'templ_name', 'Param'),  # YMM4のテンプレート保存名
            ('1', 'output_type', 'Param'),  # 「追加対象」のデフォルト値 0-4
            (default_lang, 'display', 'Language'),  # 表示言語
            (default_lang, 'exedit', 'Language'),  # 拡張編集の言語
        ]:

            if not config_ini.has_section(section):
                config_ini[section] = {}
            if not config_ini.has_option(section, option):
                config_ini[section][option] = default

        # Configファイルの初回作成時処理
        if not os.path.exists(CONFIG_PATH):
            config_ini['Param']['use_roundup'] = '1'

        # Configファイルの書き込み
        with open(CONFIG_PATH, 'w', encoding='utf-8') as file:
            config_ini.write(file)

            # パラメータの読み込み
            mydict["RPPLastDir"] = config_ini.get("Directory", "RPPDir")
            mydict["EXOLastDir"] = config_ini.get("Directory", "EXODir")
            mydict["SrcLastDir"] = config_ini.get("Directory", "SrcDir")
            mydict["AlsLastDir"] = config_ini.get("Directory", "AlsDir")
            mydict["IsCCW"] = int(config_ini.get("Param", "is_ccw"))
            mydict["AddSamePitchOption"] = int(config_ini.get("Param", "same_pitch_option"))
            mydict["PatchExists"] = int(config_ini.get("Param", "patch_exists"))
            mydict["UseRoundUp"] = int(config_ini.get("Param", "use_roundup"))
            mydict["UseYMM4"] = int(config_ini.get("Param", "use_ymm4"))
            mydict["YMM4Path"] = config_ini.get("Param", "ymm4path")
            mydict["TemplateName"] = config_ini.get("Param", "templ_name")
            mydict["OutputType"] = config_ini.get("Param", "output_type")
            mydict["DisplayLang"] = config_ini.get("Language", "display")
            mydict["ExEditLang"] = config_ini.get("Language", "exedit")

        global _
        _ = gettext.translation(
            'text',
            localedir=TEMP_PATH,
            languages=[mydict['DisplayLang']],
            fallback=True
            ).gettext

    except Exception as e:
        messagebox.showerror(R2E_TITLE, '壊れたconfig.iniを修復するため、全設定がリセットされます。\nconfig.ini is corrupted. Restoring defaults.')
        os.remove('config.ini')
        restart_software()

def write_cfg(value, setting_type, section):  # 設定保存

    if os.path.exists(CONFIG_PATH):
        config_ini = configparser.ConfigParser()
        config_ini.read(CONFIG_PATH, encoding='utf-8')
        if section == "Directory":
            value = os.path.dirname(value)
        config_ini.set(section, setting_type, str(value))
        with open(CONFIG_PATH, 'w', encoding='utf-8') as file:
            config_ini.write(file)

def restart_software(root=None):
    if root:
        root.quit()
        root.destroy()
    if os.path.abspath(sys.argv[0]).endswith('.py'):
        subprocess.call([sys.executable] + sys.argv)
    else:
        subprocess.Popen([os.path.abspath(sys.argv[0])] + sys.argv[1:])
    sys.exit()

