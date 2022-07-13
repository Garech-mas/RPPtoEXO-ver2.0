#####################################################################################
#               RPP to EXO ver 1.08                                                 #
#                                                                       2022/07/13  #
#       Written by Maimai (@Maimai22015/YTPMV.info)                                 #
#                                                                                   #
#                                                                                   #
#       協力：SHI(@sbt54864666), Garech(@Garec_)                                    #
#####################################################################################

import os
import sys
import configparser
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import binascii

EffDict = {
    #   "効果名"        :       [["設定１","デフォルト設定"],["設定２","デフォルト設定"],["設定３","デフォルト設定"]], 各設定3つ目に-1でチェックボックス
    "座標": [["X", 0.0], ["Y", 0.0], ["Z", 0.0]],
    "拡大率": [["拡大率", 100.00], ["X", 100.00], ["Y", 100.00]],
    "透明度": [["透明度", 0.0]],
    "回転": [["X", 0.0], ["Y", 0.0], ["Z", 0.0]],
    "リサイズ": [["拡大率", 100.00], ["X", 100.00], ["Y", 100.00], ["補間なし", 0, -1], ["ドット数でサイズ指定", 0, -1]],
    "反転": [["上下反転", 0, -1], ["左右反転", 0, -1], ["輝度反転", 0, -1], ["色相反転", 0, -1], ["透明度反転", 0, -1]],
    #チェックボック項目がある効果設定時に”効果のクリア”をするとバグる。
    "色調補正": [["明るさ", 100.0], ["ｺﾝﾄﾗｽﾄ", 100.0], ["色相", 0.0], ["輝度", 100.0], ["彩度", 100.0], ["飽和する", 0, -1]],
    "クリッピング": [["上", 0], ["下", 0], ["左", 0], ["右", 0], ["中心の位置を変更", 0, -1]],
    "クロマキー": [["色相範囲", 24], ["彩度範囲", 96], ["境界補正", 1], ["色彩補正", 0, -1], ["透過補正", 0, -1], ["color_yc", "cf010008b3fe"], ["status", 1]],
    # とりあえず青色透過。デフォ設定は0000000000(未設定)とかだったはず。
    "縁取り": [["サイズ", 3], ["ぼかし", 10], ["color", 000000], ["file", ""]],
    "マスク": [["X", 0.0], ["Y", 0.0], ["回転", 0.00], ["サイズ", 100], ["縦横比", 0.0], ["ぼかし", 0], ["マスクの反転", 0, -1], ["元のサイズに合わせる", 0, -1], ["type", 2], ["name", ""], ["mode", 0]],
    "放射ブラー": [["範囲", 20.0], ["X", 0], ["Y", 0], ["サイズ固定", 0, -1]],
    "方向ブラー": [["範囲", 20], ["角度", 50.0], ["サイズ固定", 0, -1]],
    "振動": [["X", 10], ["Y", 10], ["Z", 0], ["周期", 1], ["ランダムに強さを変える", 1, -1], ["複雑に振動", 0, -1]],
    "ミラー": [["透明度", 0.0], ["減衰", 0.0], ["境目調整", 0], ["中心の位置を変更", 1, -1], ["type", 1]],
    # type ミラー方向 上：0 下:1 左:2 右:3 中心位置変更のデフォは0
    "ラスター": [["横幅", 100], ["高さ", 100], ["周期", 1.00], ["縦ラスター", 0], ["ランダム振幅", 0]],
    "波紋": [["中心X", 0], ["中心Y", 0], ["幅", 30.0], ["高さ", 15.0], ["速度", 150], ["num", 0], ["interval", 0], ["add", 0]],
    "ディスプレイスメントマップ": [["param0", 0.0], ["param1", 0.0], ["X", 0.0], ["Y", 0.0], ["回転", 0.00], ["サイズ", 200], ["縦横比", 0.0], ["ぼかし", 5], ["元のサイズに合わせる", 0], ["type", 1], ["name", ""], ["mode", 0], ["calc", 0]],
    "色ずれ": [["ずれ幅", 5], ["角度", 0.0], ["強さ", 100], ["type", 0]],
    "アニメーション効果": [["track0", 0.00], ["track1", 0.00], ["track1", 0.00], ["track2", 0.00], ["track3", 0.00], ["check0", 0], ["type", 0], ["filter", 0], ["name", ""], ["param", ""]],
}

