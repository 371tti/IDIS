import eventlet
eventlet.monkey_patch()

import logging
import os
import mimetypes
from flask import Flask, request, Response, render_template, abort, g, json, jsonify
from datetime import datetime, timedelta
import time
import random
import requests
from flask_socketio import SocketIO , emit, disconnect
import threading
from pymongo import MongoClient
from bson.objectid import ObjectId
import  re
import RUID as RUID
# Flaskアプリケーションの作成
app = Flask(__name__)
app.config['SECRET_KEY'] = ')Pf76d+:=Odx7iz'
# cokedIo の作成
socketio = SocketIO(app, async_mode='eventlet',logger=True, engineio_logger=True)
# ロギングの設定
# colorlogのハンドラーを設定
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


APP_NAME = "IDIS"

class User:
    users = {}

    @staticmethod
    def search_users(search_substring):
        # 部分文字列がユーザーIDに含まれていて、フォロワー数が -1 ではないユーザーを検索
        return {user_id: followers for user_id, followers in User.users.items() if search_substring in user_id and followers != -1}

class DB:
    ruid = RUID.IDGenerator(0x0000) #server id
    try:
        client = MongoClient('mongodb://192.168.0.48:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5')
        db = client['idis-DB_v1']
        app.logger.info("DB connected")
        app.logger.info("DB loading")
        # MongoDBからユーザーIDとフォロワー情報を取得してUser.users辞書に追加
        User.users = {user['id']: user.get('followers', 0) for user in db['users'].find({}, {'id': 1, 'followers': 1})}
        app.logger.debug(User.users)
        app.logger.info("DB loaded!!")

    except:
        app.logger.error("can't connect DB")


    @staticmethod
    def d_add(DB,collection:str,data:dict):
        """
        (collection,{key:val,...})
        指定コレクションにドキュメントを追加
        返り値はid
        """
        result = DB.db[collection].insert_one(data).inserted_id
        return str(result)
    
    @staticmethod
    def d_upd(DB,collection:str,query:dict,data:dict):
        """
        (collection,{key:val,...},{key:val,...})
        query : ドキュメント識別
        指定コレクションのドキュメントをアップデート
        返り値はid
        """
        did = DB.d_fud(collection,query)
        if not did:
            return None
        result = DB.db[collection].update_one({"_id":did},{'$set':data}).matched_count
        return did if bool(result) else None

    @staticmethod
    def d_rem(DB,collection:str,query:dict,data:list):
        """
        (collection,{key:val,...},[key,...])
        query : ドキュメント識別
        data  : "*" ドキュメントrm or 要素を削除
        指定コレクションのドキュメントの内容もしくはそれ自体を削除
        """
        did = DB.d_fud(collection,query)
        if not did:
            return None
        
        if "*" in data:
            return DB.db[collection].delete_one({"_id":did}).acknowledged
        return DB.db[collection].update_one({"_id":did}, {'$unset':{ key: "" for key in data }}).acknowledged
        
    @staticmethod
    def d_get(DB,collection:str,query:dict,data:list):
        """
        (collection,{key:val,...},[key,...])
        query : ドキュメント識別
        key : 取得要素のkey
        指定コレクションの要素を取得
        """

        did = DB.d_fud(collection,query)
        
        if not (collection and did):
            return {}
        
        if "*" in data:
            return DB.db[collection].find_one({"_id":did})
        return DB.db[collection].find_one({"_id":did}, { key: True for key in data })
    
    @staticmethod
    def d_fud(DB,collection,query):
        """
        (collection,{key:val,...},[key,...])
        query : ドキュメント識別
        指定コレクションのドキュメントのIDを取得
        """
        if not collection:
            return None
        
        result = DB.db[collection].find_one(query, {"_id": 1})
       
        return result.get("_id") if result else None
    
class Session:
    sessions = {}
    session_len = 128
    session_life_time = int(timedelta(days=365).total_seconds())
    server_session_life_time = int(timedelta(days=7).total_seconds())
    httponly = True

    @staticmethod
    def check() -> None:
        session_id = request.cookies.get('session_id')
        if (session_id == None) or not(session_id in Session.sessions):
            session_id, session = Session.new()
            g.session = session
            g.session_id = session_id
        else:
            session = Session.sessions[session_id]
            session['lt'] = time.time()
            g.session_id = session_id
            g.session = session
        return

    @staticmethod
    def sets(response) -> Response:
        Session.sessions[g.session_id] = g.session
        response.set_cookie('session_id', g.session_id, httponly=Session.httponly, max_age=Session.session_life_time)
        return response

    @staticmethod
    def create() -> hex:
        id = hex(random.randint(0, 16**Session.session_len - 1))
        if id in Session.sessions:
            return Session.create()
        else:
            return id

    @staticmethod
    def new() -> tuple[str, dict]:
        session_id = Session.create()
        now_time = time.time()
        session = {
            'ct': now_time,
            'lt': now_time,
            'ua': request.headers.get('User-Agent'),
            'nu': '@example',
            'us':
            {
                '@example':
                {
                    'lt': time.time()
                }
            }
        }
        Session.sessions[session_id] = session
        return session_id, session

    @staticmethod
    def delete():
        deletes = 0
        for i in Session.sessions:
            if Session.sessions[i]['lt'] <= (time.time() - Session.server_session_life_time):
                del Session.sessions[i]
                deletes += 1
        return deletes

    @staticmethod
    def tick():
        del_num = Session.delete()
        app.logger.debug(f"session life time checked. {del_num} deletes")
        BackGroundProses.add(Session.tick, 300) # 5分に1回

