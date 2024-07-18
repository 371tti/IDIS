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

## HTTP Endpoints

### `/users/<userIDquery>` -> JSON
- **Description:** 全ユーザーIDを検索し、ヒットするユーザーとフォロワー数をJSON形式で返却します。
- **Recommendation:** WS-APIを推奨。

### `/user/<userID>` -> JSON
- **Description:** 指定したユーザーIDのユーザー情報を取得します。
- **Recommendation:** WS-APIを推奨。

### `/ls/@<userID>/<path>` -> JSON
- **Description:** 指定したパスのフォルダまたはファイルのメタデータを取得します。
- **Recommendation:** WS-APIを推奨。

### `/rm/@<userID>/<path>` -> JSON
- **Description:** 指定したパスのフォルダまたはファイルを削除し、メタデータを取得します。
- **Recommendation:** WS-APIを推奨。

### `/upload/@<userID>/<path>` -> JSON
- **Description:** ファイルをアップロードするか、フォルダを作成します。
- **Recommendation:** WS-APIを推奨。

### `/edit/@<userID>/<path>` -> JSON
- **Description:** ファイルまたはフォルダのメタデータを上書きします。
- **Recommendation:** WS-APIを推奨。

### `/get/@<userID>/<path>` -> BinaryStream
- **Description:** 指定したファイルを強制ダウンロードします。

### `/viw/@<userID>/<path>` -> BinaryStream
- **Description:** 指定したファイルを取得します。

### `/@<user>/<path>` -> HTML
- **Description:** エージェントを用いてファイルを取得します。

### `/resend?url=<URL>&ms=<Message>&time=<WaitTime>` -> HTML
- **Description:** リダイレクトページを取得します。

### `/login` -> HTML
- **Description:** ログインページ。

### `/signup` -> HTML
- **Description:** サインアップページ。

### `/root/r` -> BinaryStream
- **Description:** システムのスタックファイルを取得します。
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
