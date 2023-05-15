import os

EffDict = {
    #   "効果名"        :       [["設定１", デフォルト設定, タイプ], ["設定２", デフォルト設定. タイプ], ...]
    #   タイプ: 0でトラックバー、 -1でチェックボックス、 -2でテキスト系
    "座標": [["X", 0.0], ["Y", 0.0], ["Z", 0.0]],
    "拡大率": [["拡大率", 100.00], ["X", 100.00], ["Y", 100.00]],
    "透明度": [["透明度", 0.0]],
    "回転": [["X", 0.0], ["Y", 0.0], ["Z", 0.0]],
    "リサイズ": [["拡大率", 100.00], ["X", 100.00], ["Y", 100.00], ["補間なし", 0, -1], ["ドット数でサイズ指定", 0, -1]],
    "反転": [["上下反転", 0, -1], ["左右反転", 0, -1], ["輝度反転", 0, -1], ["色相反転", 0, -1], ["透明度反転", 0, -1]],
    "色調補正": [["明るさ", 100.0], ["ｺﾝﾄﾗｽﾄ", 100.0], ["色相", 0.0], ["輝度", 100.0], ["彩度", 100.0], ["飽和する", 0, -1]],
    "クリッピング": [["上", 0], ["下", 0], ["左", 0], ["右", 0], ["中心の位置を変更", 0, -1]],
    "クロマキー": [["色相範囲", 24], ["彩度範囲", 96], ["境界補正", 1], ["色彩補正", 0, -1], ["透過補正", 0, -1],
              ["color_yc", "cf010008b3fe", -2],
              ["status", 1, -2]],
    # とりあえず青色透過。デフォ設定は0000000000(未設定)とかだったはず。
    "縁取り": [["サイズ", 3], ["ぼかし", 10], ["color", 000000, -2], ["file", "", -2]],
    "マスク": [["X", 0.0], ["Y", 0.0], ["回転", 0.00], ["サイズ", 100], ["縦横比", 0.0], ["ぼかし", 0], ["マスクの反転", 0, -1],
            ["元のサイズに合わせる", 0, -1], ["type", 2, -2], ["name", ""], ["mode", 0]],
    "放射ブラー": [["範囲", 20.0], ["X", 0], ["Y", 0], ["サイズ固定", 0, -1]],
    "方向ブラー": [["範囲", 20], ["角度", 50.0], ["サイズ固定", 0, -1]],
    "振動": [["X", 10], ["Y", 10], ["Z", 0], ["周期", 1], ["ランダムに強さを変える", 1, -1], ["複雑に振動", 0, -1]],
    "ミラー": [["透明度", 0.0], ["減衰", 0.0], ["境目調整", 0], ["中心の位置を変更", 1, -1], ["type", 1, -2]],
    # type ミラー方向 上：0 下:1 左:2 右:3 中心位置変更のデフォは0
    "ラスター": [["横幅", 100], ["高さ", 100], ["周期", 1.00], ["縦ラスター", 0, -1], ["ランダム振幅", 0, -1]],
    "波紋": [["中心X", 0], ["中心Y", 0], ["幅", 30.0], ["高さ", 15.0], ["速度", 150],
           ["num", 0, -2], ["interval", 0, -2], ["add", 0, -2]],
    "ディスプレイスメントマップ": [["param0", 0.0], ["param1", 0.0], ["X", 0.0], ["Y", 0.0], ["回転", 0.00], ["サイズ", 200],
                      ["縦横比", 0.0], ["ぼかし", 5], ["元のサイズに合わせる", 0, -1],
                      ["type", 1, -2], ["name", "", -2], ["mode", 0, -2], ["calc", 0, -2]],
    "色ずれ": [["ずれ幅", 5], ["角度", 0.0], ["強さ", 100], ["type", 0, -2]],
    "アニメーション効果": [["track0", 0.00], ["track1", 0.00], ["track2", 0.00], ["track3", 0.00],
                  ["check0", 0, -1], ["type", 0, -2], ["filter", 0, -2], ["name", "", -2], ["param", "", -2]],
}

