import os
import json
import math
import random
import tempfile
import zipfile
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
import cv2
from rpp2exo import utils


class YMM4:
    def __init__(self, mydict):
        self.version = '0.0.0.0'
        self.json_path = ''
        self.fps = mydict["fps"]
        self.mydict = mydict
        self.setting = {}
        self.temp_list = ['',]
        # 翻訳用
        global _
        _ = utils.get_locale(mydict['DisplayLang'])

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
        for index, obj in enumerate(self.setting['Templates']):
            if obj['Name'] == name:  # パスまで完全一致した場合はその添え字を返す
                return index
        return -1

    def run(self, objdict, file_path):
        self.load()
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
        bpos = 0  # アイテム一つ前の開始フレーム
        bf = 0.0  # アイテム一つ前の最終フレーム  ==Endframe
        layer = 0  # オブジェクトのあるレイヤー（RPP上で複数トラックある場合は別トラックに配置する）
        bfidx = 0  # item_countの調整用 レイヤー頭のitem_count-bfidxが0になるような値を設定
        altidx = 0  # 同一音程判定の調整用

        opt_layer = []  # 1トラック内で重複が発生した場合の使用レイヤー状況をシミュレート
        opt_layer2 = []

        start_frame = 0
        end_frame = 0  # 動画の総フレーム数 (再生時間ランダム用)
        video_fps = 1  # 動画のFPS値 (再生時間ランダム用)
        if self.mydict['RandomPlay']:
            videoload = cv2.VideoCapture(str(self.mydict["SrcPath"]))  # 動画を読み込む
            video_fps = videoload.get(cv2.CAP_PROP_FPS)

            spl = self.mydict["RandomStart"].split(':')
            start_frame = (int(spl[0]) * 3600 + int(spl[1]) * 60 + float(spl[2])) * video_fps
            if self.mydict['RandomEnd']:
                spl = self.mydict["RandomEnd"].split(':')
                end_frame = (int(spl[0]) * 3600 + int(spl[1]) * 60 + float(spl[2])) * video_fps
            else:
                end_frame = videoload.get(cv2.CAP_PROP_FRAME_COUNT)  # フレーム数

        for index in range(1, len(objdict["length"])):
            add_layer = 0
            # オブジェクト最初のフレームと長さの計算
            obj_frame_pos = objdict["pos"][index] * self.mydict["fps"] + 1
            next_obj_frame_pos = objdict["pos"][index + 1] * self.mydict["fps"] + 1 \
                if index != len(objdict["length"]) - 1 else -1
            obj_frame_length = objdict["length"][index] * self.mydict["fps"]
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

            obj_frame_pos = self.sur_round(obj_frame_pos)
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

            # 先にダミーのitemを追加した後、必要な部分を置き換えていく
            # エイリアステンプレート読み込み
            eff_path = self.mydict['EffPaths'][(bfidx + item_count) % len(self.mydict['EffPaths'])]
            if eff_path:
                # ymmtファイルの読込み
                with zipfile.ZipFile(eff_path) as myzip:
                    with myzip.open('catalog.json') as myfile:
                        als_catalog = json.loads(myfile.read())
                        als_item = als_catalog['ItemTemplates'][0]['Items'][0]
                        items.append(deepcopy(als_item))
                        # 中間点が設定されているとYMM4上でバグが発生するので警告
                        if als_item['KeyFrames']['Count'] != 0:
                            end['keyframe_exists'] = True
            elif self.mydict["OutputType"] == 0 and objdict["filetype"][index].startswith('TEXT'):
                items.append(deepcopy(self.default_text_item))
            else:
                items.append(deepcopy(self.default_item))

            items[-1]['Frame'] = int(obj_frame_pos)
            items[-1]['Length'] = int(bf - obj_frame_pos + 1)

            # 偶数番目オブジェクトをひとつ下のレイヤに配置する
            if self.mydict["SepLayerEvenObj"] == 1:
                if (bfidx + item_count) % 2 == 0:
                    items[-1]['Layer'] = layer + add_layer * 2  # layer
                else:
                    items[-1]['Layer'] = layer + add_layer * 2 + 1  # layer
            else:
                items[-1]['Layer'] = int(layer + add_layer)

            # オブジェクトの反転の設定
            if self.mydict["ObjFlipType"] == 0:  # 反転なし
                pass
            elif self.mydict["ObjFlipType"] == 1 and (bfidx + item_count) % 2 == 1 and altidx % 2 == 0 or \
                 self.mydict["ObjFlipType"] == 2 and (bfidx + item_count) % 2 == 0 and altidx % 2 == 1:  # 左右反転
                items[-1]['IsInverted'] = True
            elif self.mydict["ObjFlipType"] == 2 and (bfidx + item_count) % 2 == 1 and altidx % 2 == 0 or \
                 self.mydict["ObjFlipType"] == 1 and (bfidx + item_count) % 2 == 0 and altidx % 2 == 1:  # 上下反転
                items[-1]['VideoEffects'].append(up_down_flip_effect)
                if not self.check_byoga_henkan():
                    end['byoga_henkan_not_exists'] = True
            elif self.mydict["ObjFlipType"] == 3:  # 時計回り反転
                if (bfidx + item_count - altidx) % 4 == 1:
                    items[-1]['IsInverted'] = True
                elif (bfidx + item_count - altidx) % 4 == 2:
                    items[-1]['IsInverted'] = True
                    items[-1]['VideoEffects'].append(up_down_flip_effect)
                elif (bfidx + item_count - altidx) % 4 == 3:
                    items[-1]['VideoEffects'].append(up_down_flip_effect)

            # エイリアステンプレートを読み込んでいる場合は、テンプレートの中身のオブジェクトをそのまま反映する (この先の処理は無視)
            if eff_path:
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
                if objdict["filetype"][index] in ["VIDEO", "IMAGE"]:
                    file = file_path[objdict["fileidx"][index]]
                else:
                    file = ""

                # 空アイテム (テキスト) の場合の処理
                if objdict["filetype"][index].startswith('TEXT'):
                    items[-1]['Text'] = objdict["filetype"][index][5:]

                # 空アイテム (画像) の場合の処理
                elif objdict["filetype"][index].startswith('IMAGE'):
                    items[-1]['$type'] = "YukkuriMovieMaker.Project.Items.ImageItem, YukkuriMovieMaker"
                    items[-1]['FilePath'] = file

                else:
                    items[-1]['ContentOffset'] = utils.format_seconds(objdict["soffs"][index])
                    items[-1]['PlaybackRate'] = int(objdict["playrate"][index] * 1000) / 10.0
                    items[-1]['IsLooped'] = bool(objdict["loop"][index]) if self.mydict["IsLoop"] else False
                    items[-1]['FilePath'] = file
            elif self.mydict["OutputType"] == 1:  # 動画オブジェクト
                if self.mydict["RandomPlay"]:   # 再生位置ランダム
                    self.mydict["SrcPosition"] = utils.format_seconds(random.uniform(start_frame, end_frame) * video_fps)
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
            elif self.mydict["OutputType"] == 4:  # シーンオブジェクト
                items[-1]['$type'] = "YukkuriMovieMaker.Project.Items.SceneItem, YukkuriMovieMaker"
                items[-1]['SceneId'] = "00000000-0000-0000-0000-000000000000"

            item_count += 1

        if item_count == 0:
            raise utils.ItemNotFoundError

        # 保存する名前のテンプレートがあるかを検索、あれば上書き確認
        catalog = deepcopy(self.default_ymmt)

        save_template = self.mydict['TemplateName']
        tempidx = self.find_template(save_template)
        if tempidx >= 0:
            catalog['ItemTemplates'][0]['Group'] = self.setting['Templates'][tempidx]['Group']
            catalog['ItemTemplates'][0]['KeyGesture'] = self.setting['Templates'][tempidx]['KeyGesture']

        catalog['ItemTemplates'][0]['Name'] = save_template
        catalog['ItemTemplates'][0]['Path'] = save_template.split('/')
        catalog['ItemTemplates'][0]['Items'] = items

        # テンプレートを保存
        print('一時フォルダ：' + str(tempfile.gettempdir()))
        with open(os.path.join(tempfile.gettempdir(), 'catalog.json'), mode='w', encoding='utf_8_sig') as f:
            f.write(json.dumps(catalog, ensure_ascii=False, indent=2))

        with zipfile.ZipFile(os.path.join(tempfile.gettempdir(), 'RPPtoYMMT_temp.ymmt'), 'w', zipfile.ZIP_DEFLATED) as ymmt:
            ymmt.write(os.path.join(tempfile.gettempdir(), 'catalog.json'), arcname='catalog.json')

        return end

    # iを設定内容の通りに丸める
    def sur_round(self, i):
        if self.mydict["UseRoundUp"] == 1:  # iを切り上げする
            return math.ceil(i)
        else:  # iを正確に四捨五入する
            result = Decimal(str(i)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
            return float(result)

    default_ymmt = {
        "FilePath": "C:\\Generated_By_RPPtoEXO.ymmt",
        "ItemTemplates": [
                {
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
            ]
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

    default_text_item = {
        "$type": "YukkuriMovieMaker.Project.Items.TextItem, YukkuriMovieMaker",
        "Text": "文字列文字列てすとてすと",
        "Decorations": [],
        "Font": "メイリオ",
        "FontSize": {
            "Values": [
                {
                    "Value": 34.0
                    }
                ],
            "Span": 0.0,
            "AnimationType": "なし"
            },
        "LineHeight2": {
            "Values": [
                {
                    "Value": 100.0
                    }
                ],
            "Span": 0.0,
            "AnimationType": "なし"
            },
        "LetterSpacing2": {
            "Values": [
                {
                    "Value": 0.0
                    }
                ],
            "Span": 0.0,
            "AnimationType": "なし"
            },
        "DisplayInterval": 0.0,
        "WordWrap": "NoWrap",
        "MaxWidth": {
            "Values": [
                {
                    "Value": 1920.0
                    }
                ],
            "Span": 0.0,
            "AnimationType": "なし"
            },
        "BasePoint": "LeftTop",
        "FontColor": "#FFFFFFFF",
        "Style": "Normal",
        "StyleColor": "#FF000000",
        "Bold": False,
        "Italic": False,
        "IsTrimEndSpace": False,
        "IsDevidedPerCharacter": False,
        "X": {
            "Values": [
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
                    }
                ],
            "Span": 0.0,
            "AnimationType": "なし"
            },
        "Z": {
            "Values": [
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
                    }
                ],
            "Span": 0.0,
            "AnimationType": "なし"
            },
        "Zoom": {
            "Values": [
                {
                    "Value": 100.0
                    }
                ],
            "Span": 0.0,
            "AnimationType": "なし"
            },
        "Rotation": {
            "Values": [
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
        "Group": 0,
        "Frame": 0,
        "Layer": 0,
        "KeyFrames": {
            "Frames": [],
            "Count": 0
            },
        "Length": 75,
        "PlaybackRate": 100.0,
        "ContentOffset": "00:00:00",
        "Remark": "",
        "IsLocked": False,
        "IsHidden": False
        }
