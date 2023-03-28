#####################################################################################
#               RPP to EXO ver 2.00 b0.2                                            #
#                                                                       2022/07/11  #
#       Written by Maimai (@Maimai22015/YTPMV.info)                                 #
#       Forked by Garech (@Garec_)                                                  #
#                                                                                   #
#       協力：SHI(@sbt54864666), Garech(@Garec_)                                    #
#####################################################################################

import binascii
import configparser
import os
import subprocess
import threading
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from ttkwidgets import CheckboxTreeview

from rpp2exo import Rpp, Exo, LoadFilterFileError
from rpp2exo.dict import EffDict, XDict, BlendDict

# やりたいこと
# 素材自動検出のとき、ソースファイル（の再生位置）によって参照すべきソースを変えるGUI・機能の作成
# エフェクト効果の表記をAviUtlのUI寄りにし、更に親しみやすい操作にできるようにしたい
# 移動方法やスクリプトなどをAviUtlのフォルダから読み取って設定できるようにする機能
# Google Colabにそのまま引き継げるような仕組みづくり
# GUIの表記を英語にも対応し、多言語にも対応しやすいようにしたい
# ソースコードのクラス化・ファイル分割

rpp_cl = Rpp('')
patch_exists = 0

mydict = {
    # 基本設定
    "fps": 60,
    "RPPPath": "test.rpp",
    "EXOPath": "test.exo",
    "SrcPath": "C:\\Users\\USER\\Documents\\ytpmv_script\\movie.mp4",  # ファイルパス。絶対パスが必要。
    "SrcPosition": 1,  # 再生位置
    "SrcRate": 100.0,  # 再生速度
    "IsAlpha": 0,  # アルファチャンネルを読み込む
    "IsLoop": 0,  # ループ再生
    "X": 0.0,  # x座標
    "Y": 0.0,  # y座標
    "Z": 0.0,  # z座標
    "Size": 100.0,  # 拡大率
    "Rotation": 0.0,  # 回転
    "Alpha": 0.0,
    "Blend": 0,  # 合成モード

    "clipping": 0,
    "SceneIdx": 0,

    # 拡張描画
    "XRotation": 0.00,
    "YRotation": 0.00,
    "ZRotation": 0.00,
    "XCenter": 0.0,
    "YCenter": 0.0,
    "ZCenter": 0.0,

    # エフェクト設定 SettingEffで追加する。
    "Effect": [
        #   ["EffName",["ConfName1","Conf"],["ConfName2","Conf"]],
    ],
    "EffNum": 0,  # 現時点で追加されているパラメータ数（GUI用）
    "EffCount": 0,  # エフェクト数（GUI用）
    "EffCount2": 0,
    "EffCbNum": 0,  # パラメータ  チェックボックスの数
    "ScriptText": '',

    # 独自設定
    "IsFlipHEvenObj": 0,  # 偶数オブジェクトを左右反転するか
    "SepLayerEvenObj": 0,  # 偶数オブジェクトを別レイヤ―に配置するか
    "NoGap": 0,  # オブジェクト間の隙間を埋めるか
    "OutputType": 0,  # 1=動画  2=画像  3=フィルタ  4=シーン  として出力
    "IsExSet": 0,  # 拡張描画を有効にするか
    "AutoSrc": 0,  # 素材自動検出が有効か

    # 設定
    "RPPLastDir": os.path.abspath(os.path.dirname(__file__)),
    "EXOLastDir": os.path.abspath(os.path.dirname(__file__)),
    "SrcLastDir": os.path.abspath(os.path.dirname(__file__)),
    "AlsLastDir": os.path.abspath(os.path.dirname(__file__)),

}


def warn_print(msg):
    print('\033[32m\033[4m' + str(msg) + '\033[0m')


def patched_error(msg):
    global patch_exists
    if patch_exists:
        warn_print('(patch.aul未導入 かつ 拡張編集 Ver0.92以下 の環境では、' + msg + ')')
        return
    rsp = messagebox.showwarning(
        "警告", msg + '\nEXOのインポート後、個別に設定してください。',
        detail='patch.aul導入済 / 拡張編集 Ver0.93rc1 の環境の方はこのエラーを修正しているため、"キャンセル"をクリックしてください。',
        type='okcancel')
    if rsp == 'cancel':
        print('キャンセルがクリックされました。今後拡張編集のバグによるEXO生成エラーはコンソール上に通知されます。')
        patch_exists = 1
        write_cfg("1", "patch_exists", "Param")


