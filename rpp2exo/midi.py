import gettext
import os
import pretty_midi


class Midi:
    def __init__(self, path, display_lang=''):  # コンストラクタ 初期化
        self.midi_path = path
        self.start_pos = 0.0
        self.end_pos = 100000.0
        self.midi = pretty_midi.PrettyMIDI()
        self.objDict = {
            "pos": [-1.0],
            "length": [-1.0],
        }
        # 翻訳用
        global _
        _ = gettext.translation(
            'text',  # domain: 辞書ファイルの名前
            localedir=os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)))),  # 辞書ファイル配置ディレクトリ
            languages=[display_lang],  # 翻訳に使用する言語
            fallback=True
        ).gettext

    def load(self, path):
        self.midi_path = path
        try:
            self.midi = pretty_midi.PrettyMIDI(path)
        except FileNotFoundError as e:
            print(_("★ファイルを開くことができませんでした。: %s") % path)
            raise e

    def load_track(self):
        inst_names = {}
        for inst in self.midi.instruments:
            name = f'{inst.name} [{len(inst.notes)}]'
            while name in inst_names:
                name += ' '
            inst_names[name] = {}
            # print("Instrument:", inst.program, inst.name, len(inst.notes),
            #       len(inst.pitch_bends), len(inst.control_changes))

        return inst_names

    def main(self, sel_track):
        failed = self.load(self.midi_path)
        if failed:
            raise PermissionError()
        self.objDict = {
            "pos": [-1.0],
            "length": [-1.0],
        }

        for i, instrument in enumerate(self.midi.instruments, start=1):
            if str(i) not in sel_track:
                continue
            # トラックが切り替わる位置に-1を入れる
            self.objDict["pos"].append(-1)
            self.objDict["length"].append(-1)

            print("Track:", i, "Instrument:", instrument.program, instrument.name, len(instrument.notes),
                  len(instrument.pitch_bends), len(instrument.control_changes))
            for note in instrument.notes:
                start_time_formatted = note.start
                end_time_formatted = note.end
                print(f'{note.pitch:10} {start_time_formatted:10} {end_time_formatted:10}')
                self.objDict['pos'].append(note.start)
                self.objDict['length'].append(note.end - note.start)

        return {}


print('5' in ['1', '15'])

# def seconds_to_minutes_seconds(seconds):
#     minutes = math.floor(seconds / 60)
#     seconds %= 60
#     return f"{minutes:02}:{seconds:02}"
#
# midi_data = pretty_midi.PrettyMIDI(r"C:\Users\msh_0\Music\【耳コピ】柴又【SD-90】.mid")
#
# print(f'{"Note":>10} {"Start":>10} {"End":>10}')



