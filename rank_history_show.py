import pymysql
import pandas as pd
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWebEngineWidgets import QWebEngineView
from pyecharts import options as opts
from pyecharts.charts import Pie, Line
from multiprocessing import Pool


class Plot:
    def __init__(self):
        """
        **************************************************
        Init params, ui and reaction on signal change
        **************************************************
        """

        """MySQL login params init"""
        self.sql = {
            'host': 'localhost',
            'user': 'root',
            'password': '121144',
            'db': 'fsg',
        }
        """class params init"""
        self.currentUni = ''
        self.currentEvent = ''
        self.edit_text = ''
        self.plot_uni_list = pd.DataFrame()
        """ui settings"""
        self.ui = QUiLoader().load('ui/fsg_rankHistory.ui')  # load Qt Designer ui
        self.line = Line()  # line graph init
        self.ui_init()  # init objects in ui
        """on signal"""
        self.ui.eventBox.currentTextChanged.connect(self.event_box_text_changed)  # on signal: EventComboBox text change
        self.ui.uniBox.currentTextChanged.connect(self.uni_box_text_changed)  # on signal: UniCombobox text change
        self.ui.uniEdit.textChanged.connect(self.uni_edit_text_changed)  # on signal: Uni LineEdit text change
        """on button"""
        self.ui.add.clicked.connect(self.add_uni_to_list)  # on signal: Add button clicked
        self.ui.dlt.clicked.connect(self.del_uni_from_list)  # on signal: Del button clicked

    def ui_init(self):
        """
        **************************************************
        Init charts and ui objects
        **************************************************
        """

        """render charts"""
        self.pie_count_by_continent()
        self.line_rank_history_init()
        """event ComboBox"""
        self.ui.eventBox.addItems(self.get_event_list())
        self.currentEvent = self.ui.eventBox.currentText()[:2]
        """uni ComboBox"""
        self.ui.uniBox.addItems(self.get_uni_list())
        self.currentUni = self.ui.uniBox.currentText()
        """buttons & uni listWidget"""

    def mysql_conn(self, port=3306, charset='utf8'):
        """
        **************************************************
        Connect to local MySQL database
        **************************************************"""

        conn = pymysql.connect(
            host=self.sql['host'],
            user=self.sql['user'],
            password=self.sql['password'],
            database=self.sql['db'],
            port=port,
            charset=charset
        )
        return conn

    def select_data(self, sql):
        """
        **************************************************
        Select data from database according to input sql phrase
        **************************************************
        """

        conn = self.mysql_conn()  # connect database
        cur = conn.cursor()  # create cursor object
        try:
            cur.execute(sql)  # execute SQL select statement
            data = cur.fetchall()  # obtain data (return data type: tuple)
            data = [list(z) for z in data]  # dhange type to list
        except Exception as e:
            print("Query Failed：case%s" % e)
            data = None
        finally:
            cur.close()  # close cursor connection
            conn.close()  # close database connection
        return data

    def select_history(self):
        sql_school_rank_history = f"""
        SELECT date, place
        FROM ev_score
        WHERE university='{self.currentUni}' AND event='{self.currentEvent}'
        ORDER BY date;
        """
        school_rank_history = self.select_data(sql_school_rank_history)
        """change data type that Pyecharts want"""
        school_rank_history_rank = [r[1] for r in school_rank_history]
        school_rank_history_year = [str(y[0]) for y in school_rank_history]
        return school_rank_history_year, school_rank_history_rank

    def pie_count_by_continent(self):
        """
        **************************************************
        Select pie chart data and draw pie chart
        **************************************************
        """

        """get quantity of university in every continent that ever participated in the competition"""
        sql_count_by_continent = """
                SELECT continent, COUNT(*)
                FROM uni_region ur LEFT JOIN country_conti cc ON ur.country = cc.country 
                GROUP BY continent;
                """  # define select statement
        count_by_continent = self.select_data(sql_count_by_continent)
        """draw pie chart"""
        pie = (
            Pie(init_opts=opts.InitOpts(width='640px', height='350px'))  # chart size
            .add(
                series_name='',
                data_pair=count_by_continent,  # data pair (2 dimension list [str, int])
            )
        )
        bro = QWebEngineView()
        bro.setHtml(pie.render_embed())
        self.ui.pieConti.setWidget(bro)  # connect HTML to ui widget

    def get_event_list(self):
        """
        **************************************************
        Select all ev event list
        **************************************************
        """

        sql_select_event = """
        SELECT *
        FROM event_mapping ev RIGHT JOIN (
        SELECT DISTINCT event
        FROM ev_score) evs ON ev.abbr = evs.event;
        """
        event_list = self.select_data(sql_select_event)
        event_list = [f'{el[0]} {el[1]}' for el in event_list]
        # print('got event list')
        return event_list

    def get_uni_list(self):
        """
        **************************************************
        Select all university participated in the selected event
        **************************************************
        """

        sql_select_uni = f"""
           SELECT DISTINCT university
           FROM ev_score
           WHERE event = '{self.currentEvent}' and university LIKE '%{self.edit_text}%';
           """
        uni_list = self.select_data(sql_select_uni)
        uni_list = [u[0] for u in uni_list]
        # print(uni_list)
        # print('got uni_list')
        return uni_list

    def event_box_text_changed(self, changed_event):
        self.currentEvent = self.ui.eventBox.currentText()[:2]  # get abbr of new selected event
        """clear original display on ui"""
        self.ui.uniList.clear()  # clear the original display widget data on ui
        self.line_rank_history_init()  # reset line graph
        self.ui.uniEdit.clear()  # clear insert line
        self.ui.uniBox.clear()  # clear the original uni ComboBox data on ui
        """renew the data and display"""
        self.plot_uni_list = pd.DataFrame()  # get university list of new selected event
        self.ui.uniBox.addItems(self.get_uni_list())  # add new uni ComboBox data on ui

    def uni_box_text_changed(self, changed_uni):
        self.currentUni = self.ui.uniBox.currentText()

    def uni_edit_text_changed(self, changed_filter):
        self.edit_text = self.ui.uniEdit.text()
        """change data"""
        self.ui.uniBox.clear()
        self.ui.uniBox.addItems(self.get_uni_list())  # add filter to original list

    def add_uni_to_list(self):
        uni = self.currentUni
        if uni not in self.plot_uni_list.index.values:  # guarantee no repeated uni displayed
            self.ui.uniList.addItem(uni)  # add new item to the ui display
            """organize data to DataFrame"""
            year, rank = self.select_history()
            for i in range(len(rank)):
                self.plot_uni_list.loc[uni, year[i]] = rank[i]
            self.plot_uni_list.sort_index(axis=1, inplace=True)  # sort columns name, guarantee 'year' ranked asc
            """render line chart"""
            self.line_rank_history_init()
            self.line_rank_history_mod()

    def del_uni_from_list(self):
        if self.ui.uniList.currentRow() >= 0:  # guarantee uniList has item
            uni = self.ui.uniList.item(self.ui.uniList.currentRow()).text()
            """reorganize DataFrame"""
            self.plot_uni_list.drop(uni, inplace=True)
            self.plot_uni_list.dropna(axis=1, how='all', inplace=True)
            """render line chart"""
            self.line_rank_history_init()
            self.line_rank_history_mod()
            """delete uni from display widget"""
            self.ui.uniList.takeItem(self.ui.uniList.currentRow())
            if len(self.plot_uni_list) == 0:  # if no data in DataFrame, init it
                self.plot_uni_list = pd.DataFrame()

    def line_rank_history_init(self):
        self.line = (
            Line()
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Rank History", subtitle=f'in {self.currentEvent}'),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),  # display data tooltip, trigger by axis
                xaxis_opts=opts.AxisOpts(
                    is_scale=True,  # coordinate scales not be forced to include zero scale
                    axisline_opts=opts.AxisLineOpts(is_show=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    interval=1  # set tick interval
                ),
                yaxis_opts=opts.AxisOpts(
                    is_inverse=True,  # small number on top
                    is_show=False
                ),
                legend_opts=opts.LegendOpts(
                    pos_right="right",
                    orient="vertical"  # 'horizontal' or 'vertical'
                )
            )
            .add_xaxis(self.plot_uni_list.columns.values)
        )
        bro = QWebEngineView()
        bro.setHtml(self.line.render_embed())
        self.ui.lineRank.setWidget(bro)

    def line_rank_history_mod(self):
        for i in range(len(self.plot_uni_list)):
            plot_uni_name = self.plot_uni_list.index.values[i]
            self.line.add_yaxis(
                series_name=f'{plot_uni_name}',  # set legend name
                y_axis=self.plot_uni_list.loc[plot_uni_name],  # y axis data
                is_symbol_show=True,
                is_connect_nones=True,  # connect data ignore None
            )
        bro = QWebEngineView()
        bro.setHtml(self.line.render_embed())
        self.ui.lineRank.setWidget(bro)
    # def render(self, graph):
    #     browser = QWebEngineView()
    #     browser.setHtml(graph.render_embed())
    #     self.ui.pieConti.setWidget(browser)


def run_app():
    app = QApplication([])
    p = Plot()
    p.ui.show()
    app.exec_()


if __name__ == '__main__':
    run_app()
