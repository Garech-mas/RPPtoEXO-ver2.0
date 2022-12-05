
srch_type = {"VIDEO": "VIDEO",  # 動画ファイル
             "WAVE": "AUDIO",  # WAV ファイル
             "MP3": "AUDIO",  # MP3 ファイル
             "VORBIS": "AUDIO",  # OGG ファイル
             "FLAC": "AUDIO",  # FLAC ファイル
             "MIDI": "XMIDI",  # MIDI アイテム
             }


def main_load(rpp_ary, auto_src, sel_track):
    end = {"exist_mode2": [], "exist_stretch_marker": []}
    file_path = []
    objDict = {
        "pos": [-1.0],
        "length": [-1.0],
        "loop": [-1],
        "soffs": [-1.0],
        "playrate": [-1.0],
        "fileidx": [-1],
        "filetype": ['']
    }

    # RPPを読み込み、必要な情報をitemdictに格納していく
    index = 0
    track_index = 0
    track_name = ""

    while index < len(rpp_ary):

        if rpp_ary[index].split()[0] == "<TRACK":  # トラック境目
            track_index += 1
            if objDict["pos"][-1] != -1:  # トラックが切り替わる位置に-1を入れる
                track_name = str(rpp_ary[index + 1][9:-1])
                objDict["pos"].append(-1)
                objDict["length"].append(-1)
                objDict["loop"].append(-1)
                objDict["soffs"].append(-1)
                objDict["playrate"].append(0)
                objDict["fileidx"].append(-1)
                objDict["filetype"].append('')

        if str(track_index) in sel_track and rpp_ary[index].split()[0] == "<ITEM":  # 該当トラックのITEMチャンクに入ったら
            itemdict = {}
            tempdict = {}
            prefix = ""
            can_assign = True
            item_lyr = 1
            index += 1

            while item_lyr > 0:  # <ITEM >を辞書化し、管理しやすくする
                if rpp_ary[index].split()[0].startswith("<"):  # 深い階層に入る
                    prefix += rpp_ary[index][rpp_ary[index].find("<") + 1:-1] + "/"
                    item_lyr += 1
                elif rpp_ary[index].split()[0] == ">":  # 階層を下る
                    slash_pos = prefix.find("/")
                    prefix = prefix[slash_pos + 1:] if slash_pos != len(prefix) - 1 else ""
                    item_lyr -= 1
                else:
                    spl = rpp_ary[index].split()
                    key = prefix + spl.pop(0)
                    if can_assign:
                        itemdict[key] = spl
                    if key == 'TAKE':
                        if not spl:  # テイクが選択されていなかったら
                            can_assign = False
                        else:
                            can_assign = True
                            tempdict["POSITION"] = itemdict["POSITION"]
                            tempdict["LENGTH"] = itemdict["LENGTH"]
                            tempdict["LOOP"] = itemdict["LOOP"]
                            itemdict.clear()
                            itemdict = tempdict

                index += 1

            index -= 2
            objDict["pos"].append(float(itemdict["POSITION"][0]))
            objDict["length"].append(float(itemdict["LENGTH"][0]))
            if auto_src:  # 素材自動検出モードの処理
                objDict["loop"].append(int(itemdict["LOOP"][0]))
                objDict["soffs"].append(float(itemdict["SOFFS"][0])) if "SOFFS" in itemdict \
                    else objDict["soffs"].append(0.0)
                objDict["playrate"].append(float(itemdict["PLAYRATE"][0])) if "PLAYRATE" in itemdict \
                    else objDict["playrate"].append(1.0)
                srchflg = 0

                if "SOURCE SECTION/MODE" in itemdict and int(itemdict["SOURCE SECTION/MODE"][0]) >= 2:  # アイテムが逆再生
                    objDict["playrate"][-1] *= -1

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
            if ("SOURCE SECTION/LENGTH" in itemdict and
                    ("SOURCE SECTION/MODE" not in itemdict or itemdict["SOURCE SECTION/MODE"][0] != "3")):

                if "SOURCE SECTION/MODE" in itemdict and itemdict["SOURCE SECTION/MODE"][0] == "2" \
                        and not end["exist_mode2"]:  # 逆再生＋セクションのアイテムがあった場合
                    end["exist_mode2"].append("トラック: " + track_name + " 開始位置(秒): " + str(objDict["pos"][-1]))

                end_length = objDict["length"][-1]
                sec_length = float(itemdict["SOURCE SECTION/LENGTH"][0]) / float(itemdict["PLAYRATE"][0])
                sec_count = 1
                objDict["soffs"][-1] = float(itemdict["SOURCE SECTION/STARTPOS"][0])
                if objDict["loop"][-1] == 1:
                    objDict["loop"][-1] = 0
                    while sec_length * sec_count < end_length:  # セクションアイテムをUtl上で複数オブジェクトに分割していく
                        objDict["length"][-1] = sec_length
                        objDict["pos"].append(objDict["pos"][-1] + sec_length)
                        objDict["length"].append(-1)
                        objDict["loop"].append(0)
                        objDict["soffs"].append(objDict["soffs"][-1])
                        objDict["playrate"].append(objDict["playrate"][-1])
                        objDict["fileidx"].append(objDict["fileidx"][-1])
                        objDict["filetype"].append(objDict["filetype"][-1])
                        sec_count += 1
                objDict["length"][-1] = sec_length * (sec_count + 1) - end_length

            if "SM" in itemdict and not end["exist_stretch_marker"]:  # 伸縮マーカーが付くアイテムがあった場合
                end["exist_stretch_marker"].append("トラック: " + track_name + " 開始位置(秒): " + str(objDict["pos"][-1]))

        index += 1

    if not end["exist_mode2"]: del end["exist_mode2"]
    if not end["exist_stretch_marker"]: del end["exist_stretch_marker"]

    return objDict, file_path, end
