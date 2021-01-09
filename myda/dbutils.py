import sqlite3
from myda.utils import get_logger


logger = get_logger(__name__)


def create_db():
    conn = sqlite3.connect("geo.db")
    logger.info("create database successfully！")


def create_table():
    ## 打开数据库连接
    conn = sqlite3.connect('geo.db')
    logger.info("Opened database successfully")
    ## 创建一个表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS geo
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT   NOT NULL,
       NAME           TEXT    NOT NULL UNIQUE,
       LNG            REAL     NOT NULL,
       LAT            REAL     NOT NULL);
    ''')
    logger.info("Table created successfully")
    conn.close()

def update_geo(data_list):
    sql = 'insert or ignore into geo (NAME,LNG,LAT) values (?,?,?)'
    conn = sqlite3.connect('geo.db')
    logger.info("Opened database successfully")
    conn.executemany(sql,data_list)
    logger.info("insert data successfully")
    conn.commit()
    conn.close()


def select_geo(name):
    sql = 'select name,lat,lng from geo where name = ?';
    conn = sqlite3.connect('geo.db')
    logger.info("Opened database successfully")
    values = conn.execute(sql,(name,)).fetchall()
    return values









