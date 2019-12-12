import MySQLdb

def connection():
    conn=MySQLdb.connect(host="us-cdbr-iron-east-05.cleardb.net",
                         user= "bf98641ce1385c",
                         passwd="4feaf642",
                         db="heroku_f580b65af1fa5c6",
                         autocommit=True,
                         charset='utf8')

    c=conn.cursor()
    c.execute("SET NAMES UTF8")
    c.execute("SET CHARACTER SET utf8")
    c.execute("SET COLLATION_CONNECTION = 'utf8_turkish_ci'")
    return c,conn
'''
conn=MySQLdb.connect(host="localhost",
                     user= "root",
                     passwd="",
                     db="duyet",
                     autocommit=True,
                     charset='utf8')
'''
