import datetime
import os
import json
import random

import cv2
from copy import deepcopy
from tkinter import messagebox
from rpp2exo import sur_round


class TemplateNotFoundError(Exception):  # テンプレート読み込みエラー
    pass


def format_seconds(seconds):
    # 秒(REAPER管理)から、hh:mm:ss.ms(YMM4管理)に直す
    delta = datetime.timedelta(seconds=seconds)
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = delta.microseconds
    return "{:02d}:{:02d}:{:02d}.{:06d}".format(hours, minutes, seconds, microseconds)


class YMM4:
    def __init__(self, mydict):
        self.json_path = ''
        self.fps = mydict["fps"]
        self.mydict = mydict
        self.setting = {}
        self.temp_list = []

    def load(self):
        # YMM4のバージョン情報を取得
        with open(os.path.dirname(self.mydict["YMM4Path"]) + '/YukkuriMovieMaker.deps.json') as f:
            deps_json = f.read()
        ymm_cnt = deps_json.find('YukkuriMovieMaker')
        version = deps_json[ymm_cnt + 18:ymm_cnt + 38]
        version = version[:version.find('"')]
        self.version = version
        print("YMM4を読込みました。 > " + self.mydict["YMM4Path"])
        print("YukkuriMovieMaker4 Ver " + version)

        self.json_path = os.path.dirname(
            self.mydict["YMM4Path"]) + '/user/setting/' + self.version + '/YukkuriMovieMaker.Settings.ItemSettings.json'
        # YMM4のItemSettings.jsonを読み込む
        with open(os.path.dirname(self.mydict["YMM4Path"]) + '/user/setting/' + version +
                  '/YukkuriMovieMaker.Settings.ItemSettings.json', encoding='utf_8_sig') as f:
            self.setting = json.loads(f.read())

        # テンプレートリストを作る
        for obj in self.setting['Templates']:
            self.temp_list.append(obj['Name'])

    def check_byoga_henkan(self):
        for root, dirs, files in os.walk(os.path.dirname(self.mydict["YMM4Path"]) + '/user/plugin/'):
            for file in files:
                if file == 'DrawConversionEffect.dll':
                    return True
        return False

    def find_template(self, name):
        """指定した文字列の名前のテンプレートを探し、その添え字を返す。無い場合は-1を返す。"""
        tempidxes = []
        for index, obj in enumerate(self.setting['Templates']):
            if obj['Name'] == name:  # パスまで完全一致した場合はその添え字を返す
                return index
            if obj['Path'][-1].endswith(name):  # パス違いで名前が一緒の場合はその添え字をリストに保存する
                tempidxes.append(index)

        # 名前が一致したテンプレートの1番目を選択して返す
        return tempidxes[0] if tempidxes else -1

    def run(self, objdict, file_path):
        ymmparam_dict = [
            [1, 'X'],
            [2, 'Y'],
            [3, 'Z'],
            [4, 'Zoom'],
            [5, 'Opacity'],
            [6, 'Rotation']
        ]
        up_down_flip_effect = {
            "$type": "DrawConversionEffect.InvertConversionEffect.InvertConversionEffect, DrawConversionEffect",
            "Horizontal": False,
            "Vertical": True,
            "IsEnabled": True
        }

        end = {}

        items = []
        item_count = 0
        bf = 0.0  # アイテム一つ前の最終フレーム  ==Endframe
        layer = 0  # オブジェクトのあるレイヤー（RPP上で複数トラックある場合は別トラックに配置する）
        bfidx = 0  # item_countの調整用 レイヤー頭のitem_count-bfidxが0になるような値を設定

        video_seconds = 0  # 動画の総秒数 (再生時間ランダム用)
        if self.mydict['RandomPlay']:
            videoload = cv2.VideoCapture(str(self.mydict["SrcPath"]))  # 動画を読み込む
            video_seconds = videoload.get(cv2.CAP_PROP_FRAME_COUNT) / videoload.get(cv2.CAP_PROP_FPS)  # 秒数

        for index in range(1, len(objdict["length"])):
            # オブジェクト最初のフレームと長さの計算
            obj_frame_pos = objdict["pos"][index] * self.mydict["fps"] + 1
            next_obj_frame_pos = objdict["pos"][index + 1] * self.mydict["fps"] + 1 \
                if index != len(objdict["length"]) - 1 else -1
            obj_frame_length = objdict["length"][index] * self.mydict["fps"]
            # 一つ前のオブジェクトとフレームがかぶらないようにする処理
            if sur_round(obj_frame_pos) == bf:
                obj_frame_pos += 1
                obj_frame_length -= 1
            # 一つ後のオブジェクトとの間に1フレームの空きがある場合の処理
            if sur_round(obj_frame_pos + obj_frame_length) == sur_round(next_obj_frame_pos) - 1:
                obj_frame_length += 1
            if obj_frame_pos < bf:
                bf = 0
                bfidx = -item_count
                layer += 1 + self.mydict["SepLayerEvenObj"]
                if obj_frame_pos < 0:
                    continue
            bf = obj_frame_pos + obj_frame_length - 1
            if self.mydict["NoGap"] == 1:
                if obj_frame_pos < sur_round(next_obj_frame_pos) - 1:
                    bf = next_obj_frame_pos - 1

            obj_frame_pos = sur_round(obj_frame_pos)
            # if obj_frame_pos == 0: obj_frame_pos = 1
            bf = sur_round(bf)

            # 先にダミーのitemを追加した後、必要な部分を置き換えていく

            # エイリアステンプレート読み込み
            if os.path.basename(self.mydict["EffPath"]) != "":
                aliasidx = self.find_template(os.path.basename(self.mydict["EffPath"]))
                if aliasidx < 0:
                    raise TemplateNotFoundError
                items.append(self.setting['Templates'][aliasidx]['Items'][0].copy())
                # 中間点が設定されているとYMM4上でバグが発生するので警告
                if items[-1]['KeyFrames']['Count'] != 0:
                    end['keyframe_exists'] = True
            else:
                items.append(deepcopy(self.default_item))

            items[-1]['Frame'] = int(obj_frame_pos)
            items[-1]['Length'] = int(bf - obj_frame_pos + 1)

            # 偶数番目オブジェクトをひとつ下のレイヤに配置する
            if self.mydict["SepLayerEvenObj"] == 1 and (bfidx + item_count) % 2 == 1:
                items[-1]['Layer'] = layer + 1
            else:
                items[-1]['Layer'] = layer

            # オブジェクトの反転の設定
            if self.mydict["ObjFlipType"] == 0:  # 反転なし
                pass
            elif self.mydict["ObjFlipType"] == 1 and (bfidx + item_count) % 2 == 1:  # 左右反転
                items[-1]['IsInverted'] = True
            elif self.mydict["ObjFlipType"] == 2 and (bfidx + item_count) % 2 == 1:  # 上下反転
                items[-1]['VideoEffects'].append(up_down_flip_effect)
                if not self.check_byoga_henkan():
                    end['byoga_henkan_not_exists'] = True
            elif self.mydict["ObjFlipType"] == 3:  # 時計回り反転
                if (bfidx + item_count) % 4 == 1:
                    items[-1]['IsInverted'] = True
                elif (bfidx + item_count) % 4 == 2:
                    items[-1]['IsInverted'] = True
                    items[-1]['VideoEffects'].append(up_down_flip_effect)
                elif (bfidx + item_count) % 4 == 3:
                    items[-1]['VideoEffects'].append(up_down_flip_effect)

            # エイリアステンプレートを読み込んでいる場合は、テンプレートの中身のオブジェクトをそのまま反映する (この先の処理は無視)
            if self.mydict['EffPath'] != "":
                items[-1]['Group'] = 1
                item_count += 1
                continue

            # 主パラメータの設定
            items[-1]['IsClippingWithObjectAbove'] = bool(self.mydict["clipping"])
            items[-1]['Blend'] = self.mydict['Param'][-1][6:]
            for paramlist in ymmparam_dict:
                prms = self.mydict['Param'][paramlist[0]].split(',')
                items[-1][paramlist[1]]['Values'][0]['Value'] = float(prms[0][prms[0].find('=') + 1:])
                if len(prms) > 1:
                    items[-1][paramlist[1]]['Values'][1]['Value'] = float(prms[1])
                    items[-1][paramlist[1]]['AnimationType'] = prms[2]

            # オブジェクトの種類等の設定
            if self.mydict["OutputType"] == 0:
                if objdict["filetype"][index] == "VIDEO":
                    file = file_path[objdict["fileidx"][index]]
                else:
                    file = ""
                items[-1]['ContentOffset'] = format_seconds(objdict["soffs"][index])
                items[-1]['PlaybackRate'] = int(objdict["playrate"][index] * 1000) / 10.0
                items[-1]['IsLooped'] = bool(objdict["loop"][index]) if self.mydict["IsLoop"] else False
                items[-1]['FilePath'] = file
            elif self.mydict["OutputType"] == 1:  # 動画オブジェクト
                if self.mydict["RandomPlay"]:   # 再生位置ランダム
                    self.mydict["SrcPosition"] = format_seconds(random.uniform(0, video_seconds))
                items[-1]['FilePath'] = str(self.mydict["SrcPath"])
                items[-1]['ContentOffset'] = self.mydict["SrcPosition"]
                items[-1]['PlaybackRate'] = self.mydict["SrcRate"]
                items[-1]['IsLooped'] = self.mydict["IsLoop"]
            elif self.mydict["OutputType"] == 2:  # 画像オブジェクト
                items[-1]['$type'] = "YukkuriMovieMaker.Project.Items.ImageItem, YukkuriMovieMaker"
                items[-1]['FilePath'] = str(self.mydict["SrcPath"])
            elif self.mydict["OutputType"] == 3:  # フィルタオブジェクト
                items[-1]['$type'] = "YukkuriMovieMaker.Project.Items.EffectItem, YukkuriMovieMaker"
                del items[-1]['Zoom']
            elif self.mydict["OutputType"] == 4:  # 立ち絵オブジェクト
                items[-1]['$type'] = "YukkuriMovieMaker.Project.Items.TachieItem, YukkuriMovieMaker"

            item_count += 1

        # 保存する名前のテンプレートがあるかを検索、あれば上書き確認
        save_template = os.path.basename(self.mydict["EXOPath"])[:-4]
        tempidx = self.find_template(save_template)
        if tempidx < 0:  # テンプレートが存在しなければ新規に作る
            self.setting['Templates'].append(self.default_temp)
            self.setting['Templates'][-1]['Name'] = save_template
            self.setting['Templates'][-1]['Path'][0] = save_template
            tempidx = len(self.setting['Templates']) - 1
        else:  # テンプレートが存在していれば上書き確認する
            ret = messagebox.askyesno("確認", f"テンプレート「{save_template}」は既に存在します。上書きしますか？", icon="info")
            if not ret:  # 括弧数字でナンバリングする
                number = 1
                while self.find_template(save_template + f' ({number})') != -1:
                    number += 1
                self.setting['Templates'].append(deepcopy(self.default_temp))
                self.setting['Templates'][-1]['Name'] = save_template + f' ({number})'
                self.setting['Templates'][-1]['Path'][0] = save_template + f' ({number})'
                tempidx = len(self.setting['Templates']) - 1

        # テンプレートを保存
        self.setting['Templates'][tempidx]['Items'] = items
        with open(self.json_path, mode='w', encoding='utf_8_sig') as f:
            f.write(json.dumps(self.setting, ensure_ascii=False, indent=2))

        return end

    default_temp = {
        "Name": "RPPtoEXO",
        "Path": [
            "RPPtoEXO"
        ],
        "Group": "None",
        "KeyGesture": {
            "Key": 0,
            "Modifiers": 2
        },
        "Items": []
    }

    default_item = {
        "$type": "YukkuriMovieMaker.Project.Items.VideoItem, YukkuriMovieMaker",
        "IsWaveformEnabled": False,
        "FilePath": "",
        "AudioTrackIndex": 0,
        "Volume": {
            "Values": [
                {
                    "Value": 0.0
                },
                {
                    "Value": 0.0
                }
            ],
            "Span": 0.0,
            "AnimationType": "なし"
        },
        "Pan": {
            "Values": [
                {
                    "Value": 0.0
                },
                {
                    "Value": 0.0
                }
            ],
            "Span": 0.0,
            "AnimationType": "なし"
        },
        "PlaybackRate": 100.0,
        "ContentOffset": "00:00:00",
        "IsLooped": False,
        "EchoIsEnabled": False,
        "EchoInterval": 0.1,
        "EchoAttenuation": 40.0,
        "AudioEffects": [],
        "X": {
            "Values": [
                {
                    "Value": 0.0
                },
                {
                    "Value": 0.0
                }
            ],
            "Span": 0.0,
            "AnimationType": "なし"
        },
        "Y": {
            "Values": [
                {
                    "Value": 0.0
                },
                {
                    "Value": 0.0
                }
            ],
            "Span": 0.0,
            "AnimationType": "なし"
        },
        "Z": {
            "Values": [
                {
                    "Value": 0.0
                },
                {
                    "Value": 0.0
                }
            ],
            "Span": 0.0,
            "AnimationType": "なし"
        },
        "Opacity": {
            "Values": [
                {
                    "Value": 100.0
                },
                {
                    "Value": 0.0
                }
            ],
            "Span": 0.0,
            "AnimationType": "なし"
        },
        "Zoom": {
            "Values": [
                {
                    "Value": 100.0
                },
                {
                    "Value": 0.0
                }
            ],
            "Span": 0.0,
            "AnimationType": "なし"
        },
        "Rotation": {
            "Values": [
                {
                    "Value": 0.0
                },
                {
                    "Value": 0.0
                }
            ],
            "Span": 0.0,
            "AnimationType": "なし"
        },
        "FadeIn": 0.0,
        "FadeOut": 0.0,
        "Blend": "Normal",
        "IsInverted": False,
        "IsClippingWithObjectAbove": False,
        "IsAlwaysOnTop": False,
        "IsZOrderEnabled": False,
        "VideoEffects": [],
        "Group": 1,
        "Frame": 1,
        "Layer": 0,
        "KeyFrames": {
            "Frames": [],
            "Count": 0
        },
        "Length": 75,
        "Remark": "",
        "IsLocked": False,
        "IsHidden": False
    }
