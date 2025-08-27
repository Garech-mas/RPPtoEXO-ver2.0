import pretty_midi
from rpp2exo import utils

class Midi:
    def __init__(self, path, display_lang=''):  # コンストラクタ 初期化
        self.midi_path = path
        self.start_pos = 0.0
        self.end_pos = 100000.0
        self.midi = pretty_midi.PrettyMIDI()
        self.objDict = {
            "pos": [-1.0],
            "length": [-1.0],
            "loop": [-1],
            "soffs": [-1.0],
            "pitch": [-99.9],
            "playrate": [-1.0],
            "fileidx": [-1],
            "filetype": ['']
        }
        # 翻訳用
        global _
        _ = utils.get_locale(display_lang)

    def load(self, path):
        self.midi_path = path
        try:
            self.midi = pretty_midi.PrettyMIDI(path)
        except FileNotFoundError as e:
            print(_("★ファイルを開くことができませんでした。: %s") % path)
            raise e

    def load_track(self):
        inst_names = {}
        if self.midi.lyrics:
            inst_names[_('歌詞')] = {}
        for inst in self.midi.instruments:
            name = f'{inst.name} [{len(inst.notes)}]'
            while name in inst_names:
                name += ' '
            inst_names[name] = {}

        return inst_names

    def main(self, sel_track):
        failed = self.load(self.midi_path)
        if failed:
            raise PermissionError()
        self.objDict = {
            "pos": [-1.0],
            "length": [-1.0],
            "loop": [-1],
            "soffs": [-1.0],
            "pitch": [-99.9],
            "playrate": [-1.0],
            "fileidx": [-1],
            "filetype": ['']
        }

        # 歌詞の処理
        if self.midi.lyrics and '1' in sel_track:
            lyrics = self.midi.lyrics
            for i, lyric in enumerate(lyrics):
                if not (self.start_pos <= lyric.time < self.end_pos):
                    continue
                self.objDict['pos'].append(lyric.time - self.start_pos)
                
                next_time = 0
                if i + 1 < len(lyrics):
                    next_time = lyrics[i+1].time
                else:
                    next_time = self.midi.get_end_time()
                
                self.objDict['length'].append(next_time - lyric.time)
                self.objDict['pitch'].append(-99.9)
                self.objDict["loop"].append(0)
                self.objDict["soffs"].append(0.0)
                self.objDict["playrate"].append(1.0)
                self.objDict["fileidx"].append(-1)
                self.objDict["filetype"].append("TEXT:" + lyric.text.encode("latin-1").decode("shift_jis"))

        for i, instrument in enumerate(self.midi.instruments, start=1 + bool(self.midi.lyrics)):
            if str(i) not in sel_track:
                continue
            # トラックが切り替わる位置に-1を入れる
            if self.objDict["pos"][-1] != -1:  # トラックが切り替わる位置に-1を入れる
                self.objDict["pos"].append(-1)
                self.objDict["length"].append(-1)
                self.objDict["loop"].append(-1)
                self.objDict["soffs"].append(-1)
                self.objDict["pitch"].append(-99.9)
                self.objDict["playrate"].append(0)
                self.objDict["fileidx"].append(-1)
                self.objDict["filetype"].append('')

            for note in instrument.notes:
                if not (self.start_pos <= note.start < self.end_pos):
                    continue
                self.objDict['pos'].append(note.start - self.start_pos)
                self.objDict['length'].append(note.end - note.start)
                self.objDict['pitch'].append(note.pitch)
                self.objDict["loop"].append(0)
                self.objDict["soffs"].append(0.0)
                self.objDict["playrate"].append(1.0)
                self.objDict["fileidx"].append(-1)
                self.objDict["filetype"].append('')

        return {}