MyDict = {
    # 基本設定
    "fps":   60,
    "RPPPath":   "test.rpp",
    "EXOPath":   "test.exo",
    "SrcPath":   "C:\\",  # ファイルパス。絶対パスが必要。
    "EffPath":   "C:\\", #効果をファイルで保存する時用
    "SrcPosition":   1,  # 再生位置
    "SrcRate":   100,  # 再生速度
    "IsAlpha":   0,  # アルファチャンネルを読み込む
    "IsLoop":   0,  # ループ再生
    "X":   0.0,  # x座標
    "Y":   0.0,  # y座標
    "Z":   0.0,  # z座標
    "Size":   100.0,  # 拡大率
    "Rotation":   0.0,  # 回転
    "Alpha":   0.0,
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
    "Effect":   [
        #   ["EffName",["ConfName1","Conf"],["ConfName2","Conf"]],
    ],
    "EffNum": 0,  # 現時点で追加されているパラメータ数（GUI用）
    "EffCount": 0,  # エフェクト数（GUI用）
    "EffCount2": 0,
    "EffCbNum": 0,  # パラメータ　チェックボックスの数

    # 独自設定
    "IsFlipHEvenObj": 0,  # 偶数オブジェクトを左右反転するか
    "IsAddFilterAsMediaObj": 0,  # 動画ファイルとしてでなく
    "IsExSet": 0,  # 拡張描画を有効にするか

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


def EXOAddEff(MyDict, ItemCount):
    count = 1
    EXOEffects = ""
    for eff in MyDict["Effect"]:
        EXOEffects += "\n["+str(ItemCount)+"." + \
            str(count)+"]\n_name="+str(eff[0])
        for x in range(1, len(eff)):
            EXOEffects += "\n"+str(eff[x][0])+"="+str(eff[x][1])
        count += 1
    return EXOEffects


def SettingEffCUI():
    # CUI用基本設定
    ans = input("RPPのファイル名(相対パス可): ")
    MyDict["RPPPath"] = ans
    ans = input("EXOのファイル名: ")
    MyDict["EXOPath"] = ans + ".exo"
    ans = input("動画素材を適用するかメディアオブジェクトとしてフィルタのみを追加するか[動画素材:0/フィルタのみ:1]")
    MyDict["IsAddFilterAsMediaObj"] = int(ans)
    if MyDict["IsAddFilterAsMediaObj"] == 0:
        ans = input("素材のファイル名(絶対パスのみ): ")
        MyDict["SrcPath"] = ans
    ans = input("EXOを読み込むAviutlのプロジェクトのfps: ")
    MyDict["fps"] = int(ans)
    ans = input("左右反転をしますか？[y:1/n:0]: ")
    MyDict["IsFlipHEvenObj"] = int(ans)
    # 今後合成モードとかの設定を可能にする（GUIを作る場合）

    # CUI用フィルタ追加設定
    effcount = 0
    while True:
        ans1 = input("フィルタ効果を追加しますか？[y/n]: ")
        if ans1 == "n":
            break
        elif ans1 == "y":
            ans2 = input("設定するフィルタ効果を入力 (hで選択可能なフィルタ効果を表示): ")
            if ans2 == "h":
                print(EffDict.keys())
            elif ans2 in EffDict:
                print("\nメモ：パラメータを変化させる際は開始点,終点,移動方法のように設定してください。\n例：0.00,100.00,1\n移動方法について\n直線移動 : 1\n加減速移動 : 103\n曲線移動 : 2\n.tra : 15@スクリプト名@設定番号\n")
                MyDict["Effect"].append([])
                MyDict["Effect"][effcount].append(ans2)
                for eff in EffDict[ans2]:
                    eff[1] = input(
                        str(eff[0]) + " (デフォルト:"+str(eff[1])+") (同じフォーマットで入力してね) : ")
                    MyDict["Effect"][effcount].append(eff)
                effcount += 1


def LoadEffectFromFile(Itemcount):
    LEFFcount = 0
    returntext = "\n"
    with open(str(MyDict["EffPath"]), mode='r', encoding='UTF-8', errors='replace') as f:
        for line in f:
            if LEFFcount == 0 and line != "[0.1]\n":
                print(line)
                messagebox.showinfo("エラー", "効果を記入したファイルに問題あり。取説参照")
            if line[0] == "[":
                line = "[" + str(Itemcount) + "." + \
                    str(len(MyDict["Effect"]) + 1 + LEFFcount) + "]\n"
                LEFFcount += 1
            returntext += line
    return returntext, LEFFcount

def AddScriptControl(Itemcount,EffNumber):
    TmpText=""
    ScriptText=""
    TmpText ="\n["+str(Itemcount)+"."+str(EffNumber)+"]\n_name=スクリプト制御\ntext="
    #スクリプト制御を追加するためのその場しのぎ関数。こんなやり方じゃいつか詰むぞ
    ScriptText=file10_text.get('1.0', 'end-1c')
    print(ScriptText)
    ScriptText=binascii.hexlify(ScriptText.encode("UTF-16LE"))
    ScriptText=str(ScriptText)[:-1][2:]
    ScriptText = ScriptText+"0"*(4096-len(str(ScriptText)))
    ##########################EXOの形式への変換とReturn　TODO
    return TmpText+ScriptText



def main():

    bf = 0.0  # アイテム一つ前の最終フレーム  ==Endframe
    layer = 0  # オブジェクトのあるレイヤー（RPP上で複数トラックある場合は別トラックに配置する）
    MediaItemsP = [-1]
    MediaItemsL = [-1]

    # EXOの設定
    EXO = "[exedit]\nwidth="+str(1280)+"\nheight="+str(720)+"\nrate="+str(
        60)+"\nscale=1\nlength=10914\naudio_rate=44100\naudio_ch=2"
    ItemCount = 0
    exo_1 = "\n["  # ItemCount
    exo_2 = "]\nstart="  # StartFrame
    exo_3 = "\nend="  # EndFrame
    exo_4 = "\nlayer="  # layer
    exo_4_2 = "\ngroup=1\noverlay=1\nclipping=" + \
        str(MyDict["clipping"])+"\ncamera=0\n["  # Itemcount
    exo_5 = ".0]\n_name=動画ファイル\n再生位置="+str(MyDict["SrcPosition"])+"\n再生速度="+str(MyDict["SrcRate"]) +                   \
        "\nループ再生="+str(MyDict["IsLoop"])+"\nアルファチャンネルを読み込む=" + \
        str(MyDict["IsAlpha"])+"\nfile="+str(MyDict["SrcPath"])
    if str(v10.get()) == str(1): #画像オブジェクトの場合の処理 （あまり正しくない書き方。）
         exo_5 = ".0]\n_name=画像ファイル\nfile="+str(MyDict["SrcPath"])
    if str(v11.get()) == str(1): #シーンオブジェクトの場合の処理
         exo_5 = ".0]\n_name=シーン\n再生位置=" + str(MyDict["SrcPosition"]) + "\n再生速度=" + str(MyDict["SrcRate"]) + \
                 "\nループ再生=" + str(MyDict["IsLoop"]) + "\nscene=" + str(MyDict["SceneIdx"])

    # この間にエフェクトの設定
    exo_6 = "\n["  # ItemCount
    # exo_7 ItemCountによる分岐のため後のループ内で記述
    exo_7 = ""

    exo_eff = ""  # エフェクト設定用、先に宣言だけしておく。ItemCountを必要とするから後のループ内で処理
    exo_script="" #スクリプト制御用

    # RPPからのPOSITIOとLENGTHの読み込み。すべて<ITEMの次、３行後にあるものとする。
    with open(MyDict["RPPPath"], mode='r', encoding='CP932', errors='replace') as f:
        RPP = f.readlines()


        #SHI 氏のトラック選択機能追加による文は ##トラック　を追記
        trackIndex=0 ##トラック

        for index in range(len(RPP)):

            if RPP[index].find("<TRACK") != -1: ##トラック
                trackIndex+=1 ##トラック
                if MediaItemsP[-1] != -1:  # トラックが切り替わる位置に-1を入れる
                    MediaItemsP.append(-1)
                    MediaItemsL.append(-1)

            if MyDict["Track"]==None or trackIndex in MyDict["Track"] :  ##トラック
               if  RPP[index].find("<ITEM") != -1:

                    if RPP[index+1].find("POSITION") != -1 and RPP[index+3].find("LENGTH") != -1:
                        MediaItemsP.append(
                            float(RPP[index+1].split("POSITION ")[1][:-1]))
                        MediaItemsL.append(
                            float(RPP[index+3].split("LENGTH ")[1][:-1]))
                    else:
                        print("異常:RPPが変")

    # オブジェクト最初のフレームと長さの計算
    for index in range(len(MediaItemsL)):
        LEFFcount = 0
        ASCCount = 0
        # EXO+=exo_1+str(ItemCount)+exo_2+exo_3+exo_4+str(ItemCount)+exo_5+exo_6+str(ItemCount)+exo_7

        FramePosition = MediaItemsP[index]*float(MyDict["fps"]) + 1
        FramePositionN = MediaItemsP[index+1] * float(MyDict["fps"]) + 1 if index != len(MediaItemsL) - 1 else -1
        FrameLength = MediaItemsL[index] * float(MyDict["fps"])

        if round(FramePosition) == bf:  # 一つ前のオブジェクトとフレームがかぶらないようにする処理
            FramePosition += 1
            FrameLength -= 1
        if round(FramePosition + FrameLength) == round(FramePositionN)-1:  # 一つ後のオブジェクトとの間に1フレームの空きがある場合の処理
            FrameLength += 1

        if FramePosition < bf:
            bf = 0
            layer += 1 + int(v7.get())
            if FramePosition < 0: continue
        bf = FramePosition + FrameLength - 1

        # 隙間なく配置するための処理
        if v9.get() == "1":
            if FramePosition < round(FramePositionN) - 1:
                bf = FramePositionN-1
        FramePosition = round(FramePosition)
        if FramePosition == 0: FramePosition = 1
        bf = round(bf)

        exo_eff = ""

        # エフェクトを追加している場合の設定
        if len(MyDict["Effect"]) != 0:
            exo_eff += EXOAddEff(MyDict, ItemCount)
        # ファイルから効果を読み込む設定
        if MyDict["EffPath"] != "":
            a, b = LoadEffectFromFile(ItemCount)
            exo_eff += a
            LEFFcount += b
        # 偶数番目オブジェクトをひとつ下のレイヤに配置する
        if str(v7.get()) == str(1) and ItemCount % 2 == 1:
            exo_4 = "\nlayer=" + str(layer + 1)  # layer
        else:
            exo_4 = "\nlayer=" + str(layer)
        # 左右反転を有効にしている場合の処理
        if int(MyDict["IsFlipHEvenObj"]) == 1 and ItemCount % 2 == 0 and int(MyDict["IsAddFilterAsMediaObj"]) == 0:  # 動画ファイル適用 左右反転あり
            exo_eff += "\n[" + str(ItemCount) + "." + str(len(MyDict["Effect"]) + 1+LEFFcount) + \
                "]\n_name=反転\n上下反転=0\n左右反転=1\n輝度反転=0\n色相反転=0\n透明度反転=0"
            if file10_text.get('1.0', 'end-1c')!="": #スクリプト制御追加する場合
                exo_script=AddScriptControl(ItemCount,len(MyDict["Effect"]) + 2+LEFFcount)
                ASCCount =1

            if MyDict["IsExSet"] == "0":
                exo_7 = "." + str(len(MyDict["Effect"])+2+ASCCount+LEFFcount)+"]\n_name=標準描画\nX="+str(
                    MyDict["X"])+"\nY="+str(MyDict["Y"])+"\nZ="+str(MyDict["Z"])+"\n拡大率="+str(MyDict["Size"])+"\n透明度="+str(MyDict["Alpha"]) + \
                    "\n回転=" + str(MyDict["Rotation"]) + \
                    "\nblend=" + str(MyDict["Blend"])
            elif MyDict["IsExSet"] == "1":  # 拡張描画の場合
                exo_7 = "." + str(len(MyDict["Effect"])+2+ASCCount+LEFFcount)+"]\n_name=拡張描画\nX="+str(
                    MyDict["X"])+"\nY="+str(MyDict["Y"])+"\nZ="+str(MyDict["Z"])+"\n拡大率="+str(MyDict["Size"])+"\n透明度="+str(MyDict["Alpha"]) + \
                    "\n縦横比=0.0\nX軸回転=" + str(MyDict["XRotation"]) + "\nY軸回転=" + str(MyDict["YRotation"]) +\
                    "\nZ軸回転=" + str(MyDict["ZRotation"]) + "\n中心X=" + str(MyDict["XCenter"]) + "\n中心Y=" + str(MyDict["YCenter"]) + \
                    "\n中心Z=" + str(MyDict["ZCenter"]) + \
                    "\n裏面を表示しない=0\nblend=" + str(MyDict["Blend"])

            EXO = (EXO+exo_1+str(ItemCount)+exo_2+str(FramePosition)+exo_3+str(bf) +
                   exo_4+exo_4_2+str(ItemCount)+exo_5+exo_eff+exo_script+exo_6+str(ItemCount)+exo_7)
        elif int(MyDict["IsAddFilterAsMediaObj"]) == 0 and (int(MyDict["IsFlipHEvenObj"]) == 0 or ItemCount % 2 != 0):
            # 動画ファイル適用 左右反転なし
            if file10_text.get('1.0', 'end-1c')!="": #スクリプト制御追加する場合
                exo_script=AddScriptControl(ItemCount,len(MyDict["Effect"]) + 1+LEFFcount)
                ASCCount =1
            exo_7 = "." + str(len(MyDict["Effect"]) +ASCCount+ 1+LEFFcount) + "]\n_name=標準描画\nX=" + str(MyDict["X"]) + "\nY=" + str(MyDict["Y"]) + "\nZ=" + str(
                MyDict["Z"]) + "\n拡大率=" + str(MyDict["Size"]) + "\n透明度=" + str(MyDict["Alpha"]) + "\n回転=" + str(MyDict["Rotation"]) + "\nblend=" + str(MyDict["Blend"])
            if MyDict["IsExSet"] == "1":  # 拡張描画の場合
                exo_7 = "." + str(len(MyDict["Effect"])+1+LEFFcount)+"]\n_name=拡張描画\nX="+str(
                    MyDict["X"])+"\nY="+str(MyDict["Y"])+"\nZ="+str(MyDict["Z"])+"\n拡大率="+str(MyDict["Size"])+"\n透明度="+str(MyDict["Alpha"]) + \
                    "\n縦横比=0.0\nX軸回転=" + str(MyDict["XRotation"]) + "\nY軸回転=" + str(MyDict["YRotation"]) +\
                    "\nZ軸回転=" + str(MyDict["ZRotation"]) + "\n中心X=" + str(MyDict["XCenter"]) + "\n中心Y=" + str(MyDict["YCenter"]) + \
                    "\n中心Z=" + str(MyDict["ZCenter"]) + \
                    "\n裏面を表示しない=0\nblend=" + str(MyDict["Blend"])
            EXO = (EXO+exo_1+str(ItemCount)+exo_2+str(FramePosition)+exo_3+str(bf) + exo_4 +
                   exo_4_2 + str(ItemCount) + exo_5 + exo_eff +exo_script+ exo_6 + str(ItemCount) + exo_7)
        elif int(MyDict["IsAddFilterAsMediaObj"]) == 1 and (int(MyDict["IsFlipHEvenObj"]) == 0 or ItemCount % 2 != 0):
            # フィルタのみの場合 左右反転なし
            if file10_text.get('1.0', 'end-1c')!="": #スクリプト制御追加する場合
                exo_script=AddScriptControl(ItemCount,len(MyDict["Effect"]) + 1+LEFFcount)
                ASCCount =1
            exo_4_2 = "\ngroup=1\noverlay=1"
            # 何も効果がかかっていないとエラー吐くので（多分）とりあえず座標0,0,0を掛けておく
            exo_5 = "\n["+str(ItemCount)+".0]\n_name=座標\nX=0.0\nY=0.0\nZ=0.0"
            EXO = (EXO+exo_1+str(ItemCount)+exo_2+str(FramePosition) +
                   exo_3+str(bf) + exo_4 + exo_4_2 + exo_5 + exo_eff+exo_script)
        elif int(MyDict["IsFlipHEvenObj"]) == 1 and ItemCount % 2 == 0 and int(MyDict["IsAddFilterAsMediaObj"]) == 1:
            # フィルタのみの場合 左右反転あり
            if file10_text.get('1.0', 'end-1c')!="": #スクリプト制御追加する場合
                exo_script=AddScriptControl(ItemCount,len(MyDict["Effect"]) + 2+LEFFcount)
                ASCCount =1
            exo_4_2 = "\ngroup=1\noverlay=1"
            exo_5 = "\n["+str(ItemCount)+".0]\n_name=座標\nX=0.0\nY=0.0\nZ=0.0"
            exo_eff += "\n[" + str(ItemCount) + "." + str(len(MyDict["Effect"]) +ASCCount+ 1+LEFFcount) + \
                "]\n_name=反転\n上下反転=0\n左右反転=1\n輝度反転=0\n色相反転=0\n透明度反転=0"
            EXO = (EXO+exo_1+str(ItemCount)+exo_2+str(FramePosition) +
                   exo_3+str(bf) + exo_4 + exo_4_2 + exo_5 + exo_eff+exo_script)

        ItemCount = ItemCount + 1

    with open(MyDict["EXOPath"], mode='w', encoding='shift_jis') as f:
        f.write(EXO)
        messagebox.showinfo("正常終了", "多分正常に生成されました")


def ReadConf():  # 設定読み込み
    config_ini_path = "config.ini"
    if os.path.exists(config_ini_path):
        config_ini = configparser.ConfigParser()
        config_ini.read(config_ini_path, encoding='utf-8')
        MyDict["RPPLastDir"] = config_ini.get("Directory", "RPPDir")
        MyDict["EXOLastDir"] = config_ini.get("Directory", "EXODir")
        MyDict["SrcLastDir"] = config_ini.get("Directory", "SrcDir")
    return 0


def WriteConf(filepath, SettingType):  # 設定保存
    config_ini_path = "config.ini"
    if os.path.exists(config_ini_path):
        config_ini = configparser.ConfigParser()
        config_ini.read(config_ini_path, encoding='utf-8')
        config_ini.set("Directory", SettingType, os.path.dirname(filepath))
        with open('config.ini', 'w', encoding='utf-8') as file:
            config_ini.write(file)


def RPPSelelctBtn():  # 参照ボタン
    Ftype = [("REAPERプロジェクトファイル", "*.rpp")]
    filepath = filedialog.askopenfilename(
        filetypes=Ftype, initialdir=MyDict["RPPLastDir"])
    if filepath != '':
        file1.set(filepath)
        WriteConf(filepath, "RPPDir")
        LoadTrackName()


def SelectSrc():  # 素材選択
    Ftype = [("動画ファイル", "*")]
    filepath = filedialog.askopenfilename(
        filetypes=Ftype, initialdir=MyDict["SrcLastDir"])
    if filepath != '':
        file4.set(filepath)
        WriteConf(filepath, "SrcDir")


def SelectEffConf():  # 効果設定ファイル読み込み
    Ftype = [("ファイル", "*")]
    filepath = filedialog.askopenfilename(
        filetypes=Ftype, initialdir=MyDict["EXOLastDir"])
    file9.set(filepath)


def EXOSaveBtn():  # EXO保存ボタン
    Ftype = [("Aviutlオブジェクトファイル", "*.exo")]
    filepath = filedialog.asksaveasfilename(
        initialdir=MyDict["EXOLastDir"], title="EXOファイル保存場所の選択", filetypes=Ftype)
    if filepath != '':
        if filepath.endswith(".exo") == False:
            filepath += ".exo"
        file2.set(filepath)
        WriteConf(filepath, "EXODir")

def LoadTrackName():  # トラック名読み込み
    filePath = file1_entry.get().replace('"', '') if file1_entry.get()[0]=="\"" else file1_entry.get() # パスをコピペした場合のダブルコーテーションを削除
    if ".rpp" in filePath.lower():
        trackList = []
        trackList.append("ﾄﾗｯｸ選択無")

        with open(filePath, mode='r', encoding='UTF-8', errors='replace') as f:
            RPP = f.readlines()
            trackIndex = 0
            for index in range(len(RPP)):
                trackFind = RPP[index].find("<TRACK")
                if trackFind != -1:
                    trackIndex += 1
                    trackList.append(str(trackIndex)+ ": " + RPP[index+1][9:])

        file8_combo.set("ﾄﾗｯｸ選択無")
        file8_combo.config(values=trackList)

    return True


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


def AddEffect():
    # エフェクト名ラベル
    hLabel.append(StringVar())
    hLabel[MyDict["EffCount"]+MyDict["EffNum"]].set(v2.get())
    b = ttk.Label(
        frame6, textvariable=hLabel[MyDict["EffCount"]+MyDict["EffNum"]])
    b.grid(row=MyDict["EffCount"]+MyDict["EffNum"] +
           MyDict["EffCbNum"], column=0)
    hLabel2.append(b)

    # 始点終点ラベル
    hSELabel.append(StringVar())
    hSELabel[MyDict["EffCount2"]].set("始点")
    b = ttk.Label(
        frame6, textvariable=hSELabel[MyDict["EffCount2"]])
    b.grid(row=MyDict["EffCount"]+MyDict["EffNum"] +
           MyDict["EffCbNum"], column=1)
    hSELabelE.append(b)
    MyDict["EffCount2"] += 1
    hSELabel.append(StringVar())
    hSELabel[MyDict["EffCount2"]].set("終点")
    b = ttk.Label(
        frame6, textvariable=hSELabel[MyDict["EffCount2"]])
    b.grid(row=MyDict["EffCount"]+MyDict["EffNum"] +
           MyDict["EffCbNum"], column=3)
    hSELabelE.append(b)
    MyDict["EffCount2"] += 1
    hSELabel.append(StringVar())
    hSELabel[MyDict["EffCount2"]].set("設定")
    b = ttk.Label(
        frame6, textvariable=hSELabel[MyDict["EffCount2"]])
    b.grid(row=MyDict["EffCount"]+MyDict["EffNum"] +
           MyDict["EffCbNum"], column=4)
    hSELabelE.append(b)
    MyDict["EffCount2"] += 1

    MyDict["Effect"].append([])
    MyDict["Effect"][MyDict["EffCount"]].append(v2.get())
    MyDict["EffCount"] += 1
    # EffDict[v2.get()]回分ループ
    for n in range(len(EffDict[v2.get()])):
        if EffDict[v2.get()][n][-1] == -1:
            hCheckBox.append(StringVar())
            hCheckBox[MyDict["EffCbNum"]].set(0)
            hCheckBoxCb.append(ttk.Checkbutton(
                frame6,
                padding=0,
                text=EffDict[v2.get()][n][0],
                onvalue=1,
                offvalue=0,
                variable=hCheckBox[MyDict["EffCbNum"]]))
            hCheckBoxCb[MyDict["EffCbNum"]].grid(
                row=MyDict["EffNum"] + MyDict["EffCount"] + MyDict["EffCbNum"], column=1, sticky=(W))
            MyDict["EffCbNum"] += 1
        else:
            hLabel.append(StringVar())
            hLabel[MyDict["EffNum"]+MyDict["EffCount"]
                   ].set(EffDict[v2.get()][n][0])
            b = ttk.Label(
                frame6, textvariable=hLabel[MyDict["EffNum"]+MyDict["EffCount"]])
            b.grid(row=MyDict["EffNum"] + MyDict["EffCount"]+MyDict["EffCbNum"],
                   column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(
                frame6, textvariable=hEntryS[MyDict["EffNum"]], width=5))
            hEntrySE[MyDict["EffNum"]].grid(
                row=MyDict["EffNum"] + MyDict["EffCount"] + MyDict["EffCbNum"], column=1, padx=5)
            hEntrySE[MyDict["EffNum"]].insert(END, EffDict[v2.get()][n][1])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(
                frame6, textvariable=hEntryX[MyDict["EffNum"]]))
            hEntryXCb[MyDict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[MyDict["EffNum"]].set("移動なし")
            hEntryXCb[MyDict["EffNum"]].grid(
                row=MyDict["EffNum"] + MyDict["EffCount"]+MyDict["EffCbNum"], column=2, padx=5)

            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(
                frame6, textvariable=hEntryE[MyDict["EffNum"]], width=5))
            hEntryEE[MyDict["EffNum"]].grid(
                row=MyDict["EffNum"] + MyDict["EffCount"] + MyDict["EffCbNum"], column=3, padx=5)

            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(
                frame6, textvariable=hEntryConf[MyDict["EffNum"]], width=5))
            hEntryConfE[MyDict["EffNum"]].grid(
                row=MyDict["EffNum"] + MyDict["EffCount"] + MyDict["EffCbNum"], column=4, padx=5)

            MyDict["EffNum"] += 1


