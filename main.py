#####################################################################################
#               RPP to EXO ver 2.07                                                 #
#                                                                       2024/02/21  #
#       Original Written by Maimai (@Maimai22015/YTPMV.info)                        #
#       Forked by Garech (@Garec_)                                                  #
#                                                                                   #
#       協力：SHI (@sbt54864666), wakanameko (@wakanameko2)                          #
#####################################################################################

import configparser
import gettext
import subprocess
import sys
import threading
import warnings
import webbrowser
from functools import partial
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk, Menu

import psutil
from ttkwidgets import CheckboxTreeview
from tkinterdnd2 import *
import rpp2exo
from rpp2exo import Rpp, Exo, YMM4, Midi
from rpp2exo.dict import *

R2E_VERSION = '2.07'

rpp_cl = Rpp("")

ymm4_cl = YMM4(mydict)
midi_cl = Midi("")


def patched_error(msg):
    mydict['HasPatchError'] = 1
    if mydict['ExEditLang'] == 'ja':
        if mydict['PatchExists']:
            print(_('(patch.aul未導入 かつ 拡張編集 Ver0.92以下 の環境では、%s)') % msg)
            return
        rsp = messagebox.showwarning(
            _("警告"), _('%s\nEXOのインポート後、個別に設定してください。') % msg,
            detail=_('patch.aul導入済 / 拡張編集 Ver0.93rc1 の環境の方はこれらのエラーを修復しています。\nこれらの環境に当てはまっていますか？'),
            type='yesno', default='no')
        if rsp == 'yes':
            print(_('★選択を記録しました。今後拡張編集のバグによるEXO生成エラーはコンソール上に通知されます。'))
            mydict['PatchExists'] = 1
            write_cfg("1", "patch_exists", "Param")
    else:
        mydict["PatchExists"] = 0
        messagebox.showwarning(
            _("警告"), _('%s\nEXOのインポート後、個別に設定してください。') % msg,
            detail=_('Tips: オリジナルの日本版拡張編集 v0.92を使い、patch.aul プラグインを導入することでこのエラーを回避できます。'))


def set_class_pos(cls):
    if ivr_slct_time.get():
        cls.start_pos = float(cmb_time1.get())
        cls.end_pos = float(cmb_time2.get()) if cmb_time2.get() != '' else 99999.0
        if cls.start_pos < cls.end_pos:
            pass
        elif cls.start_pos > cls.end_pos:
            cls.start_pos, cls.end_pos = cls.end_pos, cls.start_pos
        else:
            cls.start_pos = 0.0
            cls.end_pos = 99999.0
    else:
        cls.start_pos = 0.0
        cls.end_pos = 99999.0
    return cls


def main():
    btn_exec['state'] = 'disable'
    root['cursor'] = 'watch'
    btn_exec["text"] = _("実行中") + " (1/3)"

    try:
        end1 = objdict = {}
        file_path = file_fps = []
        min_layers = []
        exo_cl = Exo(mydict)
        chk = 0
        while chk != 1 and mydict['UseYMM4']:
            chk = check_ymm4()
            if chk < 0:
                return

        # RPPファイル用処理
        if mydict["RPPPath"].lower().endswith(".rpp"):
            set_class_pos(rpp_cl)
            file_path, end1 = rpp_cl.main(mydict["OutputType"] == 0, mydict["Track"])
            objdict = rpp_cl.objDict
        # 選択時間の設定：MIDIファイル
        elif mydict["RPPPath"].lower().endswith(".mid") or mydict["RPPPath"].lower().endswith(".midi"):
            set_class_pos(midi_cl)
            end1 = midi_cl.main(mydict["Track"])
            objdict = midi_cl.objDict

        if mydict["UseYMM4"]:
            btn_exec["text"] = _("実行中") + " (3/3)"
            end3 = ymm4_cl.run(objdict, file_path)
        else:
            exo_cl = Exo(mydict)
            btn_exec["text"] = _("実行中") + " (2/3)"
            file_fps = exo_cl.fetch_fps(file_path)

            btn_exec["text"] = _("実行中") + " (3/3)"
            end3 = exo_cl.make_exo(objdict, file_path, file_fps)
        end = end1 | end3

    except PermissionError as e:
        if e.filename.lower().endswith('.exo'):
            messagebox.showerror(_("エラー"), _("上書き先のEXOファイルが開かれているか、読み取り専用になっています。"))
        else:
            messagebox.showerror(_("エラー"), _("下記ファイルの読込み権限がありません。\n") + e.filename)
    except FileNotFoundError as e:
        messagebox.showerror(_("エラー"), _("下記パス内のファイル/フォルダは存在しませんでした。\n") + e.filename)
    except UnicodeEncodeError as e:
        # reasonに該当行の文字列、objectに該当文字を格納
        messagebox.showerror(_("エラー"), _("AviUtl上で使用できない文字がパス名に含まれています。\n"
                                         "パス名に含まれる該当文字を削除し、再度実行し直してください。\n\n")
                             + e.reason + '    "' + e.object + '"')
    except rpp2exo.exo.LoadFilterFileError:
        messagebox.showerror(_("エラー"), _("エイリアス / 効果ファイルが不正です。詳しくはREADMEを参照してください。"))
    except rpp2exo.exo.ItemNotFoundError:
        messagebox.showerror(_("エラー"), _("出力範囲内に変換対象のアイテムが見つかりませんでした。\n"
                                         "出力対象トラック、時間選択の設定を見直してください。"))
    except rpp2exo.ymm4.TemplateNotFoundError:
        messagebox.showerror(_("エラー"), _("エイリアスに指定されているテンプレートは存在しませんでした。"))
    except Exception as e:
        messagebox.showerror(_("エラー"), _("予期せぬエラーが発生しました。不正なRPPファイルの可能性があります。\n"
                                         "最新バージョンのREAPERをインストールし、RPPファイルを再保存して再試行してください。\n"
                                         "それでも症状が改善しない場合、コンソールのエラー内容を制作者まで報告ください。"))
        raise e
    else:
        if "exist_mode2" in end:
            print(_("★警告: RPP内にセクション・逆再生付きのアイテムが存在したため、該当アイテムが正常に生成できませんでした。"))
            for i, detail in enumerate(end["exist_mode2"]):
                print("    " + detail)
                if i == 4:
                    print("    " + _("その他 %s個") % str(len(end["exist_mode2"]) - 5))
                    break

        if "exist_stretch_marker" in end:
            print(_("★警告: RPP内に伸縮マーカーが設定されているアイテムが存在したため、該当アイテムが正常に生成できませんでした。"))
            for i, detail in enumerate(end["exist_stretch_marker"]):
                print("    " + detail)
                if i == 4:
                    print("    " + _("その他 %s個") % str(len(end["exist_stretch_marker"]) - 5))
                    break

        if "layer_over_100" in end:
            print(_("★警告: 出力処理時にEXOのレイヤー数が100を超えたため、正常に生成できませんでした。"))

        if 'keyframe_exists' in end:
            print("★警告: エイリアスファイルに中間点が存在したため、正常に生成できませんでした。")

        if 'byoga_henkan_not_exists' in end:
            print("★警告: YMM4では上下反転機能が実装されていないため、上下反転の設定は反映されません。\n"
                  "    描画変換プラグインを導入し、テンプレートを再生成することで読み込むことができます。")

        if not mydict['PatchExists'] and mydict['HasPatchError']:
            print(_("★警告: AviUtl 拡張編集のバグにより、オブジェクトの設定は正常に反映されません。"))
            end = end | {1: 1}

        ret_aul = False
        ret_ymm4 = False
        if not mydict['UseYMM4']:
            if end == {}:
                ret_aul = messagebox.askyesno(_("正常終了"), _("正常に生成されました。\n保存先のフォルダを開きますか？"))
            else:
                ret_aul = messagebox.askyesno(_("警告"),
                                          _("一部アイテムが正常に生成できませんでした。詳細はコンソールをご覧ください。\n保存先のフォルダを開きますか？"), icon="warning")
        else:
            if end == {}:
                ret_ymm4 = messagebox.askyesno(_("正常終了"), _("正常に生成されました。\nゆっくりMovieMaker4を開きますか？"))
            else:
                ret_ymm4 = messagebox.askyesno(_("警告"),
                                          _("一部アイテムが正常に生成できませんでした。詳細はコンソールをご覧ください。\nゆっくりMovieMaker4を開きますか？"), icon="warning")

        if ret_aul:
            path = os.path.dirname(mydict["EXOPath"]).replace('/', '\\')
            if path == "":
                path = os.getcwd()
            subprocess.Popen(['explorer', path], shell=True)
        elif ret_ymm4:
            subprocess.Popen(mydict['YMM4Path'])

    finally:
        print('--------------------------------------------------------------------------')
        btn_exec['state'] = 'normal'
        root['cursor'] = 'arrow'
        btn_exec["text"] = _("実行")


