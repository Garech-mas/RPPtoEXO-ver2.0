#####################################################################################
#               RPP to EXO ver 2.00 b0.2                                            #
#                                                                       2022/07/11  #
#       Written by Maimai (@Maimai22015/YTPMV.info)                                 #
#                                                                                   #
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
import cv2

# やりたいこと
# TODO: RPPのアイテムが特殊な場合（逆再生・セクション・テイク）にも対応する
# TODO: アイテムがMIDIだった場合、中身のMIDIの音符から自動配置をする
# TODO: ソースコードのクラス化・ファイル分割
# TODO: 素材自動検出のとき、ソースファイル（の再生位置）によって参照すべきソースを変えるGUI・機能の作成
#          ＞ GUI上で再生位置を決めるとき、動画ファイルのサムネイルを表示してあげる
# TODO: 空のアイテムの除去 or テキスト化の処理
# エフェクト効果の表記をAviUtlのUI寄りにし、更に親しみやすい操作にできるようにしたい
# 移動方法やスクリプトなどをAviUtlのフォルダから読み取って設定できるようにする機能
# Google Colabにそのまま引き継げるような仕組みづくり
# GUIの表記を英語にも対応し、多言語にも対応しやすいようにしたい

EffDict = {
    #   "効果名"        :       [["設定１","デフォルト設定"],["設定２","デフォルト設定"],["設定３","デフォルト設定"]], 各設定3つ目に-1でチェックボックス
    "座標": [["X", 0.0], ["Y", 0.0], ["Z", 0.0]],
    "拡大率": [["拡大率", 100.00], ["X", 100.00], ["Y", 100.00]],
    "透明度": [["透明度", 0.0]],
    "回転": [["X", 0.0], ["Y", 0.0], ["Z", 0.0]],
    "リサイズ": [["拡大率", 100.00], ["X", 100.00], ["Y", 100.00], ["補間なし", 0, -1], ["ドット数でサイズ指定", 0, -1]],
    "反転": [["上下反転", 0, -1], ["左右反転", 0, -1], ["輝度反転", 0, -1], ["色相反転", 0, -1], ["透明度反転", 0, -1]],
    # チェックボック項目がある効果設定時に”効果のクリア”をするとバグる。
    "色調補正": [["明るさ", 100.0], ["ｺﾝﾄﾗｽﾄ", 100.0], ["色相", 0.0], ["輝度", 100.0], ["彩度", 100.0], ["飽和する", 0, -1]],
    "クリッピング": [["上", 0], ["下", 0], ["左", 0], ["右", 0], ["中心の位置を変更", 0, -1]],
    "クロマキー": [["色相範囲", 24], ["彩度範囲", 96], ["境界補正", 1], ["色彩補正", 0, -1], ["透過補正", 0, -1], ["color_yc", "cf010008b3fe"],
              ["status", 1]],
    # とりあえず青色透過。デフォ設定は0000000000(未設定)とかだったはず。
    "縁取り": [["サイズ", 3], ["ぼかし", 10], ["color", 000000], ["file", ""]],
    "マスク": [["X", 0.0], ["Y", 0.0], ["回転", 0.00], ["サイズ", 100], ["縦横比", 0.0], ["ぼかし", 0], ["マスクの反転", 0, -1],
            ["元のサイズに合わせる", 0, -1], ["type", 2], ["name", ""], ["mode", 0]],
    "放射ブラー": [["範囲", 20.0], ["X", 0], ["Y", 0], ["サイズ固定", 0, -1]],
    "方向ブラー": [["範囲", 20], ["角度", 50.0], ["サイズ固定", 0, -1]],
    "振動": [["X", 10], ["Y", 10], ["Z", 0], ["周期", 1], ["ランダムに強さを変える", 1, -1], ["複雑に振動", 0, -1]],
    "ミラー": [["透明度", 0.0], ["減衰", 0.0], ["境目調整", 0], ["中心の位置を変更", 1, -1], ["type", 1]],
    # type ミラー方向 上：0 下:1 左:2 右:3 中心位置変更のデフォは0
    "ラスター": [["横幅", 100], ["高さ", 100], ["周期", 1.00], ["縦ラスター", 0], ["ランダム振幅", 0]],
    "波紋": [["中心X", 0], ["中心Y", 0], ["幅", 30.0], ["高さ", 15.0], ["速度", 150], ["num", 0], ["interval", 0], ["add", 0]],
    "ディスプレイスメントマップ": [["param0", 0.0], ["param1", 0.0], ["X", 0.0], ["Y", 0.0], ["回転", 0.00], ["サイズ", 200],
                      ["縦横比", 0.0], ["ぼかし", 5], ["元のサイズに合わせる", 0], ["type", 1], ["name", ""], ["mode", 0], ["calc", 0]],
    "色ずれ": [["ずれ幅", 5], ["角度", 0.0], ["強さ", 100], ["type", 0]],
    "アニメーション効果": [["track0", 0.00], ["track1", 0.00], ["track1", 0.00], ["track2", 0.00], ["track3", 0.00],
                  ["check0", 0], ["type", 0], ["filter", 0], ["name", ""], ["param", ""]],
}

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

    # 独自設定
    "IsFlipHEvenObj": 0,  # 偶数オブジェクトを左右反転するか
    "OutputType": 0,  # 1=動画  2=画像  3=フィルタ  4=シーン  として出力
    "IsExSet": 0,  # 拡張描画を有効にするか
    "AutoSrc": 0,  # 素材自動検出が有効か

    # 設定
    "RPPLastDir": os.path.abspath(os.path.dirname(__file__)),
    "EXOLastDir": os.path.abspath(os.path.dirname(__file__)),
    "SrcLastDir": os.path.abspath(os.path.dirname(__file__)),
}