class Permission:
    @staticmethod
    def check_fs() -> bool:
        g.session['nu']
        return True 

class ReCaptcha:
    secret_key = '6LfdY3MpAAAAANNgwCRSiAUTxNNQnL-RaRcUj7H0'
    
    def validate_recp(recap_responce):
        payload = {
            'secret' : ReCaptcha.secret_key,
            'response' : recap_responce
        }
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload).json()
        return response

class JsonAPI:
    @staticmethod
    def err(proses_num: int, code: int, message: str) -> dict:
        result = {
            'version': 0,
            'type': 0,
            'success': False,
            'code': code,
            'message': message,
            'proses_num': proses_num,
            'UTC': time.time()
        }
        return jsonify(result)

class FileAPI:
    streaming_chunk_size = 1024* 1024 * 1
    c_d = os.getcwd()
    base_path = os.path.join(c_d,"users")
    @staticmethod
    def send_file_strm(filename, url_fp="get", check_perm=True) -> Response:
        
        file_path = os.path.join(FileAPI.base_path, filename)
        print(file_path)
        if not os.path.exists(file_path):
            if url_fp == "viw":
                abort(404,"Maybe it's a 500 server err ...`Responses that have passed the permission check`")

            return JsonAPI.err(1,404,"file is not found.")

        file_size = os.path.getsize(file_path)
        content_type, _ = mimetypes.guess_type(file_path)

        # Rangeヘッダーの値を取得
        range_header = request.headers.get('Range')

        if range_header:
            start_end = range_header[6:].split('-')
            start = int(start_end[0]) if start_end[0] else 0
            end = int(start_end[1]) if start_end[1] else file_size - 1
            status = 206
        else:
            start, end = 0, file_size - 1
            status = 200

        print(start, end)

        def generate():
            nonlocal status
            nonlocal start 
            nonlocal end
            with open(file_path, 'rb') as file:
                file.seek(start)
                while start <= end:
                    chunk_size = min(FileAPI.streaming_chunk_size, end - start + 1)
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    start += chunk_size

        content_length = end - start + 1
        download = {'get': True, 'viw': False, 'raw': False, None: False}.get(url_fp)

        # レスポンスを生成してストリーミングで送信
        return Response(generate(), status=status,
                        content_type=content_type,
                        headers={
                            'Content-Disposition': f"{'attachment' if download else 'inline'}; filename={os.path.basename(file_path)}",
                            'Content-Range': f'bytes {start}-{end}/{file_size}',
                            'Content-Length': str(content_length),
                            'Accept-Ranges': 'bytes'
                        })
    
    @staticmethod
    def root_r(path) -> Response:
        return FileAPI.send_file_strm(os.path.join("root/r/", path), "get", False)