def check_ymm4():
    for proc in psutil.process_iter():
        try:
            if proc.exe() == mydict["YMM4Path"].replace('/', '\\'):
                ret = messagebox.askretrycancel('警告', 'YMM4が実行されている間はRPPtoYMM4の処理をすることができません。\n', icon="warning")
                if not ret:
                    return -1  # 処理を終了する
                else:
                    return 0  # 再試行する
        except psutil.AccessDenied:
            pass
    return 1  # YMM4未検知


def read_cfg():
    config_ini_path = "config.ini"
    try:
        # 設定ファイルの読み込み
        config_ini = configparser.ConfigParser()
        config_ini.read(config_ini_path, encoding='utf-8')

        # 欠損値を補完
        for default, option, section in [
            ('', 'RPPDir', 'Directory'),  # RPPの保存ディレクトリ
            ('', 'EXODir', 'Directory'),  # EXOの保存ディレクトリ
            ('', 'SrcDir', 'Directory'),  # 素材の保存ディレクトリ
            ('', 'AlsDir', 'Directory'),  # エイリアスの保存ディレクトリ
            ('1', 'is_ccw', 'Param'),     # 左右・上下反転時に反時計回りにするかどうか 0/1
            ('0', 'patch_exists', 'Param'),  # patch.aulが存在するか 0/1
            ('0', 'use_ymm4', 'Param'),   # YMM4を使うかどうか 0/1
            ('', 'ymm4path', 'Param'),    # YMM4の実行ファイルパス
            ('ja', 'display', 'Language'),  # 表示言語
            ('ja', 'exedit', 'Language'),  # 拡張編集の言語
        ]:

            if not config_ini.has_section(section):
                config_ini[section] = {}
            if not config_ini.has_option(section, option):
                config_ini[section][option] = default

        # Configファイルの書き込み
        with open(config_ini_path, 'w', encoding='utf-8') as file:
            config_ini.write(file)

            # パラメータの読み込み
            mydict["RPPLastDir"] = config_ini.get("Directory", "RPPDir")
            mydict["EXOLastDir"] = config_ini.get("Directory", "EXODir")
            mydict["SrcLastDir"] = config_ini.get("Directory", "SrcDir")
            mydict["AlsLastDir"] = config_ini.get("Directory", "AlsDir")
            mydict["IsCCW"] = int(config_ini.get("Param", "is_ccw"))
            mydict["PatchExists"] = int(config_ini.get("Param", "patch_exists"))
            mydict["UseYMM4"] = int(config_ini.get("Param", "use_ymm4"))
            mydict["YMM4Path"] = config_ini.get("Param", "ymm4path")
            mydict["DisplayLang"] = config_ini.get("Language", "display")
            mydict["ExEditLang"] = config_ini.get("Language", "exedit")

    except Exception as e:
        messagebox.showerror('RPPtoEXO v' + R2E_VERSION, '壊れたconfig.iniを修復するため、全設定がリセットされます。')
        os.remove('config.ini')
        subprocess.call([sys.executable] + sys.argv)
        sys.exit()

    return 0


def write_cfg(value, setting_type, section):  # 設定保存
    config_ini_path = "config.ini"
    if os.path.exists(config_ini_path):
        config_ini = configparser.ConfigParser()
        config_ini.read(config_ini_path, encoding='utf-8')
        if section == "Directory":
            value = os.path.dirname(value)
        config_ini.set(section, setting_type, str(value))
        with open('config.ini', 'w', encoding='utf-8') as file:
            config_ini.write(file)


def slct_rpp():  # 参照ボタン
    filetype = [
        (_("対応ファイル"), "*.rpp;*.mid;*.midi"),
        (_("REAPERプロジェクトファイル"), "*.rpp"),
        (_("MIDIファイル"), "*.mid;*.midi"),
    ]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["RPPLastDir"], title=_("RPP・MIDIファイルを選択"))
    if filepath != '':
        svr_rpp_input.set(filepath)
        write_cfg(filepath, "RPPDir", "Directory")
        set_rppinfo(reload=1)


def slct_source():  # 素材選択
    filetype = [(_("動画ファイル"), "*")] if ivr_trgt_mode.get() == 1 else [(_("画像ファイル"), "*")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["SrcLastDir"], title=_("参照する素材ファイルの選択"))
    if filepath != '':
        svr_src_input.set(filepath)
        write_cfg(filepath, "SrcDir", "Directory")


def slct_filter_cfg_file():  # 効果設定ファイル読み込み
    filetype = [(_("AviUtl エイリアス/効果ファイル"), "*.exa;*.exc;*.exo;*.txt"), (_("すべてのファイル"), "*.*")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["AlsLastDir"], title=_("参照するエイリアス/効果ファイルの選択"))
    if filepath != '':
        svr_alias_input.set(filepath)
        write_cfg(filepath, "AlsDir", "Directory")


def save_exo():  # EXO保存ボタン
    filetype = [(_("AviUtlオブジェクトファイル"), "*.exo")]
    filepath = filedialog.asksaveasfilename(
        initialdir=mydict["EXOLastDir"], title=_("EXOファイル保存場所の選択"), filetypes=filetype)
    if filepath != '':
        if not filepath.endswith(".exo"):
            filepath += ".exo"
        svr_exo_input.set(filepath)
        write_cfg(filepath, "EXODir", "Directory")


def set_rppinfo(reload=0):  # RPP内の各トラックの情報を表示する
    filepath = ent_rpp_input.get().replace('"', '')  # パスをコピペした場合のダブルコーテーションを削除
    if filepath == svr_rpp_input_temp.get() and reload == 0:
        return True
    svr_rpp_input_temp.set(filepath)
    tvw_slct_track.delete(*tvw_slct_track.get_children())
    tvw_slct_track.insert("", "end", text=_("＊全トラック"), iid="all", open=True)
    tvw_slct_track.change_state("all", 'tristate')
    tvw_slct_track.yview(0)

    if filepath.lower().endswith(".rpp"):
        rbt_trgt_auto['state'] = 'enable'
        try:
            rpp_cl.load(filepath)
        except (PermissionError, FileNotFoundError):
            return True
        tree = rpp_cl.load_track()
        change_time_cb()
        insert_treedict(tree, "", 0)
    elif filepath.lower().endswith(".mid") or filepath.lower().endswith(".midi"):
        rbt_trgt_auto['state'] = 'disable'
        rpp_cl.load('')
        change_time_cb()
        if ivr_trgt_mode.get() == 0:
            ivr_trgt_mode.set(1)
            mode_command()

        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                midi_cl.load(filepath)
            except (PermissionError, FileNotFoundError):
                return True
            except ValueError as e:
                messagebox.showerror(_('エラー'), _('MIDIファイルの容量が極端に大きいか小さいため、読み込めませんでした。'))
                raise e
            except RuntimeWarning as e:
                messagebox.showwarning(_('警告'), _('MIDIの 拍子/テンポ 情報が正しく読み込めなかった可能性があります。\n'
                                                  '生成後、FPSの値が合っているにも関わらずテンポが合わない場合、Dominoを使ってMIDIを再出力してください。'))
                warnings.filterwarnings('default')
                midi_cl.load(filepath)
            tree = midi_cl.load_track()
            insert_treedict(tree, "", 0)
    return True


