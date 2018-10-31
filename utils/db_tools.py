import os
import sys
import warnings
import glob
import pandas as pd
from datetime import timedelta, date

month = {'January': '01',
         'February': '02',
         'March': '03',
         'April': '04',
         'May': '05',
         'June': '06',
         'July': '07',
         'August': '08',
         'September': '09',
         'October': '10',
         'November': '11',
         'December': '12'}


class DB(object):

    def __init__(self, path):

        if not sys.warnoptions:
            warnings.simplefilter("ignore")

        self.columns = ['user', 'region', 'transaction_date_datetime', 'transaction_date_date',
                        'transaction_date_month', 'transaction_date_year', 'join_date_datetime',
                        'join_date_date', 'join_date_month', 'join_date_year', 'sales_amount']
        # init data
        self.data = pd.DataFrame()

        self.df1 = pd.read_csv('Data/transactions_2013.csv', sep='\t')
        self.df1 = self.process(self.df1)

        self.df2 = pd.read_csv('Data/transactions_2014.csv', sep='\t')
        self.df2 = self.process(self.df2)

        self.df3 = pd.read_csv('Data/transactions_2015.csv', sep='\t')
        self.df3 = self.process(self.df3)

        self.df4 = pd.read_csv('Data/transactions_2016.csv', sep='\t')
        self.df4 = self.process(self.df4, new=True)

        self.data = pd.concat([self.data, self.df1, self.df2, self.df3, self.df4], ignore_index=True)

    def _get_paths(self, dir_path):

        if os.path.exists(dir_path):
            files_path = os.path.join(dir_path, '*')
            files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
            return files

        else:
            print('Unable to load file : ' + dir_path)
            return None

    def _transaction_preprocessing(self, df, new):
        if new:
            temp = df['transaction_date'].str.split('-', expand=True)
            df['transaction_date_datetime'] = pd.to_datetime(df['transaction_date'])
            temp[0] = pd.to_numeric(temp[0])
            temp[1] = pd.to_numeric(temp[1])
            temp[2] = pd.to_numeric(temp[2])
            df['transaction_date_date'] = temp[0]
            df['transaction_date_month'] = temp[1]
            df['transaction_date_year'] = temp[2]
            df = df.drop(columns=['transaction_date'])
        else:
            temp = df['transaction date'].str.split('/', expand=True)
            temp[0] = temp[0].map(month)
            temp[3] = pd.to_datetime(temp[1] + '-' + temp[0] + '-' + temp[2])
            temp[0] = pd.to_numeric(temp[0])
            temp[1] = pd.to_numeric(temp[1])
            temp[2] = pd.to_numeric(temp[2])
            df['transaction_date_datetime'] = temp[3]
            df['transaction_date_date'] = temp[1]
            df['transaction_date_month'] = temp[0]
            df['transaction_date_year'] = temp[2]
            df = df.drop(columns=['transaction date'])
        return df

    def _join_preprocessing(self, df, new):

        if new:
            temp = df['join_date'].str.split('-', expand=True)
            df['join_date_datetime'] = pd.to_datetime(df['join_date'])
            temp[0] = pd.to_numeric(temp[0])
            temp[1] = pd.to_numeric(temp[1])
            temp[2] = pd.to_numeric(temp[2])
            df['join_date_date'] = temp[0]
            df['join_date_month'] = temp[1]
            df['join_date_year'] = temp[2]
            df = df.drop(columns=['join_date'])
        else:
            temp = df['join date'].str.split('/', expand=True)
            temp[0] = temp[0].map(month)
            temp[3] = pd.to_datetime(temp[1] + '-' + temp[0] + '-' + temp[2])
            temp[0] = pd.to_numeric(temp[0])
            temp[1] = pd.to_numeric(temp[1])
            temp[2] = pd.to_numeric(temp[2])
            df['join_date_datetime'] = temp[3]
            df['join_date_date'] = temp[1]
            df['join_date_month'] = temp[0]
            df['join_date_year'] = temp[2]
            df = df.drop(columns=['join date'])
        return df

    def _conversions(self, df, new):
        if new:
            df['user'] = pd.to_numeric(df['user'])
            df['sales_amount'] = pd.to_numeric(df['sales_amount'])

        else:
            df['user'] = pd.to_numeric(df['user'])
            df['sales_amount'] = pd.to_numeric(df['sales amount'])
            df = df.drop(columns=['sales amount'])
        return df

    def process(self, df, new=False):

        df = df.dropna()
        df = self._transaction_preprocessing(df, new)
        df = self._join_preprocessing(df, new)
        df = self._conversions(df, new)
        df = df[self.columns]
        return df
