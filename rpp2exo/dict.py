import os

EffDict = {
    # オリジナル拡張編集
    "ja": {
        #   "効果名"        :       [["設定１", デフォルト設定, タイプ], ["設定２", デフォルト設定, タイプ], ...]
        #   タイプ: -1でチェックボックス、 -2でテキスト系   1, 0.1, 0.01でトラックバーの移動単位変更  0で移動単位未設定
        "座標": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["Z", 0.0, 0.1]],
        "拡大率": [["拡大率", 100.00, 0.01], ["X", 100.00, 0.01], ["Y", 100.00, 0.01]],
        "透明度": [["透明度", 0.0, 0.1]],
        "回転": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["Z", 0.0, 0.1]],
        "領域拡張": [["上", 0, 1], ["下", 0, 1], ["左", 0, 1], ["右", 0, 1], ["塗りつぶし", 0, -1]],
        "リサイズ": [["拡大率", 100.00, 0.01], ["X", 100.00, 0.01], ["Y", 100.00, 0.01],
                 ["補間なし", 0, -1], ["ドット数でサイズ指定", 0, -1]],
        "ローテーション": [["90度回転", 0, 1]],
        "反転": [["上下反転", 0, -1], ["左右反転", 0, -1], ["輝度反転", 0, -1], ["色相反転", 0, -1], ["透明度反転", 0, -1]],
        "色調補正": [["明るさ", 100.0, 0.1], ["ｺﾝﾄﾗｽﾄ", 100.0, 0.1], ["色相", 0.0, 0.1], ["輝度", 100.0, 0.1],
                 ["彩度", 100.0, 0.1], ["飽和する", 0, -1]],
        "クリッピング": [["上", 0, 1], ["下", 0, 1], ["左", 0, 1], ["右", 0, 1], ["中心の位置を変更", 0, -1]],
        "ぼかし": [["範囲", 5, 1], ["縦横比", 0.0, 0.1], ["光の強さ", 0, 1], ["サイズ固定", 0, -1]],
        "境界ぼかし": [["範囲", 5, 1], ["縦横比", 0.0, 0.1], ["透明度の境界をぼかす", 0, -1]],
        "モザイク": [["サイズ", 12, 1], ["タイル風", 0, -1]],
        "発光": [["強さ", 100.0, 0.1], ["拡散", 250, 1], ["しきい値", 80.0, 0.1], ["拡散速度", 0, 1], ["サイズ固定", 0, -1],
               ["color", "ffffff", -2], ["no_color", 1, -1]],
        "閃光": [["強さ", 100.0, 0.1], ["X", 0, 1], ["Y", 0, 1], ["サイズ固定", 0, -1],
               ["color", "ffffff", -2], ["no_color", 1, -1], ["mode", 0, -2]],
        "拡散光": [["強さ", 50.0, 0.1], ["拡散", 12, 0.1], ["サイズ固定", 0, -1]],
        "グロー": [["強さ", 40.0, 0.1], ["拡散", 30, 1], ["しきい値", 40.0, 0.1], ["ぼかし", 1, 1], ["光成分のみ", 0, -1],
                ["color", "ffffff", -2], ["no_color", 1, -1], ["type", 0, -2]],
        "クロマキー": [["色相範囲", 24, 1], ["彩度範囲", 96, 1], ["境界補正", 1, 1], ["色彩補正", 0, -1], ["透過補正", 0, -1],
                  ["color_yc", "cf010008b3fe", -2],
                  ["status", 1, -2]],
        # とりあえず青色透過。デフォ設定は0000000000(未設定)とかだったはず。
        "カラーキー": [["輝度範囲", 0, 1], ["色差範囲", 0, 1], ["境界補正", 0, 1], ["color_yc", "cf010008b3fe", -2],
                  ["status", 0, -2]],
        "ルミナンスキー": [["基準輝度", 2048, 1], ["ぼかし", 512, 1], ["type", 0, -2]],
        "ライト": [["強さ", 100.0, 0.1], ["拡散", 25, 1], ["比率", 0.0, 0.1], ["逆光", 0, -1], ["color", "ffffff", -2]],
        "縁取り": [["サイズ", 3, 1], ["ぼかし", 10, 1], ["color", 000000, -2], ["file", "", -2]],
        "凸エッジ": [["幅", 4, 1], ["高さ", 1.00, 0.01], ["角度", -45.0, 0.1]],
        "エッジ抽出": [["強さ", 100.0, 0.1], ["しきい値", 0.00, 0.01], ["輝度エッジを抽出", 1, -1], ["透明度エッジを抽出", 0, -1],
                  ["color", "ffffff", -2], ["no_color", 1, -1]],
        "シャープ": [["強さ", 50.0, 0.1], ["範囲", 5, 1]],
        "フェード": [["イン", 0.50, 0.01], ["アウト", 0.50, 0.01]],
        "ワイプ": [["イン", 0.50, 0.01], ["アウト", 0.50, 0.01], ["ぼかし", 2, 1],
                ["反転(イン)", 0, 1], ["反転(アウト)", 0, 1], ["type", 1, -2], ["name", "", -2]],
        "マスク": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["回転", 0.00, 0.01], ["サイズ", 100, 1], ["縦横比", 0.0, 0.1],
                ["ぼかし", 0, 1], ["マスクの反転", 0, -1], ["元のサイズに合わせる", 0, -1],
                ["type", 2, -2], ["name", "", -2], ["mode", 0, -2]],
        "斜めクリッピング": [["中心X", 0, 1], ["中心Y", 0, 1], ["角度", 0.0, 0.1], ["ぼかし", 1, 1], ["幅", 0, 1]],
        "放射ブラー": [["範囲", 20.0, 0.1], ["X", 0, 1], ["Y", 0, 1], ["サイズ固定", 0, -1]],
        "方向ブラー": [["範囲", 20, 1], ["角度", 50.0, 0.1], ["サイズ固定", 0, -1]],
        "レンズブラー": [["範囲", 5, 1], ["光の強さ", 32, 1], ["サイズ固定", 0, -1]],
        "モーションブラー": [["間隔", 1, 1], ["分解能", 10, 1], ["残像", 0, -1], ["オフスクリーン描画", 1, -1],
                     ["出力時に分解能を上げる", 0, -1]],
        "振動": [["X", 10, 1], ["Y", 10, 1], ["Z", 0, 1], ["周期", 1, 1], ["ランダムに強さを変える", 1, -1], ["複雑に振動", 0, -1]],
        "ミラー": [["透明度", 0.0, 0.1], ["減衰", 0.0, 0.1], ["境目調整", 0, 1], ["中心の位置を変更", 1, -1], ["type", 1, -2]],
        # type ミラー方向 上：0 下:1 左:2 右:3 中心位置変更のデフォは0
        "ラスター": [["横幅", 100, 1], ["高さ", 100, 1], ["周期", 1.00, 0.01], ["縦ラスター", 0, -1], ["ランダム振幅", 0, -1]],
        "波紋": [["中心X", 0, 1], ["中心Y", 0, 1], ["幅", 30.0, 0.1], ["高さ", 15.0, 0.1], ["速度", 150, 1],
               ["num", 0, -2], ["interval", 0, -2], ["add", 0, -2]],
        "画像ループ": [["横回数", 1, 1], ["縦回数", 1, 1], ["速度X", 0.0, 0.1], ["速度Y", 0.0, 0.1], ["個別オブジェクト", 0, -1]],
        "極座標変換": [["中心幅", 0, 1], ["拡大率", 100.0, 0.1], ["回転", 0.0, 0.1], ["渦巻", 0.00, 0.01]],
        "ディスプレイスメントマップ": [["param0", 0.0, 0.1], ["param1", 0.0, 0.1],
                          ["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["回転", 0.00, 0.01],
                          ["サイズ", 200, 1], ["縦横比", 0.0, 0.1], ["ぼかし", 5, 1], ["元のサイズに合わせる", 0, -1],
                          ["type", 1, -2], ["name", "", -2], ["mode", 0, -2], ["calc", 0, -2]],
        "色ずれ": [["ずれ幅", 5, 1], ["角度", 0.0, 0.1], ["強さ", 100, 1], ["type", 0, -2]],
        "単色化": [["強さ", 100.0, 0.1], ["輝度を保持する", 1, -1], ["color", "ffffff", -2]],
        "グラデーション": [["強さ", 100.0, 0.1], ["中心X", 0, 1], ["中心Y", 0, 1], ["角度", 0.0, 0.1], ["幅", 100, 1],
                    ["blend", 0, -2], ["color", "ffffff", -2], ["no_color", 0, -1], ["color2", "000000", -2],
                    ["no_color2", 0, -1], ["type", 0, -2]],
        "拡張色設定": [["R", 255, 1], ["G", 255, 1], ["B", 255, 1], ["RGB⇔HSV", 0, -1]],
        "特定色域変換": [["色相範囲", 8, 1], ["彩度範囲", 8, 1], ["境界補正", 2, 1], ["color_yc", "000000000000"],
                   ["status", 0, -2], ["color_yc2", "000000000000"], ["status2", 0, -2]],
        "アニメーション効果": [["track0", 0.0, 0], ["track1", 0.0, 0], ["track2", 0.0, 0], ["track3", 0.0, 0],
                      ["check0", 0, -1], ["type", 0, -2], ["filter", 0, -2], ["name", "", -2], ["param", "", -2]],
        "オフスクリーン描画": [["dummy", 0, -1]],
        "オブジェクト分割": [["横分割数", 10, 1], ["縦分割数", 10, 1]]
    },
    "en": {
        "Coordinate": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["Z", 0.0, 0.1]],
        "Zoom%": [["Zoom%", 100.00, 0.01], ["X", 100.00, 0.01], ["Y", 100.00, 0.01]],
        "Clearness": [["Clearness", 0.0, 0.1]],
        "Rotation": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["Z", 0.0, 0.1]],
        "Region expansion": [["Top", 0, 1], ["Bottom", 0, 1], ["Left", 0, 1], ["Right", 0, 1], ["Fill", 0, -1]],
        "Resize": [["Zoom%", 100.00, 0.01], ["X", 100.00, 0.01], ["Y", 100.00, 0.01],
                   ["No interpolation", 0, -1], ["Specified size by the number of dots", 0, -1]],
        "Locked Rotation": [["90 degree rotation", 0, 1]],
        "Reversal": [["Flip vertical", 0, -1], ["Flip horizontal", 0, -1], ["Invert luminance", 0, -1],
                     ["Hue inversion", 0, -1], ["Transparency inversion", 0, -1]],
        "Color compensation": [["Lightness", 100.0, 0.1], ["Contrast", 100.0, 0.1], ["Hue", 0.0, 0.1],
                               ["Luminance", 100.0, 0.1], ["Chroma", 100.0, 0.1], ["Saturated", 0, -1]],
        "Clipping": [["Top", 0, 1], ["Bottom", 0, 1], ["Left", 0, 1], ["Right", 0, 1],
                     ["Change the center position", 0, -1]],
        "Blur": [["Range", 5, 1], ["rAspect", 0.0, 0.1], ["Light Stre", 0, 1], ["Fixed Size", 0, -1]],
        "Boundary blurring": [["Range", 5, 1], ["rAspect", 0.0, 0.1], ["Boundary blur of transparency", 0, -1]],
        "Mosaic": [["Size", 12, 1], ["Tile style", 0, -1]],
        "Emission": [["Strength", 100.0, 0.1], ["Diffusion", 250, 1], ["Threshold", 80.0, 0.1], ["vDiffuse", 0, 1],
                     ["Fixed Size", 0, -1], ["color", "ffffff", -2], ["no_color", 1, -1]],
        "Flash": [["Strength", 100.0, 0.1], ["X", 0, 1], ["Y", 0, 1], ["Fixed Size", 0, -1],
                  ["color", "ffffff", -2], ["no_color", 1, -1], ["mode", 0, -2]],
        "Diffusion light": [["Strength", 50.0, 0.1], ["Diffusion", 12, 0.1], ["Fixed Size", 0, -1]],
        "Glow": [["Strength", 40.0, 0.1], ["Diffusion", 30, 1], ["Threshold", 40.0, 0.1], ["Blur", 1, 1],
                 ["Light only", 0, -1], ["color", "ffffff", -2], ["no_color", 1, -1], ["type", 0, -2]],
        "Chroma Key": [["~Hue", 24, 1], ["~Chroma", 96, 1], ["dEdge", 1, 1],
                       ["Chromatic correction", 0, -1], ["Transmission correction", 0, -1],
                       ["color_yc", "cf010008b3fe", -2], ["status", 1, -2]],
        "Color Key": [["~Luminance", 0, 1], ["~DColor", 0, 1], ["dEdge", 0, 1], ["color_yc", "cf010008b3fe", -2],
                      ["status", 0, -2]],
        "Luminance Key": [["RefLuminance", 2048, 1], ["Blur", 512, 1], ["type", 0, -2]],
        "Light": [["Strength", 100.0, 0.1], ["Diffusion", 25, 1], ["Ratio", 0.0, 0.1], ["Backlight", 0, -1],
                  ["color", "ffffff", -2]],
        "Add border": [["Size", 3, 1], ["Blur", 10, 1], ["color", 000000, -2], ["file", "", -2]],
        "Bevel": [["Width", 4, 1], ["Height", 1.00, 0.01], ["Angle", -45.0, 0.1]],
        "Edge extraction": [["Strength", 100.0, 0.1], ["Threshold", 0.00, 0.01], ["Extract luminance edge", 1, -1],
                            ["Extract transparency edge", 0, -1], ["color", "ffffff", -2], ["no_color", 1, -1]],
        "Sharpen": [["Strength", 50.0, 0.1], ["Range", 5, 1]],
        "Fade": [["In", 0.50, 0.01], ["Out", 0.50, 0.01]],
        "Wipe": [["In", 0.50, 0.01], ["Out", 0.50, 0.01], ["Blur", 2, 1],
                 ["Flip (in)", 0, 1], ["Flip (Out)", 0, 1], ["type", 1, -2], ["name", "", -2]],
        "Mask": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["Rotation", 0.00, 0.01], ["Size", 100, 1], ["rAspect", 0.0, 0.1],
                 ["Blur", 0, 1], ["Invert mask", 0, -1], ["Match with original size", 0, -1],
                 ["type", 2, -2], ["name", "", -2], ["mode", 0, -2]],
        "Diagonal clipping": [["Center X", 0, 1], ["Center Y", 0, 1], ["Angle", 0.0, 0.1], ["Blur", 1, 1],
                              ["Width", 0, 1]],
        "Radial Blur": [["Range", 20.0, 0.1], ["X", 0, 1], ["Y", 0, 1], ["Fixed Size", 0, -1]],
        "Direction blur": [["Range", 20, 1], ["Angle", 50.0, 0.1], ["Fixed Size", 0, -1]],
        "Lens blur": [["Range", 5, 1], ["Light Stre", 32, 1], ["Fixed Size", 0, -1]],
        "Motion blur": [["Interval", 1, 1], ["Resolution", 10, 1], ["Afterimage", 0, -1], ["Off-screen drawing", 1, -1],
                        ["Increase resolution during export", 0, -1]],
        "Vibration": [["X", 10, 1], ["Y", 10, 1], ["Z", 0, 1], ["Period", 1, 1],
                      ["Change the strength at random", 1, -1], ["Complex vibration", 0, -1]],
        "Mirror": [["Clearness", 0.0, 0.1], ["Attenuate", 0.0, 0.1], ["dEdge", 0, 1],
                   ["Change the center position", 1, -1], ["type", 1, -2]],
        "Raster": [["Width", 100, 1], ["Height", 100, 1], ["Period", 1.00, 0.01],
                   ["Vertical raster", 0, -1], ["Random amplitude", 0, -1]],
        "Ripple": [["Center X", 0, 1], ["Center Y", 0, 1], ["Width", 30.0, 0.1], ["Height", 15.0, 0.1],
                   ["Speed", 150, 1], ["num", 0, -2], ["interval", 0, -2], ["add", 0, -2]],
        "Image tiling": [["Hx#", 1, 1], ["Vy#", 1, 1], ["Speed X", 0.0, 0.1], ["Speed Y", 0.0, 0.1],
                         ["Individual objects", 0, 1]],
        "Polar coordinate conversion": [["Center width", 0, 1], ["Zoom%", 100.0, 0.1], ["Rotation", 0.0, 0.1],
                                        ["Whirlpool", 0.00, 0.01]],
        "Displacement map": [["param0", 0.0, 0.1], ["param1", 0.0, 0.1], ["X", 0.0, 0.1], ["Y", 0.0, 0.1],
                             ["Rotation", 0.00, 0.01], ["Size", 200, 1], ["rAspect", 0.0, 0.1], ["Blur", 5, 1],
                             ["Match with original size", 0, -1],
                             ["type", 1, -2], ["name", "", -2], ["mode", 0, -2], ["calc", 0, -2]],
        "Color shift": [["Gap width", 5, 1], ["Angle", 0.0, 0.1], ["Strength", 100, 1], ["type", 0, -2]],
        "Monochromatic": [["Strength", 100.0, 0.1], ["Keep luminance", 1, -1], ["color", "ffffff", -2]],
        "Gradient": [["Strength", 100.0, 0.1], ["Center X", 0, 1], ["Center Y", 0, 1], ["Angle", 0.0, 0.1],
                     ["Width", 100, 1], ["blend", 0, -2], ["color", "ffffff", -2], ["no_color", 0, -1],
                     ["color2", "000000", -2], ["no_color2", 0, -1], ["type", 0, -2]],
        "Extended color setting": [["R", 255, 1], ["G", 255, 1], ["B", 255, 1], ["RGB⇔HSV", 0, -1]],
        "Specific color gamut conversion": [["~Hue", 8, 1], ["~Chroma", 8, 1], ["dEdge", 2, 1],
                                            ["color_yc", "000000000000"], ["status", 0, -2],
                                            ["color_yc2", "000000000000"], ["status2", 0, -2]],
        "Animation effect": [["track0", 0.0, 0], ["track1", 0.0, 0], ["track2", 0.0, 0], ["track3", 0.0, 0],
                             ["check0", 0, -1], ["type", 0, -2], ["filter", 0, -2], ["name", "", -2],
                             ["param", "", -2]],
        "Off-screen drawing": [["dummy", 0, -1]],
        "Object split": [["Hy div#", 10, 1], ["Vx div#", 10, 1]]
    }
}

