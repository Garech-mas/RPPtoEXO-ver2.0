#####################################################################################
#               RPP to EXO ver 2.05.3                                               #
#                                                                       2023/11/07  #
#       Original Written by Maimai (@Maimai22015/YTPMV.info)                        #
#       Forked by Garech (@Garec_)                                                  #
#                                                                                   #
#       協力：SHI(@sbt54864666)                                                      #
#####################################################################################

import configparser
import gettext
import subprocess
import sys
import threading
import webbrowser
from functools import partial
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk, Menu
from ttkwidgets import CheckboxTreeview
from tkinterdnd2 import *
import rpp2exo
from rpp2exo import Rpp, Exo
from rpp2exo.dict import *

R2E_VERSION = '2.05.3'

rpp_cl = Rpp("")
mydict = mydict


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


def main():
    btn_exec['state'] = 'disable'
    root['cursor'] = 'watch'
    btn_exec["text"] = _("実行中") + " (1/3)"

    try:
        exo_cl = Exo(mydict)
        if ivr_slct_time.get():
            rpp_cl.start_pos = float(cmb_time1.get())
            rpp_cl.end_pos = float(cmb_time2.get()) if cmb_time2.get() != '' else 99999.0
            if rpp_cl.start_pos < rpp_cl.end_pos:
                pass
            elif rpp_cl.start_pos > rpp_cl.end_pos:
                rpp_cl.start_pos, rpp_cl.end_pos = rpp_cl.end_pos, rpp_cl.start_pos
            else:
                rpp_cl.start_pos = 0.0
                rpp_cl.end_pos = 99999.0
        else:
            rpp_cl.start_pos = 0.0
            rpp_cl.end_pos = 99999.0
        file_path, end1 = rpp_cl.main(mydict["OutputType"] == 0, mydict["Track"])

        btn_exec["text"] = _("実行中") + " (2/3)"
        file_fps = exo_cl.fetch_fps(file_path)

        btn_exec["text"] = _("実行中") + " (3/3)"
        end3 = exo_cl.make_exo(rpp_cl.objDict, file_path, file_fps)
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

        if not mydict['PatchExists'] and mydict['HasPatchError']:
            print(_("★警告: AviUtl 拡張編集のバグにより、オブジェクトの設定は正常に反映されません。"))
            end = end | {1: 1}

        if end == {}:
            ret = messagebox.askyesno(_("正常終了"), _("正常に生成されました。\n保存先のフォルダを開きますか？"))
        else:
            ret = messagebox.askyesno(_("警告"),
                                      _("一部アイテムが正常に生成できませんでした。詳細はコンソールをご覧ください。\n保存先のフォルダを開きますか？"), icon="warning")

        if ret:
            path = os.path.dirname(mydict["EXOPath"]).replace('/', '\\')
            if path == "":
                path = os.getcwd()
            subprocess.Popen(['explorer', path], shell=True)
    finally:
        print('--------------------------------------------------------------------------')
        btn_exec['state'] = 'normal'
        root['cursor'] = 'arrow'
        btn_exec["text"] = _("実行")


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
            ('0', 'patch_exists', 'Param'),  # patch.aulが存在するか 0/1
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
            mydict["PatchExists"] = int(config_ini.get("Param", "patch_exists"))
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
    filetype = [(_("REAPERプロジェクトファイル"), "*.rpp")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["RPPLastDir"], title=_("RPPファイルを選択"))
    if filepath != '':
        svr_rpp_input.set(filepath)
        write_cfg(filepath, "RPPDir", "Directory")
        set_rppinfo()


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

    if ivr_slct_time.get():
        change_time_cb()
    if filepath.lower().endswith(".rpp"):
        try:
            rpp_cl.load(filepath)
        except (PermissionError, FileNotFoundError):
            return True
        tree = rpp_cl.load_track()
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
            hCheckBoxCb.append(ttk.Checkbutton(
                frame_effprm,
                padding=0,
                text=EffDict[svr_add_eff.get()][n][0],
                onvalue=1,
                offvalue=0,
                variable=hCheckBox[mydict["EffCbNum"]]))
            hCheckBoxCb[mydict["EffCbNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], columnspan=4, column=1, sticky=W)
            mydict["EffCbNum"] += 1
        elif EffDict[svr_add_eff.get()][n][-1] == -2:  # Entryだけの項目(めっちゃ強引な実装だから全体的に書き直したい…)
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]
                   ].set(EffDict[svr_add_eff.get()][n][0])
            b = ttk.Label(
                frame_effprm, textvariable=hLabel[mydict["EffNum"] + mydict["EffCount"]])
            b.grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                   column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(
                frame_effprm, textvariable=hEntryS[mydict["EffNum"]], width=7))
            hEntrySE[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=1, columnspan=4, sticky=W + E)
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[svr_add_eff.get()][n][1])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(
                frame_effprm, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set(list(XDict.keys())[0])

            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(
                frame_effprm, textvariable=hEntryE[mydict["EffNum"]], width=7))

            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(
                frame_effprm, textvariable=hEntryConf[mydict["EffNum"]], width=5))

            mydict["EffNum"] += 1
        else:
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]
                   ].set(EffDict[svr_add_eff.get()][n][0])
            b = ttk.Label(
                frame_effprm, textvariable=hLabel[mydict["EffNum"] + mydict["EffCount"]])
            b.grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                   column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(
                frame_effprm, textvariable=hEntryS[mydict["EffNum"]], width=7))
            hEntrySE[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=1, padx=5)
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[svr_add_eff.get()][n][1])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(
                frame_effprm, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set(list(XDict.keys())[0])
            hEntryXCb[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=2, padx=5)

            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(
                frame_effprm, textvariable=hEntryE[mydict["EffNum"]], width=7))
            hEntryEE[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=3, padx=5)

            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(
                frame_effprm, textvariable=hEntryConf[mydict["EffNum"]], width=5))
            hEntryConfE[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=4, padx=5)

            mydict["EffNum"] += 1


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