def main():
    button6['state'] = 'disable'
    root['cursor'] = 'watch'
    button6["text"] = "実行中 (1/3)"

    try:
        exo_cl = Exo(mydict)
        if slct_time.get():
            rpp_cl.start_pos = float(time1_combo.get())
            rpp_cl.end_pos = float(time2_combo.get()) if time2_combo.get() != '' else 99999.0
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

        button6["text"] = "実行中 (2/3)"
        file_fps = exo_cl.fetch_fps(file_path)

        button6["text"] = "実行中 (3/3)"
        end3 = exo_cl.make_exo(rpp_cl.objDict, file_path, file_fps)
        end = end1 | end3

    except PermissionError as e:
        if e.filename.lower().endswith('.exo'):
            messagebox.showerror("エラー", "EXOファイルへの出力に失敗しました。\n上書き先のEXOファイルが開かれているか、読み取り専用になっています。")
        else:
            messagebox.showerror("エラー", "EXOファイルへの出力に失敗しました。\n下記ファイルの読込み権限がありません。\n" + e.filename)
    except FileNotFoundError as e:
        messagebox.showerror("エラー", "EXOファイルへの出力に失敗しました。\n下記パスのファイルは見つかりませんでした。\n" + e.filename)
    except UnicodeEncodeError as e:
        # reasonに該当行の文字列、objectに該当文字を格納
        messagebox.showerror("エラー", "EXOファイルへの出力に失敗しました。\nAviUtl上で使用できない文字がパス名に含まれています。\n"
                                    "パス名に含まれる該当文字を削除し、再度実行し直してください。\n\n"
                             + e.reason + '    "' + e.object + '"')
    except LoadFilterFileError:
        messagebox.showerror("エラー", "EXOファイルへの出力に失敗しました。\n効果ファイルが不正です。詳しくはREADMEを参照してください。")
    else:
        if "exist_mode2" in end:
            warn_print("警告: RPP内にセクション・逆再生付きのアイテムが存在したため、該当アイテムが正常に生成できませんでした。")
            for i, detail in enumerate(end["exist_mode2"]):
                warn_print("    " + detail)
                if i == 4:
                    warn_print("    その他 " + str(len(end["exist_mode2"]) - 5) + "個")
                    break

        if "exist_stretch_marker" in end:
            warn_print("警告: RPP内に伸縮マーカーが設定されているアイテムが存在したため、該当アイテムが正常に生成できませんでした。")
            for i, detail in enumerate(end["exist_stretch_marker"]):
                warn_print("    " + detail)
                if i == 4:
                    warn_print("    その他 " + str(len(end["exist_stretch_marker"]) - 5) + "個")
                    break

        if "layer_over_100" in end:
            warn_print("警告: 出力処理時にEXOのレイヤー数が100を超えたため、正常に生成できませんでした。")

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
        button6['state'] = 'normal'
        root['cursor'] = 'arrow'
        button6["text"] = "実行"


def read_cfg():  # 設定読み込み
    config_ini_path = "config.ini"
    if os.path.exists(config_ini_path):
        config_ini = configparser.ConfigParser()
        config_ini.read(config_ini_path, encoding='utf-8')
        mydict["RPPLastDir"] = config_ini.get("Directory", "RPPDir")
        mydict["EXOLastDir"] = config_ini.get("Directory", "EXODir")
        mydict["SrcLastDir"] = config_ini.get("Directory", "SrcDir")
        mydict["AlsLastDir"] = config_ini.get("Directory", "AlsDir")
        global patch_exists
        patch_exists = int(config_ini.get("Param", "patch_exists"))
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
        file1.set(filepath)
        write_cfg(filepath, "RPPDir", "Directory")
        set_rppinfo()


