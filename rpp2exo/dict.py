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
    },
    "zh": {
        "坐标": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["Z", 0.0, 0.1]],
        "缩放率": [["缩放率", 100.00, 0.01], ["X", 100.00, 0.01], ["Y", 100.00, 0.01]],
        "透明度": [["透明度", 0.0, 0.1]],
        "旋转": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["Z", 0.0, 0.1]],
        "区域扩展": [["上", 0, 1], ["下", 0, 1], ["左", 0, 1], ["右", 0, 1], ["填充", 0, -1]],
        "尺寸调整": [["缩放率", 100.00, 0.01], ["X", 100.00, 0.01], ["Y", 100.00, 0.01],
                 ["无插补", 0, -1], ["顶点数指定尺寸", 0, -1]],
        "直角旋转": [["90度旋转", 0, 1]],
        "反转": [["上下翻转", 0, -1], ["左右翻转", 0, -1], ["亮度反转", 0, -1], ["色相反转", 0, -1], ["透明度反转", 0, -1]],
        "色调修正": [["亮度", 100.0, 0.1], ["对比度", 100.0, 0.1], ["色相", 0.0, 0.1], ["发光度", 100.0, 0.1],
                 ["色度", 100.0, 0.1], ["饱和化", 0, -1]],
        "裁剪遮罩": [["上", 0, 1], ["下", 0, 1], ["左", 0, 1], ["右", 0, 1], ["中心点实时变化", 0, -1]],
        "模糊": [["范围", 5, 1], ["长宽比", 0.0, 0.1], ["发光强度", 0, 1], ["固定大小", 0, -1]],
        "边缘模糊": [["范围", 5, 1], ["长宽比", 0.0, 0.1], ["透明度边缘模糊", 0, -1]],
        "马赛克": [["大小", 12, 1], ["瓷砖风格", 0, -1]],
        "发光": [["强度", 100.0, 0.1], ["扩散度", 250, 1], ["阈值", 80.0, 0.1], ["扩散速度", 0, 1], ["固定大小", 0, -1],
               ["color", "ffffff", -2], ["no_color", 1, -1]],
        "闪光": [["强度", 100.0, 0.1], ["X", 0, 1], ["Y", 0, 1], ["固定大小", 0, -1],
               ["color", "ffffff", -2], ["no_color", 1, -1], ["mode", 0, -2]],
        "扩散光": [["强度", 50.0, 0.1], ["扩散度", 12, 0.1], ["固定大小", 0, -1]],
        "辉光": [["强度", 40.0, 0.1], ["扩散度", 30, 1], ["阈值", 40.0, 0.1], ["模糊", 1, 1], ["仅显示光", 0, -1],
                ["color", "ffffff", -2], ["no_color", 1, -1], ["type", 0, -2]],
        "色度键": [["色相范围", 24, 1], ["色度范围", 96, 1], ["边缘修正", 1, 1], ["色彩修正", 0, -1], ["透明修正", 0, -1],
                  ["color_yc", "cf010008b3fe", -2],
                  ["status", 1, -2]],
        "色键": [["亮度范围", 0, 1], ["色差范围", 0, 1], ["边缘修正", 0, 1], ["color_yc", "cf010008b3fe", -2],
                  ["status", 0, -2]],
        "亮度键": [["基础亮度", 2048, 1], ["模糊", 512, 1], ["type", 0, -2]],
        "光源": [["强度", 100.0, 0.1], ["扩散度", 25, 1], ["比例", 0.0, 0.1], ["逆光", 0, -1], ["color", "ffffff", -2]],
        "描边": [["大小", 3, 1], ["模糊", 10, 1], ["color", 000000, -2], ["file", "", -2]],
        "边缘斜面": [["宽度", 4, 1], ["高度", 1.00, 0.01], ["角度", -45.0, 0.1]],
        "提取边缘": [["强度", 100.0, 0.1], ["阈值", 0.00, 0.01], ["提取亮度边缘", 1, -1], ["提取透明度边缘", 0, -1],
                  ["color", "ffffff", -2], ["no_color", 1, -1]],
        "锐化": [["强度", 50.0, 0.1], ["范围", 5, 1]],
        "淡化": [["入场", 0.50, 0.01], ["出场", 0.50, 0.01]],
        "擦除": [["入场", 0.50, 0.01], ["出场", 0.50, 0.01], ["模糊", 2, 1],
                ["反转(入场)", 0, 1], ["反转(出场)", 0, 1], ["type", 1, -2], ["name", "", -2]],
        "遮罩": [["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["旋转", 0.00, 0.01], ["大小", 100, 1], ["长宽比", 0.0, 0.1],
                ["模糊", 0, 1], ["遮罩反转", 0, -1], ["匹配源图像尺寸", 0, -1],
                ["type", 2, -2], ["name", "", -2], ["mode", 0, -2]],
        "斜向裁剪": [["中心X", 0, 1], ["中心Y", 0, 1], ["角度", 0.0, 0.1], ["模糊", 1, 1], ["宽", 0, 1]],
        "放射模糊": [["范围", 20.0, 0.1], ["X", 0, 1], ["Y", 0, 1], ["固定大小", 0, -1]],
        "方向模糊": [["范围", 20, 1], ["角度", 50.0, 0.1], ["固定大小", 0, -1]],
        "镜头模糊": [["范围", 5, 1], ["发光强度", 32, 1], ["固定大小", 0, -1]],
        "运动模糊": [["间隔", 1, 1], ["分辨率", 10, 1], ["残影", 0, -1], ["混合渲染", 1, -1],
                     ["导出时提高分辨率", 0, -1]],
        "震动": [["X", 10, 1], ["Y", 10, 1], ["Z", 0, 1], ["周期", 1, 1], ["强度随机变化", 1, -1], ["复杂震动", 0, -1]],
        "镜像": [["透明度", 0.0, 0.1], ["淡化", 0.0, 0.1], ["界限调整", 0, 1], ["中心点实时变化", 1, -1], ["type", 1, -2]],
        "光栅": [["宽度", 100, 1], ["高度", 100, 1], ["周期", 1.00, 0.01], ["縦ラスター", 0, -1], ["ランダム振幅", 0, -1]],
        "波纹": [["中心X", 0, 1], ["中心Y", 0, 1], ["宽度", 30.0, 0.1], ["高度", 15.0, 0.1], ["速度", 150, 1],
               ["num", 0, -2], ["interval", 0, -2], ["add", 0, -2]],
        "图像拼贴": [["横向数", 1, 1], ["纵向数", 1, 1], ["速度X", 0.0, 0.1], ["速度Y", 0.0, 0.1], ["物件独立", 0, -1]],
        "极坐标变换": [["中心径", 0, 1], ["缩放率", 100.0, 0.1], ["旋转", 0.0, 0.1], ["漩涡", 0.00, 0.01]],
        "置换映射": [["param0", 0.0, 0.1], ["param1", 0.0, 0.1],
                          ["X", 0.0, 0.1], ["Y", 0.0, 0.1], ["旋转", 0.00, 0.01],
                          ["大小", 200, 1], ["长宽比", 0.0, 0.1], ["模糊", 5, 1], ["匹配源图像尺寸", 0, -1],
                          ["type", 1, -2], ["name", "", -2], ["mode", 0, -2], ["calc", 0, -2]],
        "RGB分离": [["偏移度", 5, 1], ["角度", 0.0, 0.1], ["强度", 100, 1], ["type", 0, -2]],
        "单色化": [["强度", 100.0, 0.1], ["保持亮度", 1, -1], ["color", "ffffff", -2]],
        "渐变": [["强度", 100.0, 0.1], ["中心X", 0, 1], ["中心Y", 0, 1], ["角度", 0.0, 0.1], ["宽度", 100, 1],
                    ["blend", 0, -2], ["color", "ffffff", -2], ["no_color", 0, -1], ["color2", "000000", -2],
                    ["no_color2", 0, -1], ["type", 0, -2]],
        "颜色扩展": [["R", 255, 1], ["G", 255, 1], ["B", 255, 1], ["RGB⇔HSV", 0, -1]],
        "特定色域变换": [["色相范围", 8, 1], ["色度范围", 8, 1], ["边缘修正", 2, 1], ["color_yc", "000000000000"],
                   ["status", 0, -2], ["color_yc2", "000000000000"], ["status2", 0, -2]],
        "动画效果": [["track0", 0.0, 0], ["track1", 0.0, 0], ["track2", 0.0, 0], ["track3", 0.0, 0],
                      ["check0", 0, -1], ["type", 0, -2], ["filter", 0, -2], ["name", "", -2], ["param", "", -2]],
        "混合渲染": [["dummy", 0, -1]],
        "物件分割": [["横分割数", 10, 1], ["纵分割数", 10, 1]]
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
    },
    "zh": {
        "无运动": "",
        "直线运动": 1,
        "缓速运动": 103,
        "曲线运动": 2,
        "瞬间运动": 3,
        "忽略中间点": 4,
        "指定运动量": 5,
        "随机运动": 6,
        "往复运动": 8,
        "插值运动": "15@插值运动",
        "旋转": "15@旋转",
        "缓动（普通）": "15@缓动（普通）@缓动",
        "缓动（插值运动）": "15@缓动（插值运动）@缓动",
        "加速@缓动TRA": "15@加速@缓动TRA",
        "減速@缓动TRA": "15@減速@缓动TRA",
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
    },
    "zh": {
        "正常": 0,
        "相加": 1,
        "相减": 2,
        "相乘": 3,
        "滤色": 4,
        "覆盖": 5,
        "对比(明)": 6,
        "对比(暗)": 7,
        "亮度": 8,
        "色差": 9,
        "阴影": 10,
        "明暗": 11,
        "反差": 12,
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
        "拡張編集": "拡張編集",
    },
    "en": {
        "標準描画": "Standard drawing",
        "拡張描画": "Advanced drawing",
        "合成モード": "Synthesis mode",
        "上のオブジェクトでクリッピング": "Clip with the object above",

        "動画ファイル": "Video file",
        "画像ファイル": "Image file",
        "テキスト": "Text",
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

        "サイズ": "Size",
        "表示速度": "vDisplay",
        "文字毎に個別オブジェクト": "1char1obj",
        "移動座標上に表示する": "Show on motion coordinate",
        "自動スクロール": "Automatic scrolling",

        "座標": "Coordinate",
        "反転": "Reversal",
        "反転_ITEM": ["Flip vertical", "Flip horizontal", "Invert luminance", "Hue inversion", "Transparency inversion"],
        "スクリプト制御": "Script control",
        "拡張編集": "Advanced Editing",
    },
    "zh": {
        "標準描画": "标准属性",
        "拡張描画": "扩展属性",
        "合成モード": "混合模式",
        "上のオブジェクトでクリッピング": "用上方图层裁剪",
        "ループ再生": "循环播放",
        "アルファチャンネルを読み込む": "读取Alpha通道",
        
        "動画ファイル": "视频文件",
        "画像ファイル": "图片文件",
        "テキスト": "文本",
        "シーン": "次合成",
        "再生位置": "播放位置",
        "再生速度": "播放速度",
        
        "拡大率": "缩放率",
        "透明度": "透明度",
        "回転": "旋转",
        "縦横比": "宽高比",
        "X軸回転": "X轴旋转", "Y軸回転": "Y轴旋转", "Z軸回転": "Z轴旋转",
        "中心X": "中心X", "中心Y": "中心Y", "中心Z": "中心Z",
        "裏面を表示しない": "隐藏背面",
        
        "サイズ": "大小",
        "表示速度": "显示速度",
        "文字毎に個別オブジェクト": "文字单一独立",
        "移動座標上に表示する": "自动调整物件长度",
        "自動スクロール": "自动滚动",

        "座標": "坐标",
        "反転": "反转",
        "反転_ITEM": ["上下翻转", "左右翻转", "亮度反转", "色相反转", "透明度反转"],
        "スクリプト制御": "脚本控制",
        "拡張編集": "扩展编辑",
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

    "EffPaths": [
        '',
        # "test2.exa",
        # "test3.exa", ...
        ],

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
    "AddSamePitchOption": 0,  # 反転オプションを表示するか
    "AltFlipType": 0,  # 0=通常通り反転  1=同音程なら反転しない  2=同音程なら逆反転 (時計回りと併用不可)
    "SepLayerEvenObj": 0,  # 偶数オブジェクトを別レイヤ―に配置するか
    "NoGap": 0,  # オブジェクト間の隙間を埋めるか
    "UseRoundUp": 0,  # 0=四捨五入(RPPtoEXO基準)、1=切り上げ(AviUtlグリッド基準)
    "RandomPlay": 0,  # 動画の再生位置を個別にランダムにするかどうか
    "RandomStart": 0,
    "RandomEnd": 0,
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
    "HasPatchError": [],  # 拡張編集由来のバグが起きたかどうか
    "UseYMM4": 0,  # ゆっくりMovieMaker4出力にするかどうか
    "YMM4Path": "",  # YMM4の実態があるパスを選択 (テンプレート適用のため)
    "TemplateName": "RPPtoEXO",  # テンプレートの保存名
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