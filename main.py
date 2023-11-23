import os
from datetime import datetime

import numpy as np
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

import pandas as pd

import matplotlib.pyplot as plt

# Cashflow
_date = 'Data'
_concept = 'Concepte'
_category = 'Categoria'
_import = 'Import (€)'
_movement_type = 'Tipus Moviment'
_account = 'Compte/Targeta'

_expense = 'Despesa (D)'
_income = 'Ingrés (I)'

# Categories
_cost_by_category = 'Despeses per categoria'
_cost = 'Despeses (€)'
_cost_percentage = 'Percentatge Despeses (%)'
_num_movements = 'Nº Moviments'


def process_data(data: BeautifulSoup) -> pd.DataFrame:
    rows = data.find_all('Row')
    titles_data = rows[4].find_all('Data')
    titles = [title.text for title in titles_data]

    data_rows = rows[5:]
    parsed_data = list()
    for row in data_rows:
        row_data = row.find_all('Data')

        if len(row_data) == 0: break
        if len(row_data) != len(titles): break

        new_data = [cell.text for cell in row_data]

        parsed_data.append(new_data)

    categories_df = pd.DataFrame(parsed_data, columns=titles)
    return categories_df


class Month:
    def __init__(self, data: BeautifulSoup) -> None:
        expenses_data = data.find('Worksheet', {'ss:Name': 'Categories'})
        income_data = data.find_all_next('Ingressos per categoria')


        self.summary: pd.DataFrame = process_data(expenses_data)
        self.summary[_cost] =self.summary[_cost].astype(float)
        self.summary[_cost_percentage] = self.summary[_cost_percentage].astype(float)
        self.summary[_num_movements] = self.summary[_num_movements].astype(int)

        print(self.movements)
        print(self.summary)


def summary_by_month(month_df: pd.DataFrame, name: str, start: datetime = None, end: datetime = None):
    if start is not None: month_df = month_df[month_df[_date] >= start]
    if end is not None: month_df = month_df[month_df[_date] <= end]

    movements_by_month = month_df.groupby(pd.Grouper(key=_date, freq='M'))

    expenses = list()
    incomes = list()
    for _, month_df in movements_by_month:
        expenses_mask = month_df[_movement_type] == _expense
        month_expenses = month_df[expenses_mask]

        incomes_mask = month_df[_movement_type] == _income
        month_incomes = month_df[incomes_mask]

        incomes.append(month_incomes[_import].sum())
        expenses.append(month_expenses[_import].sum())

    x_axis = np.arange(len(incomes))
    incomes = np.asarray(incomes)
    expenses = np.asarray(expenses)

    plt.bar(x_axis - 0.2, incomes, 0.4, label='Incomes')
    plt.bar(x_axis + 0.2, -expenses, 0.4, label='Expenses', color='deepskyblue')

    plt.xlabel('Months')
    plt.ylabel('EUR')
    plt.title(name)
    plt.legend()
    plt.show()


def main():
    data_path = os.path.join('data', 'data.xml')
    with open(data_path, 'r') as xml_file:
        data = xml_file.read()

    bs_data = BeautifulSoup(data, 'xml')
    movements_data = bs_data.find('Worksheet', {'ss:Name': 'Ingressos i Despeses'})

    movements_df = process_data(movements_data)

    movements_df[_import] = movements_df[_import].astype(float)
    movements_df[_date] = pd.to_datetime(movements_df[_date], dayfirst=True)

    personal_mask = movements_df[_account].str.contains('0032') | movements_df[_account].str.contains('5029')
    personal_df = movements_df[personal_mask]
    flat_df = movements_df[~personal_mask]

    summary_by_month(personal_df, 'Personal monthly summary', start=datetime(2023, 4, 1))
    summary_by_month(flat_df, 'Flat monthly summary', start=datetime(2023, 4, 1))


if __name__ == '__main__':
    main()

