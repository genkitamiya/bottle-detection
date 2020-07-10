import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def get_df(path, start=None, end=None):
    """
    期間指定 or 全期間の帳簿を取得

    Parameters
    ----------
    start: int
      起算日（年月日）
    end: int
      終了日（年月日）
    """
    df = pd.concat((pd.read_csv(path+f, index_col=0) for f in os.listdir(path)))
    df['saletime'] = [datetime.strptime(str(x), '%Y/%m/%d %H:%M:%S') for x in df['saletime']]
    tmp_df = df.set_index(['saletime'])

    if not start and not end:
        label = ''
        return tmp_df, label
    elif not end:
        label = ' between {} - {}'.format(start, datetime.today().strftime('%Y/%m/%d'))
        start = datetime.strptime(start, '%Y/%m/%d')
        end = datetime.today() + timedelta(1)
        tmp_df = tmp_df.loc[start:end]
        return tmp_df, label
    else:
        label = ' between {} - {}'.format(start, end)
        date_start = datetime.strptime(str(start), '%Y/%m/%d')
        date_end = datetime.strptime(str(end), '%Y/%m/%d') + timedelta(1)
        tmp_df = tmp_df.loc[start:end]
        return tmp_df, label


def sales_day(path, datestr=datetime.today().strftime('%Y%m%d')):
    """
    1日の売上金額を表示
    """
    file = 'sales_{}.csv'.format(datestr)
    df = pd.read_csv(path+file)
    total = df['prodprice'].sum()
    print('{}年{}月{}日の売上金額は¥{}です。'.format(datestr[:4], datestr[4:6], datestr[6:], total))


def sales_history(path, start=None, end=None):
    """
    指定期間内の売上推移を表示
    """
    df, label = get_df(path, start, end)
    # 日毎に正規化
    df.index = df.index.normalize()
    #　日毎にgroupby
    df_plt = df.groupby(df.index).sum()

    # グラフ化
    plt.bar(df_plt.index.strftime('%Y/%m/%d'), df_plt['prodprice'])
    plt.title('Total sales per day'+label)
    plt.xlabel('Day')
    plt.ylabel('Sales (JPY)')
    plt.show()


def sales_by_product(path, start=None, end=None):
    """
    商品毎の売上個数
    """
    df, label = get_df(path, start, end)

    plt.hist(df['prodname'])
    plt.title('Total products sold'+label)
    plt.xlabel('Product Name')
    plt.ylabel('Quantity')
    plt.show()
        

def sales_by_time(path, start=None, end=None):
    """
    時間帯毎の売上個数
    """
    df, label = get_df(path, start, end)
    df_plt = df.groupby(df.index.hour).sum()

    # 1時間毎の総売上
    hours = np.arange(1,25)
    sales = np.zeros(24)
    sales[df_plt.index] = df_plt['prodprice']

    # グラフ化
    plt.bar(hours, sales)
    plt.title('Total sales per hour'+label)
    plt.xlabel('Hour')
    plt.ylabel('Sales (JPY)')
    plt.show()