XDict = {
    "移動なし": "",
    "直線移動": 1,
    "加減速移動": 103,
    "曲線移動": 2,
    "瞬間移動": 3,
    "中間点無視": 4,
    "移動量指定": 5,
    "ランダム": 6,
    "反復移動": 8,
    "補完移動": "15@補間移動",
    "回転": "15@回転,100",
    "スクリプト(終了値,15@スクリプト名,)": "",
    "イージング（通常）": "15@イージング（通常）@イージング",
    "加速@加減速TRA": "15@加速@加減速TRA",
    "減速@加減速TRA": "15@減速@加減速TRA",
    # 追加する際は
    # "GUI上で表示される名前": "15@スクリプト名"
}

srch_type = {"VIDEO": "VIDEO",  # 動画ファイル
             "WAVE": "AUDIO",  # WAV ファイル
             "MP3": "AUDIO",  # MP3 ファイル
             "VORBIS": "AUDIO",  # OGG ファイル
             "FLAC": "AUDIO",  # FLAC ファイル
             "MIDI": "XMIDI",  # MIDI アイテム
             "LTC": "XLTC",  # タイムコード ジェネレータ
             "CLICK": "XCLICK"  # メトロノーム ソース
             }

rpp_ary = []


def add_filter_to_exo(mydict, item_count):
    count = 1
    exo_effects = ""
    for eff in mydict["Effect"]:
        exo_effects += "\n[" + str(item_count) + "." + \
                       str(count) + "]\n_name=" + str(eff[0])
        for x in range(1, len(eff)):
            exo_effects += "\n" + str(eff[x][0]) + "=" + str(eff[x][1])
        count += 1
    return exo_effects


def load_filter_from_file(item_count):
    lfff_count = 0
    returntext = "\n"
    with open(str(mydict["EffPath"]), mode='r', encoding='UTF-8', errors='replace') as f:
        for line in f:
            if lfff_count == 0 and line != "[0.1]\n":
                print(line)
                messagebox.showinfo("エラー", "効果を記入したファイルに問題あり。取説参照")
            if line[0] == "[":
                line = "[" + str(item_count) + "." + \
                       str(len(mydict["Effect"]) + 1 + lfff_count) + "]\n"
                lfff_count += 1
            returntext += line
    return returntext, lfff_count


def add_script_control(item_count, eff_num):
    tmp_text = "\n[" + str(item_count) + "." + str(eff_num) + "]\n_name=スクリプト制御\ntext="
    # スクリプト制御を追加するためのその場しのぎ関数。こんなやり方じゃいつか詰むぞ
    script_text = file10_text.get('1.0', 'end-1c')
    script_text = binascii.hexlify(script_text.encode("UTF-16LE"))
    script_text = str(script_text)[:-1][2:]
    script_text = script_text + "0" * (4096 - len(str(script_text)))
    return tmp_text + script_text


def main():
    button6['state'] = 'disable'
    root['cursor'] = 'watch'
    button6["text"] = "実行中..."
    file_path = []
    objDict = {
        "pos": [-1],
        "length": [-1],
        "loop": [-1],
        "soffs": [-1],
        "playrate": [-1],
        "fileidx": [-1],
        "filetype": [-1],
    }

    # RPPを読み込み、必要な情報をitemdictに格納していく
    index = 0
    track_index = 0

    while index < len(rpp_ary):

        if rpp_ary[index].find("<TRACK") != -1:  # トラック境目
            track_index += 1
            if objDict["pos"][-1] != -1:  # トラックが切り替わる位置に-1を入れる
                objDict["pos"].append(-1)
                objDict["length"].append(-1)
                objDict["loop"].append(-1)
                objDict["soffs"].append(-1)
                objDict["playrate"].append(-1)
                objDict["fileidx"].append(-1)
                objDict["filetype"].append(-1)

        if ((str(track_index) in mydict["Track"])
                and rpp_ary[index].find("<ITEM") != -1):  # 該当トラックのITEMセクションに入ったら
            itemdict = {}
            prefix = ""
            item_lyr = 1
            index += 1
            while item_lyr > 0:  # <ITEM >を辞書化し、管理しやすくする
                if rpp_ary[index].find("<") != -1:  # 深い階層に入る
                    prefix += rpp_ary[index][rpp_ary[index].find("<") + 1:-1] + "/"
                    item_lyr += 1
                elif rpp_ary[index].find(">") != -1:  # 階層を下る
                    slash_pos = prefix.find("/")
                    prefix = prefix[slash_pos + 1:] if slash_pos != len(prefix) - 1 else ""
                    item_lyr -= 1
                else:
                    spl = rpp_ary[index].split()
                    key = prefix + spl.pop(0)
                    itemdict[key] = spl
                index += 1

            index -= 2
            objDict["pos"].append(float(itemdict["POSITION"][0]))
            objDict["length"].append(float(itemdict["LENGTH"][0]))
            if mydict["AutoSrc"]:  # 素材自動検出モードの処理
                objDict["loop"].append(int(itemdict["LOOP"][0]))
                objDict["soffs"].append(float(itemdict["SOFFS"][0])) if "SOFFS" in itemdict \
                    else objDict["soffs"].append(0.0)
                objDict["playrate"].append(float(itemdict["PLAYRATE"][0])) if "PLAYRATE" in itemdict \
                    else objDict["playrate"].append(1.0)
                srchflg = 0

                for srch in srch_type.keys():  # ここ以下ファイルパス処理
                    keyy = "SOURCE " + srch + "/FILE"
                    if "SOURCE SECTION/" + keyy in itemdict:
                        path = str(' '.join(itemdict["SOURCE SECTION/" + keyy])).replace('"', '')
                        if path not in file_path:
                            file_path.append(path)
                        objDict["fileidx"].append(file_path.index(path))
                        objDict["filetype"].append(srch_type[srch])
                        srchflg = 1
                    elif keyy in itemdict:
                        path = str(' '.join(itemdict[keyy])).replace('"', '')
                        if path not in file_path:
                            file_path.append(path)
                        objDict["fileidx"].append(file_path.index(path))
                        objDict["filetype"].append(srch_type[srch])
                        srchflg = 1
                if not srchflg:
                    objDict["fileidx"].append(-1)
                    objDict["filetype"].append("OTHER")

        index += 1
    make_exo(objDict, file_path)


