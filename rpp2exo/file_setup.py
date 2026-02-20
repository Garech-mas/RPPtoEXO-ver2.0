import os
import shutil
import sys
from os import path as op

import requests


def download_github(url, path):
    # APIリクエストを送信
    response = requests.get(url)
    response.raise_for_status()

    # アセットのURLを取得
    assets = response.json().get("assets", [])

    if not assets:
        print("最新バージョンの取得に失敗しました。")
    else:
        asset = assets[0]
        asset_url = asset["browser_download_url"]
        asset_name = asset["name"]

        # ダウンロード
        download_response = requests.get(asset_url, stream=True)
        download_response.raise_for_status()

        # ファイルを保存
        with open(op.join(path, asset_name), 'wb') as file:
            for chunk in download_response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Downloaded: {asset_name}")
        return op.join(path, asset_name)


def rpp2exo_update(temp_dir):
    r2e_zip = download_github("https://api.github.com/repos/Garech-mas/RPPtoEXO-ver2.0/releases/latest", temp_dir)

    shutil.unpack_archive(r2e_zip, temp_dir)
    os.remove(op.join(temp_dir, 'README.txt'))
    os.remove(op.join(temp_dir, 'changelog.txt'))

    os.remove(r2e_zip)


def rpp2exo_version_check(current_version):
    print('最新バージョンを確認しています...')
    # APIリクエストを送信
    response = requests.get("https://api.github.com/repos/Garech-mas/RPPtoEXO-ver2.0/releases/latest")
    response.raise_for_status()

    # 最新バージョンを取得
    latest_version = response.json().get("tag_name")[1:]
    print(f'現在のバージョン: {current_version}, 最新バージョン: {latest_version}')
    if current_version != latest_version:
        # 念のため、直接PYで実行している人を弾く (自分でDLしてもらう)
        if os.path.abspath(sys.argv[0]).endswith('.py'):
            return -1
        else:
            return 1
    else:
        return 0