EffDict_en = {
    "Coordinate": [["X", 0.0], ["Y", 0.0], ["Z", 0.0]],
    "Zoom%": [["Zoom%", 100.00], ["X", 100.00], ["Y", 100.00]],
    "Clearness": [["Clearness", 0.0]],
    "Rotation": [["X", 0.0], ["Y", 0.0], ["Z", 0.0]],
    "Resize": [["Zoom%", 100.00], ["X", 100.00], ["Y", 100.00], ["No interpolation", 0, -1],
               ["Specified size by the number of dots", 0, -1]],
    "Reversal": [["Flip vertical", 0, -1], ["Flip horizontal", 0, -1], ["Invert luminance", 0, -1],
                 ["Hue inversion", 0, -1], ["Transparency inversion", 0, -1]],
    "Color compensation": [["Lightness", 100.0], ["Contrast", 100.0], ["Hue", 0.0], ["Luminance", 100.0],
                           ["Chroma", 100.0], ["Saturated", 0, -1]],
    "Clipping": [["Top", 0], ["Bottom", 0], ["Left", 0], ["Right", 0], ["Change the center position", 0, -1]],
    "Chroma Key": [["~Hue", 24], ["~Chroma", 96], ["dEdge", 1],
                   ["Chromatic correction", 0, -1], ["Transmission correction", 0, -1],
                   ["color_yc", "cf010008b3fe", -2], ["status", 1, -2]],
    # とりあえず青色透過。デフォ設定は0000000000(未設定)とかだったはず。
    "Add border": [["Size", 3], ["Blur", 10], ["color", 000000, -2], ["file", "", -2]],
    "Mask": [["X", 0.0], ["Y", 0.0], ["Rotation", 0.00], ["Size", 100], ["rAspect", 0.0], ["Blur", 0],
             ["Invert mask", 0, -1], ["Match with original size", 0, -1], ["type", 2, -2], ["name", ""], ["mode", 0]],
    "Radial Blur": [["Range", 20.0], ["X", 0], ["Y", 0], ["Fixed Size", 0, -1]],
    "Direction blur": [["Range", 20], ["Angle", 50.0], ["Fixed Size", 0, -1]],
    "Vibration": [["X", 10], ["Y", 10], ["Z", 0], ["Period", 1],
                  ["Change the strength at random", 1, -1], ["Complex vibration", 0, -1]],
    "Mirror": [["Clearness", 0.0], ["Attenuate", 0.0], ["dEdge", 0],
               ["Change the center position", 1, -1], ["type", 1, -2]],
    # type ミラー方向 上：0 下:1 左:2 右:3 中心位置変更のデフォは0
    "Raster": [["Width", 100], ["Height", 100], ["Period", 1.00],
               ["Vertical raster", 0, -1], ["Random amplitude", 0, -1]],
    "Ripple": [["Center X", 0], ["Center Y", 0], ["Width", 30.0], ["Height", 15.0], ["Speed", 150],
               ["num", 0, -2], ["interval", 0, -2], ["add", 0, -2]],
    "Displacement map": [["param0", 0.0], ["param1", 0.0], ["X", 0.0], ["Y", 0.0], ["Rotation", 0.00], ["Size", 200],
                      ["rAspect", 0.0], ["ぼかし", 5], ["元のサイズに合わせる", 0, -1],
                      ["type", 1, -2], ["name", "", -2], ["mode", 0, -2], ["calc", 0, -2]],
    "Color shift": [["Gap width", 5], ["Angle", 0.0], ["Strength", 100], ["type", 0, -2]],
    "Animation effect": [["track0", 0.00], ["track1", 0.00], ["track2", 0.00], ["track3", 0.00],
                  ["check0", 0, -1], ["type", 0, -2], ["filter", 0, -2], ["name", "", -2], ["param", "", -2]],
}

XDict = {
    "移動なし": "",
    "直線移動": 1,
    "加減速移動": 103,
    "曲線移動": 2,
    "瞬間移動": 3,
    "中間点無視": 4,
    "移動量指定": 5,
    "ランダム": 6,
    "反復移動": 8,
    "補完移動": "15@補間移動",
    "回転": "15@回転,100",
    "スクリプト(終了値,15@スクリプト名,)": "",
    "イージング（通常）": "15@イージング（通常）@イージング",
    "加速@加減速TRA": "15@加速@加減速TRA",
    "減速@加減速TRA": "15@減速@加減速TRA",
    # 追加する際は
    # "GUI上で表示される名前": "15@スクリプト名"
}