def slct_source():  # 素材選択
    filetype = [("動画ファイル", "*")] if trgt_radio.get() == 1 else [("画像ファイル", "*")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["SrcLastDir"], title="参照する素材ファイルの選択")
    if filepath != '':
        file3.set(filepath)
        write_cfg(filepath, "SrcDir", "Directory")


def slct_filter_cfg_file():  # 効果設定ファイル読み込み
    filetype = [("AviUtl エイリアス/効果ファイル", "*.exa;*.exc;*.exo;*.txt"), ("すべてのファイル", "*.*")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["AlsLastDir"], title="参照するエイリアス/効果ファイルの選択")
    if filepath != '':
        file9.set(filepath)


def save_exo():  # EXO保存ボタン
    filetype = [("AviUtlオブジェクトファイル", "*.exo")]
    filepath = filedialog.asksaveasfilename(
        initialdir=mydict["EXOLastDir"], title="EXOファイル保存場所の選択", filetypes=filetype)
    if filepath != '':
        if not filepath.endswith(".exo"):
            filepath += ".exo"
        file2.set(filepath)
        write_cfg(filepath, "EXODir", "Directory")


def set_rppinfo(reload=0):  # RPP内の各トラックの情報を表示する
    filepath = file1_entry.get().replace('"', '')  # パスをコピペした場合のダブルコーテーションを削除
    if filepath == file1_tmp.get() and reload == 0:
        return True
    file1_tmp.set(filepath)
    file8_tree.delete(*file8_tree.get_children())
    file8_tree.insert("", "end", text="＊全トラック", iid="all", open=True)
    file8_tree.change_state("all", 'tristate')
    file8_tree.yview(0)

    if slct_time.get():
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
            file8_tree.insert("all", "end", text=prefix + "└" + k, iid=str(iid))

            # 該当トラック（親トラック）がミュート状態の場合、ゼロ幅スペース(​)を挿入し後から区別できるようにしている
            if "​" not in k and "​" not in prefix:
                file8_tree.change_state(str(iid), 'checked')
            if tree[k]:
                iid = insert_treedict(tree[k], prefix + "　", iid) if "​" not in k else \
                    insert_treedict(tree[k], prefix + "　​", iid)  # フォルダ開始部の場合、prefixを追加して再帰呼び出し
        else:
            file8_tree.insert("all", "end", text=prefix + "├" + k, iid=str(iid))
            if "​" not in k and "​" not in prefix:
                file8_tree.change_state(str(iid), 'checked')
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
    hLabel[mydict["EffCount"] + mydict["EffNum"]].set(v2.get())
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
    mydict["Effect"][mydict["EffCount"]].append(v2.get())
    mydict["EffCount"] += 1
    # EffDict[v2.get()]回分ループ
    for n in range(len(EffDict[v2.get()])):
        if EffDict[v2.get()][n][-1] == -1:
            hCheckBox.append(StringVar())
            hCheckBox[mydict["EffCbNum"]].set(0)
            hCheckBoxCb.append(ttk.Checkbutton(
                frame6,
                padding=0,
                text=EffDict[v2.get()][n][0],
                onvalue=1,
                offvalue=0,
                variable=hCheckBox[mydict["EffCbNum"]]))
            hCheckBoxCb[mydict["EffCbNum"]].grid(
                row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=1, sticky=W)
            mydict["EffCbNum"] += 1
        elif EffDict[v2.get()][n][-1] == -2:  # Entryだけの項目(めっちゃ強引な実装だから全体的に書き直したい…)
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]
                   ].set(EffDict[v2.get()][n][0])
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
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[v2.get()][n][1])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(
                frame6, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set("移動なし")
            # hEntryXCb[mydict["EffNum"]].grid(
            #     row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=2, padx=5)

            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(
                frame6, textvariable=hEntryE[mydict["EffNum"]], width=5))
            # hEntryEE[mydict["EffNum"]].grid(
            #     row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=3, padx=5)

            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(
                frame6, textvariable=hEntryConf[mydict["EffNum"]], width=5))
            # hEntryConfE[mydict["EffNum"]].grid(
            #     row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=4, padx=5)

            mydict["EffNum"] += 1
        else:
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]
                   ].set(EffDict[v2.get()][n][0])
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
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[v2.get()][n][1])
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
    mydict["RPPPath"] = file1.get().replace('"', '')
    if file2.get().replace('"', '').lower().endswith(".exo") or file2.get().replace('"', '') == "":
        mydict["EXOPath"] = file2.get().replace('"', '')
    else:
        mydict["EXOPath"] = file2.get().replace('"', '') + ".exo"
    mydict["OutputType"] = trgt_radio.get()
    mydict["SrcPath"] = file3.get().replace('"', '').replace('/', '\\')
    mydict["EffPath"] = file9.get().replace('"', '')
    mydict["IsAlpha"] = v4.get()
    mydict["IsLoop"] = v5.get()
    mydict["SrcPosition"] = file6.get()
    mydict["SrcRate"] = file4a.get()
    mydict["fps"] = file5.get()
    mydict["ScriptText"] = file10_text.get('1.0', 'end-1c')
    mydict["IsFlipHEvenObj"] = v3.get()
    mydict["SepLayerEvenObj"] = v7.get()
    mydict["NoGap"] = v9.get()
    mydict["clipping"] = v6.get()
    mydict["IsExSet"] = v8.get()
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
    mydict["SceneIdx"] = int(file11.get() or 0)
    mydict["Blend"] = BlendDict[ParamCombo15.get()]
    mydict["Track"] = file8_tree.get_checked()

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


