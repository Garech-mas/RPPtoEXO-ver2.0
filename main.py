#####################################################################################
#               RPP to EXO ver 2.10.1                                               #
#                                                                       2025/08/21  #
#       Original Written by Maimai (@Maimai22015/YTPMV.info)                        #
#       Forked by Garech (@Garec_)                                                  #
#                                                                                   #
#       協力：SHI (@sbt54864666)                                                     #
#            wakanameko (@wakanameko2)                                              #
#            Flowzy (@FlowZy_BA)                                                    #
#####################################################################################
import threading
import warnings
import webbrowser
from functools import partial
from tkinter import *
from tkinter import Menu, filedialog, simpledialog, ttk
import tkinter.font as tkFont

import pygetwindow
from tkinterdnd2 import *
from ttkwidgets import CheckboxTreeview

from rpp2exo import *

rpp_cl = Rpp("")
ymm4_cl = YMM4(mydict)
midi_cl = Midi("")

def patched_error():
    if mydict['PatchExists']:
        print(_('(patch.aul未導入 かつ 拡張編集 Ver0.92以下 の環境では、%s)') % '\n'.join(mydict['HasPatchError']))
        return
    rsp = messagebox.showwarning(
        _("警告"), _('AviUtl本体のバグの影響により、\n%s\nEXOのインポート後、個別に設定してください。') % '\n'.join(mydict['HasPatchError']),
        detail=_('以下に当てはまる環境の方はこのバグを修正済みのため無視できます。以下のいずれかの環境に当てはまっていますか？\n'
                 '・拡張編集 v0.92 かつ patch.aul を導入済み\n・拡張編集v0.93rc1以上 を導入済み'),
        type='yesno', default='no')
    if rsp == 'yes':
        print(_('★選択を記録しました。今後拡張編集のバグによるEXO生成エラーはコンソール上に通知されます。'))
        mydict['PatchExists'] = 1
        write_cfg("1", "patch_exists", "Param")


def set_class_pos(cls):
    if ivr_slct_time.get():
        cls.start_pos = float(cmb_time1.get())
        cls.end_pos = float(cmb_time2.get()) if cmb_time2.get() != '' else 99999.0
        if cls.start_pos < cls.end_pos:
            pass
        elif cls.start_pos > cls.end_pos:
            cls.start_pos, cls.end_pos = cls.end_pos, cls.start_pos
        else:
            cls.start_pos = 0.0
            cls.end_pos = 99999.0
    else:
        cls.start_pos = 0.0
        cls.end_pos = 99999.0
    return cls


def main():
    mbar.entryconfig(_('生成設定'), state='disabled')
    mbar.entryconfig('Language', state='disabled')
    mbar.entryconfig(_('ヘルプ'), state='disabled')
    btn_exec['state'] = 'disable'
    root['cursor'] = 'watch'
    btn_exec["text"] = _("実行中") + " (1/4)"

    try:
        end1 = end2 = objdict = {}
        file_path = []

        # RPPファイル用処理
        if mydict["RPPPath"].lower().endswith(".rpp"):
            set_class_pos(rpp_cl)
            file_path, end1 = rpp_cl.main(mydict["OutputType"] == 0, mydict["Track"])
            objdict = rpp_cl.objDict
        # 選択時間の設定：MIDIファイル
        elif mydict["RPPPath"].lower().endswith(".mid") or mydict["RPPPath"].lower().endswith(".midi"):
            set_class_pos(midi_cl)
            end1 = midi_cl.main(mydict["Track"])
            objdict = midi_cl.objDict

        if mydict["OutputApp"] == 'YMM4':
            btn_exec["text"] = _("実行中") + " (4/4)"
            end3 = ymm4_cl.run(objdict, file_path)
        elif mydict["OutputApp"] == 'AviUtl2':
            exo2_cl = Exo2(mydict, file_path)

            btn_exec["text"] = _("実行中") + " (2/4)"
            end2 = exo2_cl.fix_sjis_files()

            btn_exec["text"] = _("実行中") + " (3/4)"
            exo2_cl.fetch_fps()

            btn_exec["text"] = _("実行中") + " (4/4)"
            end3 = exo2_cl.make_exo(objdict)
        else:
            exo_cl = Exo(mydict, file_path)

            btn_exec["text"] = _("実行中") + " (2/4)"
            end2 = exo_cl.fix_sjis_files()

            btn_exec["text"] = _("実行中") + " (3/4)"
            exo_cl.fetch_fps()

            btn_exec["text"] = _("実行中") + " (4/4)"
            end3 = exo_cl.make_exo(objdict)
        end = end1 | end2 | end3

    except PermissionError as e:
        if e.filename.lower().endswith('.exo'):
            messagebox.showerror(_("エラー"), _("上書き先のEXOファイルが開かれているか、読み取り専用になっています。"))
        else:
            messagebox.showerror(_("エラー"), _("下記ファイルの読込み権限がありません。\n") + e.filename)
    except FileNotFoundError as e:
        messagebox.showerror(_("エラー"), _("下記パス内のファイル/フォルダは存在しませんでした。\n") + e.filename)
    except UnicodeEncodeError as e:
        # reasonに該当行の文字列、objectに該当文字を格納
        messagebox.showerror(_("エラー"), _("AviUtl上で使用できない文字がパス名に含まれています。\n"
                                         "パス名に含まれる該当文字を削除し、再度実行し直してください。\n\n")
                             + e.reason + '    "' + e.object + '"')
    except LoadFilterFileError as e:
        messagebox.showerror(_("エラー"), _("下記のエイリアスファイルが不正です。正規の方法でEXAファイルを生成してください。\n") + e.filename)
    except ItemNotFoundError:
        messagebox.showerror(_("エラー"), _("出力範囲内に変換対象のアイテムが見つかりませんでした。\n"
                                         "出力対象トラック、時間選択の設定を見直してください。"))
    except TemplateNotFoundError:
        messagebox.showerror(_("エラー"), _("エイリアスに指定されているテンプレートは存在しませんでした。"))
    except KeyboardInterrupt:
        messagebox.showwarning(_("エラー"), _("生成がキャンセルされました。"))
    except Exception as e:
        e_type, e_object, e_traceback = sys.exc_info()
        messagebox.showerror(_("エラー"), _("予期せぬエラーが発生しました。不正なRPPファイルの可能性があります。\n"
                                         "最新バージョンのREAPERをインストールし、RPPファイルを再保存して再試行してください。\n"
                                         ) + str(e) + ";\n" + e_traceback.tb_frame.f_code.co_filename + ": " + str(e_traceback.tb_lineno))
        raise e
    else:
        warn_msgs = []
        if "exist_mode2" in end:
            warn_msgs.append(_("★警告: RPP内にセクション・逆再生付きのアイテムが存在したため、該当アイテムが正常に生成できませんでした。") + "\n")
            for i, detail in enumerate(end["exist_mode2"]):
                warn_msgs[-1] += "    " + detail + "\n"
                if i == 4:
                    warn_msgs[-1] += "    " + _("その他 %s個") % str(len(end["exist_mode2"]) - 5)
                    break

        if "exist_stretch_marker" in end:
            warn_msgs.append(_("★警告: RPP内に伸縮マーカーが設定されているアイテムが存在したため、該当アイテムが正常に生成できませんでした。") + "\n")
            for i, detail in enumerate(end["exist_stretch_marker"]):
                warn_msgs[-1] += "    " + detail + "\n"
                if i == 4:
                    warn_msgs[-1] += "    " + _("その他 %s個") % str(len(end["exist_stretch_marker"]) - 5)
                    break

        if "file_copy_failed" in end:
            warn_msgs.append(_("★警告: ファイル名・フォルダ名が複雑のため、該当アイテムが正常に生成できませんでした。\n以下ファイルを簡潔な場所に移動してください。") + "\n")
            for i, detail in enumerate(end["file_copy_failed"]):
                warn_msgs[-1] += "    " + detail + "\n"
                if i == 4:
                    warn_msgs[-1] += "    " + _("その他 %s個") % str(len(end["file_copy_failed"]) - 5)
                    break

        if "layer_over_100" in end:
            warn_msgs.append(_("★警告: 出力処理時にEXOのレイヤー数が100を超えたため、正常に生成できませんでした。"))

        if 'keyframe_exists' in end:
            warn_msgs.append(_("★警告: エイリアスファイルに中間点が存在したため、正常に生成できませんでした。"))

        if 'multiple_items' in end:
            warn_msgs.append(_("★警告: エイリアスファイル（EXOファイル）に複数アイテムが存在しているため、１番目のアイテムのみ生成されます。"))

        if 'byoga_henkan_not_exists' in end:
            warn_msgs.append(_("★警告: YMM4では上下反転機能が実装されていないため、上下反転の設定は反映されません。\n"
                             "    描画変換プラグインを導入し、テンプレートを再生成することで読み込むことができます。"))

        if 'time_tra_exists' in end:
            warn_msgs.append(_("★警告: 一部トラックバーの時間制御設定は反映されません。\nEXOのインポート後、個別に設定してください。"))

        if 'clipping_object_exists' in end:
            warn_msgs.append(_("★警告: クリッピングオブジェクトの設定は反映されません。\nEXOのインポート後、個別に設定してください。"))

        if not mydict['PatchExists'] and mydict['HasPatchError'] and mydict['OutputApp'] == 'AviUtl':
            patched_error()

        if 'file_copied' in end:
            messagebox.showinfo(_('確認'), _("AviUtlで読み込めないファイルが含まれていたため、RPPを保存したフォルダに一部の動画ファイルをコピーしました。"))

        if end != {}:
            for msg in warn_msgs:
                messagebox.showwarning(_("警告"), msg)
        show_dropwindow()

    finally:
        mbar.entryconfig(_('生成設定'), state='normal')
        mbar.entryconfig('Language', state='normal')
        mbar.entryconfig(_('ヘルプ'), state='normal')
        print('--------------------------------------------------------------------------')
        btn_exec['state'] = 'normal'
        root['cursor'] = 'arrow'
        btn_exec["text"] = _("実行")