def make_exo(objDict, file_path):
    exo_result = "[exedit]\nwidth=" + str(1280) + "\nheight=" + str(720) + "\nrate=" + str(
        60) + "\nscale=1\nlength=99999\naudio_rate=44100\naudio_ch=2"
    item_count = 0
    exo_1 = "\n["  # item_count
    exo_2 = "]\nstart="  # StartFrame
    exo_3 = "\nend="  # EndFrame
    exo_4 = "\nlayer="  # layer
    exo_4_2 = "\ngroup=1\noverlay=1\nclipping=" + str(mydict["clipping"]) + "\ncamera=0\n["  # item_count
    # #テキストオブジェクトの場合の処理
    #     exo_5 = ".0]\n_name=テキスト\nサイズ=100\n表示速度=0.0\n文字毎に個別オブジェクト=0\n移動座標上に表示する=0" + \
    #             "\n自動スクロール=0\nB=0\nI=0\ntype=0\nautoadjust=0\nsoft=1\nmonospace=0\nalign=4" + \
    #             "\nspacing_x=0\nspacing_y=0\nprecision=1\ncolor=ffffff\ncolor2=000000\nfont=HGS明朝E" + \
    #             "\ntext=~~~"
    exo_6 = "\n["  # item_count
    # exo_7 item_countによる分岐のため後のループ内で記述
    exo_7 = ""

    exo_eff = ""  # エフェクト設定用、先に宣言だけしておく。item_countを必要とするから後のループ内で処理
    exo_script = ""  # スクリプト制御用
    bf = 0.0  # アイテム一つ前の最終フレーム  ==Endframe
    layer = 1  # オブジェクトのあるレイヤー（RPP上で複数トラックある場合は別トラックに配置する）

    bfidx = 1
    file_fps = []

    # 各動画ファイルを読み込み、必要な情報を格納する
    for index in range(len(file_path)):
        if not mydict["AutoSrc"]:
            break
        path = file_path[index]
        cap = cv2.VideoCapture(path.replace('\\', '/'))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if fps == 0.0:
            print("動画として読み込めませんでした。>", end="")
            fps = 1.0
        print(path + "; fps: " + str(fps))
        cap.release()
        file_fps.append(fps)

    for index in range(1, len(objDict["length"])):
        lfff_count = 0
        asc_count = 0

        # オブジェクト最初のフレームと長さの計算
        obj_frame_pos = objDict["pos"][index] * float(mydict["fps"]) + 1
        next_obj_frame_pos = objDict["pos"][index + 1] * float(mydict["fps"]) + 1 \
            if index != len(objDict["length"]) - 1 else -1
        obj_frame_length = objDict["length"][index] * float(mydict["fps"])
        if round(obj_frame_pos) == bf:  # 一つ前のオブジェクトとフレームがかぶらないようにする処理
            obj_frame_pos += 1
            obj_frame_length -= 1
        if round(obj_frame_pos + obj_frame_length) == round(next_obj_frame_pos) - 1:  # 一つ後のオブジェクトとの間に1フレームの空きがある場合の処理
            obj_frame_length += 1
        if obj_frame_pos < bf:
            bf = 0
            bfidx = index
            layer += 1 + int(v7.get())
            if obj_frame_pos < 0:
                continue
        bf = obj_frame_pos + obj_frame_length - 1
        if v9.get() == "1":
            if obj_frame_pos < round(next_obj_frame_pos) - 1:
                bf = next_obj_frame_pos - 1

        obj_frame_pos = round(obj_frame_pos)
        if obj_frame_pos == 0: obj_frame_pos = 1
        bf = round(bf)
        exo_eff = ""

        # エフェクトを追加している場合の設定
        if len(mydict["Effect"]) != 0:
            exo_eff += add_filter_to_exo(mydict, item_count)
        # ファイルから効果を読み込む設定
        if mydict["EffPath"] != "":
            a, b = load_filter_from_file(item_count)
            exo_eff += a
            lfff_count += b

        # 偶数番目オブジェクトをひとつ下のレイヤに配置する
        if str(v7.get()) == str(1) and (bfidx + item_count) % 2 == 0:
            exo_4 = "\nlayer=" + str(layer + 1)  # layer
        else:
            exo_4 = "\nlayer=" + str(layer)

        # オブジェクトの種類等の設定
        if not mydict["AutoSrc"]:
            exo_5 = ".0]\n_name=動画ファイル\n再生位置=" + str(mydict["SrcPosition"]) + "\n再生速度=" + str(mydict["SrcRate"]) + \
                    "\nループ再生=" + str(mydict["IsLoop"]) + "\nアルファチャンネルを読み込む=" + \
                    str(mydict["IsAlpha"]) + "\nfile=" + str(mydict["SrcPath"])
            if mydict["OutputType"] == 2:  # 画像オブジェクトの場合の処理
                exo_5 = ".0]\n_name=画像ファイル\nfile=" + str(mydict["SrcPath"])
            if mydict["OutputType"] == 4:  # シーンオブジェクトの場合の処理
                exo_5 = ".0]\n_name=シーン\n再生位置=" + str(mydict["SrcPosition"]) + "\n再生速度=" + str(mydict["SrcRate"]) + \
                        "\nループ再生=" + str(mydict["IsLoop"]) + "\nscene=" + str(mydict["SceneIdx"])
        else:  # 素材自動検出モード時の処理

            # if objDict["filetype"][index] == "VIDEO":
            is_alpha = 0
            if file_path[objDict["fileidx"][index]][file_path[objDict["fileidx"][index]].find('.'):] == ".avi":
                is_alpha = 1
            exo_5 = ".0]\n_name=動画ファイル" \
                    "\n再生位置=" + str(int(objDict["soffs"][index] * file_fps[objDict["fileidx"][index]] + 1)) \
                    + "\n再生速度=" + str(int(objDict["playrate"][index] * 1000) / 10.0) + \
                    "\nループ再生=" + str(objDict["loop"][index]) + "\nアルファチャンネルを読み込む=" + str(is_alpha) + \
                    "\nfile=" + str(file_path[objDict["fileidx"][index]])

        # メディアオブジェクト  偶数番目（反転○）
        if mydict["OutputType"] != 3 and int(mydict["IsFlipHEvenObj"]) == 1 and (bfidx + item_count) % 2 == 0:
            exo_eff += "\n[" + str(item_count) + "." + str(len(mydict["Effect"]) + 1 + lfff_count) + \
                       "]\n_name=反転\n上下反転=0\n左右反転=1\n輝度反転=0\n色相反転=0\n透明度反転=0"

            if file10_text.get('1.0', 'end-1c') != "":  # スクリプト制御追加する場合
                exo_script = add_script_control(item_count, len(mydict["Effect"]) + 2 + lfff_count)
                asc_count = 1

            if mydict["IsExSet"] == "0":
                exo_7 = "." + str(len(mydict["Effect"]) + 2 + asc_count + lfff_count) + \
                        "]\n_name=標準描画" + \
                        "\nX=" + str(mydict["X"]) + "\nY=" + str(mydict["Y"]) + "\nZ=" + str(mydict["Z"]) + \
                        "\n拡大率=" + str(mydict["Size"]) + "\n透明度=" + str(mydict["Alpha"]) + \
                        "\n回転=" + str(mydict["Rotation"]) + "\nblend=" + str(mydict["Blend"])
            else:  # 拡張描画の場合
                exo_7 = "." + str(len(mydict["Effect"]) + 2 + asc_count + lfff_count) + \
                        "]\n_name=拡張描画" + \
                        "\nX=" + str(mydict["X"]) + "\nY=" + str(mydict["Y"]) + "\nZ=" + str(mydict["Z"]) + \
                        "\n拡大率=" + str(mydict["Size"]) + "\n透明度=" + str(mydict["Alpha"]) + \
                        "\n縦横比=0.0" + "\nX軸回転=" + str(mydict["XRotation"]) + \
                        "\nY軸回転=" + str(mydict["YRotation"]) + "\nZ軸回転=" + str(mydict["ZRotation"]) + \
                        "\n中心X=" + str(mydict["XCenter"]) + "\n中心Y=" + str(mydict["YCenter"]) + \
                        "\n中心Z=" + str(mydict["ZCenter"]) + \
                        "\n裏面を表示しない=0" + "\nblend=" + str(mydict["Blend"])

            exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) + exo_4 +
                          exo_4_2 + str(item_count) + exo_5 + exo_eff + exo_script + exo_6 + str(item_count) + exo_7)
        # メディアオブジェクト  奇数番目（反転×）
        elif mydict["OutputType"] != 3 and (int(mydict["IsFlipHEvenObj"]) == 0 or (bfidx + item_count) % 2 == 1):
            if file10_text.get('1.0', 'end-1c') != "":  # スクリプト制御追加する場合
                exo_script = add_script_control(item_count, len(mydict["Effect"]) + 1 + lfff_count)
                asc_count = 1

            if mydict["IsExSet"] == "0":
                exo_7 = "." + str(len(mydict["Effect"]) + asc_count + 1 + lfff_count) + \
                        "]\n_name=標準描画" + \
                        "\nX=" + str(mydict["X"]) + "\nY=" + str(mydict["Y"]) + "\nZ=" + str(mydict["Z"]) + \
                        "\n拡大率=" + str(mydict["Size"]) + "\n透明度=" + str(mydict["Alpha"]) + \
                        "\n回転=" + str(mydict["Rotation"]) + "\nblend=" + str(mydict["Blend"])
            else:  # 拡張描画の場合
                exo_7 = "." + str(len(mydict["Effect"]) + asc_count + 1 + lfff_count) + \
                        "]\n_name=拡張描画" + \
                        "\nX=" + str(mydict["X"]) + "\nY=" + str(mydict["Y"]) + "\nZ=" + str(mydict["Z"]) + \
                        "\n拡大率=" + str(mydict["Size"]) + "\n透明度=" + str(mydict["Alpha"]) + \
                        "\n縦横比=0.0" + "\nX軸回転=" + str(mydict["XRotation"]) + \
                        "\nY軸回転=" + str(mydict["YRotation"]) + "\nZ軸回転=" + str(mydict["ZRotation"]) + \
                        "\n中心X=" + str(mydict["XCenter"]) + "\n中心Y=" + str(mydict["YCenter"]) + \
                        "\n中心Z=" + str(mydict["ZCenter"]) + \
                        "\n裏面を表示しない=0" + "\nblend=" + str(mydict["Blend"])

            exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) + exo_4 +
                          exo_4_2 + str(item_count) + exo_5 + exo_eff + exo_script + exo_6 + str(item_count) + exo_7)
        # フィルタ効果  奇数番目（反転×）
        elif mydict["OutputType"] == 3 and (int(mydict["IsFlipHEvenObj"]) == 0 or (bfidx + item_count) % 2 == 1):
            if file10_text.get('1.0', 'end-1c') != "":  # スクリプト制御追加する場合
                exo_script = add_script_control(item_count, len(mydict["Effect"]) + 1 + lfff_count)
                asc_count = 1
            exo_4_2 = "\ngroup=1\noverlay=1"
            # 何も効果がかかっていないとエラー吐くので（多分）とりあえず座標0,0,0を掛けておく
            exo_5 = "\n[" + str(item_count) + ".0]\n_name=座標\nX=0.0\nY=0.0\nZ=0.0"
            exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) + exo_4 +
                          exo_4_2 + exo_5 + exo_eff + exo_script)
        # フィルタ効果  偶数番目（反転〇）
        elif mydict["OutputType"] == 3 and int(mydict["IsFlipHEvenObj"]) == 1 and (bfidx + item_count) % 2 == 0:
            if file10_text.get('1.0', 'end-1c') != "":  # スクリプト制御追加する場合
                exo_script = add_script_control(item_count, len(mydict["Effect"]) + 2 + lfff_count)
                asc_count = 1
            exo_4_2 = "\ngroup=1\noverlay=1"
            exo_5 = ""
            exo_eff += "\n[" + str(item_count) + "." + str(len(mydict["Effect"]) + asc_count + lfff_count) + \
                       "]\n_name=反転\n上下反転=0\n左右反転=1\n輝度反転=0\n色相反転=0\n透明度反転=0"
            exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) + exo_4 +
                          exo_4_2 + exo_5 + exo_eff + exo_script)

        item_count = item_count + 1

    try:
        with open(mydict["EXOPath"], mode='w', encoding='shift_jis') as f:
            line = ""
            for t in exo_result:
                f.write(t)
                line += t
                if t == '\n':
                    line = ""
    except PermissionError:
        messagebox.showerror("エラー", "EXOファイルへの出力に失敗しました。\n上書き先のEXOファイルが開かれているか、読み取り専用になっています。")
    except UnicodeEncodeError:
        messagebox.showerror("エラー", "EXOファイルへの出力に失敗しました。\nAviUtl で使用できない文字がパス名に含まれています。\n"
                                    "パス名に含まれる該当文字を削除し、再度実行し直してください。\n\n"
                             + line + '  『' + t + '』')
    else:
        ret = messagebox.askyesno("正常終了", "正常に生成されました。\n保存先のフォルダを開きますか？")
        if ret:
            subprocess.Popen(['explorer', os.path.dirname(mydict["EXOPath"]).replace('/', '\\')], shell=True)

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
    return 0