def insert_treedict(tree, prefix, iid):  # ツリー表示でトラック１行を描画する(再帰用)
    for k in tree:
        iid += 1
        if k == list(tree.keys())[-1]:  # 最下層のフォルダ内トラックの場合 視覚上の縦繋がりを消す
            tvw_slct_track.insert("all", "end", text=str(iid).zfill(2) + prefix + "└" + k, iid=str(iid))

            # 親トラックがミュート状態の場合、こっそりゼロ幅スペース(​)を挿入して子トラックが後から区別できるように
            if "​" not in k and "​" not in prefix:
                tvw_slct_track.change_state(str(iid), 'checked')
            if tree[k]:
                iid = insert_treedict(tree[k], prefix + "　", iid) if "​" not in k else \
                    insert_treedict(tree[k], prefix + "　​", iid)  # フォルダ開始部の場合、prefixを追加して再帰呼び出し
        else:
            tvw_slct_track.insert("all", "end", text=str(iid).zfill(2) + prefix + "├" + k, iid=str(iid))
            if "​" not in k and "​" not in prefix:
                tvw_slct_track.change_state(str(iid), 'checked')
            if tree[k]:
                iid = insert_treedict(tree[k], prefix + "│", iid) if "​" not in k else \
                    insert_treedict(tree[k], prefix + "│​", iid)
    return iid


def to_absolute(path):
    if not path:
        return ''
    if os.path.isabs(path):
        return path
    else:

        return os.path.dirname(mydict["RPPPath"]) + '/' + path


# 動的なエフェクト設定生成
# 参考：https://qiita.com/nnahito/items/41be8e02a6ebc91386e7
hLabel = []  # ラベルのハンドル格納
hLabel2 = []  # ラベル実体
hSELabel = []  # 始点終点ラベルハンドル
hSELabelE = []  # 始点終点ラベル実体
hEntryS = []  # Entry 開始点
hEntryE = []  # Entry 終点
hEntryX = []  # Entry 移動方法
hEntryConf = []  # Entry 設定
hEntrySE = []  # Entry実体 開始点
hEntryEE = []  # Entry実体 終点
hEntryXCb = []  # コンボボックス実体 移動方法
hEntryConfE = []  # Entry 設定実体
hCheckBox = []  # チェックボックス用
hCheckBoxCb = []  # チェックボックス実体


def add_filter_label():
    # エフェクト名ラベル
    hLabel.append(StringVar())
    hLabel[mydict["EffCount"] + mydict["EffNum"]].set(svr_add_eff.get())
    b = ttk.Label(
        frame_effprm, textvariable=hLabel[mydict["EffCount"] + mydict["EffNum"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=0)
    hLabel2.append(b)

    # 始点終点ラベル
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set(_("始点"))
    b = ttk.Label(
        frame_effprm, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=1)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set(_("終点"))
    b = ttk.Label(
        frame_effprm, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=3)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set(_("設定"))
    b = ttk.Label(
        frame_effprm, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=4)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1

    mydict["Effect"].append([])
    mydict["Effect"][mydict["EffCount"]].append(svr_add_eff.get())
    mydict["EffCount"] += 1
    # EffDict[v2.get()]回分ループ
    for n in range(len(EffDict[svr_add_eff.get()])):
        if EffDict[svr_add_eff.get()][n][-1] == -1:
            hCheckBox.append(StringVar())
            hCheckBox[mydict["EffCbNum"]].set(0)
            hCheckBoxCb.append(ttk.Checkbutton(frame_effprm, padding=0, text=EffDict[svr_add_eff.get()][n][0],
                onvalue=1, offvalue=0, variable=hCheckBox[mydict["EffCbNum"]]))
            hCheckBoxCb[mydict["EffCbNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                                 columnspan=4, column=1, sticky=W)
            mydict["EffCbNum"] += 1
        elif EffDict[svr_add_eff.get()][n][-1] == -2:  # Entryだけの項目(めっちゃ強引な実装だから全体的に書き直したい…)
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]].set(EffDict[svr_add_eff.get()][n][0])
            b = ttk.Label(frame_effprm, textvariable=hLabel[mydict["EffNum"] + mydict["EffCount"]])
            b.grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(frame_effprm, textvariable=hEntryS[mydict["EffNum"]], width=7))
            hEntrySE[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                            column=1, columnspan=4, sticky=W + E)
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[svr_add_eff.get()][n][1])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(frame_effprm, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set(list(XDict.keys())[0])
            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(frame_effprm, textvariable=hEntryE[mydict["EffNum"]], width=7))
            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(frame_effprm, textvariable=hEntryConf[mydict["EffNum"]], width=5))
            mydict["EffNum"] += 1
        else:
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]].set(EffDict[svr_add_eff.get()][n][0])
            b = ttk.Label(frame_effprm, textvariable=hLabel[mydict["EffNum"] + mydict["EffCount"]])
            b.grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(frame_effprm, textvariable=hEntryS[mydict["EffNum"]], width=7))
            hEntrySE[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                            column=1, padx=5)
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[svr_add_eff.get()][n][1])
            set_decimal(hEntryS[mydict["EffNum"]], EffDict[svr_add_eff.get()][n][2])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(frame_effprm, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set(list(XDict.keys())[0])
            hEntryXCb[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                             column=2, padx=5)

            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(frame_effprm, textvariable=hEntryE[mydict["EffNum"]], width=7))
            hEntryEE[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                            column=3, padx=5)

            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(
                frame_effprm, textvariable=hEntryConf[mydict["EffNum"]], width=5))
            hEntryConfE[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                               column=4, padx=5)

            mydict["EffNum"] += 1
    canvas.update()
    canvas.configure(scrollregion=(0, 0, frame_right.winfo_height(), frame_right.winfo_height()))
    canvas.grid(row=0, column=2, sticky=N, ipadx=frame_right.winfo_width()/2, ipady=310)


def del_filter_label():  # 効果パラメータ入力画面破棄
    for n in range(len(hLabel)):
        hLabel2[n].grid_forget()
    for n in range(len(hSELabelE)):
        hSELabelE[n].grid_forget()
    for n in range(len(hEntryS)):
        hEntrySE[n].destroy()
        hEntryEE[n].destroy()
        hEntryXCb[n].destroy()
        hEntryConfE[n].destroy()
    for n in range(len(hCheckBoxCb)):
        hCheckBoxCb[n].destroy()
    mydict["Effect"] = []
    mydict["EffCount"] = 0
    mydict["EffCount2"] = 0
    mydict["EffNum"] = 0
    mydict["EffCbNum"] = 0
    hLabel.clear()
    hLabel2.clear()
    hSELabel.clear()
    hSELabelE.clear()
    hEntryS.clear()
    hEntryE.clear()
    hEntryX.clear()
    hEntryConf.clear()
    hEntrySE.clear()
    hEntryEE.clear()
    hEntryXCb.clear()
    hEntryConfE.clear()
    hCheckBox.clear()
    hCheckBoxCb.clear()
    canvas.update()
    canvas.configure(scrollregion=(0, 0, frame_right.winfo_height(), frame_right.winfo_height()))
    canvas.grid(row=0, column=2, sticky=N, ipadx=frame_right.winfo_width()/2, ipady=310)


mLabel = []  # ラベルのハンドル格納
mLabel2 = []  # ラベル実体
mSELabel = []  # 始点終点ラベルハンドル
mSELabelE = []  # 始点終点ラベル実体
mEntryS = []  # Entry 開始点
mEntryE = []  # Entry 終点
mEntryX = []  # Entry 移動方法
mEntryConf = []  # Entry 設定
mEntrySE = []  # Entry実体 開始点
mEntryEE = []  # Entry実体 終点
mEntryXCb = []  # コンボボックス実体 移動方法
mEntryConfE = []  # Entry 設定実体