def trgt_command():  # 「追加対象」変更時の状態切り替え
    if trgt_radio.get() == 1 or trgt_radio.get() == 2:  # 「素材」テキストボックス・参照ボタン
        button4['state'] = 'enable'
        file3_entry['state'] = 'enable'
    else:
        button4['state'] = 'disable'
        file3_entry['state'] = 'disable'

    if trgt_radio.get() == 4:  # シーン番号
        scene_entry['state'] = 'enable'
    else:
        scene_entry['state'] = 'disable'

    if trgt_radio.get() == 1:  # アルファチャンネルを読み込む
        cb4['state'] = 'enable'
    else:
        cb4['state'] = 'disable'

    if trgt_radio.get() == 1 or trgt_radio.get() == 4:  # ループ再生・再生速度・再生位置
        cb5['state'] = 'enable'
        file4a_entry['state'] = 'enable'
        file6_entry['state'] = 'enable'

    else:
        cb5['state'] = 'disable'
        file4a_entry['state'] = 'disable'
        file6_entry['state'] = 'disable'


def advdraw_command():  # 「拡張描画」変更時の状態切り替え
    if v8.get() == '0':
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


def change_time_cb():
    if slct_time.get():
        time_ps_combo['state'] = 'readonly'
        time1_combo['state'] = 'enable'
        time2_combo['state'] = 'enable'
        time_ps_list, marker_list = rpp_cl.load_marker_list()

        if len(time_ps_list) >= 2:
            time_ps.set(time_ps_list[1])
        else:
            time_ps.set('-')
        time_ps_combo['values'] = time_ps_list
        time1_combo['values'] = marker_list
        time2_combo['values'] = marker_list
        set_time(None)
    else:
        time_ps_combo['state'] = 'disable'
        time1_combo['state'] = 'disable'
        time2_combo['state'] = 'disable'


def set_time(a):
    if time_ps.get() == '-':
        time1_combo.set('0.0')
        time2_combo.set('99999.0')
    else:
        slct = time_ps.get()
        time1_combo.set(slct[slct.rfind('(') + 1:slct.rfind('~')])
        time2_combo.set(slct[slct.rfind('~') + 1:-1])


def set_time1(a):
    x = time1.get()
    time1_combo.set(x[x.rfind(':') + 2:])


def set_time2(a):
    x = time2.get()
    time2_combo.set(x[x.rfind(':') + 2:])


