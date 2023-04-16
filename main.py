#####################################################################################
#               RPP to EXO ver 2.01                                                 #
#                                                                       2023/04/13  #
#       Original Written by Maimai (@Maimai22015/YTPMV.info)                        #
#       Forked by Garech (@Garec_)                                                  #
#                                                                                   #
#       協力：SHI(@sbt54864666)                                                      #
#####################################################################################

import configparser
import os
import subprocess
import threading
from functools import partial
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
from tkinterdnd2 import *

import rpp2exo
from rpp2exo import Rpp, Exo
from rpp2exo.dict import EffDict, XDict, BlendDict

rpp_cl = Rpp('')
mydict = rpp2exo.dict.mydict

print('★RPPtoEXO実行中はこのコンソール画面を閉じないでください。')


def patched_error(msg):
    if mydict['PatchExists']:
        print('(patch.aul未導入 かつ 拡張編集 Ver0.92以下 の環境では、' + msg + ')')
        return
    rsp = messagebox.showwarning(
        "警告", msg + '\nEXOのインポート後、個別に設定してください。',
        detail='patch.aul導入済 / 拡張編集 Ver0.93rc1 の環境の方はこのエラーを修正しているため、"キャンセル"をクリックしてください。',
        type='okcancel')
    if rsp == 'cancel':
        print('★キャンセルがクリックされました。今後拡張編集のバグによるEXO生成エラーはコンソール上に通知されます。')
        mydict['PatchExists'] = 1
        write_cfg("1", "patch_exists", "Param")


def main():
    f5_run['state'] = 'disable'
    root['cursor'] = 'watch'
    f5_run["text"] = "実行中 (1/3)"

    try:
        exo_cl = Exo(mydict)
        if f11_cb4.get():
            rpp_cl.start_pos = float(f11_c2.get())
            rpp_cl.end_pos = float(f11_c3.get()) if f11_c3.get() != '' else 99999.0
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

        f5_run["text"] = "実行中 (2/3)"
        file_fps = exo_cl.fetch_fps(file_path)

        f5_run["text"] = "実行中 (3/3)"
        end3 = exo_cl.make_exo(rpp_cl.objDict, file_path, file_fps)
        end = end1 | end3

    except PermissionError as e:
        if e.filename.lower().endswith('.exo'):
            messagebox.showerror("エラー", "上書き先のEXOファイルが開かれているか、読み取り専用になっています。")
        else:
            messagebox.showerror("エラー", "下記ファイルの読込み権限がありません。\n" + e.filename)
    except FileNotFoundError as e:
        messagebox.showerror("エラー", "下記パス内のファイル/フォルダは存在しませんでした。\n" + e.filename)
    except UnicodeEncodeError as e:
        # reasonに該当行の文字列、objectに該当文字を格納
        messagebox.showerror("エラー", "AviUtl上で使用できない文字がパス名に含まれています。\n"
                                    "パス名に含まれる該当文字を削除し、再度実行し直してください。\n\n"
                             + e.reason + '    "' + e.object + '"')
    except rpp2exo.exo.LoadFilterFileError:
        messagebox.showerror("エラー", "エイリアス / 効果ファイルが不正です。詳しくはREADMEを参照してください。")
    except rpp2exo.exo.ItemNotFoundError:
        messagebox.showerror("エラー", "出力範囲内に変換対象のアイテムが見つかりませんでした。\n"
                                    "出力対象トラック、時間選択の設定を見直してください。")
    except Exception as e:
        messagebox.showerror("エラー", "予期せぬエラーが発生しました。不正なRPPファイルの可能性があります。\n"
                                    "最新バージョンのREAPERをインストールし、RPPファイルを再保存して再試行してください。\n"
                                    "それでも症状が改善しない場合、コンソールのエラー内容を報告頂けると幸いです。")
        raise e
    else:
        if "exist_mode2" in end:
            print("★警告: RPP内にセクション・逆再生付きのアイテムが存在したため、該当アイテムが正常に生成できませんでした。")
            for i, detail in enumerate(end["exist_mode2"]):
                print("    " + detail)
                if i == 4:
                    print("    その他 " + str(len(end["exist_mode2"]) - 5) + "個")
                    break

        if "exist_stretch_marker" in end:
            print("★警告: RPP内に伸縮マーカーが設定されているアイテムが存在したため、該当アイテムが正常に生成できませんでした。")
            for i, detail in enumerate(end["exist_stretch_marker"]):
                print("    " + detail)
                if i == 4:
                    print("    その他 " + str(len(end["exist_stretch_marker"]) - 5) + "個")
                    break

        if "layer_over_100" in end:
            print("★警告: 出力処理時にEXOのレイヤー数が100を超えたため、正常に生成できませんでした。")

        if end == {}:
            ret = messagebox.askyesno("正常終了", "正常に生成されました。\n保存先のフォルダを開きますか？")
        else:
            ret = messagebox.askyesno("警告", "一部アイテムが正常に生成できませんでした。詳細はコンソールをご覧ください。\n保存先のフォルダを開きますか？", icon="warning")

        if ret:
            path = os.path.dirname(mydict["EXOPath"]).replace('/', '\\')
            if path == "":
                path = os.getcwd()
            subprocess.Popen(['explorer', path], shell=True)
    finally:
        print('--------------------------------------------------------------------------')
        f5_run['state'] = 'normal'
        root['cursor'] = 'arrow'
        f5_run["text"] = "実行"


def read_cfg():  # 設定読み込み
    config_ini_path = "config.ini"
    if os.path.exists(config_ini_path):
        config_ini = configparser.ConfigParser()
        config_ini.read(config_ini_path, encoding='utf-8')
        mydict["RPPLastDir"] = config_ini.get("Directory", "RPPDir")
        mydict["EXOLastDir"] = config_ini.get("Directory", "EXODir")
        mydict["SrcLastDir"] = config_ini.get("Directory", "SrcDir")
        mydict["AlsLastDir"] = config_ini.get("Directory", "AlsDir")
        mydict['PatchExists'] = int(config_ini.get("Param", "patch_exists"))
    return 0


def write_cfg(value, setting_type, section):  # 設定保存
    config_ini_path = "config.ini"
    if os.path.exists(config_ini_path):
        config_ini = configparser.ConfigParser()
        config_ini.read(config_ini_path, encoding='utf-8')
        if section == "Directory":
            value = os.path.dirname(value)
        config_ini.set(section, setting_type, value)
        with open('config.ini', 'w', encoding='utf-8') as file:
            config_ini.write(file)


def slct_rpp():  # 参照ボタン
    filetype = [("REAPERプロジェクトファイル", "*.rpp")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["RPPLastDir"], title="RPPファイルを選択")
    if filepath != '':
        f1_sv1.set(filepath)
        write_cfg(filepath, "RPPDir", "Directory")
        set_rppinfo()


def slct_source():  # 素材選択
    filetype = [("動画ファイル", "*")] if f3_mode.get() == 1 else [("画像ファイル", "*")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["SrcLastDir"], title="参照する素材ファイルの選択")
    if filepath != '':
        f3_sv4.set(filepath)
        write_cfg(filepath, "SrcDir", "Directory")


def slct_filter_cfg_file():  # 効果設定ファイル読み込み
    filetype = [("AviUtl エイリアス/効果ファイル", "*.exa;*.exc;*.exo;*.txt"), ("すべてのファイル", "*.*")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["AlsLastDir"], title="参照するエイリアス/効果ファイルの選択")
    if filepath != '':
        f9_sv2.set(filepath)
        write_cfg(filepath, "AlsDir", "Directory")


def save_exo():  # EXO保存ボタン
    filetype = [("AviUtlオブジェクトファイル", "*.exo")]
    filepath = filedialog.asksaveasfilename(
        initialdir=mydict["EXOLastDir"], title="EXOファイル保存場所の選択", filetypes=filetype)
    if filepath != '':
        if not filepath.endswith(".exo"):
            filepath += ".exo"
        f2_sv2.set(filepath)
        write_cfg(filepath, "EXODir", "Directory")


