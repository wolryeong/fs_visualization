import pymysql
import pandas as pd


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


def insert(dataframe, table_name):
    # 创建cursor负责操作conn接口
    conn = mysql_conn('localhost', 'root', PASSWORD, DATABASE)
    cursor = conn.cursor()
    # 开启事务
    conn.begin()

    # # 构造写入sql的数据表
    # columns = list(df.columns)
    # columns.remove("COLUMN NAME")
    # new_df = df[columns].copy()
    new_df = dataframe.copy()
    # 构造符合sql语句的列，因为sql语句使用逗号分隔(column1, column2, column3)
    columns = ','.join(list(new_df.columns))

    # 构造每个列对应的数据(value1, value2, value3)
    data_list = [tuple(i) for i in new_df.values]
    # 计算一行有多少value值需要用字符串占位
    s_count = len(data_list[0]) * '%s,'

    # 构造sql语句
    #     table_name = 'uni_region'
    insert_sql = f'INSERT INTO {table_name} ({columns}) VALUES ({s_count[:-1]})'
    try:
        cursor.executemany(insert_sql, data_list)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("创建数据表失败：case%s" % e)
        # 万一失败，需要进行回滚操作
        conn.rollback()
        cursor.close()
        conn.close()


def main():
    """TABLE uni_region"""
    df = pd.read_csv(r'./data/uni_region.csv')
    # 构造写入sql的数据表
    insert(df, 'uni_region')

    """TABLE country_conti"""
    map_cont = {
        'Argentina': 'South America', 'Australia': 'Oceania', 'Austria': 'Europe',

        'Bangladesh': 'Asia', 'Belgium': 'Europe', 'Bosnia and Herzegovina': 'Europe',
        'Brazil': 'South America', 'Bulgaria': 'Europe',

        'Canada': 'North America', 'China': 'Asia', 'Colombia': 'South America',
        'Croatia': 'Europe', 'Cyprus': 'Asia', 'Czech Republic': 'Europe',

        'Denmark': 'Europe',

        'Ecuador': 'South America', 'Egypt': 'Africa', 'Estonia': 'Europe',

        'Finland': 'Europe', 'France': 'Europe',

        'Germany': 'Europe', 'Greece': 'Europe',

        'Hungary': 'Europe',

        'Iceland': 'Europe', 'India': 'Asia', 'Indonesia': 'Asia', 'Iran': 'Asia',
        'Ireland': 'Europe', 'Israel': 'Asia', 'Italy': 'Europe',

        'Japan': 'Asia', 'Jordan': 'Asia',

        'Kazakhstan': 'Asia',

        'Lithuania': 'Europe',

        'Malaysia': 'Asia', 'Malta': 'Europe',
        'Mexico': 'North America', 'Morocco': 'Africa',

        'Netherlands': 'Europe', 'New Zealand': 'Oceania',
        'Nigeria': 'Africa', 'Norway': 'Europe',

        'Pakistan': 'Asia', 'Poland': 'Europe',
        'Portugal': 'Europe', 'Puerto Rico': 'North America',

        'Qatar': 'Asia',

        'Romania': 'Europe', 'Russia': 'Europe',

        'Saudi Arabia': 'Asia', 'Serbia': 'Europe', 'Singapore': 'Asia',
        'Slovakia': 'Europe', 'Slovenia': 'Europe', 'South Africa': 'Africa',
        'South Korea': 'Asia', 'Spain': 'Europe', 'Sri Lanka': 'Asia',
        'Sweden': 'Europe', 'Switzerland': 'Europe',

        'Taiwan': 'Asia', 'Thailand': 'Asia', 'Turkey': 'Asia',

        'Ukraine': 'Europe', 'United Arab Emirates': 'Asia',
        'United Kingdom': 'Europe', 'United States': 'North America',

        'Venezuela': 'South America'
    }
    df = pd.DataFrame.from_dict(map_cont, orient='index', columns=['Continent'])
    df = df.reset_index().rename(columns={'index': 'Country'})
    # 构造写入sql的数据表
    insert(df, 'country_conti')

    """TABLE uni_region"""
    df = pd.read_csv(r'./data/ev_score_dropna.csv')
    df.rename(columns={'Unnamed: 0': 'record_id'}, inplace=True)
    df['date'] = df['date'].apply(lambda x: x[:4])
    insert(df, 'ev_score')

    """TABLE event_mapping"""
    map_event = {
        'AU': 'Australia',
        'DE': 'Germany',
        'AT': 'Austria',
        'UK': 'United Kingdom',
        'HU': 'Hungary',
        'ES': 'Spain',
        'CZ': 'Czech',
        'EA': 'East',
        'JP': 'Japan',
        'IT': 'Italy',
        'NL': 'Netherlands',
        'LN': 'Lincoln',
        'FN': 'North Canada'
    }
    df = pd.DataFrame.from_dict(map_event, orient='index',columns=['full'])
    df = df.reset_index().rename(columns={'index': 'abbr'})
    # 构造写入sql的数据表
    columns = list(df.columns)
    insert(df, 'event_mapping')


if __name__ == '__main__':
    main()
