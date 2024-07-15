







class DB():
    def __init__(self):
        self.ruid = RUID.IDGenerator(0x0000) #server id
        print("[DB] conecting data base...")
        client = MongoClient('mongodb://192.168.0.48:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5')
        print("[DB] conect data base! loading colection...")
        self.db = client['idis-DB_v1']
        self.users = self.db['users'] # load colection
        self.server = self.db['server'] # load colection

        

        print("[DB] loaded colection! loading server meta...")
        
        self.server_meta = self.server.find_one({'server':'meta'})
        if self.server_meta:
            self.user_count = self.server_meta['user_count']
        else:
            self.server.insert_one({'server':'meta','user_count':0})
            self.user_count = self.server_meta['user_count']
        
        print("[DB] loaded from data base! started DB instance!")

    def __del__(self):
        print("[DB] disconecting data base...")
        print("[DB] save stack data...")

        print("[DB] disconect data base!")


    def d_add(self,collection:str,data:dict):
        """
        (collection,{key:val,...})
        指定コレクションにドキュメントを追加
        返り値はid
        """
        result = self.db[collection].insert_one(data).inserted_id
        return str(result)
    

    
    def d_upd(self,collection:str,query:dict,data:dict):
        """
        (collection,{key:val,...},{key:val,...})
        query : ドキュメント識別
        指定コレクションのドキュメントをアップデート
        返り値はid
        """
        did = self.d_fud(collection,query)
        if not did:
            return None
        result = self.db[collection].update_one({"_id":did},{'$set':data}).matched_count
        return did if bool(result) else None


    def d_rem(self,collection:str,query:dict,data:list):
        """
        (collection,{key:val,...},[key,...])
        query : ドキュメント識別
        data  : "*" ドキュメントrm or 要素を削除
        指定コレクションのドキュメントの内容もしくはそれ自体を削除
        """
        did = self.d_fud(collection,query)
        if not did:
            return None
        
        if "*" in data:
            return self.db[collection].delete_one({"_id":did}).acknowledged
        return self.db[collection].update_one({"_id":did}, {'$unset':{ key: "" for key in data }}).acknowledged
        

    def d_get(self,collection:str,query:dict,data:list):
        """
        (collection,{key:val,...},[key,...])
        query : ドキュメント識別
        key : 取得要素のkey
        指定コレクションの要素を取得
        """

        did = self.d_fud(collection,query)
        
        if not (collection and did):
            return {}
        
        if "*" in data:
            return self.db[collection].find_one({"_id":did})
        return self.db[collection].find_one({"_id":did}, { key: True for key in data })
    
    def d_fud(self,collection,query):
        """
        (collection,{key:val,...},[key,...])
        query : ドキュメント識別
        指定コレクションのドキュメントのIDを取得
        """
        if not collection:
            return None
        
        result = self.db[collection].find_one(query, {"_id": 1})
       
        return result.get("_id") if result else None
    