def set_rppinfo(reload=0):  # RPP内の各トラックの情報を表示する
    filepath = f1_e1.get().replace('"', '')  # パスをコピペした場合のダブルコーテーションを削除
    if filepath == f1_sv1_temp.get() and reload == 0:
        return True
    f1_sv1_temp.set(filepath)
    f11_ct1.delete(*f11_ct1.get_children())
    f11_ct1.insert("", "end", text="＊全トラック", iid="all", open=True)
    f11_ct1.change_state("all", 'tristate')
    f11_ct1.yview(0)

    if f11_cb4.get():
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
            f11_ct1.insert("all", "end", text=prefix + "└" + k, iid=str(iid))

            # 親トラックがミュート状態の場合、こっそりゼロ幅スペース(​)を挿入して子トラックが後から区別できるように
            if "​" not in k and "​" not in prefix:
                f11_ct1.change_state(str(iid), 'checked')
            if tree[k]:
                iid = insert_treedict(tree[k], prefix + "　", iid) if "​" not in k else \
                    insert_treedict(tree[k], prefix + "　​", iid)  # フォルダ開始部の場合、prefixを追加して再帰呼び出し
        else:
            f11_ct1.insert("all", "end", text=prefix + "├" + k, iid=str(iid))
            if "​" not in k and "​" not in prefix:
                f11_ct1.change_state(str(iid), 'checked')
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
    hLabel[mydict["EffCount"] + mydict["EffNum"]].set(f5_sv1.get())
    b = ttk.Label(
        frame6, textvariable=hLabel[mydict["EffCount"] + mydict["EffNum"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=0)
    hLabel2.append(b)

    # 始点終点ラベル
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set("始点")
    b = ttk.Label(
        frame6, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=1)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set("終点")
    b = ttk.Label(
        frame6, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=3)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set("設定")
    b = ttk.Label(
        frame6, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=4)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1

    mydict["Effect"].append([])
    mydict["Effect"][mydict["EffCount"]].append(f5_sv1.get())
    mydict["EffCount"] += 1
    # EffDict[v2.get()]回分ループ
    for n in range(len(EffDict[f5_sv1.get()])):
        if EffDict[f5_sv1.get()][n][-1] == -1:
            hCheckBox.append(StringVar())
            hCheckBox[mydict["EffCbNum"]].set(0)
            hCheckBoxCb.append(ttk.Checkbutton(
                frame6,
                padding=0,
                text=EffDict[f5_sv1.get()][n][0],
                onvalue=1,
                offvalue=0,
                variable=hCheckBox[mydict["EffCbNum"]]))
            hCheckBoxCb[mydict["EffCbNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=1, sticky=W)
            mydict["EffCbNum"] += 1
        elif EffDict[f5_sv1.get()][n][-1] == -2:  # Entryだけの項目(めっちゃ強引な実装だから全体的に書き直したい…)
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]
                   ].set(EffDict[f5_sv1.get()][n][0])
            b = ttk.Label(
                frame6, textvariable=hLabel[mydict["EffNum"] + mydict["EffCount"]])
            b.grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                   column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(
                frame6, textvariable=hEntryS[mydict["EffNum"]], width=5))
            hEntrySE[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=1, columnspan=4, sticky=W + E)
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[f5_sv1.get()][n][1])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(
                frame6, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set("移動なし")

            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(
                frame6, textvariable=hEntryE[mydict["EffNum"]], width=5))

            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(
                frame6, textvariable=hEntryConf[mydict["EffNum"]], width=5))

            mydict["EffNum"] += 1
        else:
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]
                   ].set(EffDict[f5_sv1.get()][n][0])
            b = ttk.Label(
                frame6, textvariable=hLabel[mydict["EffNum"] + mydict["EffCount"]])
            b.grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                   column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(
                frame6, textvariable=hEntryS[mydict["EffNum"]], width=5))
            hEntrySE[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=1, padx=5)
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[f5_sv1.get()][n][1])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(
                frame6, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set("移動なし")
            hEntryXCb[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=2, padx=5)

            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(
                frame6, textvariable=hEntryE[mydict["EffNum"]], width=5))
            hEntryEE[mydict["EffNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=3, padx=5)

            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(
                frame6, textvariable=hEntryConf[mydict["EffNum"]], width=5))
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
    mydict["RPPPath"] = f1_sv1.get().replace('"', '')
    if f2_sv2.get().replace('"', '').lower().endswith(".exo") or f2_sv2.get().replace('"', '') == "":
        mydict["EXOPath"] = f2_sv2.get().replace('"', '')
    else:
        mydict["EXOPath"] = f2_sv2.get().replace('"', '') + ".exo"
    mydict["OutputType"] = f3_mode.get()
    mydict["SrcPath"] = f3_sv4.get().replace('"', '').replace('/', '\\')
    mydict["EffPath"] = f9_sv2.get().replace('"', '')
    mydict["IsAlpha"] = f4_iv1.get()
    mydict["IsLoop"] = f4_iv2.get()
    mydict["SrcPosition"] = f4_sv4.get()
    mydict["SrcRate"] = f4_sv2.get()
    mydict["fps"] = f7_sv1.get()
    mydict["ScriptText"] = f10_tx1.get('1.0', 'end-1c')
    mydict["IsFlipHEvenObj"] = f11_iv1.get()
    mydict["SepLayerEvenObj"] = f11_iv3.get()
    mydict["NoGap"] = f11_iv2.get()
    mydict["clipping"] = f4_iv3.get()
    mydict["IsExSet"] = f4_iv4.get()
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
    mydict["SceneIdx"] = int(f3_sv2.get() or 0)
    mydict["Blend"] = BlendDict[ParamCombo15.get()]
    mydict["Track"] = f11_ct1.get_checked()

    trackbar_error = False

    if mydict["RPPPath"] == "":
        messagebox.showinfo("エラー", "読み込むRPPを入力してください。")
        return 0
    elif mydict["EXOPath"] == "":
        messagebox.showinfo("エラー", "EXOの保存先パスを入力してください。")
        return 0
    elif mydict["fps"] == "":
        messagebox.showinfo("エラー", "FPSの値を入力してください。")
        return 0
    elif not mydict["Track"]:
        messagebox.showinfo("エラー", "出力するトラックを選択してください。")
        return 0

    if (mydict["SceneIdx"] <= 0 or mydict["SceneIdx"] >= 50) and mydict["OutputType"] == 4:
        messagebox.showinfo("エラー", "正しいシーン番号を入力してください。（範囲 : 1 ~ 49）")
        return 0
    elif mydict["SceneIdx"] != 1 and mydict["OutputType"] == 4:
        patched_error('AviUtl本体のバグの影響により、シーン番号は反映されません。')

    # トラックバーエラーの検知
    if (-1 < float(mydict["X"]) < 0 or -1 < float(mydict["Y"]) < 0 or -1 < float(mydict["Z"]) < 0 or
            -1 < float(mydict["Size"]) < 0 or -1 < float(mydict["Alpha"]) < 0 or -1 < float(mydict["Ratio"]) < 0 or
            -1 < float(mydict["Rotation"]) < 0 or -1 < float(mydict["XRotation"]) < 0 or
            -1 < float(mydict["YRotation"]) < 0 or -1 < float(mydict["ZRotation"]) < 0 or
            -1 < float(mydict["XCenter"]) < 0 or -1 < float(mydict["YCenter"]) < 0 or -1 < float(
                mydict["ZCenter"]) < 0 or
            -1 < float(mydict["Blend"]) < 0 or -1 < float(mydict["SrcRate"]) < 0):
        patched_error('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。')
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
                if hEntryX[runcount].get() == "移動なし":  # 移動なしの場合
                    if not trackbar_error and EffDict[mydict["Effect"][i][0]][x][-1] != -2 and \
                            -1 < float(hEntryS[runcount].get()) < 0:
                        patched_error('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。')
                        trackbar_error = True
                    eff = [EffDict[mydict["Effect"][i][0]][x][0],
                           str(hEntryS[runcount].get())]
                    mydict["Effect"][i].append(eff)
                else:  # 移動ありの場合
                    if str(hEntryE[runcount].get()) == "":
                        messagebox.showinfo("エラー", "追加フィルタ効果の終点が入力されていません。")
                        return 0
                    if not trackbar_error and EffDict[mydict["Effect"][i][0]][x][-1] != -2 and \
                            (-1 < float(hEntryS[runcount].get()) < 0 or -1 < float(hEntryE[runcount].get()) < 0):
                        patched_error('AviUtl本体のバグの影響により、トラックバーの-1越0未満 ( -0.* ) の値は反映されません。')
                        trackbar_error = True
                    eff = [EffDict[mydict["Effect"][i][0]][x][0],
                           str(hEntryS[runcount].get()) + "," + str(hEntryE[runcount].get()) + "," + str(
                               XDict[hEntryX[runcount].get()])]
                    if XDict[hEntryX[runcount].get()] != "":
                        eff[1] += str(hEntryConf[runcount].get())
                        if not str(XDict[hEntryX[runcount].get()]).isascii():
                            patched_error("AviUtl本体のバグの影響により、移動の設定の値は反映されません。")
                    if XDict[hEntryX[runcount].get()] != "" and hEntryConf[runcount].get() != "":
                        eff = [EffDict[mydict["Effect"][i][0]][x][0],
                               str(hEntryS[runcount].get()) + "," + str(hEntryE[runcount].get()) + "," + str(
                                   XDict[hEntryX[runcount].get()]) + "," + str(hEntryConf[runcount].get())]
                    mydict["Effect"][i].append(eff)
                runcount += 1
            elif EffDict[mydict["Effect"][i][0]][x][-1] == -1:  # チェックボックスの場合
                eff = [EffDict[mydict["Effect"][i][0]][x][0],
                       str(hCheckBox[runcountcb].get())]
                mydict["Effect"][i].append(eff)
                runcountcb += 1

    thread = threading.Thread(target=main)
    thread.start()


def mode_command():  # 「追加対象」変更時の状態切り替え
    if f3_mode.get() == 1 or f3_mode.get() == 2:  # 「素材」テキストボックス・参照ボタン
        f3_b1['state'] = 'enable'
        f3_e2['state'] = 'enable'
    else:
        f3_b1['state'] = 'disable'
        f3_e2['state'] = 'disable'

    if f3_mode.get() == 4:  # シーン番号
        f3_e1['state'] = 'enable'
    else:
        f3_e1['state'] = 'disable'

    if f3_mode.get() == 1:  # アルファチャンネルを読み込む
        f4_cb1['state'] = 'enable'
    else:
        f4_cb1['state'] = 'disable'

    if f3_mode.get() == 1 or f3_mode.get() == 4:  # ループ再生・再生速度・再生位置
        f4_cb2['state'] = 'enable'
        f4_e1['state'] = 'enable'
        f4_e2['state'] = 'enable'

    else:
        f4_cb2['state'] = 'disable'
        f4_e1['state'] = 'disable'
        f4_e2['state'] = 'disable'


def advdraw_command():  # 「拡張描画」変更時の状態切り替え
    if f4_iv4.get() == 0:
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
    if f11_cb4.get():
        f11_c1['state'] = 'readonly'
        f11_c2['state'] = 'enable'
        f11_c3['state'] = 'enable'
        time_ps_list, marker_list = rpp_cl.load_marker_list()

        if len(time_ps_list) >= 2:
            f11_sv1.set(time_ps_list[1])
        else:
            f11_sv1.set('-')
        f11_c1['values'] = time_ps_list
        f11_c2['values'] = marker_list
        f11_c3['values'] = marker_list
        set_time(None)
    else:
        f11_c1['state'] = 'disable'
        f11_c2['state'] = 'disable'
        f11_c3['state'] = 'disable'


def set_time(self):  # タイム選択ComboBoxのリストをリセットする
    if f11_sv1.get() == '-':
        f11_c2.set('0.0')
        f11_c3.set('99999.0')
    else:
        slct = f11_sv1.get()
        f11_c2.set(slct[slct.rfind('(') + 1:slct.rfind('~')])
        f11_c3.set(slct[slct.rfind('~') + 1:-1])


def set_time1(self):  # 上側のタイム選択ComboBox適用
    x = f11_sv2.get()
    f11_c2.set(x[x.rfind(':') + 2:])


def set_time2(self):  # 下側のタイム選択ComboBox適用
    x = f11_sv3.get()
    f11_c3.set(x[x.rfind(':') + 2:])


def drop_file(target, event):
    target.set(event.data[1:event.data.find('}')])


if __name__ == '__main__':
    read_cfg()
    # root
    root = TkinterDnD.Tk()
    root.title('RPPtoEXO v2.0')
    root.columnconfigure(1, weight=1)

    LFrame = ttk.Frame(root)
    LFrame.grid(row=0, column=0)
    CFrame = ttk.Frame(root)
    CFrame.grid(row=0, column=1)
    RFrame = ttk.Frame(root)
    RFrame.grid(row=0, column=2)
    # そのうちスクロールウィンドウに対応したい（やりかたがわからない）

    # ウィジェット変数名規則: [フレーム番号]_[ウィジェット頭文字][ウィジェット連番]     連番はフレームごとに設定
    # 変数名に迷ったらこれにすることにしました :-)

    # Frame1 RPP選択
    frame1 = ttk.Frame(LFrame, padding=5)
    frame1.grid(row=0, column=0, sticky=N)
    f1_b1 = ttk.Button(frame1, text='参照…', command=slct_rpp)
    f1_b1.grid(row=0, column=3)
    f1_s1 = StringVar()
    f1_s1.set('* RPP : ')
    f1_l1 = ttk.Label(frame1, textvariable=f1_s1)
    f1_l1.grid(row=0, column=0)

    f1_sv1 = StringVar()
    f1_sv1_temp = StringVar()
    f1_vc1 = root.register(set_rppinfo)
    f1_e1 = ttk.Entry(frame1, textvariable=f1_sv1, width=46, validate='focusout', validatecommand=f1_vc1)
    f1_e1.grid(row=0, column=1)
    f1_e1.drop_target_register(DND_FILES)
    f1_e1.dnd_bind("<<Drop>>", partial(drop_file, f1_sv1))
    f1_b2 = ttk.Button(frame1, text='↻', command=lambda: set_rppinfo(1), width=2)
    f1_b2.grid(row=0, column=2)

    # Frame2 EXO指定
    frame2 = ttk.Frame(LFrame, padding=5)
    frame2.grid(row=1, column=0)
    f2_b1 = ttk.Button(frame2, text='保存先…', command=save_exo)
    f2_b1.grid(row=1, column=3)
    f2_sv1 = StringVar()
    f2_sv1.set('* EXO : ')
    f2_l1 = ttk.Label(frame2, textvariable=f2_sv1)
    f2_l1.grid(row=1, column=0)
    f2_sv2 = StringVar()
    f2_e1 = ttk.Entry(frame2, textvariable=f2_sv2, width=50)
    f2_e1.grid(row=1, column=1)
    f2_e1.drop_target_register(DND_FILES)
    f2_e1.dnd_bind("<<Drop>>", partial(drop_file, f2_sv2))

    # frame3 追加対象オブジェクト・素材指定
    frame3 = ttk.Frame(LFrame, padding=5)
    frame3.grid(row=2, column=0)
    f3_mode = IntVar()
    f3_mode.set(1)

    f3_sv1 = StringVar()
    f3_sv1.set('追加対象 : ')
    f3_l1 = ttk.Label(frame3, textvariable=f3_sv1)
    f3_l1.grid(row=0, column=0, sticky=W)
    f3_r1 = ttk.Radiobutton(frame3, value=0, variable=f3_mode, text='自動検出(β)', command=mode_command)
    f3_r1.grid(row=0, column=1)
    f3_r2 = ttk.Radiobutton(frame3, value=1, variable=f3_mode, text='動画', command=mode_command)
    f3_r2.grid(row=0, column=2)
    f3_r3 = ttk.Radiobutton(frame3, value=2, variable=f3_mode, text='画像', command=mode_command)
    f3_r3.grid(row=0, column=3)
    f3_r4 = ttk.Radiobutton(frame3, value=3, variable=f3_mode, text='フィルタ', command=mode_command)
    f3_r4.grid(row=0, column=4)
    f3_r5 = ttk.Radiobutton(frame3, value=4, variable=f3_mode, text='シーン番号: ', command=mode_command)
    f3_r5.grid(row=0, column=5)
    f3_sv2 = StringVar()
    f3_e1 = ttk.Entry(frame3, textvariable=f3_sv2, width=3, state='disable')
    f3_e1.grid(row=0, column=6)

    f3_sv3 = StringVar()
    f3_sv3.set('素材 : ')
    f3_l2 = ttk.Label(frame3, textvariable=f3_sv3)
    f3_l2.grid(row=1, column=0, sticky=E)
    f3_sv4 = StringVar()
    f3_e2 = ttk.Entry(frame3, textvariable=f3_sv4, width=46)
    f3_e2.grid(row=1, column=1, columnspan=5, sticky=W)
    f3_e2.drop_target_register(DND_FILES)
    f3_e2.dnd_bind("<<Drop>>", partial(drop_file, f3_sv4))
    f3_b1 = ttk.Button(frame3, text='参照…', command=slct_source)
    f3_b1.grid(row=1, column=5, columnspan=2, sticky=E)

    # frame4  オブジェクト設定
    frame4 = ttk.Frame(LFrame, padding=1)
    frame4.grid(row=3, column=0)

    f4_sv1 = StringVar()
    f4_sv1.set('再生速度 : ')
    f4_l1 = ttk.Label(frame4, textvariable=f4_sv1)
    f4_l1.grid(row=0, column=3, sticky=E, padx=(36, 0))
    f4_sv2 = StringVar()
    f4_e1 = ttk.Entry(frame4, textvariable=f4_sv2, width=10)
    f4_e1.grid(row=0, column=4, sticky=W + E)
    f4_e1.insert(END, "100.0")

    f4_sv3 = StringVar()
    f4_sv3.set('再生位置 : ')
    f4_l2 = ttk.Label(frame4, textvariable=f4_sv3)
    f4_l2.grid(row=1, column=3, sticky=E, padx=(36, 0))
    f4_sv4 = StringVar()
    f4_e2 = ttk.Entry(frame4, textvariable=f4_sv4, width=10)
    f4_e2.grid(row=1, column=4, sticky=W + E)
    f4_e2.insert(END, "1")

    f4_iv1 = IntVar()
    f4_iv1.set(0)
    f4_cb1 = ttk.Checkbutton(frame4, padding=5, text='アルファチャンネルを読み込む', onvalue=1, offvalue=0, variable=f4_iv1)
    f4_cb1.grid(row=1, column=0, sticky=W)
    f4_iv2 = IntVar()
    f4_iv2.set(0)
    f4_cb2 = ttk.Checkbutton(frame4, padding=5, text='ループ再生', onvalue=1, offvalue=0, variable=f4_iv2)
    f4_cb2.grid(row=1, column=1, sticky=W)
    f4_iv3 = IntVar()
    f4_iv3.set(0)
    f4_cb3 = ttk.Checkbutton(frame4, padding=5, text='上のオブジェクトでクリッピング', onvalue=1, offvalue=0, variable=f4_iv3)
    f4_cb3.grid(row=0, column=0, sticky=W)
    f4_iv4 = IntVar()
    f4_iv4.set(0)
    f4_cb4 = ttk.Checkbutton(frame4, padding=5, text='拡張描画', onvalue=1, offvalue=0, variable=f4_iv4,
                             command=advdraw_command)
    f4_cb4.grid(row=0, column=1, sticky=W)

    # Frame11 ソフト独自設定 / 時間選択 / トラック選択
    frame11 = ttk.Frame(LFrame, padding=10)
    frame11.grid(row=4, column=0)

    # v1 = IntVar()
    # v1.set(1)
    # cb1 = ttk.Checkbutton(frame4a, padding=5, text='トラック毎に\n設定を調整する', onvalue=1, offvalue=0, variable=v1)
    # cb1.grid(row=0, column=0, sticky=W)
    f11_iv1 = IntVar()
    f11_iv1.set(0)
    f11_cb1 = ttk.Checkbutton(frame11, padding=5, text='左右反転', onvalue=1, offvalue=0, variable=f11_iv1)
    f11_cb1.grid(row=1, column=0, sticky=W)
    f11_iv2 = IntVar()
    f11_iv2.set(0)
    f11_cb2 = ttk.Checkbutton(frame11, padding=5, text='隙間なく配置', onvalue=1, offvalue=0, variable=f11_iv2)
    f11_cb2.grid(row=2, column=0, sticky=W)
    f11_iv3 = IntVar()
    f11_iv3.set(0)
    f11_cb3 = ttk.Checkbutton(frame11, padding=5, text='偶数番目Objを\n別レイヤ配置', onvalue=1, offvalue=0, variable=f11_iv3)
    f11_cb3.grid(row=3, column=0, sticky=W)

    f11_cb4 = IntVar()
    f11_cb4.set(0)
    f11_cb5 = ttk.Checkbutton(frame11, padding=5, text='時間選択 (秒)', onvalue=1, offvalue=0, variable=f11_cb4,
                              command=change_time_cb)
    f11_cb5.grid(row=4, column=0, sticky=W)
    f11_sv1 = StringVar()
    f11_sv1.set('')
    f11_c1 = ttk.Combobox(frame11, textvariable=f11_sv1, width=10, state='disable')
    f11_c1.bind('<<ComboboxSelected>>', set_time)
    f11_c1.grid(row=5, column=0, padx=5, pady=3, sticky=W + E)

    f11_sv2 = StringVar()
    f11_sv2.set('')
    f11_c2 = ttk.Combobox(frame11, textvariable=f11_sv2, width=10, state='disable')
    f11_c2.bind('<<ComboboxSelected>>', set_time1)
    f11_c2.grid(row=6, column=0, padx=5, pady=3, sticky=W + E)
    f11_sv3 = StringVar()
    f11_sv3.set('')
    f11_c3 = ttk.Combobox(frame11, textvariable=f11_sv3, width=10, state='disable')
    f11_c3.bind('<<ComboboxSelected>>', set_time2)
    f11_c3.grid(row=7, column=0, padx=5, pady=3, sticky=W + E)

    f11_ct1 = CheckboxTreeview(frame11, show='tree', height=5)
    f11_ct1.grid(row=0, column=1, rowspan=8, sticky=N + S + E + W)
    f11_ct1.column("#0", width=300)
    ttk.Style().configure('Checkbox.Treeview', rowheight=15, borderwidth=1, relief='sunken', indent=0)

    f11_sb1 = Scrollbar(frame11, orient=VERTICAL, command=f11_ct1.yview)
    f11_sb1.grid(row=0, column=2, rowspan=8, sticky=N + S)
    f11_ct1['yscrollcommand'] = f11_sb1.set

    # Frame5 エフェクト追加/削除
    frame5 = ttk.Frame(LFrame, padding=5)
    frame5.grid(row=5, column=0)
    f5_sv1 = StringVar()
    f5_cb1 = ttk.Combobox(frame5, textvariable=f5_sv1, state='readonly')
    f5_cb1['values'] = list(EffDict.keys())
    f5_cb1.set("座標")
    f5_cb1.grid(row=0, column=0)
    f5_b1 = ttk.Button(frame5, text='+', command=add_filter_label)
    f5_b1.grid(row=0, column=1)
    f5_run = ttk.Button(frame5, text='効果のクリア', command=del_filter_label)
    f5_run.grid(row=0, column=2)

    # Frame9 効果をファイルから読み込む
    frame9 = ttk.Frame(LFrame, padding=5)
    frame9.grid(row=6, column=0)
    f9_b1 = ttk.Button(frame9, text='参照…', command=slct_filter_cfg_file)
    f9_b1.grid(row=0, column=2)
    f9_sv1 = StringVar()
    f9_sv1.set('エイリアス : ')
    f9_l1 = ttk.Label(frame9, textvariable=f9_sv1)
    f9_l1.grid(row=0, column=0, sticky=W)
    f9_sv2 = StringVar()
    f9_e1 = ttk.Entry(frame9, textvariable=f9_sv2, width=40)
    f9_e1.grid(row=0, column=1)
    f9_e1.drop_target_register(DND_FILES)
    f9_e1.dnd_bind("<<Drop>>", partial(drop_file, f9_sv2))

    # Frame10 スクリプト制御
    frame10 = ttk.Frame(LFrame, padding=10)
    frame10.grid(row=7, column=0)
    f10_sv1 = StringVar()
    f10_sv1.set('スクリプト制御 ')
    f10_l1 = ttk.Label(frame10, textvariable=f10_sv1)
    f10_l1.grid(row=0, column=0, sticky=W)
    f10_sv2 = StringVar()
    f10_tx1 = Text(frame10, width=50, height=10)
    f10_tx1.grid(row=0, column=1)

    # Frame6 エフェクトのパラメータ設定 (動的)
    frame6 = ttk.Frame(RFrame, padding=10, borderwidth=3)
    frame6.grid()

    # Frame8 基本パラメータ設定
    frame8 = ttk.Frame(CFrame, padding=10)
    frame8.grid(row=0, column=0)

    Param1 = StringVar()
    Param1.set('X : ')
    ParamLabel1 = ttk.Label(frame8, textvariable=Param1)
    ParamLabel1.grid(row=0, column=0, sticky=W + E)
    ParamEntry1 = StringVar()
    ParamEntryE1 = ttk.Entry(frame8, textvariable=ParamEntry1, width=5)
    ParamEntryE1.grid(row=0, column=1, sticky=W + E)
    ParamEntryE1.insert(END, "0.0")

    Param2 = StringVar()
    Param2.set('Y : ')
    ParamLabel2 = ttk.Label(frame8, textvariable=Param2)
    ParamLabel2.grid(row=1, column=0, sticky=W + E)
    ParamEntry2 = StringVar()
    ParamEntryE2 = ttk.Entry(frame8, textvariable=ParamEntry2, width=5)
    ParamEntryE2.grid(row=1, column=1, sticky=W + E)
    ParamEntryE2.insert(END, "0.0")

    Param3 = StringVar()
    Param3.set('Z : ')
    ParamLabel3 = ttk.Label(frame8, textvariable=Param3)
    ParamLabel3.grid(row=2, column=0, sticky=W + E)
    ParamEntry3 = StringVar()
    ParamEntryE3 = ttk.Entry(frame8, textvariable=ParamEntry3, width=5)
    ParamEntryE3.grid(row=2, column=1, sticky=W + E)
    ParamEntryE3.insert(END, "0.0")

    Param4 = StringVar()
    Param4.set('拡大率 : ')
    ParamLabel4 = ttk.Label(frame8, textvariable=Param4)
    ParamLabel4.grid(row=3, column=0, sticky=W + E)
    ParamEntry4 = StringVar()
    ParamEntryE4 = ttk.Entry(frame8, textvariable=ParamEntry4, width=5)
    ParamEntryE4.grid(row=3, column=1, sticky=W + E)
    ParamEntryE4.insert(END, "100.0")

    Param5 = StringVar()
    Param5.set('透明度 : ')
    ParamLabel5 = ttk.Label(frame8, textvariable=Param5)
    ParamLabel5.grid(row=4, column=0, sticky=W + E)
    ParamEntry5 = StringVar()
    ParamEntryE5 = ttk.Entry(frame8, textvariable=ParamEntry5, width=5)
    ParamEntryE5.grid(row=4, column=1, sticky=W + E)
    ParamEntryE5.insert(END, "0.0")

    Param7 = StringVar()
    Param7.set('回転 : ')
    ParamLabel7 = ttk.Label(frame8, textvariable=Param7)
    ParamLabel7.grid(row=5, column=0, sticky=W + E)
    ParamEntry7 = StringVar()
    ParamEntryE7 = ttk.Entry(frame8, textvariable=ParamEntry7, width=5)
    ParamEntryE7.grid(row=5, column=1, sticky=W + E)
    ParamEntryE7.insert(END, "0.00")

    Param15 = StringVar()
    ParamCombo15 = ttk.Combobox(frame8, textvariable=Param15, state='readonly')
    ParamCombo15['values'] = list(BlendDict.keys())
    ParamCombo15.set("通常")
    ParamCombo15.grid(row=6, column=0, pady=(0, 10), columnspan=2, sticky=W + E)

    Param6 = StringVar()
    Param6.set('縦横比 : ')
    ParamLabel6 = ttk.Label(frame8, textvariable=Param6)
    ParamLabel6.grid(row=7, column=0, sticky=W + E)
    ParamEntry6 = StringVar()
    ParamEntryE6 = ttk.Entry(frame8, textvariable=ParamEntry6, width=5)
    ParamEntryE6.grid(row=7, column=1, sticky=W + E)
    ParamEntryE6.insert(END, "0.0")

    Param8 = StringVar()
    Param8.set('X軸回転 : ')
    ParamLabel8 = ttk.Label(frame8, textvariable=Param8)
    ParamLabel8.grid(row=8, column=0, sticky=W + E)
    ParamEntry8 = StringVar()
    ParamEntryE8 = ttk.Entry(frame8, textvariable=ParamEntry8, width=5)
    ParamEntryE8.grid(row=8, column=1, sticky=W + E)
    ParamEntryE8.insert(END, "0.00")

    Param9 = StringVar()
    Param9.set('Y軸回転 : ')
    ParamLabel9 = ttk.Label(frame8, textvariable=Param9)
    ParamLabel9.grid(row=9, column=0, sticky=W + E)
    ParamEntry9 = StringVar()
    ParamEntryE9 = ttk.Entry(frame8, textvariable=ParamEntry9, width=5)
    ParamEntryE9.grid(row=9, column=1, sticky=W + E)
    ParamEntryE9.insert(END, "0.00")

    Param10 = StringVar()
    Param10.set('Z軸回転 : ')
    ParamLabel10 = ttk.Label(frame8, textvariable=Param10)
    ParamLabel10.grid(row=10, column=0, sticky=W + E)
    ParamEntry10 = StringVar()
    ParamEntryE10 = ttk.Entry(frame8, textvariable=ParamEntry10, width=5)
    ParamEntryE10.grid(row=10, column=1, sticky=W + E)
    ParamEntryE10.insert(END, "0.00")

    Param11 = StringVar()
    Param11.set('中心X : ')
    ParamLabel11 = ttk.Label(frame8, textvariable=Param11)
    ParamLabel11.grid(row=11, column=0, sticky=W + E)
    ParamEntry11 = StringVar()
    ParamEntryE11 = ttk.Entry(frame8, textvariable=ParamEntry11, width=5)
    ParamEntryE11.grid(row=11, column=1, sticky=W + E)
    ParamEntryE11.insert(END, "0.0")

    Param12 = StringVar()
    Param12.set('中心Y : ')
    ParamLabel12 = ttk.Label(frame8, textvariable=Param12)
    ParamLabel12.grid(row=12, column=0, sticky=W + E)
    ParamEntry12 = StringVar()
    ParamEntryE12 = ttk.Entry(frame8, textvariable=ParamEntry12, width=5)
    ParamEntryE12.grid(row=12, column=1, sticky=W + E)
    ParamEntryE12.insert(END, "0.0")

    Param13 = StringVar()
    Param13.set('中心Z : ')
    ParamLabel13 = ttk.Label(frame8, textvariable=Param13)
    ParamLabel13.grid(row=13, column=0, sticky=W + E)
    ParamEntry13 = StringVar()
    ParamEntryE13 = ttk.Entry(frame8, textvariable=ParamEntry13, width=5)
    ParamEntryE13.grid(row=13, column=1, sticky=W + E)
    ParamEntryE13.insert(END, "0.0")

    ParamEntryE6['state'] = 'disable'
    ParamEntryE8['state'] = 'disable'
    ParamEntryE9['state'] = 'disable'
    ParamEntryE10['state'] = 'disable'
    ParamEntryE11['state'] = 'disable'
    ParamEntryE12['state'] = 'disable'
    ParamEntryE13['state'] = 'disable'

    # Frame7実行
    frame7 = ttk.Frame(LFrame, padding=(0, 5))
    frame7.grid(row=8, column=0)
    f7_s1 = StringVar()
    f7_s1.set('* FPS : ')
    f7_l1 = ttk.Label(frame7, textvariable=f7_s1)
    f7_l1.grid(row=0, column=0, sticky=W + E)
    f7_sv1 = StringVar()
    f7_e1 = ttk.Entry(frame7, textvariable=f7_sv1, width=10)
    f7_e1.grid(row=0, column=1, sticky=W + E, padx=10)
    f7_e1.insert(END, "")
    f5_run = ttk.Button(frame7, text='実行', command=run)
    f5_run.grid(row=0, column=2)

    root.mainloop()
