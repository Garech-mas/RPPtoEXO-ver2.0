import binascii
import filecmp
import math
import random
import os
import shutil
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

import cv2

from rpp2exo import utils, dict


class Exo2:
    def __init__(self, mydict, file_path):
        self.fps = Fraction(mydict["fps"]).limit_denominator().numerator
        self.scale = Fraction(mydict["fps"]).limit_denominator().denominator
        self.mydict = mydict
        self.file_path = file_path
        self.file_fps = []
        self.exedit_lang = mydict['ExEditLang']
        self.txt_default_font = 'MS UI Gothic' if mydict['ExEditLang'] == 'ja' else 'Arial'
        self.encoding = 'cp932' if mydict['ExEditLang'] == 'ja' else 'ANSI'
        # 翻訳用
        global _
        _ = utils.get_locale(mydict['DisplayLang'])

    def fix_sjis_files(self):
        end = {'file_copy_failed': []}
        # 素材ファイルがSJIS非対応だった場合の処理
        if self.mydict["SrcPath"] != utils.ignore_sjis(self.encoding, self.mydict["SrcPath"]):
            os.makedirs(utils.ignore_sjis(self.encoding, self.mydict["RPPPath"][:-4]), exist_ok=True)
            save_path = utils.ignore_sjis(self.encoding, self.mydict["RPPPath"][:-4] + '\\' + os.path.basename(self.mydict["SrcPath"]))
            shutil.copy(self.mydict["SrcPath"], save_path)
            end['file_copied'] = True

        for i, file in enumerate(self.file_path):
            sjis_file = utils.ignore_sjis(self.encoding, file)
            if file != sjis_file and not is_audio(file):
                os.makedirs(utils.ignore_sjis(self.encoding, self.mydict["RPPPath"][:-4]), exist_ok=True)
                save_path = utils.ignore_sjis(self.encoding, self.mydict["RPPPath"][:-4] + '\\' + os.path.basename(file))
                try:
                    shutil.copy(file, save_path)
                    self.file_path[i] = save_path
                    end['file_copied'] = True
                except (PermissionError, FileNotFoundError):
                    # コピー先とコピー元が一致している(過去にコピー済の)場合は問題なしとする
                    if filecmp.cmp(file, save_path):
                        self.file_path[i] = save_path
                    else:
                        end['file_copy_failed'].append(file)
                        self.file_path[i] = sjis_file

        if not end['file_copy_failed']: del end['file_copy_failed']
        return end

    def fetch_fps(self):
        # 各動画ファイルを読み込み、必要な情報を格納する
        for index in range(len(self.file_path)):
            fps = 0.0
            if self.mydict["OutputType"] != 0:
                break
            if is_audio(self.file_path[index]):
                fps = self.mydict['fps']
            else:
                path = self.file_path[index]
                cap = cv2.VideoCapture(path.replace('\\', '/'))
                fps = float(cap.get(cv2.CAP_PROP_FPS))
                cap.release()
            if fps == 0.0:
                print(_("★警告: 動画として読み込めませんでした。動画ファイルの場合、再生位置が正常に反映されません。\n対象ファイル: %s") % path)
            self.file_fps.append(fps)
        self.file_fps.append(0.0)

    def make_exo(self, objdict):
        end = {}
        exo_result = []
        item_count = 0
        exo_1 = "\n["  # item_count
        exo_2 = "]\nlayer="  # layer
        exo_3 = "\nframe="  # StartFrame
        exo_4 = ","  # EndFrame
        exo_4_1 = ""  # オブジェクト種類別差分
        exo_4_2 = "\ngroup=1\nclipping=" + str(self.mydict["clipping"]) + \
                  "\ncamera=" + str(self.mydict["IsExSet"]) + "\n["  # item_count
        exo_5 = ""
        exo_6 = "\n["  # item_count
        # exo_7 item_countによる分岐のため後のループ内で記述
        exo_7 = ""
        exo_7_ = ''  # filter_countがない不完全なexo_7

        exo_eff = ""  # エフェクト設定用、先に宣言だけしておく。item_countを必要とするから後のループ内で処理
        exo_script = ""  # スクリプト制御用
        bpos = 0  # アイテム一つ前の開始フレーム
        bf = 0.0  # アイテム一つ前の最終フレーム  ==Endframe
        layer = 1  # オブジェクトのあるレイヤー（RPP上で複数トラックある場合は別トラックに配置する）
        bfidx = 0  # item_countの調整用 レイヤー頭のitem_count-bfidxが0になるような値を設定
        altidx = 0  # 同一音程判定の調整用

        opt_layer = []  # 1トラック内で重複が発生した場合の使用レイヤー状況をシミュレート
        opt_layer2 = []
        if self.mydict['RandomPlay'] and not self.mydict['RandomEnd']:
            videoload = cv2.VideoCapture(str(self.mydict["SrcPath"]))  # 動画を読み込む
            if videoload.isOpened():
                frame_count = videoload.get(cv2.CAP_PROP_FRAME_COUNT)
                fps = videoload.get(cv2.CAP_PROP_FPS)
                if fps > 0:
                    self.mydict['RandomEnd'] = frame_count / fps
                else:
                    self.mydict['RandomEnd'] = '0'
                videoload.release()
            else:
                self.mydict['RandomEnd'] = '0'

        obj_frame_pos = objdict["pos"][1] * self.mydict["fps"] + 1 \
            if len(objdict["pos"]) > 1 else -1
        if obj_frame_pos > 1:  # 最初のオブジェクトが1フレーム目以降の場合
            exo_5 = (".0]\n"
                     + "effect.name=テキスト\neffect.disable=1\nサイズ=100.00\n"
                     + "字間=0.00\n行間=0.00\n表示速度=0.00\nフォント=Noto Sans JP Black\n"
                     + "文字色=ffffff\n影・縁色=000000\n文字装飾=標準文字\n文字揃え=中央揃え[中]\nB=0\nI=0\n"
                     + "テキスト=位置調整用/位置合わせした後は消してください\n"
                     + "文字毎に個別オブジェクト=0\n移動座標上に表示=0\nオブジェクトの長さを自動調節=0")
            exo_7 = '.' + str(1) + ']'
            for txt in self.mydict['Param']:
                exo_7 += '\n' + txt
            exo_result.append(exo_1 + str(item_count) + exo_2 + '1' + exo_3 + '1' +
                              exo_4 + str(self.sur_round(obj_frame_pos) - 1) + exo_4_1 + exo_4_2 + str(item_count) +
                              exo_5)
            item_count = 1
            bfidx -= 1

        for index in range(1, len(objdict["length"])):
            exo_4_1 = ""
            exo_5 = ""
            exo_eff = ""
            filter_count = 0
            add_layer = 0

            # オブジェクト最初のフレームと長さの計算
            obj_frame_pos = objdict["pos"][index] * self.mydict["fps"] + 1
            next_obj_frame_pos = objdict["pos"][index + 1] * self.mydict["fps"] + 1 \
                if index != len(objdict["length"]) - 1 else -1
            obj_frame_length = objdict["length"][index] * self.mydict["fps"]
            # 一つ前のオブジェクトとフレームがかぶらないようにする処理
            # if sur_round(obj_frame_pos) == bf:
            #     obj_frame_pos += 1
            #     obj_frame_length -= 1
            #     ここで「1個前のオブジェクトのlength(bf)をマイナス１する」処理をしたい。抜本的な書き換えが必要
            # 一つ後のオブジェクトとの間に1フレームの空きがある場合の処理
            if self.sur_round(obj_frame_pos + obj_frame_length) == self.sur_round(next_obj_frame_pos) - 1:
                obj_frame_length += 1
            if obj_frame_pos < bf:
                bf = 0
                if obj_frame_pos < 0:  # 最後
                    bfidx = -item_count
                    # track += 1
                    layer += len(opt_layer + opt_layer2)
                    opt_layer = []
                    opt_layer2 = []
                    continue
            bf = obj_frame_pos + obj_frame_length - 1
            if self.mydict["NoGap"] == 1:
                if obj_frame_pos < self.sur_round(next_obj_frame_pos) - 1:
                    bf = next_obj_frame_pos - 1

            obj_frame_pos = int(self.sur_round(obj_frame_pos))
            if obj_frame_pos == 0: obj_frame_pos = 1

            # bfidxを調整 (同一開始フレームのオブジェクトを同じ反転状況にする)
            is_pitch_repeated = objdict['pitch'][index - 1] == objdict['pitch'][index]
            if obj_frame_pos == bpos:
                bfidx -= 1
            # 同音程が連続した時、同じ反転状況にする
            elif self.mydict['AltFlipType'] > 0 and is_pitch_repeated:
                bfidx -= 1

            # 同音程が連続した時、逆方向反転する
            if self.mydict['AltFlipType'] == 2 and is_pitch_repeated:
                altidx += 1
            elif self.mydict["ObjFlipType"] != 3:
                altidx = 0

            bf = int(self.sur_round(bf))
            bpos = obj_frame_pos

            if self.mydict["SepLayerEvenObj"] == 1 and (bfidx + item_count) % 2 == 1:  # 偶数番目obj用のobj_layerに処理
                for i, end_point in enumerate(opt_layer2):
                    add_layer = i
                    if end_point >= obj_frame_pos:  # オブジェクトが被ったときはループ継続
                        if i == len(opt_layer2) - 1:  # 最終ループのときはレイヤー追加
                            opt_layer2.append(bf)
                            add_layer += 1
                            break
                    else:  # オブジェクトが被ってないので、bfを上書きしてループを抜ける
                        opt_layer2[add_layer] = bf
                        break
                if not opt_layer2:  # 初回のレイヤー追加
                    opt_layer2.append(bf)
            else:
                for i, end_point in enumerate(opt_layer):
                    add_layer = i
                    if end_point >= obj_frame_pos:
                        if i == len(opt_layer) - 1:
                            opt_layer.append(bf)
                            add_layer += 1
                            break
                    else:
                        opt_layer[add_layer] = bf
                        break
                if not opt_layer:  # 初回のレイヤー追加
                    opt_layer.append(bf)

            # 偶数番目オブジェクトをひとつ下のレイヤに配置する
            if self.mydict["SepLayerEvenObj"] == 1:
                if (bfidx + item_count) % 2 == 0:
                    exo_2 = "]\nlayer=" + str(layer + add_layer * 2)  # layer
                else:
                    exo_2 = "]\nlayer=" + str(layer + add_layer * 2 + 1)  # layer
            else:
                exo_2 = "]\nlayer=" + str(layer + add_layer)

            # エフェクトを追加している場合の設定
            if len(self.mydict["Effect"]) != 0:
                for eff in self.mydict["Effect"]:
                    filter_count += 1
                    exo_eff += "\n[" + str(item_count) + "." + \
                               str(filter_count) + "]\neffect.name=" + str(eff[0])
                    for x in range(1, len(eff)):
                        exo_eff += "\n" + str(eff[x][0]) + "=" + str(eff[x][1])

            # EXA読み込み
            eff_path = self.mydict['EffPaths'][(bfidx + item_count) % len(self.mydict['EffPaths'])]
            if not eff_path:  # EXAファイルがブランクのときは後続処理に回す
                exo_4_1 = '\noverlay=1'
            else:
                condition = ''
                exo_5 = '\n'
                exo_eff += '\n'
                with open(eff_path, mode='r', encoding='utf-8', errors='replace') as f:
                    exa = f.readlines()
                    if exa[0][0] != '[' or exa[0][-2] != ']':
                        raise utils.LoadFilterFileError('', filename=eff_path)

                    for idx in range(len(exa)):
                        if exa[idx][-10:] == 'Object.0]\n':  # オブジェクトファイル情報が存在する場合、exo_5を上書き
                            condition = 'exo_5'
                            exo_5 = '.0]\n'
                            continue
                        elif exa[idx][0] == '[' and exa[idx][-2] == ']':  # 切り替え部
                            if '.' not in exa[idx]:
                                if exa[idx + 1].startswith('frame=') and exa[idx + 1].count(',') >= 2:
                                    end['keyframe_exists'] = True
                                    break
                                if condition == '':
                                    continue
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
                        elif exa[idx] == 'overlay=1\n':
                            exo_4_1 = "\noverlay=1"
                        elif exa[idx] == 'audio=1\n':
                            exo_4_1 = "\naudio=1"
                        elif exa[idx] == 'clipping=1\n':
                            exo_4_1 = "\nclipping=1"

                # それぞれ末尾の\nを削除
                exo_5 = exo_5[:-1]
                exo_eff = exo_eff[:-1]
                exo_7_ = exo_7_[:-1]

            # オブジェクトの反転・スクリプト制御の有無の設定 …色々詰め込んだせいで最悪の実装になってしまった。
            if self.mydict["ObjFlipType"] == 0:  # 反転なし
                pass
            elif self.mydict["ObjFlipType"] == 1 and (bfidx + item_count) % 2 == 1 and altidx % 2 == 0 or \
                 self.mydict["ObjFlipType"] == 2 and (bfidx + item_count) % 2 == 0 and altidx % 2 == 1:  # 左右反転
                exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(lr=1)
                filter_count += 1
            elif self.mydict["ObjFlipType"] == 2 and (bfidx + item_count) % 2 == 1 and altidx % 2 == 0 or \
                 self.mydict["ObjFlipType"] == 1 and (bfidx + item_count) % 2 == 0 and altidx % 2 == 1:  # 上下反転
                exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(ud=1)
                filter_count += 1
            elif self.mydict["ObjFlipType"] == 3:  # 時計回り反転
                if (bfidx + item_count - altidx) % 4 == (3 if self.mydict['IsCCW'] else 1):
                    exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(lr=1)
                    filter_count += 1
                elif (bfidx + item_count - altidx) % 4 == 2:
                    exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(ud=1, lr=1)
                    filter_count += 1
                elif (bfidx + item_count - altidx) % 4 == (1 if self.mydict['IsCCW'] else 3):
                    exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(ud=1)
                    filter_count += 1

            if self.mydict["ScriptText"] != "":  # スクリプト制御追加する場合
                exo_script = ("\n[" + str(item_count) + "." + str(1 + filter_count) +
                              "]\neffect.name=" + self.t("スクリプト制御") + "\nスクリプト=" + self.mydict["ScriptText"])
                filter_count += 1

            # EXA読み込み部でexo_5部分が読み込まれていた場合、EXAファイルの中身のオブジェクトをそのまま反映する (この先の処理は無視)
            if exo_5 != '':  # メディアオブジェクト
                exo_7 = "." + str(1 + filter_count) + exo_7_
                exo_result.append(exo_1 + str(item_count) + exo_2 + exo_3 + str(obj_frame_pos) + exo_4 + str(bf) +
                              exo_4_1 + exo_4_2 + str(item_count) + exo_5 + exo_eff + exo_script +
                                  ((exo_6 + str(item_count) + exo_7) if exo_7_ != '' else ''))

                item_count = item_count + 1
                continue

            # オブジェクトの種類等の設定
            if self.mydict["OutputType"] == 0:
                if objdict["filetype"][index] in ["VIDEO", "IMAGE"]:
                    file = self.file_path[objdict["fileidx"][index]]
                else:
                    file = ""

                # 空アイテム (テキスト) の場合の処理
                if objdict["filetype"][index].startswith('TEXT'):
                    exo_5 = (".0]\n"
                           + "effect.name=" + self.t("テキスト") + "\n" + self.t("サイズ") + "=34\n"
                           + self.t("表示速度") + "=0.0\n" + self.t("文字毎に個別オブジェクト") + "=0\n"
                           + self.t("移動座標上に表示する") + "=0\nB=0\nI=0\ntype=0\nautoadjust=0\nsoft=1\nmonospace=0\n"
                             "align=0\nspacing_x=0\nspacing_y=0\nprecision=1\ncolor=ffffff\ncolor2=000000\n"
                             "font=" + self.txt_default_font + "\ntext=" + encode_txt(objdict["filetype"][index][5:]))

                # 空アイテム (画像) の場合の処理
                elif objdict["filetype"][index].startswith('IMAGE'):
                    exo_5 = ".0]\neffect.name=" + self.t("画像ファイル") + \
                            "\nfile=" + file

                else:
                    is_alpha = 0
                    if file[file.find('.'):] == ".avi":  # AVIファイルの場合だけ、透過AVIの可能性があるためアルファチャンネル有
                        is_alpha = 1

                    play_pos = objdict["soffs"][index]
                    play_rate = int(objdict["playrate"][index] * 1000) / 10.0

                    exo_5 = ".0]\neffect.name=" + self.t("動画ファイル") + \
                            "\n" + self.t("再生位置") + "=" + str(play_pos) + \
                            "\n" + self.t("再生速度") + "=" + str(play_rate) + \
                            "\n" + self.t("ループ再生") + "=" + \
                            (str(objdict["loop"][index]) if self.mydict["IsLoop"] else '0') + \
                            "\n" + self.t("アルファチャンネルを読み込む") + "=" + str(is_alpha) + \
                            "\nfile=" + file
            elif self.mydict["OutputType"] == 1:  # 動画オブジェクト
                if self.mydict["RandomPlay"]:   # 再生位置ランダム
                    self.mydict["SrcPosition"] = random.uniform(float(self.mydict['RandomStart']), float(self.mydict['RandomEnd']))
                exo_5 = ".0]\neffect.name=" + self.t("動画ファイル") + \
                        "\n" + self.t("再生位置") + "=" + str(self.mydict["SrcPosition"]) + \
                        "\n" + self.t("再生速度") + "=" + str(self.mydict["SrcRate"]) + \
                        "\n" + self.t("ループ再生") + "=" + str(self.mydict["IsLoop"]) + \
                        "\n" + self.t("アルファチャンネルを読み込む") + "=" + str(self.mydict["IsAlpha"]) + \
                        "\nfile=" + str(self.mydict["SrcPath"])

            elif self.mydict["OutputType"] == 2:  # 画像オブジェクト
                exo_5 = ".0]\neffect.name=" + self.t("画像ファイル") + \
                        "\nfile=" + str(self.mydict["SrcPath"])
            elif self.mydict["OutputType"] == 4:  # シーンオブジェクト
                if self.mydict["RandomPlay"]:   # 再生位置ランダム
                    self.mydict["SrcPosition"] = random.uniform(float(self.mydict['RandomStart']), float(self.mydict['RandomEnd']))
                exo_5 = ".0]\neffect.name=" + self.t("シーン") + \
                        "\n" + self.t("再生位置") + "=" + str(self.mydict["SrcPosition"]) + \
                        "\n" + self.t("再生速度") + "=" + str(self.mydict["SrcRate"]) + \
                        "\n" + self.t("ループ再生") + "=" + str(self.mydict["IsLoop"]) + \
                        "\nシーン=" + str(self.mydict["SceneIdx"])

            # メディアオブジェクト
            if self.mydict["OutputType"] != 3:
                exo_7 = '.' + str(1 + filter_count) + ']'
                for txt in self.mydict['Param']:
                    exo_7 += '\n' + txt
                exo_result.append(exo_1 + str(item_count) + exo_2 + exo_3 + str(obj_frame_pos) + exo_4 + str(bf) +
                              exo_4_1 + exo_4_2 + str(item_count) + exo_5 + exo_eff + exo_script + exo_6 +
                              str(item_count) + exo_7)
            # フィルタ効果
            elif self.mydict["OutputType"] == 3:
                exo_4_2 = "\ngroup=1"
                # 何も効果がかかっていないとエラー吐くので（多分）とりあえず座標0,0,0を掛けておく
                exo_5 = "\n[" + str(item_count) + ".0]\neffect.name=" + self.t("座標") + "\nX=0.0\nY=0.0\nZ=0.0"
                exo_result.append(exo_1 + str(item_count) + exo_2 + exo_3 + str(obj_frame_pos) + exo_4 + str(bf) +
                              exo_4_1 + exo_4_2 + exo_5 + exo_eff + exo_script)

            item_count += 1

        if item_count == 0:
            raise utils.ItemNotFoundError

        with open(self.mydict["EXOPath"], mode='w', encoding='utf-8') as f:
            f.write(''.join(exo_result)[1:])
        return end

    def add_reversal(self, ud=0, lr=0):  # 反転エフェクト追加用
        # 反転_ITEMのデータを持ってくる(なければオリジナルのものを使う)
        t_result = self.t("反転_ITEM")
        item = t_result if t_result != "反転_ITEM" else ['上下反転', '左右反転', '輝度反転', '色相反転', '透明度反転']

        result = ("]\neffect.name=" + self.t("反転") + "\n"
                  + item[0] + "=" + str(ud) + "\n"
                  + item[1] + "=" + str(lr) + "\n"
                  + item[2] + "=0\n"
                  + item[3] + "=0\n"
                  + item[4] + "=0"
                  )
        return result

    # 海外版拡張編集を使用する際にDictから翻訳するための関数
    def t(self, txt):
        if self.exedit_lang != 'ja':
            return dict.ExDict[self.exedit_lang][txt]
        else:
            return txt

    # iを設定内容の通りに丸める
    def sur_round(self, i):
        if self.mydict["UseRoundUp"] == 1:  # iを切り上げする
            return math.ceil(i)
        else:  # iを正確に四捨五入する
            result = Decimal(str(i)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
            return float(result)


def encode_txt(text):  # textを拡張編集のテキストエンコード形式に直す
    text = binascii.hexlify(text.encode("UTF-16LE"))
    text = str(text)[:-1][2:]
    text = text + "0" * (4096 - len(str(text)))
    return text


def is_audio(path):
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.wma', '.ogg']
    extension = os.path.splitext(path)[1]
    return extension.lower() in audio_extensions