XDict = {
    "ja": {
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
        "回転": "15@回転",
        "イージング（通常）": "15@イージング（通常）@イージング",
        "加速@加減速TRA": "15@加速@加減速TRA",
        "減速@加減速TRA": "15@減速@加減速TRA",
        "": "",
        # 追加する際は
        # "GUI上で表示される名前": "15@スクリプト名"
    },
    "ymm4": {
        "なし": "なし",
        "直線移動": "直線移動",
        "加減速移動": "加減速移動",
        "移動量指定": "移動量指定",
        "ランダム移動": "ランダム移動",
        "反復移動": "反復移動",
        "補完移動": "補完移動",
        "緩急1_加速": "Sine_In",
        "緩急1_減速": "Sine_Out",
        "緩急1_加減速": "Sine_InOut",
        "緩急2_加速": "Quad_In",
        "緩急2_減速": "Quad_Out",
        "緩急2_加減速": "Quad_InOut",
        "緩急3_加速": "Cubic_In",
        "緩急3_減速": "Cubic_Out",
        "緩急3_加減速": "Cubic_InOut",
        "緩急4_加速": "Quart_In",
        "緩急4_減速": "Quart_Out",
        "緩急4_加減速": "Quart_InOut",
        "緩急5_加速": "Quint_In",
        "緩急5_減速": "Quint_Out",
        "緩急5_加減速": "Quint_InOut",
        "緩急6_加速": "Expo_In",
        "緩急6_減速": "Expo_Out",
        "緩急6_加減速": "Expo_InOut",
        "円弧_加速": "Circ_In",
        "円弧_減速": "Circ_Out",
        "円弧_加減速": "Circ_InOut",
        "戻る_加速": "Back_In",
        "戻る_減速": "Back_Out",
        "戻る_加減速": "Back_InOut",
        "バネ_加速": "Elastic_In",
        "バネ_減速": "Elastic_Out",
        "バネ_加減速": "Elastic_InOut",
        "バウンド_加速": "Bounce_In",
        "バウンド_減速": "Bounce_Out",
        "バウンド_加減速": "Bounce_InOut"
    },
    "en": {
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
        "": "",
    }
}