def show_dropwindow():
    window = pygetwindow.getWindowsWithTitle(ExDict["拡張編集"])
    if mydict['OutputApp'] == 'YMM4':
        window = pygetwindow.getWindowsWithTitle("ゆっくりMovieMaker v" + ymm4_cl.version)
    elif mydict['OutputApp'] == 'AviUtl2':
        window = pygetwindow.getWindowsWithTitle("AviUtl ExEdit2")
    if window and window[0]:
        window[0].activate()

    # drop_root
    drop_root = TkinterDnD.Tk()
    drop_root.title(R2E_TITLE)

    drop_root.iconbitmap(default=os.path.join(TEMP_PATH, 'RPPtoEXO.ico'))
    drop_root.columnconfigure(1, weight=1)
    drop_root.resizable(False, False)
    drop_root.attributes("-topmost", True)

    lbl_drag_help = ttk.Label(drop_root, text=_('このウィンドウからAviUtlに直接ドラッグ&ドロップしてください。\n※ 挿入したいレイヤーの0秒地点にドラッグ&ドロップするようにしてください。'))
    if mydict['OutputApp'] == 'YMM4':
        lbl_drag_help['text'] = _('このウィンドウからYMM4に直接ドラッグ&ドロップしてください。\nその後、「%s」テンプレートを0秒地点に追加してください。\n'
                                  '※上書き確認ダイアログが出てきた場合、「上書きする」を選択してください。') % mydict['TemplateName']
    elif mydict['OutputApp'] == 'AviUtl2':
        lbl_drag_help['text'] = _(
            'このウィンドウからAviUtl2のシーンリストに直接ドラッグ&ドロップしてください。')
    lbl_drag_help.place(x=20,y=70)

    width = lbl_drag_help.winfo_reqwidth() + 40
    height = lbl_drag_help.winfo_reqheight() + 140
    drop_root.geometry(f"{width}x{height}")

    exo_path = ''
    def export_exo():
        nonlocal exo_path
        if exo_path:  # すでに保存パスが設定されている場合
            os.startfile(os.path.dirname(exo_path), operation='open')
            return

        exo_path = filedialog.asksaveasfilename(
            title=_("EXOファイル保存場所の選択"),
            defaultextension=".exo",
            filetypes=[(_("AviUtlオブジェクトファイル"), "*.exo"), (_("すべてのファイル"), "*.*")],
            parent=drop_root
        )
        try:
            if exo_path:  # 保存先が選択された場合
                temp_exo_path = os.path.join(tempfile.gettempdir(), 'RPPtoEXO_temp.exo')
                shutil.copy(temp_exo_path, exo_path)
                btn_export_exo['text'] = _('保存済み')
        except PermissionError as e:
            messagebox.showerror(_("エラー"), _("上書き先のEXOファイルが開かれているか、読み取り専用になっています。"))

    # EXO出力ボタンを作成
    btn_export_exo = ttk.Button(drop_root, text=_("EXO出力"), command=export_exo)
    if not mydict['OutputApp'] == 'YMM4':
        btn_export_exo.place(x=width - 100, y=height - 50, width=80, height=30)

    # ドラッグ操作
    def drag_init(event):
        data = (mydict['EXOPath'], )
        return (ASK, COPY), (DND_FILES, DND_TEXT), data

    def drag_window_close(event=None):
        drop_root.destroy()

    drop_root.protocol("WM_DELETE_WINDOW", drag_window_close)
    drop_root.drag_source_register(1, DND_FILES)
    drop_root.dnd_bind('<<DragInitCmd>>', drag_init)
    drop_root.bind('<Escape>', drag_window_close)
    lbl_drag_help.drag_source_register(1, DND_FILES)
    lbl_drag_help.dnd_bind('<<DragInitCmd>>', drag_init)
    btn_export_exo.drag_source_register(1, DND_FILES)
    btn_export_exo.dnd_bind('<<DragInitCmd>>', drag_init)

    drop_root.mainloop()


def fore_ymm4():
    try:
        window = pygetwindow.getWindowsWithTitle("ゆっくりMovieMaker v" + ymm4_cl.version)[0]
        if window:
            window.activate()
    except IndexError:
        pass

def set_rppinfo(reload=0):  # RPP内の各トラックの情報を表示する
    try:
        filepath = ent_rpp_input.get().replace('"', '')  # パスをコピペした場合のダブルコーテーションを削除
        if filepath == svr_rpp_input_temp.get() and reload == 0:
            return True
        svr_rpp_input_temp.set(filepath)
        tvw_slct_track.delete(*tvw_slct_track.get_children())
        tvw_slct_track.insert("", "end", text=_("＊全トラック"), iid="all", open=True)
        tvw_slct_track.change_state("all", 'tristate')
        tvw_slct_track.yview(0)

        rpp_cl.load_recent_path()
        if rpp_cl.rpp_list:
            opm_rpp_input.set_menu(*rpp_cl.rpp_list)

        if filepath.lower().endswith(".rpp"):
            try:
                rpp_cl.load(filepath)
            except PermissionError as e:
                messagebox.showerror(_("エラー"), _("下記ファイルの読込み権限がありません。\n") + e.filename)
                return True
            except FileNotFoundError as e:
                messagebox.showerror(_("エラー"),
                                     _("下記パス内のファイル/フォルダは存在しませんでした。\n") + e.filename)
                return True
            tree = rpp_cl.load_track()
            change_time_cb()
            insert_treedict(tree, "", 0)
        elif filepath.lower().endswith(".mid") or filepath.lower().endswith(".midi"):
            rpp_cl.load('')
            change_time_cb()
            if ivr_trgt_mode.get() == 0:
                ivr_trgt_mode.set(1)
                mode_command()

            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    midi_cl.load(filepath)
                except PermissionError as e:
                    messagebox.showerror(_("エラー"), _("下記ファイルの読込み権限がありません。\n") + e.filename)
                    return True
                except FileNotFoundError as e:
                    messagebox.showerror(_("エラー"),
                                         _("下記パス内のファイル/フォルダは存在しませんでした。\n") + e.filename)
                    return True
                except ValueError as e:
                    messagebox.showerror(_('エラー'), _('MIDIファイルの容量が極端に大きいか小さいため、読み込めませんでした。'))
                    raise e
                except RuntimeWarning as e:
                    messagebox.showwarning(_('警告'), _('MIDIの 拍子/テンポ 情報が正しく読み込めなかった可能性があります。\n'
                                                      '生成後、FPSの値が合っているにも関わらずテンポが合わない場合、Dominoを使ってMIDIを再出力してください。'))
                    warnings.filterwarnings('default')
                    midi_cl.load(filepath)
                tree = midi_cl.load_track()
                insert_treedict(tree, "", 0)
    except Exception as e:
        e_type, e_object, e_traceback = sys.exc_info()
        messagebox.showerror(_("エラー"), _("予期せぬエラーが発生しました。不正なRPPファイルの可能性があります。\n"
                                         "最新バージョンのREAPERをインストールし、RPPファイルを再保存して再試行してください。\n"
                                         ) + str(e) + ";\n" + e_traceback.tb_frame.f_code.co_filename + ": " + str(e_traceback.tb_lineno))
        raise e
    return True


def insert_treedict(tree, prefix, iid, parent_state=0):  # ツリー表示でトラック１行を描画する(再帰用)
    for k in tree:
        iid += 1
        state = 0
        if "[S​]" in k:
            state = 1
        elif "[M​]" in k:
            state = -1
        elif parent_state:
            state = parent_state

        if k == list(tree.keys())[-1]:  # 最下層のフォルダ内トラックの場合 視覚上の縦繋がりを消す
            tvw_slct_track.insert("all", "end", text=str(iid).zfill(2) + prefix + "└" + k, iid=str(iid))
            # チェックを付ける ソロトラックがない場合はstate>=0(normal)、ある場合は>=1(solo)
            if state >= rpp_cl.has_solo:
                tvw_slct_track.change_state(str(iid), 'checked')
            if tree[k]:
                iid = insert_treedict(tree[k], prefix + "　", iid, state)
        else:
            tvw_slct_track.insert("all", "end", text=str(iid).zfill(2) + prefix + "├" + k, iid=str(iid))
            if state >= rpp_cl.has_solo:
                tvw_slct_track.change_state(str(iid), 'checked')
            if tree[k]:
                iid = insert_treedict(tree[k], prefix + "│", iid, state)
    return iid


def to_absolute(path):
    if not path:
        return ''
    if os.path.isabs(path):
        return path
    else:
        return os.path.dirname(mydict["RPPPath"]) + '/' + path


# 動的なエフェクト設定生成
# 参考：https://qiita.com/nnahito/items/41be8e02a6ebc91386e7
hLabel = []  # ラベルのハンドル格納
hLabel2 = []  # ラベル実体
hSELabel = []  # 始点終点ラベルハンドル
hSELabelE = []  # 始点終点ラベル実体
hEntryS = []  # Entry 開始点
hEntryE = []  # Entry 終点
hEntryX = []  # Entry 移動方法
hEntryConf = []  # Entry 設定
hEntrySE = []  # Entry実体 開始点
hEntryEE = []  # Entry実体 終点
hEntryXCb = []  # コンボボックス実体 移動方法
hEntryConfE = []  # Entry 設定実体
hCheckBox = []  # チェックボックス用
hCheckBoxCb = []  # チェックボックス実体


def add_filter_label():
    if mydict['OutputApp'] == 'AviUtl' and mydict["EffCount"] >= 10:
        messagebox.showerror(_("エラー"), _("フィルタ効果は11個以上追加できません。"))
        return
    # エフェクト名ラベル
    hLabel.append(StringVar())
    hLabel[mydict["EffCount"] + mydict["EffNum"]].set(svr_add_eff.get())
    b = ttk.Label(
        frame_effprm, textvariable=hLabel[mydict["EffCount"] + mydict["EffNum"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=0)
    hLabel2.append(b)

    # 始点終点ラベル
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set(_("始点"))
    b = ttk.Label(
        frame_effprm, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=1)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set(_("終点"))
    b = ttk.Label(
        frame_effprm, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=3)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1
    hSELabel.append(StringVar())
    hSELabel[mydict["EffCount2"]].set(_("設定"))
    b = ttk.Label(
        frame_effprm, textvariable=hSELabel[mydict["EffCount2"]])
    b.grid(row=mydict["EffCount"] + mydict["EffNum"] +
               mydict["EffCbNum"], column=4)
    hSELabelE.append(b)
    mydict["EffCount2"] += 1

    mydict["Effect"].append([])
    mydict["Effect"][mydict["EffCount"]].append(svr_add_eff.get())
    mydict["EffCount"] += 1
    # EffDict[v2.get()]回分ループ
    for n in range(len(EffDict[svr_add_eff.get()])):
        if EffDict[svr_add_eff.get()][n][-1] == -1:
            hCheckBox.append(StringVar())
            hCheckBox[mydict["EffCbNum"]].set(0)
            hCheckBoxCb.append(ttk.Checkbutton(frame_effprm, padding=0, text=EffDict[svr_add_eff.get()][n][0],
                onvalue=1, offvalue=0, variable=hCheckBox[mydict["EffCbNum"]]))
            hCheckBoxCb[mydict["EffCbNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                                 columnspan=4, column=1, sticky=W)
            mydict["EffCbNum"] += 1
        elif EffDict[svr_add_eff.get()][n][-1] == -2:  # Entryだけの項目(めっちゃ強引な実装だから全体的に書き直したい…)
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]].set(EffDict[svr_add_eff.get()][n][0])
            b = ttk.Label(frame_effprm, textvariable=hLabel[mydict["EffNum"] + mydict["EffCount"]])
            b.grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(frame_effprm, textvariable=hEntryS[mydict["EffNum"]], width=7))
            hEntrySE[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                            column=1, columnspan=4, sticky=W + E)
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[svr_add_eff.get()][n][1])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(frame_effprm, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set(list(XDict.keys())[0])
            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(frame_effprm, textvariable=hEntryE[mydict["EffNum"]], width=7))
            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(frame_effprm, textvariable=hEntryConf[mydict["EffNum"]], width=5))
            mydict["EffNum"] += 1
        else:
            hLabel.append(StringVar())
            hLabel[mydict["EffNum"] + mydict["EffCount"]].set(EffDict[svr_add_eff.get()][n][0])
            b = ttk.Label(frame_effprm, textvariable=hLabel[mydict["EffNum"] + mydict["EffCount"]])
            b.grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"], column=0, padx=5)
            hLabel2.append(b)
            hEntryS.append(StringVar())
            hEntrySE.append(ttk.Entry(frame_effprm, textvariable=hEntryS[mydict["EffNum"]], width=7))
            hEntrySE[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                            column=1, padx=5)
            hEntrySE[mydict["EffNum"]].insert(END, EffDict[svr_add_eff.get()][n][1])
            set_decimal(hEntryS[mydict["EffNum"]], EffDict[svr_add_eff.get()][n][2])
            hEntryX.append(StringVar())
            hEntryXCb.append(ttk.Combobox(frame_effprm, textvariable=hEntryX[mydict["EffNum"]]))
            hEntryXCb[mydict["EffNum"]]['values'] = list(XDict.keys())
            hEntryXCb[mydict["EffNum"]].set(list(XDict.keys())[0])
            hEntryXCb[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                             column=2, padx=5)

            hEntryE.append(StringVar())
            hEntryEE.append(ttk.Entry(frame_effprm, textvariable=hEntryE[mydict["EffNum"]], width=7))
            hEntryEE[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                            column=3, padx=5)

            hEntryConf.append(StringVar())
            hEntryConfE.append(ttk.Entry(
                frame_effprm, textvariable=hEntryConf[mydict["EffNum"]], width=5))
            hEntryConfE[mydict["EffNum"]].grid(row=mydict["EffNum"] + mydict["EffCount"] + mydict["EffCbNum"],
                                               column=4, padx=5)

            mydict["EffNum"] += 1
    canvas.update()
    canvas.configure(scrollregion=(0, 0, frame_right.winfo_height(), frame_right.winfo_height()))
    canvas.grid(row=0, column=2, sticky=N, ipadx=frame_right.winfo_width()/2, ipady=310)