if __name__ == '__main__':
    read_cfg()
    # root
    root = Tk()
    root.title('RPPtoEXO v2.0g Developing')
    root.columnconfigure(1, weight=1)

    LFrame = ttk.Frame(root)
    LFrame.grid(row=0, column=0)
    CFrame = ttk.Frame(root)
    CFrame.grid(row=0, column=1)
    RFrame = ttk.Frame(root)
    RFrame.grid(row=0, column=2)
    # そのうちスクロールウィンドウに対応したい（やりかたがわからない）

    # Frame1 RPP選択
    frame1 = ttk.Frame(LFrame, padding=5)
    frame1.grid(row=0, column=0, sticky=N)
    button1 = ttk.Button(frame1, text='参照…', command=slct_rpp)
    button1.grid(row=0, column=3)
    s1 = StringVar()
    s1.set('* RPP : ')
    label1 = ttk.Label(frame1, textvariable=s1)
    label1.grid(row=0, column=0)
    file1 = StringVar()
    file1_tmp = StringVar()
    val_cmd = root.register(set_rppinfo)
    file1_entry = ttk.Entry(frame1, textvariable=file1, width=46, validate='focusout', validatecommand=val_cmd)
    file1_entry.grid(row=0, column=1)
    button1_reload = ttk.Button(frame1, text='↻', command=lambda: set_rppinfo(1), width=2)
    button1_reload.grid(row=0, column=2)
    frame1.rowconfigure(0, weight=1)

    # Frame2 EXO指定
    frame2 = ttk.Frame(LFrame, padding=5)
    frame2.grid(row=1, column=0)
    button2 = ttk.Button(frame2, text='保存先…', command=save_exo)
    button2.grid(row=1, column=3)
    s2 = StringVar()
    s2.set('* EXO : ')
    label2 = ttk.Label(frame2, textvariable=s2)
    label2.grid(row=1, column=0)
    file2 = StringVar()
    file2_entry = ttk.Entry(frame2, textvariable=file2, width=50)
    file2_entry.grid(row=1, column=1)

    # frame3 追加対象オブジェクト・素材指定
    trgt_radio = IntVar()
    trgt_radio.set(1)

    frame3 = ttk.Frame(LFrame, padding=5)
    frame3.grid(row=2, column=0)
    str_trgt = StringVar()
    str_trgt.set('追加対象 : ')
    label3 = ttk.Label(frame3, textvariable=str_trgt)
    label3.grid(row=0, column=0, sticky=W)
    trgt_radio1 = ttk.Radiobutton(frame3, value=0, variable=trgt_radio, text='自動検出(β)', command=trgt_command)
    trgt_radio1.grid(row=0, column=1)
    trgt_radio2 = ttk.Radiobutton(frame3, value=1, variable=trgt_radio, text='動画', command=trgt_command)
    trgt_radio2.grid(row=0, column=2)
    trgt_radio3 = ttk.Radiobutton(frame3, value=2, variable=trgt_radio, text='画像', command=trgt_command)
    trgt_radio3.grid(row=0, column=3)
    trgt_radio4 = ttk.Radiobutton(frame3, value=3, variable=trgt_radio, text='フィルタ', command=trgt_command)
    trgt_radio4.grid(row=0, column=4)
    trgt_radio5 = ttk.Radiobutton(frame3, value=4, variable=trgt_radio, text='シーン番号: ', command=trgt_command)
    trgt_radio5.grid(row=0, column=5)
    file11 = StringVar()
    scene_entry = ttk.Entry(frame3, textvariable=file11, width=3, state='disable')
    scene_entry.grid(row=0, column=6)

    s3 = StringVar()
    s3.set('素材 : ')
    label4 = ttk.Label(frame3, textvariable=s3)
    label4.grid(row=1, column=0, sticky=E)
    file3 = StringVar()
    file3_entry = ttk.Entry(frame3, textvariable=file3, width=46)
    file3_entry.grid(row=1, column=1, columnspan=5, sticky=W)
    button4 = ttk.Button(frame3, text='参照…', command=slct_source)
    button4.grid(row=1, column=5, columnspan=2, sticky=E)

    # frame4  オブジェクト設定
    frame4 = ttk.Frame(LFrame, padding=1)
    frame4.grid(row=3, column=0)

    s4a = StringVar()
    s4a.set('再生速度 : ')
    label4a = ttk.Label(frame4, textvariable=s4a)
    label4a.grid(row=0, column=3, sticky=E, padx=(36, 0))
    file4a = StringVar()
    file4a_entry = ttk.Entry(frame4, textvariable=file4a, width=10)
    file4a_entry.grid(row=0, column=4, sticky=W + E)
    file4a_entry.insert(END, "100.0")

    s6 = StringVar()
    s6.set('再生位置 : ')
    label6 = ttk.Label(frame4, textvariable=s6)
    label6.grid(row=1, column=3, sticky=E, padx=(36, 0))
    file6 = StringVar()
    file6_entry = ttk.Entry(frame4, textvariable=file6, width=10)
    file6_entry.grid(row=1, column=4, sticky=W + E)
    file6_entry.insert(END, "1")

    v4 = StringVar()
    v4.set(0)
    cb4 = ttk.Checkbutton(
        frame4,
        padding=5,
        text='アルファチャンネルを読み込む',
        onvalue=1,
        offvalue=0,
        variable=v4)
    cb4.grid(row=1, column=0, sticky=(W))
    v5 = StringVar()
    v5.set(0)
    cb5 = ttk.Checkbutton(
        frame4,
        padding=5,
        text='ループ再生',
        onvalue=1,
        offvalue=0,
        variable=v5)
    cb5.grid(row=1, column=1, sticky=(W))
    v6 = StringVar()
    v6.set(0)
    cb6 = ttk.Checkbutton(
        frame4,
        padding=5,
        text='上のオブジェクトでクリッピング',
        onvalue=1,
        offvalue=0,
        variable=v6)
    cb6.grid(row=0, column=0, sticky=(W))
    v8 = StringVar()
    v8.set(0)
    cb8 = ttk.Checkbutton(
        frame4,
        padding=5,
        text='拡張描画',
        onvalue=1,
        offvalue=0,
        variable=v8,
        command=advdraw_command)
    cb8.grid(row=0, column=1, sticky=W)

    # Frame4a ソフト独自設定 / トラック選択
    frame4a = ttk.Frame(LFrame, padding=10)
    frame4a.grid(row=4, column=0)

    # v1 = IntVar()
    # v1.set(1)
    # cb1 = ttk.Checkbutton(
    #     frame4a,
    #     padding=5,
    #     text='トラック毎に\n設定を調整する',
    #     onvalue=1,
    #     offvalue=0,
    #     variable=v1
    # )
    # cb1.grid(row=0, column=0, sticky=W)
    v3 = StringVar()
    v3.set(0)
    cb2 = ttk.Checkbutton(
        frame4a,
        padding=5,
        text='左右反転',
        onvalue=1,
        offvalue=0,
        variable=v3)
    cb2.grid(row=1, column=0, sticky=(W))
    v9 = IntVar()
    v9.set(0)
    cb9 = ttk.Checkbutton(
        frame4a,
        padding=5,
        text='隙間なく配置',
        onvalue=1,
        offvalue=0,
        variable=v9)
    cb9.grid(row=2, column=0, sticky=(W))
    v7 = IntVar()
    v7.set(0)
    cb7 = ttk.Checkbutton(
        frame4a,
        padding=5,
        text='偶数番目Objを\n別レイヤ配置',
        onvalue=1,
        offvalue=0,
        variable=v7)
    cb7.grid(row=3, column=0, sticky=(W))

    slct_time = IntVar()
    slct_time.set(0)
    time_cb = ttk.Checkbutton(frame4a, padding=5, text='時間選択 (秒)',
                              onvalue=1, offvalue=0, variable=slct_time, command=change_time_cb)
    time_cb.grid(row=4, column=0, sticky=W)

    time_ps = StringVar()
    time_ps.set('')
    time_ps_combo = ttk.Combobox(frame4a, textvariable=time_ps, width=10, state='disable')
    time_ps_combo.bind('<<ComboboxSelected>>', set_time)
    time_ps_combo.grid(row=5, column=0, padx=5, pady=3, sticky=W + E)

    time1 = StringVar()
    time1.set('')
    time1_combo = ttk.Combobox(frame4a, textvariable=time1, width=10, state='disable')
    time1_combo.bind('<<ComboboxSelected>>', set_time1)
    time1_combo.grid(row=6, column=0, padx=5, pady=3, sticky=W + E)
    time2 = StringVar()
    time2.set('')
    time2_combo = ttk.Combobox(frame4a, textvariable=time2, width=10, state='disable')
    time2_combo.bind('<<ComboboxSelected>>', set_time2)
    time2_combo.grid(row=7, column=0, padx=5, pady=3, sticky=W + E)

    file8disp = StringVar()
    file8_tree = CheckboxTreeview(frame4a, show='tree', height=5)
    file8_tree.grid(row=0, column=1, rowspan=8, sticky=N + S + E + W)
    file8_tree.column("#0", width=300)
    ttk.Style().configure('Checkbox.Treeview', rowheight=15, borderwidth=1, relief='sunken', indent=0)

    file8_scr = Scrollbar(frame4a, orient=VERTICAL, command=file8_tree.yview)
    file8_scr.grid(row=0, column=2, rowspan=8, sticky=N + S)
    file8_tree['yscrollcommand'] = file8_scr.set

    # Frame5 エフェクト追加/削除
    frame5 = ttk.Frame(LFrame, padding=5)
    frame5.grid(row=5, column=0)
    v2 = StringVar()
    cb = ttk.Combobox(frame5, textvariable=v2, state='readonly')
    cb['values'] = list(EffDict.keys())
    cb.set("座標")
    cb.grid(row=0, column=0)
    button5 = ttk.Button(frame5, text='+', command=add_filter_label)
    button5.grid(row=0, column=1)
    button6 = ttk.Button(frame5, text='効果のクリア', command=del_filter_label)
    button6.grid(row=0, column=2)

    # Frame9 効果をファイルから読み込む
    frame9 = ttk.Frame(LFrame, padding=5)
    frame9.grid(row=6, column=0)
    button7 = ttk.Button(frame9, text='参照…', command=slct_filter_cfg_file)
    button7.grid(row=0, column=2)
    s7 = StringVar()
    s7.set('エイリアス : ')
    label10 = ttk.Label(frame9, textvariable=s7)
    label10.grid(row=0, column=0, sticky=W)
    file9 = StringVar()
    file9_entry = ttk.Entry(frame9, textvariable=file9, width=40)
    file9_entry.grid(row=0, column=1)

    # Frame10スクリプト制御
    frame10 = ttk.Frame(LFrame, padding=10)
    frame10.grid(row=7, column=0)
    s9 = StringVar()
    s9.set('スクリプト制御 ')
    label15 = ttk.Label(frame10, textvariable=s9)
    label15.grid(row=0, column=0, sticky=(W))
    file10 = StringVar()
    file10_text = Text(frame10, width=50, height=10)
    file10_text.grid(row=0, column=1)

    # Frame6
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
    Param11.set('X中心 : ')
    ParamLabel11 = ttk.Label(frame8, textvariable=Param11)
    ParamLabel11.grid(row=11, column=0, sticky=W + E)
    ParamEntry11 = StringVar()
    ParamEntryE11 = ttk.Entry(frame8, textvariable=ParamEntry11, width=5)
    ParamEntryE11.grid(row=11, column=1, sticky=W + E)
    ParamEntryE11.insert(END, "0.0")

    Param12 = StringVar()
    Param12.set('Y中心 : ')
    ParamLabel12 = ttk.Label(frame8, textvariable=Param12)
    ParamLabel12.grid(row=12, column=0, sticky=W + E)
    ParamEntry12 = StringVar()
    ParamEntryE12 = ttk.Entry(frame8, textvariable=ParamEntry12, width=5)
    ParamEntryE12.grid(row=12, column=1, sticky=W + E)
    ParamEntryE12.insert(END, "0.0")

    Param13 = StringVar()
    Param13.set('Z中心 : ')
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
    s5 = StringVar()
    s5.set('* FPS : ')
    label5 = ttk.Label(frame7, textvariable=s5)
    label5.grid(row=0, column=0, sticky=W + E)
    file5 = StringVar()
    file5_entry = ttk.Entry(frame7, textvariable=file5, width=10)
    file5_entry.grid(row=0, column=1, sticky=W + E, padx=10)
    file5_entry.insert(END, "")
    button6 = ttk.Button(frame7, text='実行', command=run)
    button6.grid(row=0, column=2)

    root.mainloop()