def write_cfg(filepath, setting_type):  # 設定保存
    config_ini_path = "config.ini"
    if os.path.exists(config_ini_path):
        config_ini = configparser.ConfigParser()
        config_ini.read(config_ini_path, encoding='utf-8')
        config_ini.set("Directory", setting_type, os.path.dirname(filepath))
        with open('config.ini', 'w', encoding='utf-8') as file:
            config_ini.write(file)


def slct_rpp():  # 参照ボタン
    filetype = [("REAPERプロジェクトファイル", "*.rpp")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["RPPLastDir"], title="RPPファイルを選択")
    if filepath != '':
        file1.set(filepath)
        write_cfg(filepath, "RPPDir")
        load_track_name()


def slct_source():  # 素材選択
    filetype = [("動画ファイル", "*")] if trgt_radio.get() == 1 else [("画像ファイル", "*")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["SrcLastDir"], title="参照する素材ファイルの選択")
    if filepath != '':
        file3.set(filepath)
        write_cfg(filepath, "SrcDir")


def slct_filter_cfg_file():  # 効果設定ファイル読み込み
    filetype = [("ファイル", "*")]
    filepath = filedialog.askopenfilename(
        filetypes=filetype, initialdir=mydict["EXOLastDir"])
    file9.set(filepath)


