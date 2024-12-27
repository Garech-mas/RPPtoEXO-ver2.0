# RPPtoEXO v2.0
REAPERのプロジェクトファイル・MIDIファイルから自動で音合わせの映像を作成する音MAD制作補助スクリプト
> - AviUtl Exedit Object File (.EXO)
> 
> - ゆっくりMovieMaker4 (YMM4) テンプレート
> 
>への出力が可能になっています。
> 
**注) AviUtlは 拡張編集v0.92 + patch.aul が推奨環境となります。**

**YMM4は 描画変換プラグイン が推奨プラグインとなっています。**

それ以外の環境の場合、正しく動作しない設定項目があります。

## ダウンロード
**https://github.com/Garech-mas/RPPtoEXO-ver2.0/releases/latest**

上記のリンクにアクセスした後、RPPtoEXO-v2.**.zip からEXE版をダウンロードできます。

Pythonをインストール済みの方は、その下の Source Code (zip) からPY版をダウンロードできます。

## 起動方法
EXE版の場合、exeをダブルクリックして実行してください。

PY版 (Source Code) をダウンロードした場合、Pythonをインストールした状態で、
```commandline
pip install -r requirements.txt
```
で依存パッケージをインストールしてから実行してください。

※ Python 3.11、3.12で動作確認済みです。

## 使い方・説明
Scrapboxを見てください。
https://scrapbox.io/Garech/RPPtoEXO_v2.0

## EXE化
Nuitkaを使用することを前提としています。以下のコマンドを用いて作成してください。

`--include-data-dir` のパスなど、各環境で変更が必要な場合があります。
```commandline
nuitka --no-deployment-flag=self-execution --standalone --onefile --windows-console-mode=disable --follow-imports --enable-plugin=tk-inter --windows-icon-from-ico="RPPtoEXO.ico" --include-data-dir=en/LC_MESSAGES/=en/LC_MESSAGES --include-data-dir=venv/Lib/site-packages/ttkwidgets/assets=ttkwidgets/assets --include-data-file=RPPtoEXO.ico=./RPPtoEXO.ico -o RPPtoEXO.exe main.py
```


Original made by maimai22015
https://ytpmv.info/RPPtoEXO/