def toggle_media_label(flg):
    if flg == 2:  # 拡張描画切り替え
        # 回転を消す
        mLabel2[6].grid_remove()
        mEntrySE[5].grid_remove()
        mEntryEE[5].grid_remove()
        mEntryXCb[5].grid_remove()
        mEntryConfE[5].grid_remove()

        # 回転の値をZ軸回転にコピー
        mEntryS[9].set(mEntryS[5].get())
        mEntryE[9].set(mEntryE[5].get())
        mEntryX[9].set(mEntryX[5].get())
        mEntryConf[9].set(mEntryConf[5].get())

        # 拡張描画の設定項目を描画
        for i in range(6, 13):
            mLabel2[i+1].grid()
            mEntrySE[i].grid()
            mEntryXCb[i].grid()
            mEntryEE[i].grid()
            mEntryConfE[i].grid()
    elif flg == 1:  # 標準描画切り替え
        # 拡張描画の設定項目を消す
        for i in range(6, 13):
            mLabel2[i+1].grid_remove()
            mEntrySE[i].grid_remove()
            mEntryEE[i].grid_remove()
            mEntryXCb[i].grid_remove()
            mEntryConfE[i].grid_remove()

        # Z軸回転の値を回転にコピー
        mEntryS[5].set(mEntryS[9].get())
        mEntryE[5].set(mEntryE[9].get())
        mEntryX[5].set(mEntryX[9].get())
        mEntryConf[5].set(mEntryConf[9].get())

        # 回転を描画
        mLabel2[6].grid()
        mEntrySE[5].grid()
        mEntryXCb[5].grid()
        mEntryEE[5].grid()
        mEntryConfE[5].grid()
    elif flg == 0:
        frame_stddraw.grid(row=1)
        frame_optdraw.grid(row=2, sticky='W')

    else:  # フィルタ切り替え
        frame_stddraw.grid_remove()
        frame_optdraw.grid_remove()


