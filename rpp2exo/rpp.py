import os
import re
import gettext

srch_type = {"VIDEO": "VIDEO",  # 動画ファイル
             "WAVE": "AUDIO",  # WAV ファイル
             "MP3": "AUDIO",  # MP3 ファイル
             "VORBIS": "AUDIO",  # OGG ファイル
             "FLAC": "AUDIO",  # FLAC ファイル
             "MIDI": "XMIDI",  # MIDI アイテム
             }


class Rpp:
    def __init__(self, path, display_lang=''):  # コンストラクタ 初期化
        self.rpp_path = path
        self.start_pos = 0.0
        self.end_pos = 100000.0
        self.rpp_ary = []
        self.objDict = {
            "pos": [-1.0],
            "length": [-1.0],
            "loop": [-1],
            "soffs": [-1.0],
            "playrate": [-1.0],
            "fileidx": [-1],
            "filetype": ['']
        }
        # 翻訳用
        global _
        _ = gettext.translation(
            'text',  # domain: 辞書ファイルの名前
            localedir=os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)))),  # 辞書ファイル配置ディレクトリ
            languages=[display_lang],  # 翻訳に使用する言語
            fallback=True
        ).gettext

    def to_absolute(self, src):
        if os.path.isabs(src):
            return src
        else:
            return os.path.dirname(self.rpp_path) .replace('/', '\\') + '\\' + src

    def load_track(self):  # トラック名を読み込む
        tree = self.make_treedict(1)[0]
        return tree

    def load(self, path):  # RPPファイルをself.rpp_aryに入れる
        self.rpp_path = path
        try:
            if ".rpp" in path.lower():
                with open(path, mode='r', encoding='UTF-8', errors='replace') as f:
                    self.rpp_ary = f.readlines()
            elif path == '':
                self.rpp_ary = []
        except FileNotFoundError as e:
            print(_("★ファイルを開くことができませんでした。: %s") % path)
            raise e

    def load_marker_list(self):  # RPPからマーカー・リージョンを取得し、リスト化して返す
        index = 0
        time_ps_list = ['-']
        marker_list = ['-']
        in_region = False
        st = 0
        en = 0
        while index < len(self.rpp_ary):
            if self.rpp_ary[index].split()[0] == "SELECTION":
                st = str(int(float(self.rpp_ary[index].split()[1]) * 1000) / 1000)
                en = str(int(float(self.rpp_ary[index].split()[2]) * 1000) / 1000)
                if st > en:
                    st, en = en, st
                if not (st == en == '0.0'):
                    time_ps_list.append(_('選択時間 (%s~%s)') % (st, en))

            if self.rpp_ary[index].split()[0] == "MARKER":
                marker = self.rpp_ary[index].split()
                # <7.0 仕様のリージョン終に要素数を合わせる
                if '{' in marker[-1]:       # リージョン始/マーカー (RPP <7.0)
                    del marker[-1]
                elif '{' in marker[-2]:     # マーカー (RPP >7.0)
                    del marker[-2:]
                elif '""' in marker[-2]:    # リージョン終 (RPP >7.0)
                    marker += [1, 1, 1]

                if int(marker[-4]) % 2 == 0:  # マーカー
                    marker_name = ' ' + ' '.join(marker[3:-4]).replace('"', '')
                    pos = str(int(float(marker[2]) * 1000) / 1000)
                    marker_list.append("M" + marker[1] + marker_name + ": " + pos)
                else:  # リージョン
                    in_region = not in_region
                    if in_region:  # リージョン始点の処理
                        marker_name = ' ' + ' '.join(marker[3:-4]).replace('"', '')
                        st = str(int(float(marker[2]) * 1000) / 1000)
                    else:  # リージョン終点の処理
                        en = str(int(float(marker[2]) * 1000) / 1000)
                        time_ps_list.append('R' + marker[1] + marker_name + ' (' + st + '~' + en + ')')

            if self.rpp_ary[index].split()[0] == "<TRACK":
                break
            index += 1
        return time_ps_list, marker_list

    def make_treedict(self, index):  # CheckboxTreeviewで使う用の入れ子辞書を生成する
        value = {}
        while True:
            index += 1
            name = ''
            isbus = []
            while index < len(self.rpp_ary) and self.rpp_ary[index].split()[0] != "<TRACK":
                index += 1
            if index >= len(self.rpp_ary):
                return value, index, 0

            for i in range(index + 1, index + 12):
                spl = re.split(' +|\r\n|\n|\r', self.rpp_ary[i])[1:-1]
                key = spl.pop(0)
                if key == 'NAME':
                    name = str(self.rpp_ary[i][9:-1])
                elif key == 'MUTESOLO':
                    mute = int(self.rpp_ary[i][13])
                    name += "[M​]" * mute
                elif key == 'ISBUS':
                    isbus = self.rpp_ary[i].split()  # [1] > フォルダ始端・終端 [2] > 階層を何個下るか

            while name in value:
                name += " "  # トラック名が被っていた場合、末尾に半角スペースを被った数分付加して後から区別できるように
            value[name] = {}

            if isbus[1] == "1":
                value[name], index, skip = self.make_treedict(index)
                if skip < 0:
                    return value, index, skip + 1
            elif isbus[1] == "2":
                return value, index, int(isbus[2]) + 1

    def main(self, auto_src, sel_track):  # rpp_aryを読み込んだ結果をobjDictに入れていく
        failed = self.load(self.rpp_path)
        if failed:
            raise PermissionError()
        self.objDict = {
            "pos": [-1.0],
            "length": [-1.0],
            "loop": [-1],
            "soffs": [-1.0],
            "playrate": [-1.0],
            "fileidx": [-1],
            "filetype": ['']
        }
        end = {"exist_mode2": [], "exist_stretch_marker": []}
        file_path = []

        # RPPを読み込み、必要な情報をitemdictに格納していく
        index = 0
        track_index = 0
        track_name = ""

        while index < len(self.rpp_ary):

            if self.rpp_ary[index].split()[0] == "<TRACK":
                track_name = str(self.rpp_ary[index + 1][9:-1])
                track_index += 1
                if self.objDict["pos"][-1] != -1:  # トラックが切り替わる位置に-1を入れる
                    self.objDict["pos"].append(-1)
                    self.objDict["length"].append(-1)
                    self.objDict["loop"].append(-1)
                    self.objDict["soffs"].append(-1)
                    self.objDict["playrate"].append(0)
                    self.objDict["fileidx"].append(-1)
                    self.objDict["filetype"].append('')

            if str(track_index) in sel_track and self.rpp_ary[index].split()[0] == "<ITEM":  # 該当トラックのITEMチャンクに入ったら
                itemdict = {}
                tempdict = {}
                prefix = ""
                can_assign = True
                item_lyr = 1
                index += 1

                while item_lyr > 0:  # <ITEM>の中身を辞書化し、管理しやすくする
                    if self.rpp_ary[index].split()[0].startswith("<"):  # 深い階層に入る
                        prefix += self.rpp_ary[index][self.rpp_ary[index].find("<") + 1:-1] + "/"
                        item_lyr += 1
                    elif self.rpp_ary[index].split()[0] == ">":  # 階層を下る
                        slash_pos = prefix.find("/")
                        prefix = prefix[slash_pos + 1:] if slash_pos != len(prefix) - 1 else ""
                        item_lyr -= 1
                    else:
                        spl = re.split(' +|\r\n|\n|\r', self.rpp_ary[index])[1:-1]
                        key = prefix + spl.pop(0)
                        # splitで連続空白が削除されてしまいパスが変わってしまう為、個別にDictを設定
                        if key.endswith('FILE'):
                            spl = [self.rpp_ary[index][self.rpp_ary[index].find('FILE') + 5:-1].replace('"', '')]
                            # MP3ファイルの場合、FILE行末尾に謎の' 1'が付いてしまうので除去
                            if spl[0][-2:] == ' 1':
                                spl[0] = spl[0][:-2]
                        if can_assign:  # アイテム情報の上書きが可能なら
                            itemdict[key] = spl
                        if key == 'TAKE':
                            if not spl:  # テイクが選択されていなかったら上書き不可にする
                                can_assign = False
                            else:
                                can_assign = True
                                # itemdictの中身を全て消し、テイクによって不変な設定項目を戻す
                                tempdict["POSITION"] = itemdict["POSITION"]
                                tempdict["LENGTH"] = itemdict["LENGTH"]
                                tempdict["LOOP"] = itemdict["LOOP"]
                                itemdict.clear()
                                itemdict = tempdict

                    index += 1

                index -= 2
                if not (self.start_pos <= float(itemdict["POSITION"][0]) < self.end_pos):
                    continue

                self.objDict["pos"].append(float(itemdict["POSITION"][0]) - self.start_pos)
                self.objDict["length"].append(float(itemdict["LENGTH"][0]))
                if auto_src:  # 素材自動検出モードの処理
                    self.objDict["loop"].append(int(itemdict["LOOP"][0]))
                    self.objDict["soffs"].append(float(itemdict["SOFFS"][0])) if "SOFFS" in itemdict \
                        else self.objDict["soffs"].append(0.0)
                    self.objDict["playrate"].append(float(itemdict["PLAYRATE"][0])) if "PLAYRATE" in itemdict \
                        else self.objDict["playrate"].append(1.0)
                    srchflg = 0

                    if "SOURCE SECTION/MODE" in itemdict and int(itemdict["SOURCE SECTION/MODE"][0]) >= 2:  # アイテムが逆再生
                        self.objDict["playrate"][-1] *= -1

                    for srch in srch_type.keys():  # ファイルパス処理
                        keyy = "SOURCE " + srch + "/FILE"
                        if "SOURCE SECTION/" + keyy in itemdict:
                            path = self.to_absolute(itemdict["SOURCE SECTION/" + keyy][-1])
                            # if is_audio(path):
                            #     continue
                            if path not in file_path:
                                file_path.append(path)
                            self.objDict["fileidx"].append(file_path.index(path))
                            self.objDict["filetype"].append(srch_type[srch])
                            srchflg = 1
                        elif keyy in itemdict:
                            path = self.to_absolute(itemdict[keyy][-1])
                            # if is_audio(path):
                            #     continue
                            if path not in file_path:
                                file_path.append(path)
                            self.objDict["fileidx"].append(file_path.index(path))
                            self.objDict["filetype"].append(srch_type[srch])
                            srchflg = 1
                    if not srchflg:
                        self.objDict["fileidx"].append(-1)
                        self.objDict["filetype"].append("OTHER")

                # ループ＋セクションアイテムだったら
                if itemdict["LOOP"][0] == '1' and ("SOURCE SECTION/LENGTH" in itemdict and
                   ("SOURCE SECTION/MODE" not in itemdict or itemdict["SOURCE SECTION/MODE"][0] != "3")):
                    # 逆再生＋セクションのアイテムだったら
                    if "SOURCE SECTION/MODE" in itemdict and itemdict["SOURCE SECTION/MODE"][0] == "2":
                        end["exist_mode2"].append(_("トラック: %s / 開始位置(秒): %s") %
                                                  (track_name, str(int(self.objDict["pos"][-1] * 1000) / 1000)))

                    end_length = self.objDict["length"][-1]
                    sec_length = float(itemdict["SOURCE SECTION/LENGTH"][0]) / float(itemdict["PLAYRATE"][0])
                    sec_count = 1
                    self.objDict["soffs"][-1] = float(itemdict["SOURCE SECTION/STARTPOS"][0])
                    self.objDict["loop"][-1] = 0
                    while sec_length * sec_count - end_length < -0.001:  # セクションアイテムをUtl上で複数オブジェクトに分割
                        self.objDict["length"][-1] = sec_length
                        self.objDict["pos"].append(self.objDict["pos"][-1] + sec_length)
                        self.objDict["length"].append(-1)
                        self.objDict["loop"].append(0)
                        self.objDict["soffs"].append(self.objDict["soffs"][-1])
                        self.objDict["playrate"].append(self.objDict["playrate"][-1])
                        self.objDict["fileidx"].append(self.objDict["fileidx"][-1])
                        self.objDict["filetype"].append(self.objDict["filetype"][-1])
                        sec_count += 1
                    self.objDict["length"][-1] = sec_length * (sec_count + 1) - end_length

                if "SM" in itemdict:  # 伸縮マーカー付きアイテム
                    end["exist_stretch_marker"].append(_("トラック: %s / 開始位置(秒): %s") %
                                                  (track_name, str(int(self.objDict["pos"][-1] * 1000) / 1000)))

            index += 1

        if not auto_src or not end["exist_mode2"]: del end["exist_mode2"]
        if not auto_src or not end["exist_stretch_marker"]: del end["exist_stretch_marker"]

        return file_path, end