def save_exo():  # EXO保存ボタン
    filetype = [("AviUtlオブジェクトファイル", "*.exo")]
    filepath = filedialog.asksaveasfilename(
        initialdir=mydict["EXOLastDir"], title="EXOファイル保存場所の選択", filetypes=filetype)
    if filepath != '':
        if not filepath.endswith(".exo"):
            filepath += ".exo"
        file2.set(filepath)
        write_cfg(filepath, "EXODir")


def load_track_name():  # トラック名読み込み
    file8_tree.delete(*file8_tree.get_children())
    filepath = file1_entry.get().replace('"', '')  # パスをコピペした場合のダブルコーテーションを削除
    file8_tree.insert("", "end", text="＊全トラック", iid="all", open=True)
    file8_tree.change_state("all", 'checked')
    global rpp_ary
    if ".rpp" in filepath.lower():
        track_list = ["全トラック"]
        with open(filepath, mode='r', encoding='UTF-8', errors='replace') as f:
            rpp_ary = f.readlines()
        tree = make_treedict(1)[0]
        insert_treedict(tree, "", 0)
    return True


def make_treedict(index):
    global rpp_ary
    value = {}
    while True:
        index += 1
        while rpp_ary[index].find("<TRACK") == -1:
            index += 1
            if index >= len(rpp_ary):
                return value, index, 0

        name = rpp_ary[index + 1][9:-1]
        isbus = rpp_ary[index + 9].split()  # [1] > フォルダ始端・終端 [2] > 階層を何個下るか
        while name in value:
            name += " "
        value[name] = {}

        if isbus[1] == "1":
            value[name], index, skip = make_treedict(index)
            if skip < 0:
                return value, index, skip + 1
        elif isbus[1] == "2":
            return value, index, int(isbus[2]) + 1