def del_filter_label():  # 効果パラメータ入力画面破棄
    for n in range(len(hLabel)):
        hLabel2[n].grid_forget()
    for n in range(len(hSELabelE)):
        hSELabelE[n].grid_forget()
    for n in range(len(hEntryS)):
        hEntrySE[n].destroy()
        hEntryEE[n].destroy()
        hEntryXCb[n].destroy()
        hEntryConfE[n].destroy()
    for n in range(len(hCheckBoxCb)):
        hCheckBoxCb[n].destroy()
    mydict["Effect"] = []
    mydict["EffCount"] = 0
    mydict["EffCount2"] = 0
    mydict["EffNum"] = 0
    mydict["EffCbNum"] = 0
    hLabel.clear()
    hLabel2.clear()
    hSELabel.clear()
    hSELabelE.clear()
    hEntryS.clear()
    hEntryE.clear()
    hEntryX.clear()
    hEntryConf.clear()
    hEntrySE.clear()
    hEntryEE.clear()
    hEntryXCb.clear()
    hEntryConfE.clear()
    hCheckBox.clear()
    hCheckBoxCb.clear()
    canvas.update()
    canvas.configure(scrollregion=(0, 0, frame_right.winfo_height(), frame_right.winfo_height()))
    canvas.grid(row=0, column=2, sticky=N, ipadx=frame_right.winfo_width()/2, ipady=310)


mLabel = []  # ラベルのハンドル格納
mLabel2 = []  # ラベル実体
mSELabel = []  # 始点終点ラベルハンドル
mSELabelE = []  # 始点終点ラベル実体
mEntryS = []  # Entry 開始点
mEntryE = []  # Entry 終点
mEntryX = []  # Entry 移動方法
mEntryConf = []  # Entry 設定
mEntrySE = []  # Entry実体 開始点
mEntryEE = []  # Entry実体 終点
mEntryXCb = []  # コンボボックス実体 移動方法
mEntryConfE = []  # Entry 設定実体


def toggle_media_label(flg):
    if flg == 2:  # 拡張描画切り替え
        mLabel[0].set(ExDict['拡張描画'])
        # 回転を消す
        mLabel2[6].grid_remove()
        mEntrySE[5].grid_remove()
        mEntryEE[5].grid_remove()
        mEntryXCb[5].grid_remove()
        mEntryConfE[5].grid_remove()

        # 回転の値をZ軸回転にコピー
        mEntryS[9].set(mEntryS[5].get())
        mEntryE[9].set(mEntryE[5].get())
        mEntryX[9].set(mEntryX[5].get())
        mEntryConf[9].set(mEntryConf[5].get())

        # 拡張描画の設定項目を描画
        for i in range(6, 13):
            mLabel2[i+1].grid()
            mEntrySE[i].grid()
            mEntryXCb[i].grid()
            mEntryEE[i].grid()
            mEntryConfE[i].grid()
    elif flg == 1:  # 標準描画切り替え
        mLabel[0].set(ExDict['標準描画'])
        # 拡張描画の設定項目を消す
        for i in range(6, 13):
            mLabel2[i+1].grid_remove()
            mEntrySE[i].grid_remove()
            mEntryEE[i].grid_remove()
            mEntryXCb[i].grid_remove()
            mEntryConfE[i].grid_remove()

        # Z軸回転の値を回転にコピー
        mEntryS[5].set(mEntryS[9].get())
        mEntryE[5].set(mEntryE[9].get())
        mEntryX[5].set(mEntryX[9].get())
        mEntryConf[5].set(mEntryConf[9].get())

        # 回転を描画
        mLabel2[6].grid()
        mEntrySE[5].grid()
        mEntryXCb[5].grid()
        mEntryEE[5].grid()
        mEntryConfE[5].grid()
    elif flg == 0:
        frame_stddraw.grid(row=1)
        frame_optdraw.grid(row=2, sticky='W')

    else:  # フィルタ切り替え
        frame_stddraw.grid_remove()
        frame_optdraw.grid_remove()


