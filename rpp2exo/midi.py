import gettext
import os

import mido


class Midi:
    def __init__(self, path, display_lang=''):  # コンストラクタ 初期化
        self.midi_path = path
        self.start_pos = 0.0
        self.end_pos = 100000.0
        self.midi = None
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
            self.midi = mido.MidiFile(path)
        except FileNotFoundError as e:
            print(_("★ファイルを開くことができませんでした。: %s") % path)
            raise e

    def load_track(self):
        track_names = {}

        for track in self.midi.tracks:
            track_name = None
            for msg in track:
                if msg.type == 'track_name':
                    track_name = msg.name
                    break

            if track_name:
                track_names[track_name] = {}

        return track_names

    def main(self, sel_track):
        failed = self.load(self.midi_path)
        if failed:
            raise PermissionError()
        self.objDict = {
            "pos": [-1.0],
            "length": [-1.0],
        }

        tick_to_second = mido.tick2second(1, self.midi.ticks_per_beat, tempo=self.midi.tracks[0][0].tempo)

        total_ticks = 0
        layers = {str(x + 1): [] for x in range(99)}
        for track in self.midi.tracks:
            for msg in track:

                if msg.type == "note_on":
                    _layer = "0"
                    for x in list(layers.keys())[additional_layer:]:
                        if layers[x] == []:
                            if _layer == "0":
                                _layer = x
                        elif layers[x][0] == msg.note:
                            raise ValueError()
                            # raise NotesOverlapError(
                            #     f"同チャンネルのノーツが重なっています！\nExcepted Notes {msg.note}\nExcepted Channel:{msg.channel}")

                    # if option1:
                    #     additional_layer = int(not additional_layer)

                    layers[_layer] = [msg.note, current_frame]
                    max_layer = max(0, int(_layer))

                # note_on_time = 0
                # if msg.type == 'note_on' and msg.velocity > 0:
                #     note_on_time = msg.time
                # elif msg.type == 'note_off':
                #     note_off_time = msg.time
                #
                # if note_on_time is not None and note_off_time is not None:
                #     return (note_off_time - note_on_time) * tick_to_second
                #
                # total_ticks += msg.time