def run():
    try:
        read_cfg()
        mydict["RPPPath"] = svr_rpp_input.get().replace('"', '')
        if svr_exo_input.get().replace('"', '').lower().endswith(".exo") or svr_exo_input.get().replace('"', '') == "":
            mydict["EXOPath"] = svr_exo_input.get().replace('"', '')
        else:
            mydict["EXOPath"] = svr_exo_input.get().replace('"', '') + ".exo"
        mydict["OutputType"] = ivr_trgt_mode.get()
        mydict["SrcPath"] = svr_src_input.get().replace('"', '').replace('/', '\\')
        mydict["EffPath"] = svr_alias_input.get().replace('"', '')
        mydict["IsAlpha"] = ivr_import_alpha.get()
        mydict["IsLoop"] = ivr_loop.get()
        mydict["SrcPosition"] = svr_obj_playpos.get()
        mydict["SrcRate"] = svr_obj_playrate.get()
        # mydict["BreakFrames"] = list(map(int, svr_stop_frame.get().split(','))) if svr_stop_frame.get() else []
        mydict["fps"] = float(svr_fps_input.get())
        mydict["ScriptText"] = txt_script.get('1.0', 'end-1c')
        mydict["ObjFlipType"] = ivr_v_flip.get() + ivr_h_flip.get()
        mydict["SepLayerEvenObj"] = ivr_sep_even.get()
        mydict["NoGap"] = ivr_no_gap.get()
        mydict["clipping"] = ivr_clipping.get()
        mydict["IsExSet"] = ivr_adv_draw.get()
        mydict["X"] = ParamEntry1.get()
        mydict["Y"] = ParamEntry2.get()
        mydict["Z"] = ParamEntry3.get()
        mydict["Size"] = ParamEntry4.get()
        mydict["Alpha"] = ParamEntry5.get()
        mydict["Ratio"] = ParamEntry6.get()
        mydict["Rotation"] = ParamEntry7.get()
        mydict["XRotation"] = ParamEntry8.get()
        mydict["YRotation"] = ParamEntry9.get()
        mydict["ZRotation"] = ParamEntry10.get()
        mydict["XCenter"] = ParamEntry11.get()
        mydict["YCenter"] = ParamEntry12.get()
        mydict["ZCenter"] = ParamEntry13.get()
        mydict["SceneIdx"] = int(svr_scene_idx.get() or 0)
        mydict["Blend"] = BlendDict[ParamCombo15.get()]
        mydict["Track"] = tvw_slct_track.get_checked()
        mydict["DisplayLang"] = svr_lang_r2e.get()
        mydict["ExEditLang"] = svr_lang_aul.get()
    except ValueError:
        if svr_fps_input.get() != '':
            messagebox.showinfo(_("エラー"), _("半角の数値を入力すべき箇所へ不正な文字列が入力されています。"))
            return 0
        else:
            mydict["fps"] = ""

    trackbar_error = False

    try:
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

        if (mydict["SceneIdx"] <= 0 or mydict["SceneIdx"] >= 50) and mydict["OutputType"] == 4:
            messagebox.showinfo(_("エラー"), _("正しいシーン番号を入力してください。（範囲 : 1 ~ 49）"))
            return 0
        elif mydict["SceneIdx"] != 1 and mydict["OutputType"] == 4:
            patched_error(_('AviUtl本体のバグの影響により、シーン番号は反映されません。'))

        # トラックバーエラーの検知
        if (-1 < float(mydict["X"]) < 0 or -1 < float(mydict["Y"]) < 0 or -1 < float(mydict["Z"]) < 0 or
                -1 < float(mydict["Size"]) < 0 or -1 < float(mydict["Alpha"]) < 0 or -1 < float(mydict["Ratio"]) < 0 or
                -1 < float(mydict["Rotation"]) < 0 or -1 < float(mydict["XRotation"]) < 0 or
                -1 < float(mydict["YRotation"]) < 0 or -1 < float(mydict["ZRotation"]) < 0 or
                -1 < float(mydict["XCenter"]) < 0 or -1 < float(mydict["YCenter"]) < 0 or -1 < float(
                    mydict["ZCenter"]) < 0 or
                -1 < float(mydict["Blend"]) < 0 or -1 < float(mydict["SrcRate"]) < 0):
            patched_error(_('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
            trackbar_error = True

        count = mydict["EffCount"]
        runcount = 0
        runcountcb = 0
        eff = ""

        for i in range(0, int(count)):
            # runcount += 1
            del mydict["Effect"][i][1:]
            for x in range(len(EffDict[mydict["Effect"][i][0]])):
                if EffDict[mydict["Effect"][i][0]][x][-1] != -1:  # チェックボックスでない場合
                    if hEntryX[runcount].get() == list(XDict.keys())[0]:  # 移動なしの場合
                        if not trackbar_error and EffDict[mydict["Effect"][i][0]][x][-1] != -2 and \
                                -1 < float(hEntryS[runcount].get()) < 0:
                            patched_error(_('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
                            trackbar_error = True

                        eff = [EffDict[mydict["Effect"][i][0]][x][0],
                               set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1])]
                        mydict["Effect"][i].append(eff)
                    else:  # 移動ありの場合
                        if str(hEntryE[runcount].get()) == "":
                            messagebox.showinfo(_("エラー"), _("追加フィルタ効果の終点が入力されていません。"))
                            return 0
                        # 移動方法の終点にスクリプト名などの文字列が入力できなくなっていたため削除  近いうちに全て作り直さなきゃ
                        # if not trackbar_error and EffDict[mydict["Effect"][i][0]][x][-1] != -2 and \
                        #         (-1 < float(hEntryS[runcount].get()) < 0 or -1 < float(hEntryE[runcount].get()) < 0):
                        #     patched_error(_('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
                        #     trackbar_error = True
                        eff = [EffDict[mydict["Effect"][i][0]][x][0],
                               set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                               + set_decimal(hEntryE[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                               + str(XDict[hEntryX[runcount].get()])]
                        if XDict[hEntryX[runcount].get()] != "":
                            eff[1] += str(hEntryConf[runcount].get())
                            if not str(XDict[hEntryX[runcount].get()]).isascii():
                                patched_error(_("AviUtl本体のバグの影響により、移動の設定の値は反映されません。"))
                        if XDict[hEntryX[runcount].get()] != "" and hEntryConf[runcount].get() != "":
                            eff = [EffDict[mydict["Effect"][i][0]][x][0],
                                   set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                                   + set_decimal(hEntryE[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                                   + str(XDict[hEntryX[runcount].get()]) + "," + str(hEntryConf[runcount].get())]
                        mydict["Effect"][i].append(eff)
                    runcount += 1
                elif EffDict[mydict["Effect"][i][0]][x][-1] == -1:  # チェックボックスの場合
                    eff = [EffDict[mydict["Effect"][i][0]][x][0],
                           str(hCheckBox[runcountcb].get())]
                    mydict["Effect"][i].append(eff)
                    runcountcb += 1
    except ValueError as e:
        messagebox.showinfo(_("エラー"), _("半角の数値を入力すべき箇所へ不正な文字列が入力されています。"))
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

    if ivr_trgt_mode.get() == 1:  # アルファチャンネルを読み込む
        chk_import_alpha['state'] = 'enable'
    else:
        chk_import_alpha['state'] = 'disable'

    if ivr_trgt_mode.get() == 1 or ivr_trgt_mode.get() == 4:  # ループ再生・再生速度・再生位置
        chk_loop['state'] = 'enable'
        ent_obj_playrate['state'] = 'enable'
        ent_obj_playpos['state'] = 'enable'

    else:
        chk_loop['state'] = 'disable'
        ent_obj_playrate['state'] = 'disable'
        ent_obj_playpos['state'] = 'disable'


def advdraw_command():  # 「拡張描画」変更時の状態切り替え
    if ivr_adv_draw.get() == 0:
        ParamEntryE6['state'] = 'disable'
        ParamEntryE8['state'] = 'disable'
        ParamEntryE9['state'] = 'disable'
        ParamEntryE10['state'] = 'disable'
        ParamEntryE11['state'] = 'disable'
        ParamEntryE12['state'] = 'disable'
        ParamEntryE13['state'] = 'disable'
    else:
        ParamEntryE6['state'] = 'enable'
        ParamEntryE8['state'] = 'enable'
        ParamEntryE9['state'] = 'enable'
        ParamEntryE10['state'] = 'enable'
        ParamEntryE11['state'] = 'enable'
        ParamEntryE12['state'] = 'enable'
        ParamEntryE13['state'] = 'enable'


def change_time_cb():  # 「時間選択」変更時の状態切り替え
    if ivr_slct_time.get():
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
    target.set(event.data[1:event.data.find('}')])


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
    ivr_patch_exists = IntVar()
    ivr_patch_exists.set(mydict['PatchExists'])
    menu_setting.add_checkbutton(label=_('拡張編集v0.92由来のエラーを無視'), variable=ivr_patch_exists,
                                 command=lambda: write_cfg(int(ivr_patch_exists.get()), "patch_exists", "Param"))

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
                              _('https://scrapbox.io/Garech/RPPtoEXO%E3%81%AE%E7%94%BB%E9%9D%A2%E3%81%AE%E8%AA%AC%E6%98%8E')))
    menu_help.add_command(label=_('最新バージョンを確認(GitHub)'),
                          command=lambda: open_website('https://github.com/Garech-mas/RPPtoEXO-ver2.0/releases/latest'))
    menu_help.add_command(label=_('制作者の連絡先(Twitter)'),
                          command=lambda: open_website('https://twitter.com/Garec_'))
    menu_help.add_command(label=_('このソフトについて'), command=about_rpp2exo)

    frame_left = ttk.Frame(root)
    frame_left.grid(row=0, column=0)
    frame_center = ttk.Frame(root)
    frame_center.grid(row=0, column=1)
    frame_right = ttk.Frame(root)
    frame_right.grid(row=0, column=2)

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
    lbl_exo_input = ttk.Label(frame_exo, text='* EXO : ')
    lbl_exo_input.grid(row=1, column=0)
    svr_exo_input = StringVar()
    ent_exo_input = ttk.Entry(frame_exo, textvariable=svr_exo_input, width=50)
    ent_exo_input.grid(row=1, column=1)
    ent_exo_input.drop_target_register(DND_FILES)
    ent_exo_input.dnd_bind("<<Drop>>", partial(drop_file, svr_exo_input))
    btn_exo_saveas = ttk.Button(frame_exo, text=_('保存先…'), command=save_exo)
    btn_exo_saveas.grid(row=1, column=3)

    # frame_trgt 追加対象オブジェクト・素材指定
    frame_trgt = ttk.Frame(frame_left, padding=5)
    frame_trgt.grid(row=2, column=0)
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
    rbt_trgt_scene = ttk.Radiobutton(frame_trgt, value=4, variable=ivr_trgt_mode, text=_('シーン番号: '),
                                     command=mode_command)
    rbt_trgt_scene.grid(row=0, column=5)
    svr_scene_idx = StringVar()
    ent_scene_idx = ttk.Entry(frame_trgt, textvariable=svr_scene_idx, width=3, state='disable')
    ent_scene_idx.grid(row=0, column=6)

    lbl_src_input = ttk.Label(frame_trgt, text=_('素材 : '))
    lbl_src_input.grid(row=1, column=0, sticky=E)
    svr_src_input = StringVar()
    ent_src_input = ttk.Entry(frame_trgt, textvariable=svr_src_input, width=46)
    ent_src_input.grid(row=1, column=1, columnspan=5, sticky=W)
    ent_src_input.drop_target_register(DND_FILES)
    ent_src_input.dnd_bind("<<Drop>>", partial(drop_file, svr_src_input))
    btn_src_browse = ttk.Button(frame_trgt, text=_('参照…'), command=slct_source)
    btn_src_browse.grid(row=1, column=5, columnspan=2, sticky=E)

    # lbl_stop_frame = ttk.Label(frame_trgt, text='強制停止F : ')
    # lbl_stop_frame.grid(row=2, column=0, sticky=E)
    # svr_stop_frame = StringVar()
    # ent_stop_frame = ttk.Entry(frame_trgt, textvariable=svr_stop_frame, width=60)
    # ent_stop_frame.grid(row=2, column=1, columnspan=6, sticky=W)

    # frame_obj  オブジェクト設定
    frame_obj = ttk.Frame(frame_left, padding=1)
    frame_obj.grid(row=3, column=0)

    ivr_clipping = IntVar()
    chk_clipping = ttk.Checkbutton(frame_obj, padding=5, text=_('上のオブジェクトでクリッピング'), onvalue=1, offvalue=0,
                                   variable=ivr_clipping)
    chk_clipping.grid(row=0, column=0, sticky=W)
    ivr_adv_draw = IntVar()
    ivr_adv_draw.set(0)
    chk_adv_draw = ttk.Checkbutton(frame_obj, padding=5, text=_('拡張描画'), onvalue=1, offvalue=0, variable=ivr_adv_draw,
                                   command=advdraw_command)
    chk_adv_draw.grid(row=0, column=1, sticky=W)
    ivr_import_alpha = IntVar()
    ivr_import_alpha.set(0)
    chk_import_alpha = ttk.Checkbutton(frame_obj, padding=5, text=_('アルファチャンネルを読み込む'), onvalue=1, offvalue=0,
                                       variable=ivr_import_alpha)
    chk_import_alpha.grid(row=1, column=0, sticky=W)
    ivr_loop = IntVar()
    ivr_loop.set(0)
    chk_loop = ttk.Checkbutton(frame_obj, padding=5, text=_('ループ再生'), onvalue=1, offvalue=0, variable=ivr_loop)
    chk_loop.grid(row=1, column=1, sticky=W)

    lbl_obj_playrate = ttk.Label(frame_obj, text=_('再生速度 : '))
    lbl_obj_playrate.grid(row=0, column=3, sticky=E, padx=(8, 0))
    svr_obj_playrate = StringVar()
    ent_obj_playrate = ttk.Entry(frame_obj, textvariable=svr_obj_playrate, width=10)
    ent_obj_playrate.grid(row=0, column=4, sticky=W + E)
    ent_obj_playrate.insert(END, "100.0")

    lbl_obj_playpos = ttk.Label(frame_obj, text=_('再生位置 : '))
    lbl_obj_playpos.grid(row=1, column=3, sticky=E, padx=(8, 0))
    svr_obj_playpos = StringVar()
    ent_obj_playpos = ttk.Entry(frame_obj, textvariable=svr_obj_playpos, width=10)
    ent_obj_playpos.grid(row=1, column=4, sticky=W + E)
    ent_obj_playpos.insert(END, "1")

    # frame_r2e ソフト独自設定 / 時間選択 / トラック選択
    frame_r2e = ttk.Frame(frame_left, padding=10)
    frame_r2e.grid(row=4, column=0)

    # v1 = IntVar()
    # v1.set(1)
    # cb1 = ttk.Checkbutton(frame4a, padding=5, text='トラック毎に\n設定を調整する', onvalue=1, offvalue=0, variable=v1)
    # cb1.grid(row=0, column=0, sticky=W)
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
                                    variable=ivr_slct_time,
                                    command=change_time_cb)
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
    cmb_time2.grid(row=8, column=0, padx=5, pady=3, sticky=W + E)

    tvw_slct_track = CheckboxTreeview(frame_r2e, show='tree', height=5)
    tvw_slct_track.grid(row=0, column=1, rowspan=9, sticky=N + S + E + W)
    tvw_slct_track.column("#0", width=300)
    ttk.Style().configure('Checkbox.Treeview', rowheight=15, borderwidth=1, relief='sunken', indent=0)

    vsb_slct_track = Scrollbar(frame_r2e, orient=VERTICAL, command=tvw_slct_track.yview)
    vsb_slct_track.grid(row=0, column=2, rowspan=9, sticky=N + S)
    tvw_slct_track['yscrollcommand'] = vsb_slct_track.set

    # frame_eff エフェクト追加/削除
    frame_eff = ttk.Frame(frame_left, padding=5)
    frame_eff.grid(row=5, column=0)
    svr_add_eff = StringVar()
    cmb_add_eff = ttk.Combobox(frame_eff, textvariable=svr_add_eff, state='readonly')
    cmb_add_eff['values'] = list(EffDict.keys())
    cmb_add_eff.set(list(EffDict.keys())[0])
    cmb_add_eff.grid(row=0, column=0)
    btn_add_eff = ttk.Button(frame_eff, text='+', command=add_filter_label)
    btn_add_eff.grid(row=0, column=1)
    btn_clear_eff = ttk.Button(frame_eff, text=_('効果のクリア'), command=del_filter_label)
    btn_clear_eff.grid(row=0, column=2)

    # frame_alias 効果をファイルから読み込む
    frame_alias = ttk.Frame(frame_left, padding=5)
    frame_alias.grid(row=6, column=0)
    btn_alias_browse = ttk.Button(frame_alias, text=_('参照…'), command=slct_filter_cfg_file)
    btn_alias_browse.grid(row=0, column=2)
    lbl_alias_input = ttk.Label(frame_alias, text=_('エイリアス : '))
    lbl_alias_input.grid(row=0, column=0, sticky=W)
    svr_alias_input = StringVar()
    ent_alias_input = ttk.Entry(frame_alias, textvariable=svr_alias_input, width=40)
    ent_alias_input.grid(row=0, column=1)
    ent_alias_input.drop_target_register(DND_FILES)
    ent_alias_input.dnd_bind("<<Drop>>", partial(drop_file, svr_alias_input))

    # frame_script スクリプト制御
    frame_script = ttk.Frame(frame_left, padding=10)
    frame_script.grid(row=7, column=0)
    lbl_script = ttk.Label(frame_script, text=_('スクリプト制御 '))
    lbl_script.grid(row=0, column=0, sticky=W)
    svr_script = StringVar()
    txt_script = Text(frame_script, width=50, height=10)
    txt_script.grid(row=0, column=1)

    # frame_effprm エフェクトのパラメータ設定 (動的)
    frame_effprm = ttk.Frame(frame_right, padding=10, borderwidth=3)
    frame_effprm.grid()

    # frame_baseprm 基本パラメータ設定
    frame_baseprm = ttk.Frame(frame_center, padding=10)
    frame_baseprm.grid(row=0, column=0)

    Param1 = StringVar()
    Param1.set('X : ')
    ParamLabel1 = ttk.Label(frame_baseprm, textvariable=Param1)
    ParamLabel1.grid(row=0, column=0, sticky=W + E)
    ParamEntry1 = StringVar()
    ParamEntryE1 = ttk.Entry(frame_baseprm, textvariable=ParamEntry1, width=5)
    ParamEntryE1.grid(row=0, column=1, sticky=W + E)
    ParamEntryE1.insert(END, "0.0")

    Param2 = StringVar()
    Param2.set('Y : ')
    ParamLabel2 = ttk.Label(frame_baseprm, textvariable=Param2)
    ParamLabel2.grid(row=1, column=0, sticky=W + E)
    ParamEntry2 = StringVar()
    ParamEntryE2 = ttk.Entry(frame_baseprm, textvariable=ParamEntry2, width=5)
    ParamEntryE2.grid(row=1, column=1, sticky=W + E)
    ParamEntryE2.insert(END, "0.0")

    Param3 = StringVar()
    Param3.set('Z : ')
    ParamLabel3 = ttk.Label(frame_baseprm, textvariable=Param3)
    ParamLabel3.grid(row=2, column=0, sticky=W + E)
    ParamEntry3 = StringVar()
    ParamEntryE3 = ttk.Entry(frame_baseprm, textvariable=ParamEntry3, width=5)
    ParamEntryE3.grid(row=2, column=1, sticky=W + E)
    ParamEntryE3.insert(END, "0.0")

    Param4 = StringVar()
    Param4.set(ExDict['拡大率'] + ' : ')
    ParamLabel4 = ttk.Label(frame_baseprm, textvariable=Param4)
    ParamLabel4.grid(row=3, column=0, sticky=W + E)
    ParamEntry4 = StringVar()
    ParamEntryE4 = ttk.Entry(frame_baseprm, textvariable=ParamEntry4, width=5)
    ParamEntryE4.grid(row=3, column=1, sticky=W + E)
    ParamEntryE4.insert(END, "100.0")

    Param5 = StringVar()
    Param5.set(ExDict['透明度'] + ' : ')
    ParamLabel5 = ttk.Label(frame_baseprm, textvariable=Param5)
    ParamLabel5.grid(row=4, column=0, sticky=W + E)
    ParamEntry5 = StringVar()
    ParamEntryE5 = ttk.Entry(frame_baseprm, textvariable=ParamEntry5, width=5)
    ParamEntryE5.grid(row=4, column=1, sticky=W + E)
    ParamEntryE5.insert(END, "0.0")

    Param7 = StringVar()
    Param7.set(ExDict['回転'] + ' : ')
    ParamLabel7 = ttk.Label(frame_baseprm, textvariable=Param7)
    ParamLabel7.grid(row=5, column=0, sticky=W + E)
    ParamEntry7 = StringVar()
    ParamEntryE7 = ttk.Entry(frame_baseprm, textvariable=ParamEntry7, width=5)
    ParamEntryE7.grid(row=5, column=1, sticky=W + E)
    ParamEntryE7.insert(END, "0.00")

    Param15 = StringVar()
    ParamCombo15 = ttk.Combobox(frame_baseprm, textvariable=Param15, state='readonly')
    ParamCombo15['values'] = list(BlendDict.keys())
    ParamCombo15.set(list(BlendDict.keys())[0])
    ParamCombo15.grid(row=6, column=0, pady=(0, 10), columnspan=2, sticky=W + E)

    Param6 = StringVar()
    Param6.set(ExDict['縦横比'] + ' : ')
    ParamLabel6 = ttk.Label(frame_baseprm, textvariable=Param6)
    ParamLabel6.grid(row=7, column=0, sticky=W + E)
    ParamEntry6 = StringVar()
    ParamEntryE6 = ttk.Entry(frame_baseprm, textvariable=ParamEntry6, width=5)
    ParamEntryE6.grid(row=7, column=1, sticky=W + E)
    ParamEntryE6.insert(END, "0.0")

    Param8 = StringVar()
    Param8.set(ExDict['X軸回転'] + ' : ')
    ParamLabel8 = ttk.Label(frame_baseprm, textvariable=Param8)
    ParamLabel8.grid(row=8, column=0, sticky=W + E)
    ParamEntry8 = StringVar()
    ParamEntryE8 = ttk.Entry(frame_baseprm, textvariable=ParamEntry8, width=5)
    ParamEntryE8.grid(row=8, column=1, sticky=W + E)
    ParamEntryE8.insert(END, "0.00")

    Param9 = StringVar()
    Param9.set(ExDict['Y軸回転'] + ' : ')
    ParamLabel9 = ttk.Label(frame_baseprm, textvariable=Param9)
    ParamLabel9.grid(row=9, column=0, sticky=W + E)
    ParamEntry9 = StringVar()
    ParamEntryE9 = ttk.Entry(frame_baseprm, textvariable=ParamEntry9, width=5)
    ParamEntryE9.grid(row=9, column=1, sticky=W + E)
    ParamEntryE9.insert(END, "0.00")

    Param10 = StringVar()
    Param10.set(ExDict['Z軸回転'] + ' : ')
    ParamLabel10 = ttk.Label(frame_baseprm, textvariable=Param10)
    ParamLabel10.grid(row=10, column=0, sticky=W + E)
    ParamEntry10 = StringVar()
    ParamEntryE10 = ttk.Entry(frame_baseprm, textvariable=ParamEntry10, width=5)
    ParamEntryE10.grid(row=10, column=1, sticky=W + E)
    ParamEntryE10.insert(END, "0.00")

    Param11 = StringVar()
    Param11.set(ExDict['中心X'] + ' : ')
    ParamLabel11 = ttk.Label(frame_baseprm, textvariable=Param11)
    ParamLabel11.grid(row=11, column=0, sticky=W + E)
    ParamEntry11 = StringVar()
    ParamEntryE11 = ttk.Entry(frame_baseprm, textvariable=ParamEntry11, width=5)
    ParamEntryE11.grid(row=11, column=1, sticky=W + E)
    ParamEntryE11.insert(END, "0.0")

    Param12 = StringVar()
    Param12.set(ExDict['中心Y'] + ' : ')
    ParamLabel12 = ttk.Label(frame_baseprm, textvariable=Param12)
    ParamLabel12.grid(row=12, column=0, sticky=W + E)
    ParamEntry12 = StringVar()
    ParamEntryE12 = ttk.Entry(frame_baseprm, textvariable=ParamEntry12, width=5)
    ParamEntryE12.grid(row=12, column=1, sticky=W + E)
    ParamEntryE12.insert(END, "0.0")

    Param13 = StringVar()
    Param13.set(ExDict['中心Z'] + ' : ')
    ParamLabel13 = ttk.Label(frame_baseprm, textvariable=Param13)
    ParamLabel13.grid(row=13, column=0, sticky=W + E)
    ParamEntry13 = StringVar()
    ParamEntryE13 = ttk.Entry(frame_baseprm, textvariable=ParamEntry13, width=5)
    ParamEntryE13.grid(row=13, column=1, sticky=W + E)
    ParamEntryE13.insert(END, "0.0")

    ParamEntryE6['state'] = 'disable'
    ParamEntryE8['state'] = 'disable'
    ParamEntryE9['state'] = 'disable'
    ParamEntryE10['state'] = 'disable'
    ParamEntryE11['state'] = 'disable'
    ParamEntryE12['state'] = 'disable'
    ParamEntryE13['state'] = 'disable'

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