def DelEffect():  # 効果パラメータ入力画面破棄
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
    MyDict["Effect"] = []
    MyDict["EffCount"] = 0
    MyDict["EffCount2"] = 0
    MyDict["EffNum"] = 0
    MyDict["EffCbNum"] = 0
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


def Run():
    MyDict["RPPPath"] = file1.get().replace('"', '') if file1.get()[0]=="\"" else file1.get()
    MyDict["EXOPath"] = file2.get().replace('"', '') if file2.get()[0]=="\"" else file2.get()
    MyDict["IsAddFilterAsMediaObj"] = v1.get()
    MyDict["SrcPath"] = "" if file4.get() == "" else file4.get().replace('"', '') if  file4.get()[0]=="\"" else file4.get()
    MyDict["EffPath"] = "" if file9.get() == "" else file9.get().replace('"', '') if  file9.get()[0]=="\"" else file9.get()
    MyDict["IsAlpha"] = v4.get()
    MyDict["IsLoop"] = v5.get()
    MyDict["SrcPosition"] = file6.get()
    MyDict["fps"] = file5.get()
    MyDict["IsFlipHEvenObj"] = v3.get()
    MyDict["clipping"] = v6.get()
    MyDict["IsExSet"] = v8.get()
    MyDict["X"] = ParamEntry1.get()
    MyDict["Y"] = ParamEntry2.get()
    MyDict["Z"] = ParamEntry3.get()
    MyDict["Size"] = ParamEntry4.get()
    MyDict["Alpha"] = ParamEntry5.get()
    MyDict["Rotation"] = ParamEntry7.get()
    MyDict["XRotation"] = ParamEntry8.get()
    MyDict["YRotation"] = ParamEntry9.get()
    MyDict["ZRotation"] = ParamEntry10.get()
    MyDict["XCenter"] = ParamEntry11.get()
    MyDict["YCenter"] = ParamEntry12.get()
    MyDict["ZCenter"] = ParamEntry13.get()
    MyDict["SceneIdx"] = int(file11.get() or 0)

    ##トラック
    findColon = file8disp.get().find(':')
    if ':' in file8disp.get():
        file8 = StringVar(value=file8disp.get()[:findColon])  # file8にdispの内容を保存。この先の処理との互換維持
    else:
        file8 = file8disp

    if file8.get()!="ﾄﾗｯｸ選択無":
        track=file8.get().split(",")

        MyDict["Track"]=[]
        for  t in track:
            if t.isdecimal():
                MyDict["Track"].append(int(t))
    else:
        MyDict["Track"]=None
    ##トラック

    if MyDict["RPPPath"] == "" or MyDict["EXOPath"] == "" or MyDict["fps"] == "":
        messagebox.showinfo("エラー", "値を入力して実行")
        return 0
    if (MyDict["SceneIdx"] <= 0 or MyDict["SceneIdx"] > 100) and v11.get() == "1":
        messagebox.showinfo("エラー", "正しいシーン番号を入力")
        return 0
    if v10.get() == "1" and v11.get() == "1":
        messagebox.showinfo("エラー", "画像/シーンとして配置オプションはどちらか一つを選択")
        return 0

    count = MyDict["EffCount"]
    runcount = 0
    runcountcb = 0
    eff = ""
    for i in range(0, int(count)):
        # runcount += 1
        del MyDict["Effect"][i][1:]
        for x in range(len(EffDict[MyDict["Effect"][i][0]])):
            if EffDict[MyDict["Effect"][i][0]][x][-1] != -1:  # チェックボックスでない場合
                if hEntryX[runcount].get() == "移動なし":  # 移動なしの場合
                    eff = [EffDict[MyDict["Effect"][i][0]][x][0],
                           str(hEntryS[runcount].get())]
                    MyDict["Effect"][i].append(eff)
                else:  # 移動ありの場合
                    if str(hEntryE[runcount].get()) == "":
                        messagebox.showinfo("エラー", "値を入力して実行")
                        return 0
                    eff = [EffDict[MyDict["Effect"][i][0]][x][0],
                           str(hEntryS[runcount].get())+","+str(hEntryE[runcount].get())+","+str(XDict[hEntryX[runcount].get()])]
                    if XDict[hEntryX[runcount].get()] != "":
                        eff[1] += str(hEntryConf[runcount].get())
                        messagebox.showinfo(
                            "注意", "AviUtlのバグのため設定の値は反映されません。インポート後設定してください\n拡張編集0.93rc か patch.aul導入済 の環境は影響を受けません")
                    if XDict[hEntryX[runcount].get()] != "" and hEntryConf[runcount].get() != "":
                        eff = [EffDict[MyDict["Effect"][i][0]][x][0],
                               str(hEntryS[runcount].get())+","+str(hEntryE[runcount].get())+","+str(XDict[hEntryX[runcount].get()])+","+str(hEntryConf[runcount].get())]
                    MyDict["Effect"][i].append(eff)
                runcount += 1
            elif EffDict[MyDict["Effect"][i][0]][x][-1] == -1:  # チェックボックスの場合
                eff = [EffDict[MyDict["Effect"][i][0]][x][0],
                       str(hCheckBox[runcountcb].get())]
                MyDict["Effect"][i].append(eff)
                runcountcb += 1
    main()


