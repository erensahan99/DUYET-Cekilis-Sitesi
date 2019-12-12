import MySQLdb

def connection():
    conn=MySQLdb.connect(host="localhost",
                         user= "root",
                         passwd="",
                         db="duyet",
                         autocommit=True,
                         charset='utf8')
    c=conn.cursor()
    c.execute("SET NAMES UTF8")
    c.execute("SET CHARACTER SET utf8")
    c.execute("SET COLLATION_CONNECTION = 'utf8_turkish_ci'")
    return c,conn