def run():
    mydict["RPPPath"] = svr_rpp_input.get().replace('"', '')
    mydict["EXOPath"] = os.path.join(tempfile.gettempdir(), 'RPPtoYMMT_temp.ymmt' if mydict['OutputApp'] == 'YMM4' else 'RPPtoEXO_temp.exo')
    mydict["OutputType"] = ivr_trgt_mode.get()
    mydict["SrcPath"] = to_absolute(svr_src_input.get().replace('"', '')).replace('/', '\\')
    mydict["EffPaths"][0] = to_absolute(svr_alias_input.get().replace('"', ''))
    while len(mydict['EffPaths']) > 1 and mydict['EffPaths'][-1] == '':
        mydict['EffPaths'].pop()
    mydict["IsAlpha"] = ivr_import_alpha.get()
    mydict["IsLoop"] = ivr_loop.get()
    if is_float(svr_fps_input.get()):
        mydict["fps"] = float(svr_fps_input.get())
    else:
        mydict["fps"] = ''
    mydict["ScriptText"] = txt_script.get('1.0', 'end-1c')
    mydict["ObjFlipType"] = ivr_v_flip.get() + ivr_h_flip.get()
    mydict["AltFlipType"] = ivr_alt_flip.get()
    mydict["SepLayerEvenObj"] = ivr_sep_even.get()
    mydict["NoGap"] = ivr_no_gap.get()
    mydict["RandomPlay"] = ivr_randplay.get()

    if mydict["RandomPlay"]:
        if mydict["OutputType"] == 1 and not os.path.isfile(mydict["SrcPath"]):
            messagebox.showinfo(_("エラー"), _("動画の素材パスを入力してください。"))
            ent_src_input.focus_set()
            return 0
        if mydict["OutputType"] == 4 and svr_randplay_en.get() == '':
            messagebox.showinfo(_("エラー"), _("再生位置ランダムの終点の値を入力してください。"))
            ent_randplay_en.focus_set()

        if mydict['OutputApp'] == 'YMM4':
            if is_float(svr_randplay_st.get()):
                svr_randplay_st.set(format_seconds(float(svr_randplay_st.get())))
            elif svr_randplay_st.get() == '':
                svr_randplay_st.set(format_seconds(0))
            if is_float(svr_randplay_en.get()):
                svr_randplay_en.set(format_seconds(float(svr_randplay_en.get())))

            if not is_float(svr_randplay_st.get()) and not re.match(r'^\d{2}:\d{2}:\d{2}(\.\d+)?$', svr_randplay_st.get()):
                messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (_('再生位置ランダム'), _('始点')))
                ent_randplay_st.focus_set()
                return 0
            if not is_float(svr_randplay_en.get()) and not re.match(r'^\d{2}:\d{2}:\d{2}(\.\d+)?$', svr_randplay_en.get()):
                if not(mydict["OutputType"] == 1 and svr_randplay_en.get() == ''):
                    messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (_('再生位置ランダム'), _('終点')))
                    ent_randplay_en.focus_set()
                    return 0
        elif mydict['OutputApp'] == 'AviUtl2':
            if svr_randplay_st.get() == '':
                svr_randplay_st.set('0.0')
            if not is_float(svr_randplay_st.get()):
                messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (_('再生位置ランダム'), _('始点')))
                ent_randplay_st.focus_set()
                return 0
            if svr_randplay_en.get() and not is_float(svr_randplay_en.get()):
                if not(mydict["OutputType"] == 1 and svr_randplay_en.get() == ''):
                    messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (_('再生位置ランダム'), _('終点')))
                    ent_randplay_en.focus_set()
                    return 0
        else:
            if svr_randplay_st.get() == '':
                svr_randplay_st.set('1')
            if not re.match(r'^[0-9]+$', svr_randplay_st.get()):
                messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (_('再生位置ランダム'), _('始点')))
                ent_randplay_st.focus_set()
                return 0
            if not re.match(r'^[0-9]+$', svr_randplay_en.get()):
                if not(mydict["OutputType"] == 1 and svr_randplay_en.get() == ''):
                    messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (_('再生位置ランダム'), _('終点')))
                    ent_randplay_en.focus_set()
                    return 0

        mydict["RandomStart"] = svr_randplay_st.get()
        mydict["RandomEnd"] = svr_randplay_en.get()
        if mydict["RandomStart"] > mydict["RandomEnd"] and mydict["RandomEnd"]:
            mydict["RandomStart"], mydict["RandomEnd"] = mydict["RandomEnd"], mydict["RandomStart"]


    mydict["clipping"] = ivr_clipping.get()
    mydict["IsExSet"] = ivr_adv_draw.get()
    mydict["SceneIdx"] = int(svr_scene_idx.get() or 0)
    mydict["Track"] = tvw_slct_track.get_checked()
    mydict["DisplayLang"] = svr_lang_r2e.get()
    mydict["ExEditLang"] = svr_lang_aul.get()
    mydict['HasPatchError'] = []

    mydict["Param"] = []
    write_cfg(mydict['OutputType'], "output_type", "Param")

    def set_mparam(i, mv=1, tp=1):
        if mydict['OutputApp'] == 'YMM4' and i == 13:  # YMM4の再生位置（00:00:00の形式）だけ独自処理を取る
            if is_float(mEntryS[i].get()):
                mEntryS[i].set(format_seconds(float(mEntryS[i].get())))
            if not re.match(r'^\d{2}:\d{2}:\d{2}(\.\d+)?$', mEntryS[i].get()):
                messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (
                mLabel[0].get(), mLabel[i + 1].get()))
                mEntrySE[i].focus_set()
                raise ValueError
            mydict["Param"].append(mLabel[i + 1].get() + '=' + set_decimal(mEntryS[i], prmlist[i][2]))
            return mv, tp
        elif not is_float(mEntryS[i].get()):
            messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。") % (mLabel[0].get(), mLabel[i+1].get()))
            mEntrySE[i].focus_set()
            raise ValueError
        if mv and -1 < float(mEntryS[i].get()) < 0:
            mydict['HasPatchError'].append(_('・トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
            mv = 0
        mydict["Param"].append(mLabel[i+1].get() + '=' + set_decimal(mEntryS[i], prmlist[i][2]))
        if mEntryX[i].get() == list(XDict.keys())[0] or mEntryX[i].get() == "":
            return mv, tp
        # 以下、移動方法ありの場合の処理
        if not is_float(mEntryE[i].get()):
            messagebox.showinfo(_("エラー"), _("%s : %s の終点が正しく入力されていません。") % (mLabel[0].get(), mLabel[i+1].get()))
            mEntryEE[i].focus_set()
            raise ValueError
        if mv and -1 < float(mEntryE[i].get()) < 0:
            mydict['HasPatchError'].append(_('・トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
            mv = 0
        mydict["Param"][-1] += ',' + set_decimal(mEntryE[i], prmlist[i][2]) + ','\
            + str(XDict.get(mEntryX[i].get(), '15@' + mEntryX[i].get()))
        if mEntryConf[i].get() != '':
            if not is_float(mEntryE[i].get()):
                messagebox.showinfo(_("エラー"),
                                    _("%s : %s の終点が正しく入力されていません。") % (mLabel[0].get(), mLabel[i + 1].get()))
                mEntryEE[i].focus_set()
                raise ValueError
            mydict["Param"][-1] += ',' + str(int(mEntryConf[i].get()))
            if tp and not str(XDict.get(mEntryX[i].get(), mEntryX[i].get())).isascii():
                mydict['HasPatchError'].append(_("・移動方法の設定の値は反映されません。"))
                tp = 0
        return mv, tp

    try:
        show_mv, show_tp = (1, 1)  # -1越0未満エラー(mv)・移動設定値エラー(tp)を表示する場合は1 一度表示したら0になる
        if mydict['OutputType'] != 3 or mydict['OutputApp'] == 'YMM4':
            if ivr_adv_draw.get():
                mydict['Param'].append('_name=' + ExDict['拡張描画'])
                for i in [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
                    show_mv, show_tp = set_mparam(i, show_mv, show_tp)
            else:
                mydict['Param'].append('_name=' + ExDict['標準描画'])
                for i in [0, 1, 2, 3, 4, 5, 13, 14]:
                    show_mv, show_tp = set_mparam(i, show_mv, show_tp)

            mydict['SrcRate'] = mydict['Param'].pop()[5:]
            mydict['SrcPosition'] = mydict['Param'].pop()[5:]
            mydict['Param'].append('blend=' + str(BlendDict[ParamCombo15.get()]))

        if mydict["RPPPath"] == "":
            messagebox.showinfo(_("エラー"), _("読み込むRPPを入力してください。"))
            ent_rpp_input.focus_set()
            return 0
        elif mydict["fps"] == "" or mydict["fps"] <= 0:
            messagebox.showinfo(_("エラー"), _("正しいFPSの値を入力してください。"))
            ent_fps_input.focus_set()
            return 0
        elif not mydict["Track"]:
            messagebox.showinfo(_("エラー"), _("出力するトラックを選択してください。"))
            tvw_slct_track.focus_set()
            return 0
        elif ivr_slct_time.get() and not is_float(cmb_time1.get()):
            messagebox.showinfo(_("エラー"), _("時間選択 (秒) の値が正しく入力されていません。"))
            cmb_time1.focus_set()
            return 0
        elif ivr_slct_time.get() and not is_float(cmb_time2.get()):
            messagebox.showinfo(_("エラー"), _("時間選択 (秒) の値が正しく入力されていません。"))
            cmb_time2.focus_set()
            return 0
        elif svr_alias_input.get() and not os.path.isfile(svr_alias_input.get()):
            messagebox.showinfo(_("エラー"), _("正しいエイリアスのパスを入力してください。"))
            ent_alias_input.focus_set()
            return 0
        elif svr_alias_input2.get() and not os.path.isfile(svr_alias_input2.get()):
            messagebox.showinfo(_("エラー"), _("正しいエイリアスのパスを入力してください。"))
            ent_alias_input2.focus_set()
            return 0

        if (mydict["SceneIdx"] <= 0 or mydict["SceneIdx"] >= 50) and mydict["OutputType"] == 4 and mydict['OutputApp'] != 'AviUtl2':
            messagebox.showinfo(_("エラー"), _("正しいシーン番号を入力してください。（範囲 : 1 ~ 49）"))
            ent_scene_idx.focus_set()
            return 0
        elif mydict["SceneIdx"] != 1 and mydict["OutputType"] == 4:
            mydict['HasPatchError'].append(_('・シーン番号は反映されません。'))

        count = mydict["EffCount"]
        runcount = 0
        runcountcb = 0
        eff = ""
        for i in range(0, int(count)):
            del mydict["Effect"][i][1:]
            for x in range(len(EffDict[mydict["Effect"][i][0]])):
                if EffDict[mydict["Effect"][i][0]][x][-1] != -1:  # チェックボックスでない場合
                    if EffDict[mydict["Effect"][i][0]][x][-1] != -2 and not is_float(hEntryS[runcount].get()):
                        messagebox.showinfo(_("エラー"), _("%s : %s の値が正しく入力されていません。")
                                            % (mydict["Effect"][i][0], EffDict[mydict["Effect"][i][0]][x][0]))
                        hEntrySE[runcount].focus_set()
                        return 0
                    if hEntryX[runcount].get() == list(XDict.keys())[0] or hEntryX[runcount].get() == "":  # 移動なしの場合
                        if show_mv and EffDict[mydict["Effect"][i][0]][x][-1] != -2 and \
                                -1 < float(hEntryS[runcount].get()) < 0:
                            mydict['HasPatchError'].append(_('・トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
                            show_mv = False

                        eff = [EffDict[mydict["Effect"][i][0]][x][0],
                               set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1])]
                        mydict["Effect"][i].append(eff)
                    else:  # 移動ありの場合
                        if not is_float(hEntryE[runcount].get()):
                            messagebox.showinfo(_("エラー"), _("%s : %s の終点が正しく入力されていません。")
                                                % (mydict["Effect"][i][0], EffDict[mydict["Effect"][i][0]][x][0]))
                            hEntryEE[runcount].focus_set()
                            return 0
                        if show_mv and EffDict[mydict["Effect"][i][0]][x][-1] != -2 and \
                                (-1 < float(hEntryS[runcount].get()) < 0 or -1 < float(hEntryE[runcount].get()) < 0):
                            mydict['HasPatchError'].append(_('・トラックバーの-1越0未満 ( -0.* ) の値は反映されません。'))
                            show_mv = False
                        eff = [EffDict[mydict["Effect"][i][0]][x][0],
                               set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                               + set_decimal(hEntryE[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                               + str(XDict.get(hEntryX[runcount].get(), '15@' + hEntryX[runcount].get()))]
                        if XDict.get(hEntryX[runcount].get(), 'a') != "":
                            eff[1] += str(hEntryConf[runcount].get())
                            if show_tp and not str(XDict.get(hEntryX[runcount].get(), hEntryX[runcount].get())).isascii():
                                mydict['HasPatchError'].append(_("・移動の設定の値は反映されません。"))
                                show_tp = False
                        if XDict.get(hEntryX[runcount].get(), 'a') != "" and hEntryConf[runcount].get() != "":
                            eff = [EffDict[mydict["Effect"][i][0]][x][0],
                                   set_decimal(hEntryS[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                                   + set_decimal(hEntryE[runcount], EffDict[mydict["Effect"][i][0]][x][-1]) + ","
                                   + str(XDict.get(hEntryX[runcount].get(), '15@' + hEntryX[runcount].get())) + ","
                                   + str(hEntryConf[runcount].get())]
                        mydict["Effect"][i].append(eff)
                    runcount += 1
                elif EffDict[mydict["Effect"][i][0]][x][-1] == -1:  # チェックボックスの場合
                    eff = [EffDict[mydict["Effect"][i][0]][x][0],
                           str(hCheckBox[runcountcb].get())]
                    mydict["Effect"][i].append(eff)
                    runcountcb += 1
    except ValueError:
        return 0

    if mydict["RPPPath"].lower().endswith(".rpp") and check_reaper_editing() == -1:
        messagebox.showwarning(_("エラー"), _("生成がキャンセルされました。"))
        return 0
    thread = threading.Thread(target=main)
    thread.start()

def check_reaper_editing():
    msg_root = Tk()
    msg_root.withdraw()
    ret = None
    last_mtime = os.path.getmtime(mydict["RPPPath"])
    while ret != messagebox.IGNORE:
        ret = messagebox.IGNORE
        windows = pygetwindow.getWindowsWithTitle("REAPER v")
        # REAPERを閉じている状態、又はファイルに更新が見られた場合はループを抜ける
        if not windows or os.path.getmtime(mydict["RPPPath"]) != last_mtime:
            break
        for window in windows:
            is_proj_open = os.path.basename(mydict["RPPPath"][:-4]) in window.title
            is_modified = '[変更済み]' in window.title or '[modified]' in window.title
            if not is_proj_open or is_modified:
                window.activate()
                msg_root.attributes("-topmost", True)  # メッセージボックスを最前面に固定する
                ret = messagebox.showwarning(
                    _('警告'),
                    _('未保存状態の可能性のあるREAPERを検出しました。\n未保存プロジェクトを保存後、「再試行」ボタンを押してください。'),
                    type=messagebox.ABORTRETRYIGNORE,
                    parent=msg_root
                )
                if ret == messagebox.ABORT:
                    msg_root.destroy()
                    return -1  # 処理を終了
                break
    msg_root.destroy()



def set_decimal(entry, unit):
    if unit == 0:
        return entry.get()
    try:
        m = float(entry.get())
    except ValueError:
        return entry.get()
    if unit == 0.001:
        n = format(m, '.3f')
    elif unit == 0.01:
        n = format(m, '.2f')
    elif unit == 0.1:
        n = format(m, '.1f')
    else:
        n = str(int(m))

    entry.set(n)
    return n


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


# GUI変更時に値の状態を変更する関数
def mode_command():  # 「追加対象」変更時の状態切り替え
    if ivr_trgt_mode.get() == 1 or ivr_trgt_mode.get() == 2:  # 「素材」テキストボックス・参照ボタン
        btn_src_browse['state'] = 'enable'
        ent_src_input['state'] = 'enable'
    else:
        btn_src_browse['state'] = 'disable'
        ent_src_input['state'] = 'disable'

    if ivr_trgt_mode.get() == 4:  # シーン番号
        ent_scene_idx['state'] = 'enable'
    else:
        ent_scene_idx['state'] = 'disable'

    if ivr_trgt_mode.get() == 3 and mydict['OutputApp'] != 'YMM4':  # 上のオブジェクトでクリッピング・拡張描画・設定項目
        chk_clipping['state'] = 'disable'
        chk_adv_draw['state'] = 'disable'
        toggle_media_label(-1)
    else:
        chk_clipping['state'] = 'enable'
        chk_adv_draw['state'] = 'enable'
        toggle_media_label(0)

    if ivr_trgt_mode.get() == 1:  # アルファチャンネルを読み込む
        chk_import_alpha['state'] = 'enable'
    else:
        chk_import_alpha['state'] = 'disable'


    if ivr_trgt_mode.get() == 1 or ivr_trgt_mode.get() == 4:  # ループ再生・再生速度・再生位置・再生位置ランダム
        chk_loop['state'] = chk_randplay['state'] = 'enable'
        if ivr_randplay.get() == 1:
            ent_randplay_st['state'] = ent_randplay_en['state'] = 'enable'
        # 拡張描画の設定項目を描画
        for i in range(13, 15):
            mLabel2[i + 1].grid()
            mEntrySE[i].grid()
            mEntryXCb[i].grid()
            mEntryEE[i].grid()
            mEntryConfE[i].grid()
    else:
        chk_loop['state'] = 'disable'
        chk_randplay['state'] = ent_randplay_st['state'] = ent_randplay_en['state'] = 'disable'
        ivr_randplay.set(0)
        # 拡張描画の設定項目を消す
        for i in range(13, 15):
            mLabel2[i + 1].grid_remove()
            mEntrySE[i].grid_remove()
            mEntryEE[i].grid_remove()
            mEntryXCb[i].grid_remove()
            mEntryConfE[i].grid_remove()

# さらに詳細な反転設定の表示/非表示
def toggle_same_pitch_option(state=None):
    if state is None: mydict["AddSamePitchOption"] = not mydict["AddSamePitchOption"]
    if mydict["AddSamePitchOption"]:
        lbl_alt_flip.grid()
        chk_alt_flip_off.grid()
        chk_alt_flip_on.grid()
        cmb_time2.grid(row=11, column=0, padx=5, pady=(3, 30), sticky=W + E)
    else:
        lbl_alt_flip.grid_remove()
        chk_alt_flip_on.grid_remove()
        chk_alt_flip_off.grid_remove()
        ivr_alt_flip.set(0)
        cmb_time2.grid(row=11, column=0, padx=5, pady=(3, 110), sticky=W + E)

# 再起動通知
def confirm_restart():
    ret = messagebox.askyesno(_("注意"), _("設定を反映するにはソフトを再起動する必要があります。再起動しますか？"),
                              detail=_("現在設定中の項目は失われます。"), icon="info")
    if ret:
        mydict["RPPPath"] = svr_rpp_input.get().replace('"', '')
        mydict["SrcPath"] = to_absolute(svr_src_input.get().replace('"', '')).replace('/', '\\')
        write_cfg(mydict['OutputType'], "output_type", "Param")
        restart_software(root, mydict["RPPPath"], mydict["SrcPath"])


# EXOインポート時の設定
def exo_import_setting():
    import_setting_root = Toplevel(root)
    import_setting_root.title(R2E_TITLE)
    import_setting_root.resizable(False, False)
    import_setting_root.attributes("-toolwindow", True)

    frm = ttk.Frame(import_setting_root, padding=10)
    frm.grid()

    # バリデーション関数
    def validate_int(P):
        return P.isdigit() or P == ""

    def validate_float(P):
        if P == "": return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    int_vcmd = (import_setting_root.register(validate_int), '%P')
    float_vcmd = (import_setting_root.register(validate_float), '%P')

    # 画像サイズ
    ttk.Label(frm, text=_("画像サイズ")).grid(row=0, column=0, sticky="w")
    width_entry = ttk.Entry(frm, width=6, validate="key", validatecommand=int_vcmd)
    width_entry.insert(0, str(mydict["res_x"]))
    width_entry.grid(row=0, column=1)
    ttk.Label(frm, text="×").grid(row=0, column=2)
    height_entry = ttk.Entry(frm, width=6, validate="key", validatecommand=int_vcmd)
    height_entry.insert(0, str(mydict["res_y"]))
    height_entry.grid(row=0, column=3)

    # フレームレート
    ttk.Label(frm, text=_("FPS(初期値)")).grid(row=1, column=0, sticky="w")
    fps_entry = ttk.Entry(frm, width=6, validate="key", validatecommand=float_vcmd)
    fps_entry.insert(0, str(mydict["default_fps"]))
    fps_entry.grid(row=1, column=1)
    ttk.Label(frm, text="fps").grid(row=1, column=2, sticky="w")

    # 音声レート
    ttk.Label(frm, text=_("音声レート")).grid(row=2, column=0, sticky="w")
    audio_entry = ttk.Entry(frm, width=6, validate="key", validatecommand=int_vcmd)
    audio_entry.insert(0, str(mydict["audio_rate"]))
    audio_entry.grid(row=2, column=1)
    ttk.Label(frm, text="Hz").grid(row=2, column=2, sticky="w")

    def check_null(entry, name):
        if not entry.get():
            messagebox.showerror(R2E_TITLE, _("%sの値が入力されていません。") % name)
            entry.focus_set()
            raise ValueError

    def on_ok():
        try:
            check_null(width_entry, _("画像サイズ(横)"))
            check_null(height_entry, _("画像サイズ(縦)"))
            check_null(audio_entry, _("音声レート"))
            if None in (width_entry.get(), height_entry.get(), fps_entry.get(), audio_entry.get()): return
            mydict.update({"res_x": width_entry.get(), "res_y": height_entry.get(), "default_fps": fps_entry.get(), "audio_rate": audio_entry.get()})
            for key in ("res_x", "res_y", "default_fps", "audio_rate"):
                write_cfg(mydict[key], key, "ImportSetting")
            if fps_entry.get():
                svr_fps_input.set(fps_entry.get())
            import_setting_root.destroy()
        except ValueError:
            pass

    # ボタン
    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=4, column=0, columnspan=4, pady=5)

    ok_btn = ttk.Button(btn_frame, text="OK", command=on_ok)
    ok_btn.grid(row=0, column=0, padx=5)

    cancel_btn = ttk.Button(btn_frame, text=_("キャンセル"), command=import_setting_root.destroy)
    cancel_btn.grid(row=0, column=1, padx=5)

    # root に配置
    import_setting_root.geometry(f"+{root.winfo_x()}+{root.winfo_y()}")

    # モーダルにする
    root.wait_window(import_setting_root)




if __name__ == '__main__':
    read_cfg()
    # 翻訳用クラスの設定
    rpp_cl.__init__('', mydict['DisplayLang'])
    midi_cl.__init__('', mydict['DisplayLang'])
    _ = get_locale(mydict['DisplayLang'])

    if os.path.exists(os.path.abspath(sys.argv[0]) + '_old'):
        os.remove(os.path.abspath(sys.argv[0]) + '_old')

    print(_('★RPPtoEXO実行中はこのコンソール画面を閉じないでください。'))

    # 拡張編集の言語ごとに使用辞書を切り替える
    prmlist = prmlist["1"]
    EffDict = EffDict[mydict['ExEditLang']]
    XDict = XDict[mydict['ExEditLang']]
    BlendDict = BlendDict[mydict['ExEditLang']]
    ExDict = ExDict[mydict['ExEditLang']]
    # root
    root = TkinterDnD.Tk()
    root.title(R2E_TITLE)

    root.iconbitmap(default=os.path.join(TEMP_PATH, 'RPPtoEXO.ico'))
    root.columnconfigure(1, weight=1)
    root.resizable(False, False)
    #Chinese translation:Use Arial font and resize window.
    if mydict['DisplayLang'] == "zh":
        default_font=tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Arial",size=8)
    if mydict['ExEditLang']=="zh":
        root.option_add("*Font","Arial 10")
    else:
        root.option_add("*Label.Font","HomuraM 10")

    def click_close():
        try:
            if os.path.isfile(os.path.join(tempfile.gettempdir(), 'RPPtoEXO_temp.exo')):
                os.remove(os.path.join(tempfile.gettempdir(), 'RPPtoEXO_temp.exo'))
            if os.path.isfile(os.path.join(tempfile.gettempdir(), 'RPPtoYMMT_temp.ymmt')):
                os.remove(os.path.join(tempfile.gettempdir(), 'RPPtoYMMT_temp.ymmt'))
            if os.path.isfile(os.path.join(tempfile.gettempdir(), 'catalog.json')):
                os.remove(os.path.join(tempfile.gettempdir(), 'catalog.json'))
        finally:
            root.destroy()
    root.protocol("WM_DELETE_WINDOW", click_close)

    # メニューバー作成
    mbar = Menu(root, tearoff=0)
    root.config(menu=mbar)

    # ファイルメニュー
    menu_file = Menu(mbar, tearoff=0)
    mbar.add_cascade(label=_('ファイル'), menu=menu_file)

    def slct_rpp():  # 参照ボタン
        filetype = [
            (_("対応ファイル"), "*.rpp;*.mid;*.midi"),
            (_("REAPERプロジェクトファイル"), "*.rpp"),
            (_("MIDIファイル"), "*.mid;*.midi"),
            ]
        filepath = filedialog.askopenfilename(
            filetypes=filetype, initialdir=mydict["RPPLastDir"], title=_("RPP・MIDIファイルを選択"))
        if filepath != '':
            svr_rpp_input.set(filepath)
            write_cfg(filepath, "RPPDir", "Directory")
            set_rppinfo(reload=1)
    menu_file.add_command(label=_('RPPを開く...'), command=slct_rpp)
    menu_file.add_command(label=_('終了'), command=click_close)

    # 生成設定メニュー
    menu_setting = Menu(mbar, tearoff=0)
    mbar.add_cascade(label=_('生成設定'), menu=menu_setting)
    ivr_is_ccw = IntVar()
    ivr_is_ccw.set(mydict['IsCCW'])
    menu_is_ccw = Menu(mbar, tearoff=0)
    menu_setting.add_cascade(label=_('左右上下反転時の回転方向'), menu=menu_is_ccw)
    menu_is_ccw.add_radiobutton(label=_('時計回り'), value=0, variable=ivr_is_ccw, command=lambda: [
                                     write_cfg(0, "is_ccw", "Param"),
                                     mydict.update(IsCCW=0)
                                  ])
    menu_is_ccw.add_radiobutton(label=_('反時計回り'), value=1, variable=ivr_is_ccw, command=lambda: [
                                     write_cfg(1, "is_ccw", "Param"),
                                     mydict.update(IsCCW=1)
                                  ])
    ivr_use_roundup = IntVar()
    ivr_use_roundup.set(mydict['UseRoundUp'])
    menu_setting.add_checkbutton(label=_('オブジェクトをAviUtlグリッドに合わせる'), variable=ivr_use_roundup,
                                 command=lambda: [
                                     write_cfg(int(ivr_use_roundup.get()), "use_roundup", "Param"),
                                     mydict.update(UseRoundUp=ivr_use_roundup.get())
                                 ])
    ivr_patch_exists = IntVar()
    ivr_patch_exists.set(mydict['PatchExists'])
    menu_setting.add_checkbutton(label=_('拡張編集v0.92由来のエラーを無視'), variable=ivr_patch_exists,
                                 command=lambda: [
                                     write_cfg(int(ivr_patch_exists.get()), "patch_exists", "Param"),
                                     mydict.update(PatchExists=ivr_patch_exists.get())
                                  ])
    ivr_same_pitch_option = IntVar(value=mydict['AddSamePitchOption'])
    menu_setting.add_checkbutton(label=_('さらに詳細な反転設定を追加'), variable=ivr_same_pitch_option,
                                 command=lambda: [
                                    write_cfg(int(ivr_same_pitch_option.get()), "same_pitch_option", "Param"),
                                    toggle_same_pitch_option()
                                  ])
    ivr_use_ymm4 = IntVar()
    ivr_use_ymm4.set(mydict['OutputApp'] == 'YMM4')

    def change_ymm4_path():
        filetype = [(_("ゆっくりMovieMaker4実行ファイル"), "YukkuriMovieMaker.exe")]
        filepath = filedialog.askopenfilename(
            filetypes=filetype, initialdir=os.path.dirname(mydict["YMM4Path"]),
            title=_("ゆっくりMovieMaker4の実行ファイルを選択"))
        if filepath != '':
            mydict['YMM4Path'] = filepath
            ymm4_cl.load()
            write_cfg(filepath, "ymm4Path", "Param")
        return filepath != ''

    menu_setting.add_separator()

    # 選択処理
    ivr_output_app = StringVar()
    ivr_output_app.set(mydict['OutputApp'])
    def change_output_app():
        selected = ivr_output_app.get()
        if selected == mydict['OutputApp']:
            return

        if selected == 'YMM4':
            if not change_ymm4_path():
                ivr_output_app.set(mydict['OutputApp'])
                return

        write_cfg(selected, "output_app", "Param")
        confirm_restart()

    # メニューにラジオボタン追加
    menu_setting.add_radiobutton(label=_('AviUtlモードで使う'),
                                 variable=ivr_output_app, value='AviUtl',
                                 command=change_output_app)
    menu_setting.add_radiobutton(label=_('AviUtl2モードで使う (beta)'),
                                 variable=ivr_output_app, value='AviUtl2',
                                 command=change_output_app)
    menu_setting.add_radiobutton(label=_('ゆっくりMovieMaker4モードで使う'),
                                 variable=ivr_output_app, value='YMM4',
                                 command=change_output_app)

    menu_setting.add_separator()
    menu_setting.add_command(label=_('EXOインポート時の設定'), command=exo_import_setting)

    # ゆっくりMovieMaker4 使用時の書き換え処理
    if mydict['OutputApp'] == 'YMM4':
        try:
            ymm4_cl.load()
            XDict = dict.XDict['ymm4']
            BlendDict = dict.BlendDict['ymm4']
            R2E_TITLE = 'RPPtoYMM4 (RPPtoEXO) v' + R2E_VERSION
            root.title(R2E_TITLE)
            ivr_byohen_exists = IntVar()
            menu_setting.add_command(label=_('YMM4の読込み場所を変更'), command=change_ymm4_path)

            def change_template_name():
                while True:
                    temp_name = simpledialog.askstring(R2E_TITLE, _("保存テンプレート名を入力してください"), initialvalue=mydict['TemplateName'])
                    if temp_name is None:
                        break
                    elif temp_name != '' and not temp_name.isspace():
                        mydict['TemplateName'] = temp_name
                        break
                    else:
                        mydict['TemplateName'] = 'RPPtoEXO'
                write_cfg(mydict['TemplateName'], "templ_name", "Param")
            menu_setting.add_command(label=_('保存テンプレート名を変更'), command=change_template_name)
        except FileNotFoundError:
            write_cfg('AviUtl', "output_app", "Param")
            restart_software(root)
    
    # AviUtl2 使用時の書き換え処理
    elif mydict['OutputApp'] == 'AviUtl2':
        prmlist = dict.prmlist["2"]
        ExDict = dict.ExDict["2"]
        XDict = dict.XDict['ja']
        BlendDict = dict.BlendDict['ja']
        EffDict = dict.EffDict["2"]
        R2E_TITLE = 'RPPtoEXO (for AviUtl2) v' + R2E_VERSION
        root.title(R2E_TITLE)

    # 言語設定メニュー
    menu_lang = Menu(mbar, tearoff=0)
    mbar.add_cascade(label='Language', menu=menu_lang)

    menu_lang_r2e = Menu(menu_lang, tearoff=0)
    menu_lang.add_cascade(label=_('表示言語'), menu=menu_lang_r2e)
    svr_lang_r2e = StringVar()
    svr_lang_r2e.set(mydict['DisplayLang'])

    def change_lang_r2e():
        if mydict['DisplayLang'] == svr_lang_r2e.get():
            return
        write_cfg(svr_lang_r2e.get(), 'display', 'Language')
        confirm_restart()

    menu_lang_r2e.add_radiobutton(label='日本語', value='ja', variable=svr_lang_r2e, command=change_lang_r2e)
    menu_lang_r2e.add_radiobutton(label='English', value='en', variable=svr_lang_r2e, command=change_lang_r2e)
    menu_lang_r2e.add_radiobutton(label='简体中文', value='zh', variable=svr_lang_r2e, command=change_lang_r2e)

    menu_lang_aul = Menu(menu_lang, tearoff=0)
    menu_lang.add_cascade(label=_('拡張編集の言語'), menu=menu_lang_aul)
    svr_lang_aul = StringVar()
    svr_lang_aul.set(mydict['ExEditLang'])
    def change_lang_aul():
        if mydict['ExEditLang'] == svr_lang_aul.get():
            return
        write_cfg(svr_lang_aul.get(), 'exedit', 'Language')
        confirm_restart()
    menu_lang_aul.add_radiobutton(label='日本語', value='ja', variable=svr_lang_aul, command=change_lang_aul)
    menu_lang_aul.add_radiobutton(label='English', value='en', variable=svr_lang_aul, command=change_lang_aul)
    if locale.getencoding() == 'cp936':
        menu_lang_aul.add_radiobutton(label='简体中文', value='zh', variable=svr_lang_aul, command=change_lang_aul)

    # ヘルプメニュー
    menu_help = Menu(mbar, tearoff=0)
    mbar.add_cascade(label=_('ヘルプ'), menu=menu_help)

    menu_help.add_command(label=_('使い方(Cosense/Scrapbox)'),
                          command=lambda: webbrowser.open(
                              _('https://cosen.se/Garech/RPPtoEXO%E3%81%AE%E7%94%BB%E9%9D%A2%E3%81%AE%E8%AA%AC%E6%98%8E_(v2.08~)')))

    def update_check():
        try:
            result = file_setup.rpp2exo_version_check(R2E_VERSION)
            if result == 1:
                ret = messagebox.askyesno(R2E_TITLE,
                                          _('最新バージョンが見つかりました。ダウンロードしますか？'))
                if ret:
                    file_setup.rpp2exo_update()
                    messagebox.showinfo(R2E_TITLE, _('最新バージョンのインストールが完了しました。'))
                    confirm_restart()

            elif result == 0:
                messagebox.showinfo(R2E_TITLE, _('お使いのRPPtoEXOは最新です。'))
            elif result == -1:
                ret = messagebox.askyesno(R2E_TITLE,
                                          _('最新バージョンが見つかりました。PY版は自動インストール非対応のため、ご自身で置き換える必要があります。\nGitHubのリンクを開きますか？'))
                if ret:
                    webbrowser.open('https://github.com/Garech-mas/RPPtoEXO-ver2.0/releases/latest')

        except Exception as e:
            messagebox.showerror(_('エラー'), _('エラーが発生しました: %s') % f'{str(e)}\n{e.args}')
    menu_help.add_command(label=_('最新バージョンを確認(GitHub)'), command=update_check)
    menu_help.add_command(label=_('制作者の連絡先(%s/Twitter)') % '𝕏',
                          command=lambda: webbrowser.open('https://x.com/Garec_'))

    def about_rpp2exo():
        messagebox.showinfo(R2E_TITLE, 'RPPtoEXO ver' + R2E_VERSION +
                            '\nOriginal (~v1.08) made by maimai22015\n   %s/Twitter: @Maimai22016'
                            '\nLatest Version (v2.0~) made by Garech\n   %s/Twitter: @Garec_' % ('𝕏', '𝕏'))
    menu_help.add_command(label=_('このソフトについて'), command=about_rpp2exo)

    # フレーム・キャンバス設定
    frame_left = ttk.Frame(root)
    frame_left.grid(row=0, column=0)
    frame_center = ttk.Frame(root)
    frame_center.grid(row=0, column=1)

    canvas = Canvas(root, width=200, height=200, highlightthickness=0)
    vsb_canvas = ttk.Scrollbar(canvas, orient=VERTICAL, command=canvas.yview)

    canvas.grid(row=0, column=2, sticky=N, ipadx=200, ipady=210 if mydict['OutputApp'] == 'YMM4' else 290)
    canvas.configure(yscrollcommand=vsb_canvas.set)
    frame_right = ttk.Frame(canvas)
    vsb_canvas.pack(side=RIGHT, fill=Y)
    canvas.create_window((0, 0), window=frame_right, anchor='nw')
    canvas.configure(scrollregion=(0, 0, 392, 392))

    # frame_rpp RPP選択
    frame_rpp = ttk.Frame(frame_left, padding=5)
    frame_rpp.grid(row=0, column=0, sticky=N)

    lbl_rpp_input = ttk.Label(frame_rpp, text='* RPP : ')
    lbl_rpp_input.grid(row=0, column=0)
    svr_rpp_input = StringVar()
    svr_rpp_input_temp = StringVar()
    ent_rpp_input = ttk.Entry(frame_rpp, textvariable=svr_rpp_input, width=46, validate='focusout',
                              validatecommand=root.register(set_rppinfo))
    ent_rpp_input.grid(row=0, column=1)
    ent_rpp_input.drop_target_register(DND_FILES)

    def drop_file(target, event):
        paths = root.tk.splitlist(event.data)
        target.set(paths[0].replace('\\', '/'))
    ent_rpp_input.dnd_bind("<<Drop>>", partial(drop_file, svr_rpp_input))
    btn_rpp_reload = ttk.Button(frame_rpp, text='↻', command=lambda: set_rppinfo(1), width=2)
    btn_rpp_reload.grid(row=0, column=2)

    def slct_rpp_path(value):
        svr_rpp_input2.set(_('参照…'))
        if value == rpp_cl.rpp_list[1]:
            slct_rpp()
        else:
            svr_rpp_input.set(value)
            set_rppinfo()

    # REAPER.iniが存在していればOptionMenuにする
    if rpp_cl.rpp_list:
        svr_rpp_input2 = StringVar()
        svr_rpp_input2.set(_('参照…'))
        opm_rpp_input = ttk.OptionMenu(frame_rpp, svr_rpp_input2, *rpp_cl.rpp_list, command=slct_rpp_path)
        opm_rpp_input.grid(row=0, column=3)
    else:
        btn_rpp_browse = ttk.Button(frame_rpp, text=_('参照…'), command=slct_rpp)
        btn_rpp_browse.grid(row=0, column=3)

    # frame_r2e ソフト独自設定 / 時間選択 / トラック選択
    frame_r2e = ttk.Frame(frame_left, padding=5)
    frame_r2e.grid(row=4, column=0)

    def change_flip():
        if ivr_v_flip.get() + ivr_h_flip.get() > 0:
            lbl_alt_flip['state'] = 'enable'
            chk_alt_flip_off['state'] = 'enable'
            chk_alt_flip_on['state'] = 'enable'
        else:
            lbl_alt_flip['state'] = 'disable'
            chk_alt_flip_off['state'] = 'disable'
            chk_alt_flip_on['state'] = 'disable'

    ivr_v_flip = IntVar()
    chk_v_flip = ttk.Checkbutton(frame_r2e, padding=5, text=_('左右反転'), onvalue=1, offvalue=0, variable=ivr_v_flip, command=change_flip)
    chk_v_flip.grid(row=1, column=0, sticky=W)
    ivr_h_flip = IntVar()
    chk_h_flip = ttk.Checkbutton(frame_r2e, padding=5, text=_('上下反転'), onvalue=2, offvalue=0, variable=ivr_h_flip, command=change_flip)
    chk_h_flip.grid(row=2, column=0, sticky=W)

    ivr_alt_flip = IntVar()
    lbl_alt_flip = ttk.Label(frame_r2e, text=_('　同音程が\n　連続した時...'), state='disable')
    lbl_alt_flip.grid(row=3, column=0, sticky=W)

    chk_alt_flip_off = ttk.Checkbutton(frame_r2e, padding=5, text=_('反転しない'), onvalue=1, offvalue=0, variable=ivr_alt_flip, state='disable')
    chk_alt_flip_off.grid(row=4, column=0, sticky=W)

    chk_alt_flip_on = ttk.Checkbutton(frame_r2e, padding=5, text=_('逆方向に反転'), onvalue=2, offvalue=0, variable=ivr_alt_flip, state='disable')
    chk_alt_flip_on.grid(row=5, column=0, pady=(0, 10), sticky=W)

    ivr_no_gap = IntVar()
    chk_no_gap = ttk.Checkbutton(frame_r2e, padding=5, text=_('隙間なく配置'), onvalue=1, offvalue=0, variable=ivr_no_gap)
    chk_no_gap.grid(row=6, column=0, sticky=W)

    ivr_sep_even = IntVar()
    chk_sep_even = ttk.Checkbutton(frame_r2e, padding=5, text=_('偶数番目Objを\n別レイヤ配置'), onvalue=1, offvalue=0,
                                   variable=ivr_sep_even)
    chk_sep_even.grid(row=7, column=0, sticky=W)

    ivr_slct_time = IntVar()

    def change_time_cb():  # 「時間選択」変更時の状態切り替え
        if ivr_slct_time.get() == 1:
            cmb_time_preset['state'] = 'readonly'
            cmb_time1['state'] = 'enable'
            cmb_time2['state'] = 'enable'
            time_ps_list, marker_list = rpp_cl.load_marker_list()

            if len(time_ps_list) >= 2:
                svr_time_preset.set(time_ps_list[1])
            else:
                svr_time_preset.set('-')
            cmb_time_preset['values'] = time_ps_list
            cmb_time1['values'] = marker_list
            cmb_time2['values'] = marker_list
            set_time(None)
        else:
            cmb_time_preset['state'] = 'disable'
            cmb_time1['state'] = 'disable'
            cmb_time2['state'] = 'disable'
    chk_slct_time = ttk.Checkbutton(frame_r2e, padding=5, text=_('時間選択 (秒)'), onvalue=1, offvalue=0,
                                    variable=ivr_slct_time, command=change_time_cb)
    chk_slct_time.grid(row=8, column=0, sticky=W)
    svr_time_preset = StringVar()
    svr_time_preset.set('')
    cmb_time_preset = ttk.Combobox(frame_r2e, textvariable=svr_time_preset, width=10, state='disable')

    def set_time(self):  # タイム選択ComboBoxのリストをリセットする
        if svr_time_preset.get() == '-':
            cmb_time1.set('0.0')
            cmb_time2.set('99999.0')
        else:
            slct = svr_time_preset.get()
            cmb_time1.set(slct[slct.rfind('(') + 1:slct.rfind('~')])
            cmb_time2.set(slct[slct.rfind('~') + 1:-1])
    cmb_time_preset.bind('<<ComboboxSelected>>', set_time)
    cmb_time_preset.grid(row=9, column=0, padx=5, pady=3, sticky=W + E)

    svr_time1 = StringVar()
    cmb_time1 = ttk.Combobox(frame_r2e, textvariable=svr_time1, width=10, state='disable')

    def set_time1(event=None):  # 上側のタイム選択ComboBox適用
        x = svr_time1.get()
        cmb_time1.set(x[x.rfind(':') + 2:])
    cmb_time1.bind('<<ComboboxSelected>>', set_time1)
    cmb_time1.grid(row=10, column=0, padx=5, pady=3, sticky=W + E)
    svr_time2 = StringVar()
    cmb_time2 = ttk.Combobox(frame_r2e, textvariable=svr_time2, width=10, state='disable')

    def set_time2(event=None):  # 下側のタイム選択ComboBox適用
        x = svr_time2.get()
        cmb_time2.set(x[x.rfind(':') + 2:])
    cmb_time2.bind('<<ComboboxSelected>>', set_time2)
    toggle_same_pitch_option(mydict['AddSamePitchOption'])

    tvw_slct_track = CheckboxTreeview(frame_r2e, show='tree', height=24)
    tvw_slct_track.grid(row=0, column=1, rowspan=12, sticky=N + S + E + W)
    tvw_slct_track.column("#0", width=300)
    ttk.Style().configure('Checkbox.Treeview', rowheight=15, borderwidth=1, relief='sunken', indent=0)

    vsb_slct_track = Scrollbar(frame_r2e, orient=VERTICAL, command=tvw_slct_track.yview)
    vsb_slct_track.grid(row=0, column=2, rowspan=12, sticky=N + S)
    tvw_slct_track['yscrollcommand'] = vsb_slct_track.set
    tvw_slct_track.bind('<<TreeviewClose>>', lambda event: tvw_slct_track.expand_all())

    # frame_alias 効果をファイルから読み込む
    frame_alias = ttk.Frame(frame_left, padding=2)
    frame_alias.grid(row=6, column=0)
    lbl_alias_input = ttk.Label(frame_alias, text=_('エイリアス : '))
    lbl_alias_input.grid(row=0, column=0, sticky=W)
    svr_alias_input = StringVar()
    svr_alias_input2 = StringVar()
    str_alias_spinbox = replace_ordinal(_('%01.0f番目') % 2)
    svr_alias_spinbox = StringVar(value=str_alias_spinbox)  # 初期値を2に設定
    def chg_alias_idx():
        alias_idx = int(re.search(r'\d+', svr_alias_spinbox.get()).group()) - 1
        if len(mydict['EffPaths']) - 1 < alias_idx:
            svr_alias_input2.set('')
        else:
            svr_alias_input2.set(mydict['EffPaths'][alias_idx])
        ent_alias_input2.focus_set()
        ent_alias_input2.icursor('end')
        ent_alias_input2.xview_moveto(1)
        svr_alias_spinbox.set(replace_ordinal(svr_alias_spinbox.get()))

    spn_alias_index = ttk.Spinbox(frame_alias, from_=2, to=50, increment=-1, format=_('%01.0f番目'),
                                  textvariable=svr_alias_spinbox, width=8, state="readonly", command=chg_alias_idx)
    spn_alias_index.grid(row=1, column=0, sticky=W)
    def drop_alias_files(event):
        paths = list(root.tk.splitlist(event.data))
        if event.widget == ent_alias_input:
            path0 = paths.pop(0)
            svr_alias_input.set(path0)
            svr_alias_spinbox.set(str_alias_spinbox)
            if not paths: return

        alias_idx = int(re.search(r'\d+', svr_alias_spinbox.get()).group()) - 1
        svr_alias_input2.set(paths[0].replace('\\', '/') if paths else '')

        # `paths[1:]` の要素を `mydict['EffPaths']` に反映
        for i, path in enumerate(paths, start=alias_idx):
            if i < len(mydict['EffPaths']):
                mydict['EffPaths'][i] = path.replace('\\', '/')
            else:
                mydict['EffPaths'].insert(i, path.replace('\\', '/'))
    def slct_filter_cfg_files(target):  # 効果設定ファイル読み込み
        if mydict['OutputApp'] == 'AviUtl':
            filetype = [(_("AviUtl エイリアス/効果ファイル"), "*.exa;*.exc;*.exo;*.txt"),
                        (_("すべてのファイル"), "*.*")]
        elif mydict['OutputApp'] == 'AviUtl2':
            filetype = [(_("AviUtl2 エイリアスファイル"), "*.object;*.effect"),
                        (_("すべてのファイル"), "*.*")]
        else:
            filetype = [(_("ゆっくりMovieMaker4 エイリアスファイル"), "*.ymmt;"), (_("すべてのファイル"), "*.*")]
        filepaths = filedialog.askopenfilenames(
            filetypes=filetype, initialdir=mydict["AlsLastDir"], title=_("参照するエイリアス/効果ファイルの選択"))
        if filepaths:
            # 擬似イベントオブジェクトを作成
            event = Event()
            event.data = filepaths  # ファイルパスをイベントに設定
            event.widget = target  # ウィジェットをイベントに設定
            drop_alias_files(event)
            write_cfg(filepaths[0], "AlsDir", "Directory")
            if target == svr_alias_input:
                ent_alias_input.focus_set()
            else:
                ent_alias_input2.focus_set()
    btn_alias_browse = ttk.Button(frame_alias, text=_('参照…'), command=lambda: slct_filter_cfg_files(ent_alias_input))
    btn_alias_browse.grid(row=0, column=3)
    btn_alias_browse2 = ttk.Button(frame_alias, text=_('参照…'), command=lambda: slct_filter_cfg_files(ent_alias_input2))
    btn_alias_browse2.grid(row=1, column=3)
    ent_alias_input = ttk.Entry(frame_alias, textvariable=svr_alias_input, width=40)
    ent_alias_input.grid(row=0, column=1)
    ent_alias_input.drop_target_register(DND_FILES)
    ent_alias_input.dnd_bind("<<Drop>>", drop_alias_files)
    def set_alias_path(args=None):
        alias_idx = int(re.search(r'\d+', svr_alias_spinbox.get()).group()) - 1
        if len(mydict['EffPaths']) - 1 < alias_idx:
            mydict['EffPaths'].append(to_absolute(svr_alias_input2.get().replace('"', '')))
        else:
            mydict['EffPaths'][alias_idx] = to_absolute(svr_alias_input2.get().replace('"', ''))
        return 1

    ent_alias_input2 = ttk.Entry(frame_alias, textvariable=svr_alias_input2, width=40, validate='all',
                              validatecommand=set_alias_path)
    ent_alias_input2.grid(row=1, column=1)
    ent_alias_input2.drop_target_register(DND_FILES)

    ent_alias_input2.dnd_bind("<<Drop>>", drop_alias_files)
    ent_alias_input2.bind("<KeyRelease>", set_alias_path)

    btn_clear_alias = ttk.Button(frame_alias, text='×', command=lambda:[
                                        mydict['EffPaths'].clear(),
                                        mydict['EffPaths'].append(''),
                                        svr_alias_input2.set(''),
                                        svr_alias_spinbox.set(_('%01.0f番目') % 2)
                                  ], width=2)
    btn_clear_alias.grid(row=1, column=4)

    # frame_script スクリプト制御
    frame_script = ttk.Frame(frame_left, padding=5)
    txt_script = Text(frame_script, width=50, height=10)
    if mydict['OutputApp'] != 'YMM4':
        frame_script.grid(row=7, column=0)
        lbl_script = ttk.Label(frame_script, text=_('スクリプト制御 '))
        lbl_script.grid(row=0, column=0, sticky=W)
        svr_script = StringVar()
        txt_script.grid(row=0, column=1)

    # frame_trgt 追加対象オブジェクト・素材指定、オブジェクト設定チェックボックス
    frame_trgt = ttk.Frame(frame_right, padding=5)
    frame_trgt.grid(row=0, column=0, columnspan=2)
    ivr_trgt_mode = IntVar()
    ivr_trgt_mode.set(mydict['OutputType'])

    lbl_trgt_mode = ttk.Label(frame_trgt, text=_('追加対象 : '))
    lbl_trgt_mode.grid(row=0, column=0, sticky=W)
    rbt_trgt_auto = ttk.Radiobutton(frame_trgt, value=0, variable=ivr_trgt_mode, text=_('自動検出'), command=mode_command)
    rbt_trgt_auto.grid(row=0, column=1)
    rbt_trgt_video = ttk.Radiobutton(frame_trgt, value=1, variable=ivr_trgt_mode, text=_('動画'), command=mode_command)
    rbt_trgt_video.grid(row=0, column=2)
    rbt_trgt_pic = ttk.Radiobutton(frame_trgt, value=2, variable=ivr_trgt_mode, text=_('画像'), command=mode_command)
    rbt_trgt_pic.grid(row=0, column=3)
    rbt_trgt_filter = ttk.Radiobutton(frame_trgt, value=3, variable=ivr_trgt_mode, text=_('フィルタ'), command=mode_command)
    rbt_trgt_filter.grid(row=0, column=4)

    svr_scene_idx = StringVar()
    ent_scene_idx = ttk.Entry(frame_trgt, textvariable=svr_scene_idx, width=3, state='disable')

    if mydict['OutputApp'] != 'YMM4':
        rbt_trgt_scene = ttk.Radiobutton(frame_trgt, value=4, variable=ivr_trgt_mode, text=_('シーン番号: '),
                                         command=mode_command)
        rbt_trgt_scene.grid(row=0, column=5)
        ent_scene_idx.grid(row=0, column=6)
    else:
        rbt_trgt_scene = ttk.Radiobutton(frame_trgt, value=4, variable=ivr_trgt_mode, text=_('シーン'),
                                         command=mode_command)
        rbt_trgt_scene.grid(row=0, column=5)
        svr_scene_idx.set('1')

    lbl_src_input = ttk.Label(frame_trgt, text=_('素材 : '))
    lbl_src_input.grid(row=1, column=0, sticky=E)
    svr_src_input = StringVar()
    ent_src_input = ttk.Entry(frame_trgt, textvariable=svr_src_input, width=41)
    ent_src_input.grid(row=1, column=1, columnspan=5, sticky=W)
    ent_src_input.drop_target_register(DND_FILES)
    ent_src_input.dnd_bind("<<Drop>>", partial(drop_file, svr_src_input))

    def slct_source():  # 素材選択
        filetype = [(_("動画ファイル"), "*")] if ivr_trgt_mode.get() == 1 else [(_("画像ファイル"), "*")]
        filepath = filedialog.askopenfilename(
            filetypes=filetype, initialdir=mydict["SrcLastDir"], title=_("参照する素材ファイルの選択"))
        if filepath != '':
            svr_src_input.set(filepath)
            write_cfg(filepath, "SrcDir", "Directory")
    btn_src_browse = ttk.Button(frame_trgt, text=_('参照…'), command=slct_source)
    btn_src_browse.grid(row=1, column=5, columnspan=2, sticky=E)
    ivr_randplay = IntVar()

    def change_randplay():
        if ivr_randplay.get() == 1:
            ent_randplay_st['state'] = ent_randplay_en['state'] = 'enable'
        else:
            ent_randplay_st['state'] = ent_randplay_en['state'] = 'disable'
    chk_randplay = ttk.Checkbutton(frame_trgt, padding=5, text=_('再生位置ランダム : '), onvalue=1, offvalue=0, variable=ivr_randplay, command=change_randplay)
    chk_randplay.grid(row=2, column=0, columnspan=3, sticky=W)
    svr_randplay_st = StringVar()
    if mydict['OutputApp'] == 'YMM4':
        svr_randplay_st.set('00:00:00')
    elif mydict['OutputApp'] == 'AviUtl2':
        svr_randplay_st.set('0.0')
    else:
        svr_randplay_st.set('1')
    ent_randplay_st = ttk.Entry(frame_trgt, textvariable=svr_randplay_st, width=7, state='disable')
    ent_randplay_st.grid(row=2, column=1, padx=(50, 0), columnspan=2, sticky=W)
    lbl_randplay = ttk.Label(frame_trgt, text='~')
    lbl_randplay.grid(row=2, column=2, padx=24, columnspan=2, sticky=W)
    svr_randplay_en = StringVar()
    ent_randplay_en = ttk.Entry(frame_trgt, textvariable=svr_randplay_en, width=7, state='disable')
    ent_randplay_en.grid(row=2, column=2, padx=(35, 0), columnspan=2, sticky=W)

    ivr_clipping = IntVar()
    chk_clipping = ttk.Checkbutton(frame_trgt, padding=5, text=ExDict['上のオブジェクトでクリッピング'],
                                   onvalue=1, offvalue=0, variable=ivr_clipping)
    if mydict['OutputApp'] != 'AviUtl2':
        chk_clipping.grid(row=3, column=0, columnspan=3, sticky=W)
    ivr_adv_draw = IntVar()
    ivr_adv_draw.set(0 if mydict['OutputApp'] != 'AviUtl2' else 1)
    chk_adv_draw = ttk.Checkbutton(frame_trgt, padding=5, text=ExDict['拡張描画'], onvalue=1, offvalue=0,
                                   variable=ivr_adv_draw, command=lambda: toggle_media_label(ivr_adv_draw.get() + 1))
    if mydict['OutputApp'] == 'AviUtl':
        chk_adv_draw.grid(row=3, column=5, columnspan=2, sticky=E)

    # frame_stddraw オブジェクトの標準パラメータ設定
    frame_stddraw = ttk.Frame(frame_right, padding=5, borderwidth=3)
    frame_stddraw.grid(row=1)

    # 描画名ラベル
    mLabel.append(StringVar())
    mLabel[0].set(ExDict['標準描画'])
    b = ttk.Label(frame_stddraw, textvariable=mLabel[0])
    b.grid(row=0, column=0)
    mLabel2.append(b)
    # 始点終点ラベル
    mSELabel.append(StringVar())
    mSELabel[0].set(_("始点"))
    b = ttk.Label(frame_stddraw, textvariable=mSELabel[0])
    b.grid(row=0, column=1)
    mSELabelE.append(b)
    mSELabel.append(StringVar())
    mSELabel[1].set(_("終点"))
    b = ttk.Label(frame_stddraw, textvariable=mSELabel[1])
    b.grid(row=0, column=3)
    mSELabelE.append(b)
    mSELabel.append(StringVar())
    mSELabel[2].set(_("設定"))
    b = ttk.Label(frame_stddraw, textvariable=mSELabel[2])
    b.grid(row=0, column=4)
    mSELabelE.append(b)

    for n in range(len(prmlist)):
        mLabel.append(StringVar())
        mLabel[n+1].set(ExDict.get(prmlist[n][0], prmlist[n][0]))
        b = ttk.Label(frame_stddraw, textvariable=mLabel[n+1])
        b.grid(row=n+1, column=0, padx=5)
        mLabel2.append(b)
        mEntryS.append(StringVar())
        mEntrySE.append(ttk.Entry(frame_stddraw, textvariable=mEntryS[n], width=7))
        mEntrySE[n].grid(row=n+1, column=1, padx=5)
        mEntrySE[n].insert(END, prmlist[n][1])
        mEntryX.append(StringVar())
        mEntryXCb.append(ttk.Combobox(frame_stddraw, textvariable=mEntryX[n]))
        mEntryXCb[n]['values'] = list(XDict.keys())
        mEntryXCb[n].set(list(XDict.keys())[0])
        mEntryXCb[n].grid(row=n+1, column=2, padx=5)

        mEntryE.append(StringVar())
        mEntryEE.append(ttk.Entry(frame_stddraw, textvariable=mEntryE[n], width=7))
        mEntryEE[n].grid(row=n+1, column=3, padx=5)

        mEntryConf.append(StringVar())
        mEntryConfE.append(ttk.Entry(frame_stddraw, textvariable=mEntryConf[n], width=5))
        mEntryConfE[n].grid(row=n+1, column=4, padx=5)
        if mydict['OutputApp'] == 'YMM4':
            mEntryConfE[n]['state'] = 'disabled'

    if mydict['OutputApp'] == 'YMM4':
        mEntryS[4].set('100.0')
        mEntryS[13].set('00:00:00')
        mLabel[5].set(_('不透明度'))
        mLabel[6].set(_('回転角'))
        mEntryXCb[13]['state'] = 'disable'
        mEntryXCb[14]['state'] = 'disable'
        toggle_media_label(1)
    elif mydict['OutputApp'] == 'AviUtl2':
        toggle_media_label(2)
    else:
        toggle_media_label(1)

    frame_optdraw = ttk.Frame(frame_right, borderwidth=3)
    frame_optdraw.grid(row=2, sticky='W')

    lbl_blend = ttk.Label(frame_optdraw, text=ExDict['合成モード'])
    lbl_blend.grid(row=0, column=0, padx=10)
    Param15 = StringVar()
    ParamCombo15 = ttk.Combobox(frame_optdraw, textvariable=Param15, state='readonly')
    ParamCombo15['values'] = list(BlendDict.keys())
    ParamCombo15.set(list(BlendDict.keys())[0])
    ParamCombo15.grid(row=0, column=1, columnspan=2, sticky=W + E)
    ivr_import_alpha = IntVar()
    ivr_import_alpha.set(0)
    chk_import_alpha = ttk.Checkbutton(frame_optdraw, padding=5, text=ExDict['アルファチャンネルを読み込む'],
                                       onvalue=1, offvalue=0, variable=ivr_import_alpha)
    if mydict['OutputApp'] != 'AviUtl2':
        chk_import_alpha.grid(row=1, column=2, sticky=W)
    ivr_loop = IntVar()
    ivr_loop.set(0)
    chk_loop = ttk.Checkbutton(frame_optdraw, padding=5, text=ExDict['ループ再生'], onvalue=1, offvalue=0, variable=ivr_loop)
    chk_loop.grid(row=1, column=1, sticky=W)

    # frame_eff エフェクト追加/削除
    if mydict['OutputApp'] != 'YMM4':
        frame_eff = ttk.Frame(frame_right, padding=5)
        frame_eff.grid(row=3, column=0)
        svr_add_eff = StringVar()
        cmb_add_eff = ttk.Combobox(frame_eff, textvariable=svr_add_eff, state='readonly')
        cmb_add_eff['values'] = list(EffDict.keys())
        cmb_add_eff.set(list(EffDict.keys())[0])
        cmb_add_eff.grid(row=0, column=0)
        btn_add_eff = ttk.Button(frame_eff, text='+', command=add_filter_label)
        btn_add_eff.grid(row=0, column=1)
        btn_clear_eff = ttk.Button(frame_eff, text=_('効果のクリア'), command=del_filter_label)
        btn_clear_eff.grid(row=0, column=2)

        # frame_effprm エフェクトのパラメータ設定
        frame_effprm = ttk.Frame(frame_right, padding=5, borderwidth=3)
        frame_effprm.grid(row=4)

    # frame_exec 実行
    frame_exec = ttk.Frame(frame_left, padding=(0, 5))
    frame_exec.grid(row=8, column=0)
    lbl_fps_input = ttk.Label(frame_exec, text='* FPS : ')
    lbl_fps_input.grid(row=0, column=0, sticky=W + E)
    svr_fps_input = StringVar()
    ent_fps_input = ttk.Entry(frame_exec, textvariable=svr_fps_input, width=10)
    ent_fps_input.grid(row=0, column=1, sticky=W + E, padx=10)
    ent_fps_input.insert(END, mydict['default_fps'])
    btn_exec = ttk.Button(frame_exec, text=_('実行'), command=run)
    btn_exec.grid(row=0, column=2)

    # プログラムから開かれた場合 (パスを挿入)
    try:
        # パスの取得
        paths = sys.argv[1:]

        # パスの取出し
        for path in paths:
            if path.lower().endswith('.rpp') or path.lower().endswith('.mid') or path.lower().endswith('.midi'):
                svr_rpp_input.set(path)
                set_rppinfo()
            elif path.lower().endswith('.ymmt') or path.lower().endswith('.exa') or path.lower().endswith('.exo'):
                svr_alias_input.set(path)
            elif not path.lower().endswith('.exe'):
                svr_src_input.set(path)
    except Exception:
        pass

    canvas.update()
    canvas.configure(scrollregion=(0, 0, frame_right.winfo_height(), frame_right.winfo_height()))
    canvas.grid(row=0, column=2, sticky=N, ipadx=frame_right.winfo_width()/2, ipady=210 if mydict['OutputApp'] == 'YMM4' else 290)
    mode_command()

    root.mainloop()
