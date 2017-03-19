# このソフトウェアについて

GitHubリポジトリ作成スクリプトに編集機能を追加した。

[前回](https://github.com/ytyaru/GitHub.Upload.ByPython.DeleteRepo.201703091329)の改良版。CUI対話によって編集できる。

# 開発環境

* Linux Mint 17.3 MATE 32bit
* [Python 3.4.3](https://www.python.org/downloads/release/python-343/)
    * [requests](http://requests-docs-ja.readthedocs.io/en/latest/)
    * [dataset](https://github.com/pudo/dataset)

## WebService

* [GitHub](https://github.com/)
    * [アカウント](https://github.com/join?source=header-home)
    * [AccessToken](https://github.com/settings/tokens)
    * [Two-Factor認証](https://github.com/settings/two_factor_authentication/intro)
    * [API v3](https://developer.github.com/v3/)

# 準備

[前回](https://github.com/ytyaru/GitHub.Upload.ByPython.201703090838)の手順に従い、リポジトリ作成しておくこと。

# 実行

## 1. 起動する

1. ターミナルを起動する
1. 以下のコマンドを実行する（今回のスクリプトを実行する）

```sh
bash call.sh
```

### 2. 編集する

```sh
リポジトリ名： ytyaru/{call.shを実行したディレクトリ名}
説明: 説明文。
URL: http://abc
----------------------------------------
add 'LICENSE.txt'
add 'ReadMe.md'
add 'main.py'
commit,pushするならメッセージを入力してください。Enterかnで終了します。
サブコマンド    n:終了 a:集計 e:編集 d:削除 i:Issue作成
```

```
e
```
```
変更したくない項目は無記入のままEnterキー押下してください。
```

```
リポジトリ名を入力してください。
```
以下のように任意のリポジトリ名を入力する。
```
GitHub.Upload.ByPython.EditRepo.201703101422
```
```
説明文を入力してください。
```
以下のように任意の説明文を入力する。
```
リポジトリの説明文ですよ。
```
```
Homepageを入力してください。
```
以下のように任意のURLを入力する。
```
http://abcdefg
```
```
編集しました。
```

* リモートリポジトリを見ると更新されている
* リポジトリ名を変更したときは、ローカルリポジトリのディレクトリ名も変更される
* DBレコードの値を確認したいときは「d: 削除」を選択すると確認できる

# ライセンス #

このソフトウェアはCC0ライセンスである。

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)

