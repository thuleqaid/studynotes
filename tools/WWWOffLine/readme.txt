※未テスト
■手順
①curlで最初のhtmlを取得します。
　※例　http://xxx/yyy/zzz/index.html
②checklinks.pyの最終の行でbaseurlを設定する。
　※例　http://xxx/yyy/zzz/
③python checklinks.py > out.sh
④chmod +x out.sh
⑤./out.sh
⑥out.shが空きファイルまで、③～⑤を繰り返す。
