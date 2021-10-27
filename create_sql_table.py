import pymysql

PASSWORD = 'YourPassword'
DATABASE = 'YourDatabaseName'


def mysql_conn(host, user, password, db, port=3306, charset='utf8'):
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db,
        port=port,
        charset=charset
    )
    return conn


def create_table(table_name, sql):
    # 连接本地数据库
    conn = mysql_conn('localhost', 'root', PASSWORD, DATABASE)

    # 创建游标
    cursor = conn.cursor()
    # 如果存在表，则删除
    cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

    try:
        # 执行SQL语句
        cursor.execute(sql)
        print("创建数据表成功")
    except Exception as e:
        print("创建数据表失败：case%s"%e)
    finally:
        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        conn.close()


sql_create_ev_score = """
CREATE TABLE ev_score(
record_id SMALLINT,
university VARCHAR(150) NOT NULL,
date YEAR NOT NULL,
event CHAR(2) NOT NULL,
C FLOAT(3,2) UNSIGNED NOT NULL COMMENT 'competitiveness',
teams SMALLINT NOT NULL,
place SMALLINT NOT NULL,
cost FLOAT(5,2) COMMENT 'cost report',
bp FLOAT(5,2) COMMENT 'business presentation',
ed FLOAT(5,2) COMMENT 'engineering design',
acc FLOAT(5,2) COMMENT 'acceleration',
sp FLOAT(5,2) COMMENT 'skid pad',
autox FLOAT(5,2) COMMENT 'auto X',
endu FLOAT(5,2) COMMENT 'endurance',
fuel FLOAT(5,2),
pen SMALLINT,
total FLOAT(5,2),
wrl SMALLINT NOT NULL,
PRIMARY KEY (record_id)
) ENGINE=InnoDB;
"""
sql_create_event_mapping = """
CREATE TABLE event_mapping (
abbr CHAR(2) NOT NULL,
full VARCHAR(20) NOT NULL, 
PRIMARY KEY (abbr)
) ENGINE=InnoDB;
"""
sql_create_uni_region = """
CREATE TABLE uni_region(
country VARCHAR(25) NOT NULL,
city VARCHAR(30) NOT NULL,
university VARCHAR(150) NOT NULL,
PRIMARY KEY (university)
) ENGINE=InnoDB;
"""
sql_create_country_conti = """
CREATE TABLE country_conti(
continent VARCHAR(15) NOT NULL,
country VARCHAR(25) NOT NULL,
PRIMARY KEY (country)
) ENGINE=InnoDB;
"""
table_name_list = ['ev_score', 'event_mapping', 'uni_region', 'country_conti']
sql_create = [sql_create_ev_score, sql_create_event_mapping, sql_create_uni_region, sql_create_country_conti]

for i in range(4):
    create_table(table_name_list[i], sql_create[i])