def run():
    mydict["RPPPath"] = svr_rpp_input.get().replace('"', '')
    if svr_exo_input.get().replace('"', '').lower().endswith(".exo") or svr_exo_input.get().replace('"', '') == "":
        mydict["EXOPath"] = to_absolute(svr_exo_input.get().replace('"', ''))
    else:
        mydict["EXOPath"] = to_absolute(svr_exo_input.get().replace('"', '') + ".exo")
    mydict["OutputType"] = ivr_trgt_mode.get()
    mydict["SrcPath"] = to_absolute(svr_src_input.get().replace('"', '')).replace('/', '\\')
    mydict["EffPath"] = to_absolute(svr_alias_input.get().replace('"', ''))
    mydict["IsAlpha"] = ivr_import_alpha.get()
    mydict["IsLoop"] = ivr_loop.get()
    if is_float(svr_fps_input.get()):
        mydict["fps"] = float(svr_fps_input.get())
    else:
        mydict["fps"] = ''
    mydict["ScriptText"] = txt_script.get('1.0', 'end-1c')
    mydict["ObjFlipType"] = ivr_v_flip.get() + ivr_h_flip.get()
    mydict["SepLayerEvenObj"] = ivr_sep_even.get()
    mydict["NoGap"] = ivr_no_gap.get()
    mydict["RandomPlay"] = ivr_randplay.get()
    mydict["clipping"] = ivr_clipping.get()
    mydict["IsExSet"] = ivr_adv_draw.get()
    mydict["SceneIdx"] = int(svr_scene_idx.get() or 0)
    mydict["Track"] = tvw_slct_track.get_checked()
    mydict["DisplayLang"] = svr_lang_r2e.get()
    mydict["ExEditLang"] = svr_lang_aul.get()

    mydict["Param"] = []

    def set_mparam(i, mv=1, tp=1):
        if not is_float(mEntryS[i].get()) and not mydict['UseYMM4']:
            messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (mLabel[0].get(), mLabel[i+1].get()))
            raise ValueError
        if mv and -1 < float(mEntryS[i].get()) < 0:
            patched_error(_('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
            return 1, tp
        mydict["Param"].append(mLabel[i+1].get() + '=' + set_decimal(mEntryS[i], prmlist[i][2]))
        if mEntryX[i].get() == list(XDict.keys())[0] or mEntryX[i].get() == "":
            return mv, tp
        # 以下、移動方法ありの場合の処理
        if not is_float(mEntryE[i].get()):
            messagebox.showinfo(_("エラー"), _("%s : %s の終点が正しく入力されていません。") % (mLabel[0].get(), mLabel[i+1].get()))
            raise ValueError
        if mv and -1 < float(mEntryE[i].get()) < 0:
            patched_error(_('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
            return 1, tp
        mydict["Param"][-1] += ',' + set_decimal(mEntryE[i], prmlist[i][2]) + ','\
            + str(XDict.get(mEntryX[i].get(), '15@' + mEntryX[i].get()))
        if mEntryConf[i].get() != '':
            if not is_float(mEntryE[i].get()):
                messagebox.showinfo(_("エラー"),
                                    _("%s : %s の終点が正しく入力されていません。") % (mLabel[0].get(), mLabel[i + 1].get()))
                raise ValueError
            mydict["Param"][-1] += ',' + str(int(mEntryConf[i].get()))
            if tp and not str(XDict.get(mEntryX[i].get(), mEntryX[i].get())).isascii():
                patched_error(_("AviUtl本体のバグの影響により、移動の設定の値は反映されません。"))
                return mv, 1
        return mv, tp

    try:
        show_mv, show_tp = (0, 0)
        if ivr_adv_draw.get():
            mydict['Param'].append('_name=' + ExDict['拡張描画'])
            for i in [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
                show_mv, show_tp = set_mparam(i, show_mv, show_tp)
            mydict['Param'].append(ExDict['裏面を表示しない'] + '=0')
        else:
            mydict['Param'].append('_name=' + ExDict['標準描画'])
            for i in [0, 1, 2, 3, 4, 5, 13, 14]:
                show_mv, show_tp = set_mparam(i, show_mv, show_tp)

        mydict['SrcRate'] = mydict['Param'].pop()[5:]
        mydict['SrcPosition'] = mydict['Param'].pop()[5:]
        mydict['Param'].append('blend=' + str(BlendDict[ParamCombo15.get()]))

        if mydict["RPPPath"] == "":
            messagebox.showinfo(_("エラー"), _("読み込むRPPを入力してください。"))
            return 0
        elif mydict["EXOPath"] == "":
            messagebox.showinfo(_("エラー"), _("EXOの保存先パスを入力してください。"))
            return 0
        elif mydict["fps"] == "" or mydict["fps"] <= 0:
            messagebox.showinfo(_("エラー"), _("正しいFPSの値を入力してください。"))
            return 0
        elif not mydict["Track"]:
            messagebox.showinfo(_("エラー"), _("出力するトラックを選択してください。"))
            return 0
        elif ivr_slct_time.get() and (not is_float(cmb_time1.get()) or not is_float(cmb_time2.get())):
            messagebox.showinfo(_("エラー"), _("時間選択 (秒) の値が正しく入力されていません。"))
            return 0

        if (mydict["SceneIdx"] <= 0 or mydict["SceneIdx"] >= 50) and mydict["OutputType"] == 4:
            messagebox.showinfo(_("エラー"), _("正しいシーン番号を入力してください。（範囲 : 1 ~ 49）"))
            return 0
        elif mydict["SceneIdx"] != 1 and mydict["OutputType"] == 4:
            patched_error(_('AviUtl本体のバグの影響により、シーン番号は反映されません。'))

        count = mydict["EffCount"]
        runcount = 0
        runcountcb = 0
        eff = ""
        for i in range(0, int(count)):
            del mydict["Effect"][i][1:]
            for x in range(len(EffDict[mydict["Effect"][i][0]])):
                if EffDict[mydict["Effect"][i][0]][x][-1] != -1:  # チェックボックスでない場合
                    if EffDict[mydict["Effect"][i][0]][x][-1] != -2 and not is_float(hEntryS[runcount].get()):
                        messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。")
                                            % (mydict["Effect"][i][0], EffDict[mydict["Effect"][i][0]][x][0]))
                        return 0
                    if hEntryX[runcount].get() == list(XDict.keys())[0] or hEntryX[runcount].get() == "":  # 移動なしの場合
                        if show_mv and EffDict[mydict["Effect"][i][0]][x][-1] != -2 and \
                                -1 < float(hEntryS[runcount].get()) < 0:
                            patched_error(_('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
                            show_mv = False

                        eff = [EffDict[mydict["Effect"][i][0]][x][0],
                               set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1])]
                        mydict["Effect"][i].append(eff)
                    else:  # 移動ありの場合
                        if not is_float(hEntryE[runcount].get()):
                            messagebox.showinfo(_("エラー"), _("%s : %s の終点が正しく入力されていません。")
                                                % (mydict["Effect"][i][0], EffDict[mydict["Effect"][i][0]][x][0]))
                            return 0
                        if show_mv and EffDict[mydict["Effect"][i][0]][x][-1] != -2 and \
                                (-1 < float(hEntryS[runcount].get()) < 0 or -1 < float(hEntryE[runcount].get()) < 0):
                            patched_error(_('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
                            show_mv = False
                        eff = [EffDict[mydict["Effect"][i][0]][x][0],
                               set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                               + set_decimal(hEntryE[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                               + str(XDict.get(hEntryX[runcount].get(), '15@' + hEntryX[runcount].get()))]
                        if XDict.get(hEntryX[runcount].get(), 'a') != "":
                            eff[1] += str(hEntryConf[runcount].get())
                            if show_tp and not str(XDict.get(hEntryX[runcount].get(), hEntryX[runcount].get())).isascii():
                                patched_error(_("AviUtl本体のバグの影響により、移動の設定の値は反映されません。"))
                                show_tp = False
                        if XDict.get(hEntryX[runcount].get(), 'a') != "" and hEntryConf[runcount].get() != "":
                            eff = [EffDict[mydict["Effect"][i][0]][x][0],
                                   set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                                   + set_decimal(hEntryE[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                                   + str(XDict.get(hEntryX[runcount].get(), '15@' + hEntryX[runcount].get())) + ","
                                   + str(hEntryConf[runcount].get())]
                        mydict["Effect"][i].append(eff)
                    runcount += 1
                elif EffDict[mydict["Effect"][i][0]][x][-1] == -1:  # チェックボックスの場合
                    eff = [EffDict[mydict["Effect"][i][0]][x][0],
                           str(hCheckBox[runcountcb].get())]
                    mydict["Effect"][i].append(eff)
                    runcountcb += 1
    except ValueError:
        return 0
    thread = threading.Thread(target=main)
    thread.start()


def set_decimal(entry, unit):
    if unit == 0:
        return entry.get()
    try:
        m = float(entry.get())
    except ValueError:
        return entry.get()
    if unit == 0.01:
        n = format(m, '.2f')
    elif unit == 0.1:
        n = format(m, '.1f')
    else:
        n = str(int(m))

    entry.set(n)
    return n


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


# GUI変更時に値の状態を変更する関数
def mode_command():  # 「追加対象」変更時の状態切り替え
    if ivr_trgt_mode.get() == 1 or ivr_trgt_mode.get() == 2:  # 「素材」テキストボックス・参照ボタン
        btn_src_browse['state'] = 'enable'
        ent_src_input['state'] = 'enable'
    else:
        btn_src_browse['state'] = 'disable'
        ent_src_input['state'] = 'disable'

    if ivr_trgt_mode.get() == 4:  # シーン番号
        ent_scene_idx['state'] = 'enable'
    else:
        ent_scene_idx['state'] = 'disable'

    if ivr_trgt_mode.get() == 3 and not mydict['UseYMM4']:  # 上のオブジェクトでクリッピング・拡張描画・設定項目
        chk_clipping['state'] = 'disable'
        chk_adv_draw['state'] = 'disable'
        toggle_media_label(-1)
    else:
        chk_clipping['state'] = 'enable'
        chk_adv_draw['state'] = 'enable'
        toggle_media_label(0)

    if ivr_trgt_mode.get() == 1:  # アルファチャンネルを読み込む・再生位置ランダム
        chk_import_alpha['state'] = chk_randplay['state'] = 'enable'
    else:
        chk_import_alpha['state'] = chk_randplay['state'] = 'disable'

    if ivr_trgt_mode.get() == 1 or ivr_trgt_mode.get() == 4:  # ループ再生・再生速度・再生位置
        chk_loop['state'] = 'enable'

        # 拡張描画の設定項目を描画
        for i in range(13, 15):
            mLabel2[i + 1].grid()
            mEntrySE[i].grid()
            mEntryXCb[i].grid()
            mEntryEE[i].grid()
            mEntryConfE[i].grid()
    else:
        # 拡張描画の設定項目を消す
        for i in range(13, 15):
            mLabel2[i + 1].grid_remove()
            mEntrySE[i].grid_remove()
            mEntryEE[i].grid_remove()
            mEntryXCb[i].grid_remove()
            mEntryConfE[i].grid_remove()


def change_time_cb():  # 「時間選択」変更時の状態切り替え
    if ivr_slct_time.get() == 1:
        cmb_time_preset['state'] = 'readonly'
        cmb_time1['state'] = 'enable'
        cmb_time2['state'] = 'enable'
        time_ps_list, marker_list = rpp_cl.load_marker_list()

        if len(time_ps_list) >= 2:
            svr_time_preset.set(time_ps_list[1])
        else:
            svr_time_preset.set('-')
        cmb_time_preset['values'] = time_ps_list
        cmb_time1['values'] = marker_list
        cmb_time2['values'] = marker_list
        set_time(None)
    else:
        cmb_time_preset['state'] = 'disable'
        cmb_time1['state'] = 'disable'
        cmb_time2['state'] = 'disable'


def set_time(self):  # タイム選択ComboBoxのリストをリセットする
    if svr_time_preset.get() == '-':
        cmb_time1.set('0.0')
        cmb_time2.set('99999.0')
    else:
        slct = svr_time_preset.get()
        cmb_time1.set(slct[slct.rfind('(') + 1:slct.rfind('~')])
        cmb_time2.set(slct[slct.rfind('~') + 1:-1])


def set_time1(self):  # 上側のタイム選択ComboBox適用
    x = svr_time1.get()
    cmb_time1.set(x[x.rfind(':') + 2:])


def set_time2(self):  # 下側のタイム選択ComboBox適用
    x = svr_time2.get()
    cmb_time2.set(x[x.rfind(':') + 2:])


# ファイルD&D時に使う関数
def drop_file(target, event):
    paths = root.tk.splitlist(event.data)
    target.set(paths[0].replace('\\', '/'))


# メニューバー用
def close_r2e():
    sys.exit()


# 表示言語切り替え
def change_lang_r2e():
    if mydict['DisplayLang'] == svr_lang_r2e.get():
        return
    write_cfg(svr_lang_r2e.get(), 'display', 'Language')
    confirm_restart()


# 拡張編集言語切り替え
def change_lang_aul():
    if mydict['ExEditLang'] == svr_lang_aul.get():
        return
    write_cfg(svr_lang_aul.get(), 'exedit', 'Language')
    confirm_restart()


# YMM4パス切り替え
def change_ymm4_path():
    filetype = [(_("ゆっくりMovieMaker4実行ファイル"), "YukkuriMovieMaker.exe")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=os.path.dirname(mydict["YMM4Path"]),
        title=_("ゆっくりMovieMaker4の実行ファイルを選択"))
    if filepath != '':
        mydict['YMM4Path'] = filepath
        ymm4_cl.load()
        write_cfg(filepath, "ymm4Path", "Param")
    return filepath != ''


# YMM4使用切り替え
def change_ymm4():
    if ivr_use_ymm4.get() == mydict['UseYMM4']:
        return
    if ivr_use_ymm4.get() == 1:
        if change_ymm4_path():
            write_cfg(int(ivr_use_ymm4.get()), "use_ymm4", "Param")
            confirm_restart()
            return
        else:
            ivr_use_ymm4.set(mydict['UseYMM4'])
            return

    write_cfg(int(ivr_use_ymm4.get()), "use_ymm4", "Param")
    confirm_restart()


# 再起動通知
def confirm_restart():
    ret = messagebox.askyesno(_("注意"), _("設定を反映するにはソフトを再起動する必要があります。再起動しますか？"),
                              detail=_("現在設定中の項目は失われます。"), icon="info")
    if ret:
        root.quit()
        root.destroy()
        subprocess.call([sys.executable] + sys.argv)


def open_website(site):
    webbrowser.open(site)


def about_rpp2exo():
    messagebox.showinfo('RPPtoEXO v' + R2E_VERSION, 'RPPtoEXO ver' + R2E_VERSION +
                        '\nOriginal (~v1.08) made by maimai22015\n   Twitter: @Maimai22016'
                        '\nLatest Version (v2.0~) made by Garech\n   Twitter: @Garec_')


if __name__ == '__main__':
    read_cfg()
    rpp_cl.__init__('', mydict['DisplayLang'])
    midi_cl.__init__('', mydict['DisplayLang'])

    # 翻訳用クラスの設定
    _ = gettext.translation(
        'text',  # domain: 辞書ファイルの名前
        localedir=os.path.join(os.path.dirname(__file__)),  # 辞書ファイル配置ディレクトリ
        languages=[mydict['DisplayLang']],  # 翻訳に使用する言語
        fallback=True
    ).gettext

    print(_('★RPPtoEXO実行中はこのコンソール画面を閉じないでください。'))

    # 拡張編集の言語ごとに使用辞書を切り替える
    EffDict = EffDict[mydict['ExEditLang']]
    XDict = XDict[mydict['ExEditLang']]
    BlendDict = BlendDict[mydict['ExEditLang']]
    ExDict = ExDict[mydict['ExEditLang']]

    # root
    root = TkinterDnD.Tk()
    root.title('RPPtoEXO v' + R2E_VERSION)
    root.columnconfigure(1, weight=1)
    root.resizable(False, False)

    # メニューバー作成
    mbar = Menu(root, tearoff=0)
    root.config(menu=mbar)

    # ファイルメニュー
    menu_file = Menu(mbar, tearoff=0)
    mbar.add_cascade(label=_('ファイル'), menu=menu_file)
    menu_file.add_command(label=_('RPPを開く...'), command=slct_rpp)
    menu_file.add_command(label=_('終了'), command=close_r2e)

    # 生成設定メニュー
    menu_setting = Menu(mbar, tearoff=0)
    mbar.add_cascade(label=_('生成設定'), menu=menu_setting)
    ivr_is_ccw = IntVar()
    ivr_is_ccw.set(mydict['IsCCW'])
    menu_is_ccw = Menu(mbar, tearoff=0)
    menu_setting.add_cascade(label='左右上下反転時の回転方向', menu=menu_is_ccw)
    menu_is_ccw.add_radiobutton(label='時計回り', value=0, variable=ivr_is_ccw, command=lambda: [
                                     write_cfg(0, "is_ccw", "Param"),
                                     mydict.update(IsCCW=0)
                                  ])
    menu_is_ccw.add_radiobutton(label='反時計回り', value=1, variable=ivr_is_ccw, command=lambda: [
                                     write_cfg(1, "is_ccw", "Param"),
                                     mydict.update(IsCCW=1)
                                  ])
    ivr_patch_exists = IntVar()
    ivr_patch_exists.set(mydict['PatchExists'])
    menu_setting.add_checkbutton(label=_('拡張編集v0.92由来のエラーを無視'), variable=ivr_patch_exists,
                                 command=lambda: [
                                     write_cfg(int(ivr_patch_exists.get()), "patch_exists", "Param"),
                                     mydict.update(PatchExists=ivr_patch_exists.get())
                                  ])
    ivr_use_ymm4 = IntVar()
    ivr_use_ymm4.set(mydict['UseYMM4'])
    menu_setting.add_checkbutton(label=_('ゆっくりMovieMaker4モードで使う'), variable=ivr_use_ymm4, command=change_ymm4)

    # ゆっくりMovieMaker4 使用時の書き換え処理
    if mydict['UseYMM4']:
        ymm4_cl.load()
        XDict = rpp2exo.dict.XDict['ymm4']
        BlendDict = rpp2exo.dict.BlendDict['ymm4']
        root.title('RPPtoYMM4 (RPPtoEXO) v' + R2E_VERSION)
        ivr_byohen_exists = IntVar()
        menu_setting.add_command(label='YMM4の読込み場所を変更', command=change_ymm4_path)

    # 言語設定メニュー
    menu_lang = Menu(mbar, tearoff=0)
    mbar.add_cascade(label='Language', menu=menu_lang)

    menu_lang_r2e = Menu(menu_lang, tearoff=0)
    menu_lang.add_cascade(label=_('表示言語'), menu=menu_lang_r2e)
    svr_lang_r2e = StringVar()
    svr_lang_r2e.set(mydict['DisplayLang'])
    menu_lang_r2e.add_radiobutton(label='日本語', value='ja', variable=svr_lang_r2e, command=change_lang_r2e)
    menu_lang_r2e.add_radiobutton(label='English', value='en', variable=svr_lang_r2e, command=change_lang_r2e)

    menu_lang_aul = Menu(menu_lang, tearoff=0)
    menu_lang.add_cascade(label=_('拡張編集の言語'), menu=menu_lang_aul)
    svr_lang_aul = StringVar()
    svr_lang_aul.set(mydict['ExEditLang'])
    menu_lang_aul.add_radiobutton(label='日本語', value='ja', variable=svr_lang_aul, command=change_lang_aul)
    menu_lang_aul.add_radiobutton(label='English', value='en', variable=svr_lang_aul, command=change_lang_aul)

    # ヘルプメニュー
    menu_help = Menu(mbar, tearoff=0)
    mbar.add_cascade(label=_('ヘルプ'), menu=menu_help)

    menu_help.add_command(label=_('使い方(Scrapbox)'),
                          command=lambda: open_website(
                              _('https://scrapbox.io/Garech/RPPtoEXO%E3%81%AE%E7%94%BB%E9%9D%A2%E3%81%AE%E8%AA%AC%E6%98%8E_(v2.6~)')))
    menu_help.add_command(label=_('最新バージョンを確認(GitHub)'),
                          command=lambda: open_website('https://github.com/Garech-mas/RPPtoEXO-ver2.0/releases/latest'))
    menu_help.add_command(label=_('制作者の連絡先(Twitter)'),
                          command=lambda: open_website('https://twitter.com/Garec_'))
    menu_help.add_command(label=_('このソフトについて'), command=about_rpp2exo)

    # フレーム・キャンバス設定
    frame_left = ttk.Frame(root)
    frame_left.grid(row=0, column=0)
    frame_center = ttk.Frame(root)
    frame_center.grid(row=0, column=1)

    canvas = Canvas(root, width=200, height=200, highlightthickness=0)
    vsb_canvas = ttk.Scrollbar(canvas, orient=VERTICAL, command=canvas.yview)

    canvas.grid(row=0, column=2, sticky=N, ipadx=200, ipady=230 if mydict['UseYMM4'] else 310)
    canvas.configure(yscrollcommand=vsb_canvas.set)
    frame_right = ttk.Frame(canvas)
    vsb_canvas.pack(side=RIGHT, fill=Y)
    canvas.create_window((0, 0), window=frame_right, anchor='nw')
    canvas.configure(scrollregion=(0, 0, 392, 392))

    # frame_rpp RPP選択
    frame_rpp = ttk.Frame(frame_left, padding=5)
    frame_rpp.grid(row=0, column=0, sticky=N)

    lbl_rpp_input = ttk.Label(frame_rpp, text='* RPP : ')
    lbl_rpp_input.grid(row=0, column=0)
    svr_rpp_input = StringVar()
    svr_rpp_input_temp = StringVar()
    ent_rpp_input = ttk.Entry(frame_rpp, textvariable=svr_rpp_input, width=46, validate='focusout',
                              validatecommand=root.register(set_rppinfo))
    ent_rpp_input.grid(row=0, column=1)
    ent_rpp_input.drop_target_register(DND_FILES)
    ent_rpp_input.dnd_bind("<<Drop>>", partial(drop_file, svr_rpp_input))
    btn_rpp_reload = ttk.Button(frame_rpp, text='↻', command=lambda: set_rppinfo(1), width=2)
    btn_rpp_reload.grid(row=0, column=2)
    btn_rpp_browse = ttk.Button(frame_rpp, text=_('参照…'), command=slct_rpp)
    btn_rpp_browse.grid(row=0, column=3)

    # frame_exo EXO指定
    frame_exo = ttk.Frame(frame_left, padding=5)
    frame_exo.grid(row=1, column=0)
    lbl_exo_input = ttk.Label(frame_exo, text='* EXO : ') if not mydict["UseYMM4"] else ttk.Label(
        frame_exo, text='* 保存ﾃﾝﾌﾟﾚｰﾄ名 : ')
    lbl_exo_input.grid(row=1, column=0)
    svr_exo_input = StringVar()
    ent_exo_input = ttk.Entry(frame_exo, textvariable=svr_exo_input, width=50)
    ent_exo_input.grid(row=1, column=1)
    if not mydict["UseYMM4"]:
        ent_exo_input.drop_target_register(DND_FILES)
        ent_exo_input.dnd_bind("<<Drop>>", partial(drop_file, svr_exo_input))
        btn_exo_saveas = ttk.Button(frame_exo, text=_('保存先…'), command=save_exo)
        btn_exo_saveas.grid(row=1, column=3)

    # frame_r2e ソフト独自設定 / 時間選択 / トラック選択
    frame_r2e = ttk.Frame(frame_left, padding=10)
    frame_r2e.grid(row=4, column=0)

    ivr_v_flip = IntVar()
    chk_v_flip = ttk.Checkbutton(frame_r2e, padding=5, text=_('左右反転'), onvalue=1, offvalue=0, variable=ivr_v_flip)
    chk_v_flip.grid(row=1, column=0, sticky=W)
    ivr_h_flip = IntVar()
    chk_h_flip = ttk.Checkbutton(frame_r2e, padding=5, text=_('上下反転'), onvalue=2, offvalue=0, variable=ivr_h_flip)
    chk_h_flip.grid(row=2, column=0, sticky=W)
    ivr_no_gap = IntVar()
    chk_no_gap = ttk.Checkbutton(frame_r2e, padding=5, text=_('隙間なく配置'), onvalue=1, offvalue=0, variable=ivr_no_gap)
    chk_no_gap.grid(row=3, column=0, sticky=W)

    ivr_sep_even = IntVar()
    chk_sep_even = ttk.Checkbutton(frame_r2e, padding=5, text=_('偶数番目Objを\n別レイヤ配置'), onvalue=1, offvalue=0,
                                   variable=ivr_sep_even)
    chk_sep_even.grid(row=4, column=0, sticky=W)

    ivr_slct_time = IntVar()
    chk_slct_time = ttk.Checkbutton(frame_r2e, padding=5, text=_('時間選択 (秒)'), onvalue=1, offvalue=0,
                                    variable=ivr_slct_time, command=change_time_cb)
    chk_slct_time.grid(row=5, column=0, sticky=W)
    svr_time_preset = StringVar()
    svr_time_preset.set('')
    cmb_time_preset = ttk.Combobox(frame_r2e, textvariable=svr_time_preset, width=10, state='disable')
    cmb_time_preset.bind('<<ComboboxSelected>>', set_time)
    cmb_time_preset.grid(row=6, column=0, padx=5, pady=3, sticky=W + E)

    svr_time1 = StringVar()
    cmb_time1 = ttk.Combobox(frame_r2e, textvariable=svr_time1, width=10, state='disable')
    cmb_time1.bind('<<ComboboxSelected>>', set_time1)
    cmb_time1.grid(row=7, column=0, padx=5, pady=3, sticky=W + E)
    svr_time2 = StringVar()
    cmb_time2 = ttk.Combobox(frame_r2e, textvariable=svr_time2, width=10, state='disable')
    cmb_time2.bind('<<ComboboxSelected>>', set_time2)
    cmb_time2.grid(row=8, column=0, padx=5, pady=(3, 110), sticky=W + E)

    tvw_slct_track = CheckboxTreeview(frame_r2e, show='tree', height=24)
    tvw_slct_track.grid(row=0, column=1, rowspan=9, sticky=N + S + E + W)
    tvw_slct_track.column("#0", width=300)
    ttk.Style().configure('Checkbox.Treeview', rowheight=15, borderwidth=1, relief='sunken', indent=0)

    vsb_slct_track = Scrollbar(frame_r2e, orient=VERTICAL, command=tvw_slct_track.yview)
    vsb_slct_track.grid(row=0, column=2, rowspan=9, sticky=N + S)
    tvw_slct_track['yscrollcommand'] = vsb_slct_track.set
    tvw_slct_track.bind('<<TreeviewClose>>', lambda event: tvw_slct_track.expand_all())

    # frame_alias 効果をファイルから読み込む
    frame_alias = ttk.Frame(frame_left, padding=5)
    frame_alias.grid(row=6, column=0)
    lbl_alias_input = ttk.Label(frame_alias, text=_('エイリアス : '))
    lbl_alias_input.grid(row=0, column=0, sticky=W)
    svr_alias_input = StringVar()
    if not mydict['UseYMM4']:
        btn_alias_browse = ttk.Button(frame_alias, text=_('参照…'), command=slct_filter_cfg_file)
        btn_alias_browse.grid(row=0, column=2)
        ent_alias_input = ttk.Entry(frame_alias, textvariable=svr_alias_input, width=40)
        ent_alias_input.grid(row=0, column=1)
        ent_alias_input.drop_target_register(DND_FILES)
        ent_alias_input.dnd_bind("<<Drop>>", partial(drop_file, svr_alias_input))
    else:
        cmb_ymm4_saveas = ttk.Combobox(frame_alias, textvariable=svr_alias_input, values=ymm4_cl.temp_list, width=50, state='readonly')
        cmb_ymm4_saveas.grid(row=0, column=1)
        btn_rpp_reload = ttk.Button(frame_alias, text='↻', command=ymm4_cl.load, width=2)
        btn_rpp_reload.grid(row=0, column=2)

    # frame_script スクリプト制御
    frame_script = ttk.Frame(frame_left, padding=10)
    txt_script = Text(frame_script, width=50, height=10)
    if not mydict['UseYMM4']:
        frame_script.grid(row=7, column=0)
        lbl_script = ttk.Label(frame_script, text=_('スクリプト制御 '))
        lbl_script.grid(row=0, column=0, sticky=W)
        svr_script = StringVar()
        txt_script.grid(row=0, column=1)

    # frame_trgt 追加対象オブジェクト・素材指定、オブジェクト設定チェックボックス
    frame_trgt = ttk.Frame(frame_right, padding=5)
    frame_trgt.grid(row=0, column=0, columnspan=2)
    ivr_trgt_mode = IntVar()
    ivr_trgt_mode.set(1)

    lbl_trgt_mode = ttk.Label(frame_trgt, text=_('追加対象 : '))
    lbl_trgt_mode.grid(row=0, column=0, sticky=W)
    rbt_trgt_auto = ttk.Radiobutton(frame_trgt, value=0, variable=ivr_trgt_mode, text=_('自動検出'), command=mode_command)
    rbt_trgt_auto.grid(row=0, column=1)
    rbt_trgt_video = ttk.Radiobutton(frame_trgt, value=1, variable=ivr_trgt_mode, text=_('動画'), command=mode_command)
    rbt_trgt_video.grid(row=0, column=2)
    rbt_trgt_pic = ttk.Radiobutton(frame_trgt, value=2, variable=ivr_trgt_mode, text=_('画像'), command=mode_command)
    rbt_trgt_pic.grid(row=0, column=3)
    rbt_trgt_filter = ttk.Radiobutton(frame_trgt, value=3, variable=ivr_trgt_mode, text=_('フィルタ'), command=mode_command)
    rbt_trgt_filter.grid(row=0, column=4)

    svr_scene_idx = StringVar()
    ent_scene_idx = ttk.Entry(frame_trgt, textvariable=svr_scene_idx, width=3, state='disable')

    if not mydict['UseYMM4']:
        rbt_trgt_scene = ttk.Radiobutton(frame_trgt, value=4, variable=ivr_trgt_mode, text=_('シーン番号: '),
                                         command=mode_command)
        rbt_trgt_scene.grid(row=0, column=5)
        ent_scene_idx.grid(row=0, column=6)
    else:
        rbt_trgt_scene = ttk.Radiobutton(frame_trgt, value=4, variable=ivr_trgt_mode, text=_('立ち絵'),
                                         command=mode_command)
        rbt_trgt_scene.grid(row=0, column=5)
        svr_scene_idx.set('1')

    lbl_src_input = ttk.Label(frame_trgt, text=_('素材 : '))
    lbl_src_input.grid(row=1, column=0, sticky=E)
    svr_src_input = StringVar()
    ent_src_input = ttk.Entry(frame_trgt, textvariable=svr_src_input, width=46)
    ent_src_input.grid(row=1, column=1, columnspan=5, sticky=W)
    ent_src_input.drop_target_register(DND_FILES)
    ent_src_input.dnd_bind("<<Drop>>", partial(drop_file, svr_src_input))
    btn_src_browse = ttk.Button(frame_trgt, text=_('参照…'), command=slct_source)
    btn_src_browse.grid(row=1, column=5, columnspan=2, sticky=E)
    ivr_randplay = IntVar()
    chk_randplay = ttk.Checkbutton(frame_trgt, padding=5, text=_('再生位置ランダム'), onvalue=1, offvalue=0, variable=ivr_randplay)
    chk_randplay.grid(row=2, column=0, columnspan=3, sticky=W)

    ivr_clipping = IntVar()
    chk_clipping = ttk.Checkbutton(frame_trgt, padding=5, text=ExDict['上のオブジェクトでクリッピング'],
                                   onvalue=1, offvalue=0, variable=ivr_clipping)
    chk_clipping.grid(row=3, column=0, columnspan=3, sticky=W)
    ivr_adv_draw = IntVar()
    ivr_adv_draw.set(0)
    chk_adv_draw = ttk.Checkbutton(frame_trgt, padding=5, text=ExDict['拡張描画'], onvalue=1, offvalue=0,
                                   variable=ivr_adv_draw, command=lambda: toggle_media_label(ivr_adv_draw.get() + 1))
    if not mydict['UseYMM4']:
        chk_adv_draw.grid(row=3, column=5, columnspan=2, sticky=E)

    # frame_stddraw オブジェクトの標準パラメータ設定
    frame_stddraw = ttk.Frame(frame_right, padding=5, borderwidth=3)
    frame_stddraw.grid(row=1)

    # 描画名ラベル
    mLabel.append(StringVar())
    mLabel[0].set(ExDict['標準描画'])
    b = ttk.Label(frame_stddraw, textvariable=mLabel[0])
    b.grid(row=0, column=0)
    mLabel2.append(b)
    # 始点終点ラベル
    mSELabel.append(StringVar())
    mSELabel[0].set(_("始点"))
    b = ttk.Label(frame_stddraw, textvariable=mSELabel[0])
    b.grid(row=0, column=1)
    mSELabelE.append(b)
    mSELabel.append(StringVar())
    mSELabel[1].set(_("終点"))
    b = ttk.Label(frame_stddraw, textvariable=mSELabel[1])
    b.grid(row=0, column=3)
    mSELabelE.append(b)
    mSELabel.append(StringVar())
    mSELabel[2].set(_("設定"))
    b = ttk.Label(frame_stddraw, textvariable=mSELabel[2])
    b.grid(row=0, column=4)
    mSELabelE.append(b)

    for n in range(len(prmlist)):
        mLabel.append(StringVar())
        mLabel[n+1].set(ExDict.get(prmlist[n][0], prmlist[n][0]))
        b = ttk.Label(frame_stddraw, textvariable=mLabel[n+1])
        b.grid(row=n+1, column=0, padx=5)
        mLabel2.append(b)
        mEntryS.append(StringVar())
        mEntrySE.append(ttk.Entry(frame_stddraw, textvariable=mEntryS[n], width=7))
        mEntrySE[n].grid(row=n+1, column=1, padx=5)
        mEntrySE[n].insert(END, prmlist[n][1])
        mEntryX.append(StringVar())
        mEntryXCb.append(ttk.Combobox(frame_stddraw, textvariable=mEntryX[n]))
        mEntryXCb[n]['values'] = list(XDict.keys())
        mEntryXCb[n].set(list(XDict.keys())[0])
        mEntryXCb[n].grid(row=n+1, column=2, padx=5)

        mEntryE.append(StringVar())
        mEntryEE.append(ttk.Entry(frame_stddraw, textvariable=mEntryE[n], width=7))
        mEntryEE[n].grid(row=n+1, column=3, padx=5)

        mEntryConf.append(StringVar())
        mEntryConfE.append(ttk.Entry(frame_stddraw, textvariable=mEntryConf[n], width=5))
        mEntryConfE[n].grid(row=n+1, column=4, padx=5)
    toggle_media_label(1)
    if mydict['UseYMM4']:
        mEntryS[4].set('100.0')
        mEntryS[13].set('00:00:00')
        mLabel[5].set('不透明度')
        mLabel[6].set('回転角')
        mEntryXCb[13]['state'] = 'disable'
        mEntryXCb[14]['state'] = 'disable'

    frame_optdraw = ttk.Frame(frame_right, borderwidth=3)
    frame_optdraw.grid(row=2, sticky='W')

    lbl_blend = ttk.Label(frame_optdraw, text=ExDict['合成モード'])
    lbl_blend.grid(row=0, column=0, padx=10)
    Param15 = StringVar()
    ParamCombo15 = ttk.Combobox(frame_optdraw, textvariable=Param15, state='readonly')
    ParamCombo15['values'] = list(BlendDict.keys())
    ParamCombo15.set(list(BlendDict.keys())[0])
    ParamCombo15.grid(row=0, column=1, columnspan=2, sticky=W + E)
    ivr_import_alpha = IntVar()
    ivr_import_alpha.set(0)
    chk_import_alpha = ttk.Checkbutton(frame_optdraw, padding=5, text=ExDict['アルファチャンネルを読み込む'],
                                       onvalue=1, offvalue=0, variable=ivr_import_alpha)
    chk_import_alpha.grid(row=1, column=2, sticky=W)
    ivr_loop = IntVar()
    ivr_loop.set(0)
    chk_loop = ttk.Checkbutton(frame_optdraw, padding=5, text=ExDict['ループ再生'], onvalue=1, offvalue=0, variable=ivr_loop)
    chk_loop.grid(row=1, column=1, sticky=W)

    # frame_eff エフェクト追加/削除
    if not mydict['UseYMM4']:
        frame_eff = ttk.Frame(frame_right, padding=5)
        frame_eff.grid(row=3, column=0)
        svr_add_eff = StringVar()
        cmb_add_eff = ttk.Combobox(frame_eff, textvariable=svr_add_eff, state='readonly')
        cmb_add_eff['values'] = list(EffDict.keys())
        cmb_add_eff.set(list(EffDict.keys())[0])
        cmb_add_eff.grid(row=0, column=0)
        btn_add_eff = ttk.Button(frame_eff, text='+', command=add_filter_label)
        btn_add_eff.grid(row=0, column=1)
        btn_clear_eff = ttk.Button(frame_eff, text=_('効果のクリア'), command=del_filter_label)
        btn_clear_eff.grid(row=0, column=2)

        # frame_effprm エフェクトのパラメータ設定
        frame_effprm = ttk.Frame(frame_right, padding=5, borderwidth=3)
        frame_effprm.grid(row=4)

    # frame_exec 実行
    frame_exec = ttk.Frame(frame_left, padding=(0, 5))
    frame_exec.grid(row=8, column=0)
    lbl_fps_input = ttk.Label(frame_exec, text='* FPS : ')
    lbl_fps_input.grid(row=0, column=0, sticky=W + E)
    svr_fps_input = StringVar()
    ent_fps_input = ttk.Entry(frame_exec, textvariable=svr_fps_input, width=10)
    ent_fps_input.grid(row=0, column=1, sticky=W + E, padx=10)
    ent_fps_input.insert(END, "")
    btn_exec = ttk.Button(frame_exec, text=_('実行'), command=run)
    btn_exec.grid(row=0, column=2)

    root.mainloop()
