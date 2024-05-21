import pymysql

host = '127.0.0.1'
user = 'root'
password = ''
database = 'acg資料庫'
port = 3306

def Connect_Database(host,user,password,database,port):
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                port=port,
                                db=database,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

def Initial_state(connection,user_id):
    try:
        with connection.cursor() as cursor:
            sql = f'''INSERT INTO 使用者狀態(user_id,user_state)
                      VALUES("{user_id}","initial")'''
            cursor.execute(sql)
            return user_id
    except Exception as e:
        print(e)
    finally:
        # connection.close()
        pass

def Change_state(connection,user_id,state):
    try:
        with connection.cursor() as cursor:
            sql = f'''UPDATE 使用者狀態
                      SET user_state = "{state}"
                      WHERE user_id = "{user_id}"'''
            cursor.execute(sql)
            return state
    except Exception as e:
        print(e)
    finally:
        # connection.close()
        pass

def Select_state(connection,user_id):
    try:
        with connection.cursor() as cursor:
            sql = f'''SELECT user_state
                      FROM  使用者狀態
                      WHERE user_id = "{user_id}"'''
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(e)
    finally:
        connection.close()

def clean_state(connection,user_id):
    try:
        with connection.cursor() as cursor:
            sql = f'''UPDATE 使用者狀態
                      SET user_state = "unstarted"
                      WHERE user_id = "{user_id}"'''
            cursor.execute(sql)
            pass
    except Exception as e:
        print(e)
    finally:
        connection.close()

connect = Connect_Database(host,user,password,database,port)
Initial_state(connect,'123')
selected_state = Select_state(connect,'123')
selected_state_1 = selected_state[0]['user_state']
print(selected_state_1)

# x = Connect_Database(host,user,password,database,port)
# y = Initial_state(x,'123')
# z = Select_state(x,'123')

# print(y)
# print(z)
# print(z[0]['user_state'])