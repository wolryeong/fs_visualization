# fs_visualization
![FSAE 德国赛 (FSG) LOGO](https://www.formulastudent.de/fileadmin/user_upload/all/CD/FSG_Logo/FSG_Logo_rgb.jpg)
本项目意在对[FSAE德国赛官网](https://www.formulastudent.de/)中记录的世界FSAE赛事历史成绩与排名数据进行爬取后，进行简单的可视化工作。  
项目使用Python及SQL语言，涉及：
1. 基础爬虫：request, BeautifulSoup4, multiprocessing  
    > `main_get_allinfo.py`, `get_rank_pool.py`, `get_score_pool.py`
2. 数据清洗及处理：pandas, NumPy  
    > `split_data.py`, `data_cleaning.py`
3. MySQL数据库操作：SQL, pymysql  
    > `create_sql_table.py`,  `insert_sql_data.py`
4. 可视化作图：pyecharts  
    > `rank_history_show.py`
5. 图形界面编写：PySide2, Qt Designer  
    > `rank_history_show.py`  

## 目录
<a href="#mga">main_get_allinfo.py</a>  
<a href="#grp">get_rank_pool.py</a>  
<a href="#gsp">get_score_pool.py</a>  
<a href="#sd">split_data.py</a>  
<a href="#dc">data_cleaning.py</a>  
<a href="#cst">create_sql_table.py</a>  
<a href="#isd">insert_sql_data.py</a>  
<a href="#rhs">rank_history_show.py</a>  

## main_get_allinfo.py<a id="mga"/>  

## get_rank_pool.py<a id="grp"/>

## get_score_pool.py<a id="gsp"/>

## split_data.py<a id="sd"/>

## data_cleaning.py<a id="dc"/>

## create_sql_table.py<a id="cst"/>

## insert_sql_data.py<a id="isd"/>

## rank_history_show.py<a id="rhs"/>