def insert_treedict(tree, prefix, iid):
    for k in tree:
        iid += 1
        if k == next(reversed(tree.keys()), None):
            file8_tree.insert("all", "end", text=prefix + "└" + k, iid=str(iid))
            if tree[k] != {}:
                iid = insert_treedict(tree[k], prefix + "　", iid)
        else:
            file8_tree.insert("all", "end", text=prefix + "├" + k, iid=str(iid))
            if tree[k] != {}:
                iid = insert_treedict(tree[k], prefix + "│", iid)
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
    mydict["EXOPath"] = file2.get().replace('"', '')
    mydict["OutputType"] = trgt_radio.get()
    mydict["SrcPath"] = file3.get().replace('"', '').replace('/', '\\')
    mydict["EffPath"] = file9.get().replace('"', '')
    mydict["IsAlpha"] = v4.get()
    mydict["IsLoop"] = v5.get()
    mydict["SrcPosition"] = file6.get()
    mydict["SrcRate"] = file4a.get()
    mydict["fps"] = file5.get()
    mydict["IsFlipHEvenObj"] = v3.get()
    mydict["clipping"] = v6.get()
    mydict["IsExSet"] = v8.get()
    mydict["X"] = ParamEntry1.get()
    mydict["Y"] = ParamEntry2.get()
    mydict["Z"] = ParamEntry3.get()
    mydict["Size"] = ParamEntry4.get()
    mydict["Alpha"] = ParamEntry5.get()
    mydict["Rotation"] = ParamEntry7.get()
    mydict["XRotation"] = ParamEntry8.get()
    mydict["YRotation"] = ParamEntry9.get()
    mydict["ZRotation"] = ParamEntry10.get()
    mydict["XCenter"] = ParamEntry11.get()
    mydict["YCenter"] = ParamEntry12.get()
    mydict["ZCenter"] = ParamEntry13.get()
    mydict["SceneIdx"] = int(file11.get() or 0)
    mydict["AutoSrc"] = int(trgt_radio.get() == 0)

    mydict["Track"] = file8_tree.get_checked()

    if mydict["RPPPath"] == "" or mydict["EXOPath"] == "" or mydict["fps"] == "":
        messagebox.showinfo("エラー", "必須項目（RPP/EXO/FPS）が入力されていません。")
        return 0
    if (mydict["SceneIdx"] <= 0 or mydict["SceneIdx"] >= 50) and mydict["OutputType"] == 4:
        messagebox.showinfo("エラー", "正しいシーン番号を入力してください。（範囲 : 1 ~ 49）")
        return 0
    elif mydict["SceneIdx"] != 1 and mydict["OutputType"] == 4:
        messagebox.showinfo(
            "注意", "AviUtlのバグの影響により、シーン番号は反映されません。\nインポート後、個別に設定してください。"
                  "\n拡張編集0.93rc か patch.aul導入済 の環境の方は無視できます。")

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
                    eff = [EffDict[mydict["Effect"][i][0]][x][0],
                           str(hEntryS[runcount].get())]
                    mydict["Effect"][i].append(eff)
                else:  # 移動ありの場合
                    if str(hEntryE[runcount].get()) == "":
                        messagebox.showinfo("エラー", "追加フィルタ効果の終点が入力されていません。")
                        return 0
                    eff = [EffDict[mydict["Effect"][i][0]][x][0],
                           str(hEntryS[runcount].get()) + "," + str(hEntryE[runcount].get()) + "," + str(
                               XDict[hEntryX[runcount].get()])]
                    if XDict[hEntryX[runcount].get()] != "":
                        eff[1] += str(hEntryConf[runcount].get())
                        messagebox.showinfo(
                            "注意", "AviUtlのバグの影響により、移動の設定の値は反映されません。\nインポート後、個別に設定してください。"
                                  "\n拡張編集0.93rc か patch.aul導入済 の環境の方は無視できます。")
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


def trgt_command():
    if trgt_radio.get() == 1 or trgt_radio.get() == 2:
        button4['state'] = 'enable'
        file3_entry['state'] = 'enable'
    else:
        button4['state'] = 'disable'
        file3_entry['state'] = 'disable'
    if trgt_radio.get() == 4:
        scene_entry['state'] = 'enable'
    else:
        scene_entry['state'] = 'disable'


