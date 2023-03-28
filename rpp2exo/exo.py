import binascii

import cv as cv
import cv2
from decimal import Decimal, ROUND_HALF_UP


class LoadFilterFileError(Exception):
    pass


# class ExoObject:
#     output_type = 0  # 1=動画  2=画像  3=フィルタ  4=シーン  として出力
#     auto_src = False  # 素材自動検出が有効か
#
#     x = 0.0
#     y = 0.0
#     z = 0.0
#     size = 100.0  # 拡大率
#     rotation = 0.0  # 回転
#     alpha = 0.0  # 透明度
#     blend = 0  # 合成モード
#
#     adv_draw = False  # 拡張描画か
#     spin_x = 0.0  # X軸回転
#     spin_y = 0.0
#     spin_z = 0.0
#     center_x = 0.0  # 中心X
#     center_y = 0.0
#     center_z = 0.0
#
#     effect = []  # ["EffName",["ConfName1","Conf"],["ConfName2","Conf"]],
#     script_text = ''
#
#     horizon_flip_even = 0  # 偶数オブジェクトを左右反転するか
#     sep_layer_even = 0  # a              別レイヤ―配置するか
#     no_gap = 0  # オブジェクト間の隙間を埋めるか
#
#     def __init__(self):
#         self.output_type = 0    # 1=動画  2=画像  3=フィルタ  4=シーン  として出力
#         self.auto_src = False   # 素材自動検出が有効か
#
#         self.x = 0.0
#         self.y = 0.0
#         self.z = 0.0
#         self.size = 100.0       # 拡大率
#         self.rotation = 0.0     # 回転
#         self.alpha = 0.0        # 透明度
#         self.blend = 0          # 合成モード
#
#         self.adv_draw = False       # 拡張描画か
#         self.spin_x = 0.0       # X軸回転
#         self.spin_y = 0.0
#         self.spin_z = 0.0
#         self.center_x = 0.0     # 中心X
#         self.center_y = 0.0
#         self.center_z = 0.0
#
#         self.effect = []        # ["EffName",["ConfName1","Conf"],["ConfName2","Conf"]],
#         self.script_text = ''
#
#         self.horizon_flip_even = 0  # 偶数オブジェクトを左右反転するか
#         self.sep_layer_even = 0     # a              別レイヤ―配置するか
#         self.no_gap = 0             # オブジェクト間の隙間を埋めるか
#
#
class Exo:
    def __init__(self, mydict):
        self.fps = 60.0
        self.res_x = 1920       # 解像度X
        self.res_y = 1080
        self.mydict = mydict

    def fetch_fps(self, file_path):
        if self.mydict["NoGap"]:
            a = 1
        file_fps = []
        # 各動画ファイルを読み込み、必要な情報を格納する
        for index in range(len(file_path)):
            if self.mydict["OutputType"] != 0:
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
        return file_fps

    def make_exo(self, objdict, file_path, file_fps):
        end = {}
        exo_result = "[exedit]\nwidth=" + str(1280) + "\nheight=" + str(720) + "\nrate=" + str(
            60) + "\nscale=1\nlength=99999\naudio_rate=44100\naudio_ch=2"
        item_count = 0
        exo_1 = "\n["  # item_count
        exo_2 = "]\nstart="  # StartFrame
        exo_3 = "\nend="  # EndFrame
        exo_4 = "\nlayer="  # layer
        exo_4_2 = "\ngroup=1\noverlay=1\nclipping=" + str(self.mydict["clipping"]) + "\ncamera=0\n["  # item_count
        exo_6 = "\n["  # item_count
        # exo_7 item_countによる分岐のため後のループ内で記述
        exo_7 = ""

        exo_eff = ""  # エフェクト設定用、先に宣言だけしておく。item_countを必要とするから後のループ内で処理
        exo_script = ""  # スクリプト制御用
        bf = 0.0  # アイテム一つ前の最終フレーム  ==Endframe
        layer = 1  # オブジェクトのあるレイヤー（RPP上で複数トラックある場合は別トラックに配置する）
        bfidx = 1

        for index in range(1, len(objdict["length"])):
            exo_eff = ""
            filter_count = 0
            has_script_ctrl = False  # スクリプト制御がある場合
            has_flip = False  # 左右反転をする場合

            if layer > 100:
                break

            # オブジェクト最初のフレームと長さの計算
            obj_frame_pos = objdict["pos"][index] * float(self.mydict["fps"]) + 1
            next_obj_frame_pos = objdict["pos"][index + 1] * float(self.mydict["fps"]) + 1 \
                if index != len(objdict["length"]) - 1 else -1
            obj_frame_length = objdict["length"][index] * float(self.mydict["fps"])
            if sur_round(obj_frame_pos) == bf:  # 一つ前のオブジェクトとフレームがかぶらないようにする処理
                obj_frame_pos += 1
                obj_frame_length -= 1
            if sur_round(obj_frame_pos + obj_frame_length) == sur_round(
                    next_obj_frame_pos) - 1:  # 一つ後のオブジェクトとの間に1フレームの空きがある場合の処理
                obj_frame_length += 1
            if obj_frame_pos < bf:
                bf = 0
                bfidx = index
                layer += 1 + self.mydict["SepLayerEvenObj"]
                if obj_frame_pos < 0:
                    continue
            bf = obj_frame_pos + obj_frame_length - 1
            if self.mydict["NoGap"] == 1:
                if obj_frame_pos < sur_round(next_obj_frame_pos) - 1:
                    bf = next_obj_frame_pos - 1

            obj_frame_pos = sur_round(obj_frame_pos)
            if obj_frame_pos == 0: obj_frame_pos = 1
            bf = sur_round(bf)

            # エフェクトを追加している場合の設定
            if len(self.mydict["Effect"]) != 0:
                for eff in self.mydict["Effect"]:
                    filter_count += 1
                    exo_eff += "\n[" + str(item_count) + "." + \
                                   str(filter_count) + "]\n_name=" + str(eff[0])
                    for x in range(1, len(eff)):
                        exo_eff += "\n" + str(eff[x][0]) + "=" + str(eff[x][1])

            # 偶数番目オブジェクトをひとつ下のレイヤに配置する
            if self.mydict["SepLayerEvenObj"] == 1 and (bfidx + item_count) % 2 == 0:
                exo_4 = "\nlayer=" + str(layer + 1)  # layer
            else:
                exo_4 = "\nlayer=" + str(layer)

            # EXA読み込み
            if self.mydict["EffPath"] != "":
                condition = ''
                exo_5 = '\n'
                exo_eff += '\n'
                exo_7_ = ''
                with open(str(self.mydict["EffPath"]), mode='r', encoding='shift_jis', errors='replace') as f:
                    exa = f.readlines()
                    if exa[0][0] != '[' or exa[0][-2] != ']' or '.' not in exa[0]:
                        raise LoadFilterFileError

                    for idx in range(len(exa)):
                        if exa[idx][-4:] == '.0]\n':  # オブジェクトファイル情報が存在する場合、exo_5を上書き
                            condition = 'exo_5'
                            exo_5 = '.0]\n'
                            continue
                        elif exa[idx][0] == '[' and exa[idx][-2] == ']':  # 切り替え部
                            if exa[idx + 1][6:] == '標準描画\n' or exa[idx + 1][6:] == '拡張描画\n':
                                condition = 'exo_7_'
                                exo_7_ = ']\n'
                            else:
                                condition = 'exo_eff'
                                filter_count += 1
                                exo_eff += '\n[' + str(item_count) + "." + str(filter_count) + ']\n'
                            continue

                        if condition == 'exo_5':
                            exo_5 += exa[idx]
                        elif condition == 'exo_eff':
                            exo_eff += exa[idx]
                        elif condition == 'exo_7_':
                            exo_7_ += exa[idx]
                # それぞれ末尾の\nを削除
                exo_5 = exo_5[:-1]
                exo_eff = exo_eff[:-1]
                exo_7_ = exo_7_[:-1]

                # exo_5部分が読み込まれた場合、EXAファイルの中身のオブジェクトをそのまま反映する
                if exo_5 != '':
                    if int(self.mydict["IsFlipHEvenObj"]) == 1 and (bfidx + item_count) % 2 == 0:
                        exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + \
                                   "]\n_name=反転\n上下反転=0\n左右反転=1\n輝度反転=0\n色相反転=0\n透明度反転=0"
                        has_flip = True
                    if self.mydict["ScriptText"] != "":  # スクリプト制御追加する場合
                        exo_script = ("\n[" + str(item_count) + "." + str(2 + filter_count) +
                                      "]\n_name=スクリプト制御\ntext=" + encode_txt(self.mydict["ScriptText"]))
                        has_script_ctrl = True

                    exo_7 = "." + str(1 + has_script_ctrl + has_flip + filter_count) + exo_7_
                    exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) +
                                  exo_4 + exo_4_2 + str(item_count) + exo_5 + exo_eff + exo_script + exo_6 +
                                  str(item_count) + exo_7)
                    item_count = item_count + 1
                    continue

            # オブジェクトの種類等の設定
            if self.mydict["OutputType"] == 0:
                if objdict["filetype"][index] == "VIDEO":
                    file = file_path[objdict["fileidx"][index]]
                else:
                    file = ""
                is_alpha = 0
                if file[file.find('.'):] == ".avi":  # AVIファイルの場合だけ、透過AVIの可能性があるためアルファチャンネル有
                    is_alpha = 1

                exo_5 = ".0]\n_name=動画ファイル" \
                        "\n再生位置=" + str(int(objdict["soffs"][index] * file_fps[objdict["fileidx"][index]] + 1)) \
                        + "\n再生速度=" + str(int(objdict["playrate"][index] * 1000) / 10.0) + \
                        "\nループ再生=" + str(objdict["loop"][index]) + "\nアルファチャンネルを読み込む=" + str(is_alpha) + \
                        "\nfile=" + file
            elif self.mydict["OutputType"] == 1:  # 動画オブジェクト
                exo_5 = ".0]\n_name=動画ファイル\n再生位置=" + str(self.mydict["SrcPosition"]) + "\n再生速度=" + str(self.mydict["SrcRate"]) + \
                        "\nループ再生=" + str(self.mydict["IsLoop"]) + "\nアルファチャンネルを読み込む=" + \
                        str(self.mydict["IsAlpha"]) + "\nfile=" + str(self.mydict["SrcPath"])
            elif self.mydict["OutputType"] == 2:  # 画像オブジェクト
                exo_5 = ".0]\n_name=画像ファイル\nfile=" + str(self.mydict["SrcPath"])
            elif self.mydict["OutputType"] == 4:  # シーンオブジェクト
                exo_5 = ".0]\n_name=シーン\n再生位置=" + str(self.mydict["SrcPosition"]) + "\n再生速度=" + str(self.mydict["SrcRate"]) + \
                        "\nループ再生=" + str(self.mydict["IsLoop"]) + "\nscene=" + str(self.mydict["SceneIdx"])

            # メディアオブジェクト
            if self.mydict["OutputType"] != 3:
                if int(self.mydict["IsFlipHEvenObj"]) == 1 and (bfidx + item_count) % 2 == 0:  # 反転
                    exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + \
                               "]\n_name=反転\n上下反転=0\n左右反転=1\n輝度反転=0\n色相反転=0\n透明度反転=0"
                    has_flip = True
                if self.mydict["ScriptText"] != "":  # スクリプト制御追加する場合
                    exo_script = ("\n[" + str(item_count) + "." + str(has_flip + 1 + filter_count) +
                                  "]\n_name=スクリプト制御\ntext=" + encode_txt(self.mydict["ScriptText"]))
                    has_script_ctrl = 1

                if self.mydict["IsExSet"] == "0":  # 標準描画
                    exo_7 = "." + str(has_script_ctrl + has_flip + 1 + filter_count) + \
                            "]\n_name=標準描画" + \
                            "\nX=" + str(self.mydict["X"]) + "\nY=" + str(self.mydict["Y"]) + "\nZ=" + str(self.mydict["Z"]) + \
                            "\n拡大率=" + str(self.mydict["Size"]) + "\n透明度=" + str(self.mydict["Alpha"]) + \
                            "\n回転=" + str(self.mydict["Rotation"]) + "\nblend=" + str(self.mydict["Blend"])
                else:  # 拡張描画
                    exo_7 = "." + str(has_script_ctrl + has_flip + 1 + filter_count) + \
                            "]\n_name=拡張描画" + \
                            "\nX=" + str(self.mydict["X"]) + "\nY=" + str(self.mydict["Y"]) + "\nZ=" + str(self.mydict["Z"]) + \
                            "\n拡大率=" + str(self.mydict["Size"]) + "\n透明度=" + str(self.mydict["Alpha"]) + \
                            "\n縦横比=" + str(self.mydict["Ratio"]) + "\nX軸回転=" + str(self.mydict["XRotation"]) + \
                            "\nY軸回転=" + str(self.mydict["YRotation"]) + "\nZ軸回転=" + str(self.mydict["ZRotation"]) + \
                            "\n中心X=" + str(self.mydict["XCenter"]) + "\n中心Y=" + str(self.mydict["YCenter"]) + \
                            "\n中心Z=" + str(self.mydict["ZCenter"]) + \
                            "\n裏面を表示しない=0" + "\nblend=" + str(self.mydict["Blend"])

                exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) +
                              exo_4 + exo_4_2 + str(item_count) + exo_5 + exo_eff + exo_script + exo_6 +
                              str(item_count) + exo_7)
            # フィルタ効果
            elif self.mydict["OutputType"] == 3:
                if int(self.mydict["IsFlipHEvenObj"]) == 1 and (bfidx + item_count) % 2 == 0:  # 反転
                    exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + \
                               "]\n_name=反転\n上下反転=0\n左右反転=1\n輝度反転=0\n色相反転=0\n透明度反転=0"
                    has_flip = True
                if self.mydict["ScriptText"] != "":  # スクリプト制御追加する場合
                    exo_script = ("\n[" + str(item_count) + "." + str(has_flip + 1 + filter_count) +
                                  "]\n_name=スクリプト制御\ntext=" + encode_txt(self.mydict["ScriptText"]))
                exo_4_2 = "\ngroup=1\noverlay=1"
                # 何も効果がかかっていないとエラー吐くので（多分）とりあえず座標0,0,0を掛けておく
                exo_5 = "\n[" + str(item_count) + ".0]\n_name=座標\nX=0.0\nY=0.0\nZ=0.0"
                exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) +
                              exo_4 + exo_4_2 + exo_5 + exo_eff + exo_script)

            item_count = item_count + 1

        try:
            with open(self.mydict["EXOPath"], mode='w', encoding='shift_jis') as f:
                line = ""
                # 一文字ずつファイルに書き込んでいく (詳細エラー表示をできるようにするため)
                for t in exo_result:
                    f.write(t)
                    line += t
                    if t == '\n':
                        line = ""

                if layer > 100:
                    end["layer_over_100"] = True  # レイヤー100超

        except UnicodeEncodeError:
            raise UnicodeEncodeError('', t, 0, 0, line)  # objectとreasonにエラーの文字情報を渡して返す (本来の使い方じゃなさそう…)
        return end


def encode_txt(text):
    text = binascii.hexlify(text.encode("UTF-16LE"))
    text = str(text)[:-1][2:]
    text = text + "0" * (4096 - len(str(text)))
    return text


def sur_round(i):
    result = Decimal(str(i)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
    return float(result)
