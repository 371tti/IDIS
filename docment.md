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
idis api have some template element.
1. num responce
   - `version` : the api version 
   - `type` : responce type
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

## session
save at cokie > session_id