if __name__ == '__main__':
    read_cfg()
    # root
    root = Tk()
    root.title('RPPtoEXO v2.0 Developing')
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
    button1.grid(row=0, column=2)
    s1 = StringVar()
    s1.set('* RPP : ')
    label1 = ttk.Label(frame1, textvariable=s1)
    label1.grid(row=0, column=0)
    file1 = StringVar()
    # file1_entry = ttk.Entry(frame1, textvariable=file1, width=50)
    val_cmd = root.register(load_track_name)
    file1_entry = ttk.Entry(frame1, textvariable=file1, width=50, validate='focusout', validatecommand=val_cmd)
    file1_entry.grid(row=0, column=1)
    frame1.rowconfigure(0, weight=1)

    # Frame2 EXO指定
    frame2 = ttk.Frame(LFrame, padding=5)
    frame2.grid(row=1, column=0)
    button2 = ttk.Button(frame2, text='保存先…', command=save_exo)
    button2.grid(row=1, column=2)
    s2 = StringVar()
    s2.set('* EXO : ')
    label2 = ttk.Label(frame2, textvariable=s2)
    label2.grid(row=1, column=0)
    file2 = StringVar()
    file2_entry = ttk.Entry(frame2, textvariable=file2, width=50)
    file2_entry.grid(row=1, column=1)

    # frame3 追加対象オブジェクト・素材指定
    trgt_radio = IntVar()
    trgt_radio.set(0)

    frame3 = ttk.Frame(LFrame, padding=5)
    frame3.grid(row=2, column=0)
    str_trgt = StringVar()
    str_trgt.set('追加対象 : ')
    label3 = ttk.Label(frame3, textvariable=str_trgt)
    label3.grid(row=0, column=0, sticky=W)
    trgt_radio1 = ttk.Radiobutton(frame3, value=0, variable=trgt_radio, text='自動検出', width=10, command=trgt_command)
    trgt_radio1.grid(row=0, column=1)
    trgt_radio2 = ttk.Radiobutton(frame3, value=1, variable=trgt_radio, text='動画', command=trgt_command)
    trgt_radio2.grid(row=0, column=2)
    trgt_radio3 = ttk.Radiobutton(frame3, value=2, variable=trgt_radio, text='画像', command=trgt_command)
    trgt_radio3.grid(row=0, column=3)
    trgt_radio4 = ttk.Radiobutton(frame3, value=3, variable=trgt_radio, text='フィルタ効果', command=trgt_command)
    trgt_radio4.grid(row=0, column=4)
    trgt_radio5 = ttk.Radiobutton(frame3, value=4, variable=trgt_radio, text='シーン 番号: ', command=trgt_command)
    trgt_radio5.grid(row=0, column=5)
    file11 = StringVar()
    scene_entry = ttk.Entry(frame3, textvariable=file11, width=3, state='disable')
    scene_entry.grid(row=0, column=6)

    s3 = StringVar()
    s3.set('素材 : ')
    label4 = ttk.Label(frame3, textvariable=s3)
    label4.grid(row=1, column=0, sticky=E)
    file3 = StringVar()
    file3_entry = ttk.Entry(frame3, textvariable=file3, width=46, state="disable")
    file3_entry.grid(row=1, column=1, columnspan=5, sticky=W)
    button4 = ttk.Button(frame3, text='参照…', command=slct_source, state="disable")
    button4.grid(row=1, column=5, columnspan=2, sticky=E)

    #frame4  オブジェクト設定
    frame4 = ttk.Frame(LFrame, padding=1)
    frame4.grid(row=3, column=0)

    s4a = StringVar()
    s4a.set('再生速度 : ')
    label4a = ttk.Label(frame4, textvariable=s4a)
    label4a.grid(row=0, column=3, sticky=E, padx=(36, 0))
    file4a = StringVar()
    file4a_entry = ttk.Entry(frame4, textvariable=file4a, width=10)
    file4a_entry.grid(row=0, column=4, sticky=W+E)
    file4a_entry.insert(END, "100.0")

    s6 = StringVar()
    s6.set('再生位置 : ')
    label6 = ttk.Label(frame4, textvariable=s6)
    label6.grid(row=1, column=3, sticky=E, padx=(36, 0))
    file6 = StringVar()
    file6_entry = ttk.Entry(frame4, textvariable=file6, width=10)
    file6_entry.grid(row=1, column=4, sticky=W+E)
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
        variable=v8)
    cb8.grid(row=0, column=1, sticky=W)

    # Frame4a ソフト独自設定 / トラック選択
    frame4a = ttk.Frame(LFrame, padding=10)
    frame4a.grid(row=4, column=0)

    v3 = StringVar()
    v3.set(0)
    cb2 = ttk.Checkbutton(
        frame4a,
        padding=5,
        text='左右反転',
        onvalue=1,
        offvalue=0,
        variable=v3)
    cb2.grid(row=0, column=0, sticky=(W))
    v9 = StringVar()
    v9.set(0)
    cb9 = ttk.Checkbutton(
        frame4a,
        padding=5,
        text='隙間なく配置',
        onvalue=1,
        offvalue=0,
        variable=v9)
    cb9.grid(row=1, column=0, sticky=(W))
    v7 = StringVar()
    v7.set(0)
    cb7 = ttk.Checkbutton(
        frame4a,
        padding=5,
        text='偶数番目Objを\n別レイヤ配置',
        onvalue=1,
        offvalue=0,
        variable=v7)
    cb7.grid(row=2, column=0, sticky=(W))

    file8disp = StringVar()
    file8_tree = CheckboxTreeview(frame4a, show='tree', height=5)
    file8_tree.grid(row=0, column=1, rowspan=3, sticky=N+S+E+W)
    file8_tree.column("#0", width=300)
    ttk.Style().configure('Checkbox.Treeview', rowheight=15, borderwidth=1, relief='sunken', indent=0)

    # Frame5 エフェクト追加/削除
    frame5 = ttk.Frame(LFrame, padding=10)
    frame5.grid(row=5, column=0)
    v2 = StringVar()
    cb = ttk.Combobox(frame5, textvariable=v2)
    cb['values'] = list(EffDict.keys())
    cb.set("座標")
    cb.grid(row=0, column=0)
    button5 = ttk.Button(frame5, text='+', command=add_filter_label)
    button5.grid(row=0, column=1)
    button6 = ttk.Button(frame5, text='効果のクリア', command=del_filter_label)
    button6.grid(row=0, column=2)

    # Frame9 効果をファイルから読み込む
    frame9 = ttk.Frame(LFrame, padding=10)
    frame9.grid(row=6, column=0)
    button7 = ttk.Button(frame9, text='参照…', command=slct_filter_cfg_file)
    button7.grid(row=3, column=2)
    s7 = StringVar()
    s7.set('効果ファイル ')
    label10 = ttk.Label(frame9, textvariable=s7)
    label10.grid(row=3, column=0, sticky=(W))
    file9 = StringVar()
    file9_entry = ttk.Entry(frame9, textvariable=file9, width=30)
    file9_entry.grid(row=3, column=1)

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
    ParamLabel1.grid(row=0, column=0, sticky=(W + E))
    ParamEntry1 = StringVar()
    ParamEntryE1 = ttk.Entry(frame8, textvariable=ParamEntry1, width=5)
    ParamEntryE1.grid(row=0, column=1, sticky=(W + E))
    ParamEntryE1.insert(END, "0.0")

    Param2 = StringVar()
    Param2.set('Y : ')
    ParamLabel2 = ttk.Label(frame8, textvariable=Param2)
    ParamLabel2.grid(row=1, column=0, sticky=(W + E))
    ParamEntry2 = StringVar()
    ParamEntryE2 = ttk.Entry(frame8, textvariable=ParamEntry2, width=5)
    ParamEntryE2.grid(row=1, column=1, sticky=(W + E))
    ParamEntryE2.insert(END, "0.0")

    Param3 = StringVar()
    Param3.set('Z : ')
    ParamLabel3 = ttk.Label(frame8, textvariable=Param3)
    ParamLabel3.grid(row=2, column=0, sticky=(W + E))
    ParamEntry3 = StringVar()
    ParamEntryE3 = ttk.Entry(frame8, textvariable=ParamEntry3, width=5)
    ParamEntryE3.grid(row=2, column=1, sticky=(W + E))
    ParamEntryE3.insert(END, "0.0")

    Param4 = StringVar()
    Param4.set('拡大率 : ')
    ParamLabel4 = ttk.Label(frame8, textvariable=Param4)
    ParamLabel4.grid(row=3, column=0, sticky=(W + E))
    ParamEntry4 = StringVar()
    ParamEntryE4 = ttk.Entry(frame8, textvariable=ParamEntry4, width=5)
    ParamEntryE4.grid(row=3, column=1, sticky=(W + E))
    ParamEntryE4.insert(END, "100.0")

    Param5 = StringVar()
    Param5.set('透明度 : ')
    ParamLabel5 = ttk.Label(frame8, textvariable=Param5)
    ParamLabel5.grid(row=4, column=0, sticky=(W + E))
    ParamEntry5 = StringVar()
    ParamEntryE5 = ttk.Entry(frame8, textvariable=ParamEntry5, width=5)
    ParamEntryE5.grid(row=4, column=1, sticky=(W + E))
    ParamEntryE5.insert(END, "0.0")
    '''
    Param6 = StringVar()
    Param6.set('縦横比 : ')
    ParamLabel6 = ttk.Label(frame8, textvariable=Param6)
    ParamLabel6.grid(row=5, column=0, sticky=(W+E))
    ParamEntry6 = StringVar()
    ParamEntryE6 = ttk.Entry(frame8, textvariable=ParamEntry6, width=5)
    ParamEntryE6.grid(row=5, column=1, sticky=(W + E))
    ParamEntryE6.insert(END, "0.0")
    '''
    Param7 = StringVar()
    Param7.set('回転 : ')
    ParamLabel7 = ttk.Label(frame8, textvariable=Param7)
    ParamLabel7.grid(row=6, column=0, sticky=(W + E))
    ParamEntry7 = StringVar()
    ParamEntryE7 = ttk.Entry(frame8, textvariable=ParamEntry7, width=5)
    ParamEntryE7.grid(row=6, column=1, sticky=(W + E))
    ParamEntryE7.insert(END, "0.00")

    Param14 = StringVar()
    Param14.set('これ以下の項目は拡張描画用')
    ParamLabel14 = ttk.Label(frame8, textvariable=Param14)
    ParamLabel14.grid(row=7, column=0, sticky=(W + E))

    Param8 = StringVar()
    Param8.set('X軸回転 : ')
    ParamLabel8 = ttk.Label(frame8, textvariable=Param8)
    ParamLabel8.grid(row=8, column=0, sticky=(W + E))
    ParamEntry8 = StringVar()
    ParamEntryE8 = ttk.Entry(frame8, textvariable=ParamEntry8, width=5)
    ParamEntryE8.grid(row=8, column=1, sticky=(W + E))
    ParamEntryE8.insert(END, "0.00")

    Param9 = StringVar()
    Param9.set('Y軸回転 : ')
    ParamLabel9 = ttk.Label(frame8, textvariable=Param9)
    ParamLabel9.grid(row=9, column=0, sticky=(W + E))
    ParamEntry9 = StringVar()
    ParamEntryE9 = ttk.Entry(frame8, textvariable=ParamEntry9, width=5)
    ParamEntryE9.grid(row=9, column=1, sticky=(W + E))
    ParamEntryE9.insert(END, "0.00")

    Param10 = StringVar()
    Param10.set('Z軸回転 : ')
    ParamLabel10 = ttk.Label(frame8, textvariable=Param10)
    ParamLabel10.grid(row=10, column=0, sticky=(W + E))
    ParamEntry10 = StringVar()
    ParamEntryE10 = ttk.Entry(frame8, textvariable=ParamEntry10, width=5)
    ParamEntryE10.grid(row=10, column=1, sticky=(W + E))
    ParamEntryE10.insert(END, "0.00")

    Param11 = StringVar()
    Param11.set('X中心 : ')
    ParamLabel11 = ttk.Label(frame8, textvariable=Param11)
    ParamLabel11.grid(row=11, column=0, sticky=(W + E))
    ParamEntry11 = StringVar()
    ParamEntryE11 = ttk.Entry(frame8, textvariable=ParamEntry11, width=5)
    ParamEntryE11.grid(row=11, column=1, sticky=(W + E))
    ParamEntryE11.insert(END, "0.0")

    Param12 = StringVar()
    Param12.set('Y中心 : ')
    ParamLabel12 = ttk.Label(frame8, textvariable=Param12)
    ParamLabel12.grid(row=12, column=0, sticky=(W + E))
    ParamEntry12 = StringVar()
    ParamEntryE12 = ttk.Entry(frame8, textvariable=ParamEntry12, width=5)
    ParamEntryE12.grid(row=12, column=1, sticky=(W + E))
    ParamEntryE12.insert(END, "0.0")

    Param13 = StringVar()
    Param13.set('Z中心 : ')
    ParamLabel13 = ttk.Label(frame8, textvariable=Param13)
    ParamLabel13.grid(row=13, column=0, sticky=(W + E))
    ParamEntry13 = StringVar()
    ParamEntryE13 = ttk.Entry(frame8, textvariable=ParamEntry13, width=5)
    ParamEntryE13.grid(row=13, column=1, sticky=(W + E))
    ParamEntryE13.insert(END, "0.0")

    # Frame7実行
    frame7 = ttk.Frame(LFrame, padding=(0, 5))
    frame7.grid(row=8, column=0)
    s5 = StringVar()
    s5.set('* FPS : ')
    label5 = ttk.Label(frame7, textvariable=s5)
    label5.grid(row=0, column=0, sticky=(W + E))
    file5 = StringVar()
    file5_entry = ttk.Entry(frame7, textvariable=file5, width=10)
    file5_entry.grid(row=0, column=1, sticky=(W + E), padx=10)
    file5_entry.insert(END, "60")
    button6 = ttk.Button(frame7, text='実行', command=run)
    button6.grid(row=0, column=2)

    file1.set("D:/Reaper_Media/Editing Project/rpptest.rpp")
    file2.set("D:/Aviutl  編集ファイル/RPP_to_EXO/test.exo")

    root.mainloop()
