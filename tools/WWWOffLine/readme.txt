※未テスト
■手順
�@curlで最初のhtmlを取得します。
　※例　http://xxx/yyy/zzz/index.html
�Achecklinks.pyの最終の行でbaseurlを設定する。
　※例　http://xxx/yyy/zzz/
�Bpython checklinks.py > out.sh
�Cchmod +x out.sh
�D./out.sh
�Eout.shが空きファイルまで、�B〜�Dを繰り返す。