class ErrorHandler:
    extended_error_code_color = {
        4: "#ff9900ff",
        5: "#ff0000bb"
    }

    extended_error_handling = {
        400: 'BadRequest',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'NotFound',
        405: 'MethodNotAllowed',
        406: 'NotAcceptable',
        408: 'RequestTimeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'LengthRequired',
        412: 'PreconditionFailed',
        413: 'RequestEntityTooLarge',
        414: 'RequestURITooLarge',
        415: 'UnsupportedMediaType',
        416: 'RequestedRangeNotSatisfiable',
        417: 'ExpectationFailed',
        418: 'ImATeapot',
        422: 'UnprocessableEntity',
        423: 'Locked',
        424: 'FailedDependency',
        428: 'PreconditionRequired',
        429: 'TooManyRequests',
        431: 'RequestHeaderFieldsTooLarge',
        451: 'UnavailableForLegalReasons',
        500: 'InternalServerError',
        501: 'NotImplemented',
        502: 'BadGateway',
        503: 'ServiceUnavailable',
        504: 'GatewayTimeout',
        505: 'HTTPVersionNotSupported'
    }

    extended_error_handling_suggestions = {
        400: {1: "Check the request syntax", 2: "Verify the request parameters", 3: "Ensure the URL is correct"},
        401: {1: "Check the authentication credentials", 2: "Login again", 3: "Contact the website administrator"},
        403: {1: "Check the URL for errors", 2: "Request access from the administrator", 3: "Ensure you have the necessary permissions"},
        404: {1: "Check the URL", 2: "Reload the page", 3: "Clear the browser cache", 4: "Try using another browser", 5: "Contact customer support"},
        405: {1: "Check the request method (GET, POST, etc.)", 2: "Refer to the website's API documentation", 3: "Ensure the method is supported"},
        408: {1: "Check your internet connection", 2: "Ensure the server is not overloaded", 3: "Retry the request after a moment"},
        500: {1: "Wait a few moments and retry the request", 2: "Check the website's social media for updates", 3: "Contact customer support"},
        501: {1: "Verify the request method is correct", 2: "Check if the feature is implemented", 3: "Contact the website administrator"},
        502: {1: "Check your internet connection", 2: "Wait a few moments and retry the request", 3: "Contact the website if the issue persists"},
        503: {1: "Check if the website is under maintenance", 2: "Wait and retry later", 3: "Contact the website for more information"},
        504: {1: "Check your internet connection", 2: "Ensure the server is reachable", 3: "Retry the request after a moment"},
    }

    @staticmethod
    def errorhandler(err) -> Response:
        app.logger.debug('Track back ->', exc_info=True)
        
        code = 500
        if hasattr(err, 'code'):
            code = err.code

        debug = {
            'Host': request.headers.get('Host'),
            'Path': request.path,
            'Connection': request.headers.get('Connection'),
            'User-Agent': request.headers.get('User-Agent'),
            'Last-Time': datetime.now().strftime("%Y.%m/%d %H:%M:%S.%f"),
            'Cf-Connecting-Ip': request.headers.get('Cf-Connecting-Ip'),
            'Accept-Encoding': request.headers.get('Accept-Encoding'),
            'Accept-Language': request.headers.get('Accept-Language')
        }
        return render_template(
            "ERRN.html",
            code=code,
            ms=ErrorHandler.extended_error_handling.get(code, 'Unknown Error') + (f" - {err.description}" if hasattr(err, 'description') and err.description else ""),
            solution=ErrorHandler.extended_error_handling_suggestions.get(code),
            debug=debug,
            collor=ErrorHandler.extended_error_code_color.get(code // 100)
        ), code

class EndPoints:

    @staticmethod
    @app.errorhandler(Exception)
    def err(err):
        return ErrorHandler.errorhandler(err)
    
    @staticmethod
    @app.before_request
    def before_request():
        Session.check()

    @staticmethod
    @app.after_request
    def after_request(response):
        request_info = {
        'time': datetime.now().strftime("%Y.%m/%d %H:%M-%S"),
        'ip': request.remote_addr,
        'method': request.method,
        'path': request.path,
        'referrer': request.headers.get('Referer'),
        'user-agent': request.headers.get('User-Agent'),
        'status_code': response.status_code,
        'content_type': response.content_type,
        'content_size': response.content_length
        }
        app.logger.info(f"response {response.status_code} : {request.path}")
        app.logger.debug(json.dumps(request_info, indent=4, ensure_ascii=False))
        return Session.sets(response)
    
    @staticmethod
    @app.route('/root/r/<path:path>')
    def root_r(path):
        return FileAPI.root_r(path)

    @staticmethod
    @app.route('/favicon.ico')
    def favicon():
        return FileAPI.root_r("favicon.ico")

    @staticmethod
    @app.route('/robots.txt')
    def robots():
        return FileAPI.root_r("robots.txt")

    @staticmethod
    @app.route('/ads.txt')
    def ads():
        return FileAPI.root_r("ads.txt")

    @staticmethod
    @app.route('/viw/<path:filename>')
    def viw(filename):
        return FileAPI.send_file_strm(filename, "viw", True)
    
    @staticmethod
    @app.route('/get/<path:filename>')
    def get(filename):
        return FileAPI.send_file_strm(filename, "get", True)
    
    @staticmethod
    @app.route('/')
    def root():
        return render_template("index.html", APP_NAME = APP_NAME)

class BackGroundProses:
    tick = 0
    schedule = {0:[Session.tick]}

    @staticmethod
    def periodic_task() ->None:
        cant_keep = 0
        next_tick = 0
        while True:
            next_tick = time.time() + 1
            BackGroundProses.server_tick(BackGroundProses.tick)
            BackGroundProses.tick += 1
            if time.time() > next_tick:
                cant_keep += 1
                if cant_keep < 9:
                    app.logger.error("The server is overloaded and will be shut down soon.")
                app.logger.warning(f"can't keep server,{time.time() - next_tick}s over.")
                continue
            cant_keep = 0
            while time.time() < next_tick:
                time.sleep(0.01)
            if BackGroundProses.tick % 10 == 0:
                app.logger.debug(f"{BackGroundProses.tick}tick passed")

    @staticmethod
    def server_tick(now_tick) ->None:
        if now_tick in BackGroundProses.schedule:
            for i in BackGroundProses.schedule[now_tick]:
                try:
                    i()
                except Exception as e:
                    app.logger.error(f"Error during scheduled task: {e}")

    @staticmethod
    def add(method, set_tick=1) -> None:
        schedule_tick = BackGroundProses.tick + set_tick
        if schedule_tick not in BackGroundProses.schedule:
            BackGroundProses.schedule[schedule_tick] = []
        BackGroundProses.schedule[schedule_tick].append(method)

if __name__ == '__main__':
    # アプリケーションの起動
    # 定期的に実行するスレッドを開始
    socketio.start_background_task(target=BackGroundProses.periodic_task)

    socketio.run(app,host='0.0.0.0',
            port=83,
            debug=False, 
            use_reloader=False
            )