if __name__ == '__main__':
    ReadConf()
    # root
    root = Tk()
    root.title('RPPtoEXO')
    root.columnconfigure(1, weight=1)

    LFrame = ttk.Frame(root)
    LFrame.grid(row=0, column=0)
    CFrame = ttk.Frame(root)
    CFrame.grid(row=0, column=1)
    RFrame = ttk.Frame(root)
    RFrame.grid(row=0, column=2)
    # そのうちスクロールウィンドウに対応したい（やりかたがわからない）

    # Frame1 RPP選択
    frame1 = ttk.Frame(LFrame, padding=10)
    frame1.grid(row=0, column=0, sticky=(N))
    button1 = ttk.Button(frame1, text='参照',command=RPPSelelctBtn)
    button1.grid(row=0, column=2)
    s1 = StringVar()
    s1.set('.RPP : ')
    label1 = ttk.Label(frame1, textvariable=s1)
    label1.grid(row=0, column=0)
    file1 = StringVar()
    val_cmd = root.register(LoadTrackName)
    file1_entry = ttk.Entry(frame1, textvariable=file1, width=50, validate='focusout', validatecommand=val_cmd)
    file1_entry.grid(row=0, column=1)
    frame1.rowconfigure(0, weight=1)

    # Frame2 EXO指定
    frame2 = ttk.Frame(LFrame, padding=10)
    frame2.grid(row=1, column=0)
    button2 = ttk.Button(frame2, text='参照', command=EXOSaveBtn)
    button2.grid(row=1, column=2)
    s2 = StringVar()
    s2.set('.EXO : ')
    label2 = ttk.Label(frame2, textvariable=s2)
    label2.grid(row=1, column=0)
    file2 = StringVar()
    file2_entry = ttk.Entry(frame2, textvariable=file2, width=50)
    file2_entry.grid(row=1, column=1)

    # Frame3 IsAddFilterAsMediaObj IsFlipHEvenObj FPS他
    frame3 = ttk.Frame(LFrame, padding=10)
    frame3.grid(row=2, column=0)
    v1 = StringVar()
    v1.set(0)
    cb1 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='フィルタのみを追加する',
        onvalue=1,
        offvalue=0,
        variable=v1)
    cb1.grid(row=0, column=0, sticky=(W))

    s5 = StringVar()
    s5.set('FPS : ')
    label5 = ttk.Label(frame3, textvariable=s5)
    label5.grid(row=0, column=3, sticky=(W+E))
    file5 = StringVar()
    file5_entry = ttk.Entry(frame3, textvariable=file5, width=3)
    file5_entry.grid(row=0, column=4, sticky=(W + E))
    file5_entry.insert(END, "60")

    s6 = StringVar()
    s6.set('再生位置 : ')
    label6 = ttk.Label(frame3, textvariable=s6)
    label6.grid(row=1, column=3, sticky=(W+E))
    file6 = StringVar()
    file6_entry = ttk.Entry(frame3, textvariable=file6, width=3)
    file6_entry.grid(row=1, column=4, sticky=(W + E))
    file6_entry.insert(END, "1")

    s10 = StringVar()
    s10.set('ｼｰﾝ番号 : ')
    label16 = ttk.Label(frame3, textvariable=s10)
    label16.grid(row=4, column=3, sticky=(W+E))
    file11 = StringVar()
    file11_entry = ttk.Entry(frame3, textvariable=file11, width=3)
    file11_entry.grid(row=4, column=4, sticky=(W + E))
    file11_entry.insert(END, "")

   ##トラック
    s8 = StringVar()
    s8.set('トラック : ')
    label8 = ttk.Label(frame3, textvariable=s8)
    label8.grid(row=2, column=3, sticky=(W+E))
    file8disp = StringVar()
    file8_combo = ttk.Combobox(frame3, textvariable=file8disp, width=3)
    file8_combo.grid(columnspan=2, row=3, column=3, sticky=(W+E))
    file8_combo.insert(END, "")

   ##トラック

    v3 = StringVar()
    v3.set(0)
    cb2 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='左右反転',
        onvalue=1,
        offvalue=0,
        variable=v3)
    cb2.grid(row=0, column=1, sticky=(W))
    v4 = StringVar()
    v4.set(0)
    cb4 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='アルファチャンネルを読み込む',
        onvalue=1,
        offvalue=0,
        variable=v4)
    cb4.grid(row=1, column=0, sticky=(W))
    v5 = StringVar()
    v5.set(0)
    cb5 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='ループ再生',
        onvalue=1,
        offvalue=0,
        variable=v5)
    cb5.grid(row=1, column=1, sticky=(W))
    v6 = StringVar()
    v6.set(0)
    cb6 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='上のオブジェクトでクリッピング',
        onvalue=1,
        offvalue=0,
        variable=v6)
    cb6.grid(row=2, column=0, sticky=(W))
    v7 = StringVar()
    v7.set(0)
    cb7 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='偶数番目Objを別レイヤ配置',
        onvalue=1,
        offvalue=0,
        variable=v7)
    cb7.grid(row=2, column=1, sticky=(W))
    v8 = StringVar()
    v8.set(0)
    cb8 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='拡張描画',
        onvalue=1,
        offvalue=0,
        variable=v8)
    cb8.grid(row=3, column=0, sticky=(W))
    v9 = StringVar()
    v9.set(0)
    cb9 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='隙間なく配置',
        onvalue=1,
        offvalue=0,
        variable=v9)
    cb9.grid(row=3, column=1, sticky=(W))
    v10 = StringVar()
    v10.set(0)
    cb10 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='画像として配置',
        onvalue=1,
        offvalue=0,
        variable=v10)
    cb10.grid(row=4, column=0, sticky=(W))
    v11 = StringVar()
    v11.set(0)
    cb11 = ttk.Checkbutton(
        frame3,
        padding=5,
        text='シーンとして配置',
        onvalue=1,
        offvalue=0,
        variable=v11)
    cb11.grid(row=4, column=1, sticky=(W))

    # Frame4 動画素材選択
    frame4 = ttk.Frame(LFrame, padding=10)
    frame4.grid(row=3, column=0)
    button4 = ttk.Button(frame4, text='参照', command=SelectSrc)
    button4.grid(row=3, column=2)
    s4 = StringVar()
    s4.set('素材 : ')
    label4 = ttk.Label(frame4, textvariable=s4)
    label4.grid(row=3, column=0, sticky=(W))
    file4 = StringVar()
    file4_entry = ttk.Entry(frame4, textvariable=file4, width=50)
    file4_entry.grid(row=3, column=1)

    # Frame5 エフェクト追加/削除
    frame5 = ttk.Frame(LFrame, padding=10)
    frame5.grid(row=4, column=0)
    v2 = StringVar()
    cb = ttk.Combobox(frame5, textvariable=v2)
    cb['values'] = list(EffDict.keys())
    cb.set("座標")
    cb.grid(row=0, column=0)
    button5 = ttk.Button(frame5, text='+', command=AddEffect)
    button5.grid(row=0, column=1)
    button6 = ttk.Button(frame5, text='効果のクリア', command=DelEffect)
    button6.grid(row=0, column=2)

    # Frame9 効果をファイルから読み込む
    frame9 = ttk.Frame(LFrame, padding=10)
    frame9.grid(row=5, column=0)
    button7 = ttk.Button(frame9, text='参照', command=SelectEffConf)
    button7.grid(row=3, column=2)
    s7 = StringVar()
    s7.set('効果をファイルから読み込む ')
    label10 = ttk.Label(frame9, textvariable=s7)
    label10.grid(row=3, column=0, sticky=(W))
    file9 = StringVar()
    file9_entry = ttk.Entry(frame9, textvariable=file9, width=30)
    file9_entry.grid(row=3, column=1)

    #Frame10スクリプト制御
    frame10 = ttk.Frame(LFrame, padding=10)
    frame10.grid(row=6, column=0)
    s9 = StringVar()
    s9.set('スクリプト制御 ')
    label15 = ttk.Label(frame10, textvariable=s9)
    label15.grid(row=0, column=0, sticky=(W))
    file10 = StringVar()
    file10_text = Text(frame10, width=50,height=10)
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
    ParamLabel1.grid(row=0, column=0, sticky=(W+E))
    ParamEntry1 = StringVar()
    ParamEntryE1 = ttk.Entry(frame8, textvariable=ParamEntry1, width=5)
    ParamEntryE1.grid(row=0, column=1, sticky=(W + E))
    ParamEntryE1.insert(END, "0.0")

    Param2 = StringVar()
    Param2.set('Y : ')
    ParamLabel2 = ttk.Label(frame8, textvariable=Param2)
    ParamLabel2.grid(row=1, column=0, sticky=(W+E))
    ParamEntry2 = StringVar()
    ParamEntryE2 = ttk.Entry(frame8, textvariable=ParamEntry2, width=5)
    ParamEntryE2.grid(row=1, column=1, sticky=(W + E))
    ParamEntryE2.insert(END, "0.0")

    Param3 = StringVar()
    Param3.set('Z : ')
    ParamLabel3 = ttk.Label(frame8, textvariable=Param3)
    ParamLabel3.grid(row=2, column=0, sticky=(W+E))
    ParamEntry3 = StringVar()
    ParamEntryE3 = ttk.Entry(frame8, textvariable=ParamEntry3, width=5)
    ParamEntryE3.grid(row=2, column=1, sticky=(W + E))
    ParamEntryE3.insert(END, "0.0")

    Param4 = StringVar()
    Param4.set('拡大率 : ')
    ParamLabel4 = ttk.Label(frame8, textvariable=Param4)
    ParamLabel4.grid(row=3, column=0, sticky=(W+E))
    ParamEntry4 = StringVar()
    ParamEntryE4 = ttk.Entry(frame8, textvariable=ParamEntry4, width=5)
    ParamEntryE4.grid(row=3, column=1, sticky=(W + E))
    ParamEntryE4.insert(END, "100.0")

    Param5 = StringVar()
    Param5.set('透明度 : ')
    ParamLabel5 = ttk.Label(frame8, textvariable=Param5)
    ParamLabel5.grid(row=4, column=0, sticky=(W+E))
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
    ParamLabel7.grid(row=6, column=0, sticky=(W+E))
    ParamEntry7 = StringVar()
    ParamEntryE7 = ttk.Entry(frame8, textvariable=ParamEntry7, width=5)
    ParamEntryE7.grid(row=6, column=1, sticky=(W + E))
    ParamEntryE7.insert(END, "0.00")

    Param14 = StringVar()
    Param14.set('これ以下の項目は拡張描画用')
    ParamLabel14 = ttk.Label(frame8, textvariable=Param14)
    ParamLabel14.grid(row=7, column=0, sticky=(W+E))

    Param8 = StringVar()
    Param8.set('X軸回転 : ')
    ParamLabel8 = ttk.Label(frame8, textvariable=Param8)
    ParamLabel8.grid(row=8, column=0, sticky=(W+E))
    ParamEntry8 = StringVar()
    ParamEntryE8 = ttk.Entry(frame8, textvariable=ParamEntry8, width=5)
    ParamEntryE8.grid(row=8, column=1, sticky=(W + E))
    ParamEntryE8.insert(END, "0.00")

    Param9 = StringVar()
    Param9.set('Y軸回転 : ')
    ParamLabel9 = ttk.Label(frame8, textvariable=Param9)
    ParamLabel9.grid(row=9, column=0, sticky=(W+E))
    ParamEntry9 = StringVar()
    ParamEntryE9 = ttk.Entry(frame8, textvariable=ParamEntry9, width=5)
    ParamEntryE9.grid(row=9, column=1, sticky=(W + E))
    ParamEntryE9.insert(END, "0.00")

    Param10 = StringVar()
    Param10.set('Z軸回転 : ')
    ParamLabel10 = ttk.Label(frame8, textvariable=Param10)
    ParamLabel10.grid(row=10, column=0, sticky=(W+E))
    ParamEntry10 = StringVar()
    ParamEntryE10 = ttk.Entry(frame8, textvariable=ParamEntry10, width=5)
    ParamEntryE10.grid(row=10, column=1, sticky=(W + E))
    ParamEntryE10.insert(END, "0.00")

    Param11 = StringVar()
    Param11.set('X中心 : ')
    ParamLabel11 = ttk.Label(frame8, textvariable=Param11)
    ParamLabel11.grid(row=11, column=0, sticky=(W+E))
    ParamEntry11 = StringVar()
    ParamEntryE11 = ttk.Entry(frame8, textvariable=ParamEntry11, width=5)
    ParamEntryE11.grid(row=11, column=1, sticky=(W + E))
    ParamEntryE11.insert(END, "0.0")

    Param12 = StringVar()
    Param12.set('Y中心 : ')
    ParamLabel12 = ttk.Label(frame8, textvariable=Param12)
    ParamLabel12.grid(row=12, column=0, sticky=(W+E))
    ParamEntry12 = StringVar()
    ParamEntryE12 = ttk.Entry(frame8, textvariable=ParamEntry12, width=5)
    ParamEntryE12.grid(row=12, column=1, sticky=(W + E))
    ParamEntryE12.insert(END, "0.0")

    Param13 = StringVar()
    Param13.set('Z中心 : ')
    ParamLabel13 = ttk.Label(frame8, textvariable=Param13)
    ParamLabel13.grid(row=13, column=0, sticky=(W+E))
    ParamEntry13 = StringVar()
    ParamEntryE13 = ttk.Entry(frame8, textvariable=ParamEntry13, width=5)
    ParamEntryE13.grid(row=13, column=1, sticky=(W + E))
    ParamEntryE13.insert(END, "0.0")

    # Frame7実行
    frame7 = ttk.Frame(LFrame, padding=(0, 5))
    frame7.grid(row=7, column=0)
    button6 = ttk.Button(frame7, text='実行', command=Run)
    button6.grid()

    root.mainloop()
