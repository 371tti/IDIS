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