BlendDict = {
    "ja": {
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
    },
    "ymm4": {
        "通常": "Normal",
        "加算": "Add",
        "減算": "Subtract",
        "乗算": "Multiply",
        "スクリーン": "Screen",
        "オーバーレイ": "Overlay",
        "比較(明)": "Lighter",
        "比較(暗)": "Darker",
        "輝度": "Luminosity",
        "焼き込みリニア": "LinearBurn",
        "リニアライト": "LinearLight",
        "差分": "Difference",
    },
    "en": {
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
}

ExDict = {
    "ja": {
        # GUI表示用
        "標準描画": "標準描画",
        "拡張描画": "拡張描画",
        "合成モード": "合成モード",
        "上のオブジェクトでクリッピング": "上のオブジェクトでクリッピング",
        "拡大率": "拡大率",
        "透明度": "透明度",
        "回転": "回転",
        "縦横比": "縦横比",
        "X軸回転": "X軸回転", "Y軸回転": "Y軸回転", "Z軸回転": "Z軸回転",
        "中心X": "中心X", "中心Y": "中心Y", "中心Z": "中心Z",
        "ループ再生": "ループ再生",
        "アルファチャンネルを読み込む": "アルファチャンネルを読み込む",
        "裏面を表示しない": "裏面を表示しない",
    },
    "en": {
        "標準描画": "Standard drawing",
        "拡張描画": "Advanced drawing",
        "合成モード": "Synthesis mode",
        "上のオブジェクトでクリッピング": "Clip with the object above",

        "動画ファイル": "Video file",
        "画像ファイル": "Image file",
        "シーン": "Scene",
        "再生位置": "Playback position",
        "再生速度": "vPlay",
        "ループ再生": "Loop playback",
        "アルファチャンネルを読み込む": "Import alpha channel",

        "拡大率": "Zoom%",
        "透明度": "Clearness",
        "回転": "Rotation",
        "縦横比": "rAspect",
        "X軸回転": "X-Spin", "Y軸回転": "Y-Spin", "Z軸回転": "Z-Spin",
        "中心X": "Center X", "中心Y": "Center Y", "中心Z": "Center Z",
        "裏面を表示しない": "Do not show backside",

        "座標": "Coordinate",
        "反転": "Reversal",
        "反転_ITEM": ["Flip vertical", "Flip horizontal", "Invert luminance", "Hue inversion", "Transparency inversion"],
        "スクリプト制御": "Script control",

    }
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

    "clipping": 0,
    "SceneIdx": 0,

    "Param": [],

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
    "RandomPlay": 0,  # 動画の再生位置を個別にランダムにするかどうか
    # "BreakFrames": [0],  # 強制停止フレームのリスト  動画オブジェクトがこのフレームを越えないように処理
    "OutputType": 0,  # 1=動画  2=画像  3=フィルタ  4=シーン  として出力
    "IsExSet": 0,  # 拡張描画を有効にするか

    # 設定 (config.iniから適用する)
    "RPPLastDir": os.path.abspath(os.path.dirname(__file__)),  # 最後にRPPを保存したフォルダパス
    "EXOLastDir": os.path.abspath(os.path.dirname(__file__)),  # EXO
    "SrcLastDir": os.path.abspath(os.path.dirname(__file__)),  # 素材
    "AlsLastDir": os.path.abspath(os.path.dirname(__file__)),  # エイリアス
    "IsCCW": 0,  # 左右・上下反転時に反時計回りにするかどうか
    "PatchExists": 0,  # patch.aulが導入済みか
    "HasPatchError": 0,  # 拡張編集由来のバグが起きたかどうか
    "UseYMM4": 0,  # ゆっくりMovieMaker4出力にするかどうか
    "YMM4Path": "",  # YMM4の実態があるパスを選択 (テンプレート適用のため)
    "ByogaHenkanExists": 0,  # 描画変換プラグインが導入済みか
    "HasYMM4FlipError": 0,  # YMM4上下反転の警告が出たかどうか

    "DisplayLang": "ja",  # 表示言語
    "ExEditLang": "ja",  # 拡張編集の言語

}

prmlist = [
    ['X', 0.0, 0.1],
    ['Y', 0.0, 0.1],
    ['Z', 0.0, 0.1],
    ['拡大率', 100.00, 0.01],
    ['透明度', 0.0, 0.1],
    ['回転', 0.0, 0.01],
    ['縦横比', 0.0, 0.1],
    ['X軸回転', 0.0, 0.01],
    ['Y軸回転', 0.0, 0.01],
    ['Z軸回転', 0.0, 0.01],
    ['中心X', 0.0, 0.1],
    ['中心Y', 0.0, 0.1],
    ['中心Z', 0.0, 0.1],
    ['再生位置', 1, 1],
    ['再生速度', 100.0, 0.1]
]