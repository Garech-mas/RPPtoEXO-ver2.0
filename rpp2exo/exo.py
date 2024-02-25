import binascii
import random
import cv2
import gettext
import os
from decimal import Decimal, ROUND_HALF_UP
from rpp2exo.dict import ExDict


class LoadFilterFileError(Exception):  # EXA読み込みエラー
    pass


class ItemNotFoundError(Exception):  # 出力対象アイテム数0エラー
    pass


class Exo:
    def __init__(self, mydict):
        self.fps, self.scale = mydict['fps'], 1
        self.res_x = 1920  # 解像度X
        self.res_y = 1080
        self.mydict = mydict
        self.exedit_lang = mydict['ExEditLang']
        # 翻訳用
        global _
        _ = gettext.translation(
            'text',  # domain: 辞書ファイルの名前
            localedir=os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)))),  # 辞書ファイル配置ディレクトリ
            languages=[mydict['DisplayLang']],  # 翻訳に使用する言語
            fallback=True
        ).gettext

    def fetch_fps(self, file_path):
        file_fps = []
        # 各動画ファイルを読み込み、必要な情報を格納する
        for index in range(len(file_path)):
            fps = 0.0
            if self.mydict["OutputType"] != 0:
                break
            if is_audio(file_path[index]):
                fps = self.mydict['fps']
            else:
                path = file_path[index]
                cap = cv2.VideoCapture(path.replace('\\', '/'))
                fps = float(cap.get(cv2.CAP_PROP_FPS))
                cap.release()
            if fps == 0.0:
                print(_("★警告: 動画として読み込めませんでした。動画ファイルの場合、再生位置が正常に反映されません。\n対象ファイル: %s") % path)
            file_fps.append(fps)
        file_fps.append(0.0)
        return file_fps

    def make_exo(self, objdict, file_path, file_fps):
        end = {}
        exo_result = "[exedit]\nwidth=" + str(1280) + "\nheight=" + str(720) + \
                     "\nrate=" + str(int(self.fps)) + "\nscale=" + str(int(self.scale)) + \
                     "\nlength=99999\naudio_rate=44100\naudio_ch=2"
        item_count = 0
        exo_1 = "\n["  # item_count
        exo_2 = "]\nstart="  # StartFrame
        exo_3 = "\nend="  # EndFrame
        exo_4 = "\nlayer="  # layer
        exo_4_2 = "\ngroup=1\noverlay=1\nclipping=" + str(self.mydict["clipping"]) + \
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

        opt_layer = []  # 1トラック内で重複が発生した場合の使用レイヤー状況をシミュレート
        opt_layer2 = []
        video_frame_count = 0  # 動画の総フレーム数 (再生時間ランダム用)
        if self.mydict['RandomPlay']:
            videoload = cv2.VideoCapture(str(self.mydict["SrcPath"]))  # 動画を読み込む
            video_frame_count = videoload.get(cv2.CAP_PROP_FRAME_COUNT)  # フレーム数

        for index in range(1, len(objdict["length"])):
            exo_5 = ""
            exo_eff = ""
            filter_count = 0
            add_layer = 0

            if layer > 100:
                break

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
            if sur_round(obj_frame_pos + obj_frame_length) == sur_round(next_obj_frame_pos) - 1:
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
                if obj_frame_pos < sur_round(next_obj_frame_pos) - 1:
                    bf = next_obj_frame_pos - 1

            obj_frame_pos = int(sur_round(obj_frame_pos))
            if obj_frame_pos == 0: obj_frame_pos = 1

            # bfidxを調整 (同一開始フレームのオブジェクトを同じ反転状況にする)
            if obj_frame_pos == bpos:
                bfidx -= 1

            bf = int(sur_round(bf))
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
                    exo_4 = "\nlayer=" + str(layer + add_layer * 2)  # layer
                else:
                    exo_4 = "\nlayer=" + str(layer + add_layer * 2 + 1)  # layer
            else:
                exo_4 = "\nlayer=" + str(layer + add_layer)

            # エフェクトを追加している場合の設定
            if len(self.mydict["Effect"]) != 0:
                for eff in self.mydict["Effect"]:
                    filter_count += 1
                    exo_eff += "\n[" + str(item_count) + "." + \
                               str(filter_count) + "]\n_name=" + str(eff[0])
                    for x in range(1, len(eff)):
                        exo_eff += "\n" + str(eff[x][0]) + "=" + str(eff[x][1])

            # EXA読み込み
            if self.mydict["EffPath"] != "":
                condition = ''
                exo_5 = '\n'
                exo_eff += '\n'
                with open(str(self.mydict["EffPath"]), mode='r', encoding='shift_jis', errors='replace') as f:
                    exa = f.readlines()
                    if exa[0][0] != '[' or exa[0][-2] != ']' or exa[0] == '[exedit]\n':
                        raise LoadFilterFileError

                    for idx in range(len(exa)):
                        if exa[idx][-4:] == '.0]\n':  # オブジェクトファイル情報が存在する場合、exo_5を上書き
                            condition = 'exo_5'
                            exo_5 = '.0]\n'
                            continue
                        elif exa[idx][0] == '[' and exa[idx][-2] == ']':  # 切り替え部
                            if exa[idx] == '[vo]\n':
                                if condition == '':
                                    continue
                                else:
                                    break
                            if (exa[idx + 1][6:] == self.t('標準描画') + '\n' or
                                    exa[idx + 1][6:] == self.t('拡張描画') + '\n'):
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

            # オブジェクトの反転・スクリプト制御の有無の設定
            if self.mydict["ObjFlipType"] == 0:  # 反転なし
                pass
            elif self.mydict["ObjFlipType"] == 1 and (bfidx + item_count) % 2 == 1:  # 左右反転
                exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(lr=1)
                filter_count += 1
            elif self.mydict["ObjFlipType"] == 2 and (bfidx + item_count) % 2 == 1:  # 上下反転
                exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(ud=1)
                filter_count += 1
            elif self.mydict["ObjFlipType"] == 3:  # 時計回り反転
                if (bfidx + item_count) % 4 == (3 if self.mydict['IsCCW'] else 1):
                    exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(lr=1)
                    filter_count += 1
                elif (bfidx + item_count) % 4 == 2:
                    exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(ud=1, lr=1)
                    filter_count += 1
                elif (bfidx + item_count) % 4 == (1 if self.mydict['IsCCW'] else 3):
                    exo_eff += "\n[" + str(item_count) + "." + str(1 + filter_count) + self.add_reversal(ud=1)
                    filter_count += 1

            if self.mydict["ScriptText"] != "":  # スクリプト制御追加する場合
                exo_script = ("\n[" + str(item_count) + "." + str(1 + filter_count) +
                              "]\n_name=" + self.t("スクリプト制御") + "\ntext=" + encode_txt(self.mydict["ScriptText"]))
                filter_count += 1

            # EXA読み込み部でexo_5部分が読み込まれていた場合、EXAファイルの中身のオブジェクトをそのまま反映する (この先の処理は無視)
            if exo_5 != '':
                exo_7 = "." + str(1 + filter_count) + exo_7_
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

                play_pos = int(objdict["soffs"][index] * file_fps[objdict["fileidx"][index]] + 1)
                play_rate = int(objdict["playrate"][index] * 1000) / 10.0

                exo_5 = ".0]\n_name=" + self.t("動画ファイル") + \
                        "\n" + self.t("再生位置") + "=" + str(play_pos) + \
                        "\n" + self.t("再生速度") + "=" + str(play_rate) + \
                        "\n" + self.t("ループ再生") + "=" + \
                        (str(objdict["loop"][index]) if self.mydict["IsLoop"] else '0') + \
                        "\n" + self.t("アルファチャンネルを読み込む") + "=" + str(is_alpha) + \
                        "\nfile=" + file
            elif self.mydict["OutputType"] == 1:  # 動画オブジェクト
                if self.mydict["RandomPlay"]:   # 再生位置ランダム
                    self.mydict["SrcPosition"] = random.randint(1, int(video_frame_count))
                exo_5 = ".0]\n_name=" + self.t("動画ファイル") + \
                        "\n" + self.t("再生位置") + "=" + str(self.mydict["SrcPosition"]) + \
                        "\n" + self.t("再生速度") + "=" + str(self.mydict["SrcRate"]) + \
                        "\n" + self.t("ループ再生") + "=" + str(self.mydict["IsLoop"]) + \
                        "\n" + self.t("アルファチャンネルを読み込む") + "=" + str(self.mydict["IsAlpha"]) + \
                        "\nfile=" + str(self.mydict["SrcPath"])

            elif self.mydict["OutputType"] == 2:  # 画像オブジェクト
                exo_5 = ".0]\n_name=" + self.t("画像ファイル") + \
                        "\nfile=" + str(self.mydict["SrcPath"])
            elif self.mydict["OutputType"] == 4:  # シーンオブジェクト
                exo_5 = ".0]\n_name=" + self.t("シーン") + \
                        "\n" + self.t("再生位置") + "=" + str(self.mydict["SrcPosition"]) + \
                        "\n" + self.t("再生速度") + "=" + str(self.mydict["SrcRate"]) + \
                        "\n" + self.t("ループ再生") + "=" + str(self.mydict["IsLoop"]) + \
                        "\nscene=" + str(self.mydict["SceneIdx"])

            # メディアオブジェクト
            if self.mydict["OutputType"] != 3:
                exo_7 = '.' + str(1 + filter_count) + ']'
                for txt in self.mydict['Param']:
                    exo_7 += '\n' + txt

                exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) +
                              exo_4 + exo_4_2 + str(item_count) + exo_5 + exo_eff + exo_script + exo_6 +
                              str(item_count) + exo_7)
            # フィルタ効果
            elif self.mydict["OutputType"] == 3:
                exo_4_2 = "\ngroup=1\noverlay=1"
                # 何も効果がかかっていないとエラー吐くので（多分）とりあえず座標0,0,0を掛けておく
                exo_5 = "\n[" + str(item_count) + ".0]\n_name=" + self.t("座標") + "\nX=0.0\nY=0.0\nZ=0.0"
                exo_result = (exo_result + exo_1 + str(item_count) + exo_2 + str(obj_frame_pos) + exo_3 + str(bf) +
                              exo_4 + exo_4_2 + exo_5 + exo_eff + exo_script)

            item_count += 1

        if item_count == 0:
            raise ItemNotFoundError

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

    def add_reversal(self, ud=0, lr=0):  # 反転エフェクト追加用
        # 反転_ITEMのデータを持ってくる(なければオリジナルのものを使う)
        t_result = self.t("反転_ITEM")
        item = t_result if t_result != "反転_ITEM" else ['上下反転', '左右反転', '輝度反転', '色相反転', '透明度反転']

        result = ("]\n_name=" + self.t("反転") + "\n"
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
            return ExDict[self.exedit_lang][txt]
        else:
            return txt


def encode_txt(text):  # textを拡張編集のテキストエンコード形式に直す
    text = binascii.hexlify(text.encode("UTF-16LE"))
    text = str(text)[:-1][2:]
    text = text + "0" * (4096 - len(str(text)))
    return text


def sur_round(i):  # iを正確に四捨五入する
    result = Decimal(str(i)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
    return float(result)


def is_audio(path):
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.wma', '.ogg']
    extension = os.path.splitext(path)[1]
    return extension.lower() in audio_extensions
