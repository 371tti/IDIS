# idisのざっくりしようしょ

えー。適当にかいてきますね。（破壊的変更多々あり

## 概要ぅ♡
idisはマイクロブログSNSとしていますが本質的にはデータクラウドサービスに近いです。idisではすべてのデータを独自に構成されたファイルシステムで管理されます。

メッセージはすべて短いドキュメントファイルとして保存され、ファイルIDもしくはユーザー任意の名前とそこまでのパスが割り当てられます。

このシステムに高機能な権限管理機能を加えることでマイクロブログ形式のSNSを成り立たせています。

### DBについて
デフォルトではmongoDBと実行環境が提供するファイルシステムを組み合わせます。

すべてのファイルおよびフォルダーはmongoDBでドキュメント単位でメタデータを割り当てられています。

ファイルおよびフォルダーへのアクセスは

1. mongoDBでファイルのメタデータを検索
2. 取得したメタデータで権限情報を確認
3. ファイルシステムからファイルを取得

の順で処理が行われます。  
またサイズが1MB未満のファイルはDBのメタデータ内に埋め込まれます。  
これは1MB未満のファイルの多くが高速でアクセスすることを必要とするためです。

### apiについて
APIはhttpとWSの2種があり、完全に互換性を持ちます。

WSのリアルタイム性はHTTPではストリームを使用しますが多くの制限がかかります。
クライアントは基本WSにプロトコルをアップグレードすることを推奨します。

### 分散型snsとして
ActivePubのサーバーAPIを完全にサポートします。


### セキュリティ
Cookieによるサーバーサイドのセッション管理と

httpヘッダによるクライアントの正常性を毎アクセス必ず確認します。

# idisの詳細仕様書

## account type
There are different types of accounts in IDIS that are represented by numbers
- -1: root acount
- -2: example account. Accounts for non-logged-in users
- 0: private account
- 1: public account
- -3: chief admin account
- -4: admin account

## prosess number
this number include many idis api.
- `0***`: file_prosess
- `0001`: file send get
- `0002`: file send viw

## HTTP−Endpoints

### /users/<userIDquery> -> Json
ユーザーIDを全検索　ヒットするユーザーとフォロワー数のJsonを返却(WS−APIを推奨)

### /user/<userID> -> Json
ユーザー情報を取得(WS−APIを推奨)

### /ls/@<userID>/<path> -> Json
パスのフォルダ又はファイルのメタデータを取得(WS−APIを推奨)

### /rm/@<userID>/<path> -> Json
パスのフォルダ又はファイルを削除。メタデータを取得。(WS−APIを推奨)

###　/upload/@<userID>/<path> -> Json
ファイルをアップロードもしくはフォルダの作成。(WS−APIを推奨)

### /edit/@<userID>/<path> ->　Json
ファイルまたはフォルダのメタデータを上書き(WS−APIを推奨)

### /get/@<userID>/<path> -> BinaryStream
ファイルを取得（強制ダウンロード）

### /viw/@<userID>/<path> -> BinaryStream
ファイルを取得

### /@<user>/<path> -> Html
エージェントを用いてファイルを取得

### /resend?url=<URL>&ms=<Message>&time=<WaitTime> -> HTML
リダイレクトページを取得

### /login -> HTML
ログインページ

### /signup -> HTML
サインアップページ

### /root/r ->　BinaryStream
システムのスタックファイル

## json_api ver0

またこれは  
`server.py > Class JsonApi`  
に定義されています  
レスポンスのフォーマットです  

idis api have some template element.
1. num responce
   - `version` : the api version 
   - `type` : responce,data type
   - `code` : like http status code
   - `prosess_num` : the number of the process that was executed
   - `UTC` : the time at which the API exited

2. bool responce
   - `success` : Was the request successful

3. str responce
   - `message` : this is just message


### examples
- type 0 reaction responce
    ```json
    {
        'version': 0,
        'type': 0,
        'success': bool,
        'code': code,
        'message': message,
        'proses_num': proses_num,
        'UTC': time.time()
    }
    ```

## json_db v0
これはjsonのdbフォーマットです。mongodbで使います。
mongoDBにはコレクション内では同一のフォーマットが使用されます。
これは厳守されなければいけません。

- `users > @` のフォーマット
  ユーザーについてのデータを保存します。
   ```json
   {
      'account-type': account_type,
      'id': user_id,
      'name': username,
      'password': user_password,
      'e-mail': user_mail_address,
      'berth': berth_date,
      'RUID': User_RUID,
      'root-path': account_root_folder_path
   }
   ```
    作成時間はRUIDに含まれるUTCを参照
## session
save at cokie > session_id