XDict_en = {
    "No movement": "",
    "Rectilinear": 1,
    "Acceleration": 103,
    "Curve": 2,
    "Teleportation": 3,
    "Ignored midpoints": 4,
    "Specified amount": 5,
    "Random": 6,
    "Repetitive": 8,
    "Tween": "15@Tween",
    "Rotation": "15@Rotation,100",
    "TRA Script(end,15@Script name,)": "",
    "Easing(Normal) Script": "15@Easing(Normal)@easing",
    "イージング（通常）": "15@イージング（通常）@イージング",
    "加速@加減速TRA": "15@加速@加減速TRA",
    "減速@加減速TRA": "15@減速@加減速TRA",
}

BlendDict = {
    "通常": 0,
    "加算": 1,
    "減算": 2,
    "乗算": 3,
    "スクリーン": 4,
    "オーバーレイ": 5,
    "比較(明)": 6,
    "比較(暗)": 7,
    "輝度": 8,
    "色差": 9,
    "陰影": 10,
    "明暗": 11,
    "差分": 12,
}

BlendDict_en = {
    "Normal": 0,
    "Additive": 1,
    "Subtractive": 2,
    "Multiply": 3,
    "Screen": 4,
    "Overlay": 5,
    "Brighter": 6,
    "Darker": 7,
    "Luminance": 8,
    "Color difference": 9,
    "Shadow": 10,
    "Contrast": 11,
    "Difference": 12,
}

mydict = {
    # 基本設定
    "fps": 60,
    "RPPPath": "test.rpp",
    "EXOPath": "test.exo",
    "SrcPath": "C:\\Users\\USER\\Documents\\ytpmv_script\\movie.mp4",  # ファイルパス。絶対パスが必要。
    "SrcPosition": 1,  # 再生位置
    "SrcRate": 100.0,  # 再生速度
    "IsAlpha": 0,  # アルファチャンネルを読み込む
    "IsLoop": 0,  # ループ再生
    "X": 0.0,  # x座標
    "Y": 0.0,  # y座標
    "Z": 0.0,  # z座標
    "Size": 100.0,  # 拡大率
    "Rotation": 0.0,  # 回転
    "Alpha": 0.0,
    "Blend": 0,  # 合成モード

    "clipping": 0,
    "SceneIdx": 0,

    # 拡張描画
    "XRotation": 0.00,
    "YRotation": 0.00,
    "ZRotation": 0.00,
    "XCenter": 0.0,
    "YCenter": 0.0,
    "ZCenter": 0.0,

    # エフェクト設定 SettingEffで追加する。
    "Effect": [
        #   ["EffName",["ConfName1","Conf"],["ConfName2","Conf"]],
    ],
    "EffNum": 0,  # 現時点で追加されているパラメータ数（GUI用）
    "EffCount": 0,  # エフェクト数（GUI用）
    "EffCount2": 0,
    "EffCbNum": 0,  # パラメータ  チェックボックスの数
    "ScriptText": '',

    # 独自設定
    "ObjFlipType": 0,  # 0=反転なし  1=左右反転  2=上下反転  3=時計回り反転
    "SepLayerEvenObj": 0,  # 偶数オブジェクトを別レイヤ―に配置するか
    "NoGap": 0,  # オブジェクト間の隙間を埋めるか
    # "BreakFrames": [0],  # 強制停止フレームのリスト  動画オブジェクトがこのフレームを越えないように処理
    "OutputType": 0,  # 1=動画  2=画像  3=フィルタ  4=シーン  として出力
    "IsExSet": 0,  # 拡張描画を有効にするか

    # 設定 (config.iniから適用する)
    "RPPLastDir": os.path.abspath(os.path.dirname(__file__)),  # 最後にRPPを保存したフォルダパス
    "EXOLastDir": os.path.abspath(os.path.dirname(__file__)),  # EXO
    "SrcLastDir": os.path.abspath(os.path.dirname(__file__)),  # 素材
    "AlsLastDir": os.path.abspath(os.path.dirname(__file__)),  # エイリアス
    "PatchExists": 0,  # patch.aulが導入済みか
    "HasPatchError": 0,  # 拡張編集由来のバグが起きたかどうか

    "DisplayLang": "ja",    # 表示言語
    "AdvEditLang": "ja",    # 拡張編集の言語

}
