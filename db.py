import os, psycopg2, string, random, hashlib

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

def get_salt():
    charset = string.ascii_letters + string.digits
    
    salt = ''.join(random.choices(charset, k=30))
    return salt

def get_hash(password, salt):
    b_pw = bytes(password, 'utf-8')
    b_salt = bytes(salt,'utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', b_pw, b_salt, 1246).hex()
    return hashed_password

def insert_user(user_name, password):
    sql = 'INSERT INTO user2 VALUES(default, %s, %s, %s)'
    
    salt = get_salt()
    hashed_password = get_hash(password, salt)
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (user_name, hashed_password, salt))
        count = cursor.rowcount #更新件数を取得
        connection.commit()
        
    except psycopg2.DatabaseError :
        cpunt = 0
        
    finally :
        cursor.close()
        connection.close()
        
    return count
        
def login(user_name, password):
    sql = 'SELECT hashed_password, salt FROM user2 WHERE name = %s'
    flg = False
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (user_name,))
        user = cursor.fetchone()
        
        if user != None:
            salt = user[1]
            
            hashed_password = get_hash(password, salt)
            
            if hashed_password == user[0]:
                flg = True
    except psycopg2.DatabaseError:
        flg = False
    finally :
        cursor.close()
        connection.close()
        
    return flg

def insert_book(name, author, publisher, isbn):
    sql = 'INSERT INTO tosho2 (name, author, publisher, isbn) VALUES (%s, %s, %s, %s)'
    count = 0
    try:
        connection = get_connection()
        cursor = connection.cursor()
        if is_book_isbn_taken(isbn):
            count = -1
        else:
            cursor.execute(sql, (name, author, publisher, isbn))
            count = cursor.rowcount
            connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
    return count

def is_book_isbn_taken(isbn):
    sql = 'SELECT COUNT(*) FROM tosho2 WHERE isbn = %s'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (isbn,))
        count = cursor.fetchone()[0]
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
    return count > 0
        
def delete_book(id):
    connection = get_connection()
    connection.cursor()
    cursor = connection.cursor()
    sql = 'DELETE FROM tosho2 WHERE id = %s'
    cursor.execute(sql,(id))
    count = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()
    return count

def select_all_books():
    connection = get_connection()
    cursor = connection.cursor()
    sql = 'SELECT * FROM tosho2 ORDER BY id ASC;'
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows