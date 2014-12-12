"""
Create CSV file for Sydbank based on a list of transactions.

"""

import csv
import datetime
import cStringIO as StringIO
import unicodedata

def prepend_zeros(string, min_length):
    if isinstance(string, unicode):
        string = unicodedata.normalize('NFKD', string).encode('ascii','ignore')

    current_length = len(string)
    if current_length > min_length:
        raise Exception("The string is longer than %s chars" % min_length)

    padding = min_length - current_length
    return padding * '0' + string


def append_spaces(string, min_length):
    if isinstance(string, unicode):
        string = unicodedata.normalize('NFKD', string).encode('ascii','ignore')

    current_length = len(string)
    if current_length > min_length:
        raise Exception("The string is longer than %s chars" % min_length)

    padding = min_length - current_length
    return string + padding * ' '


def blank_column(length):
    return append_spaces('', length)


def export_transactions(transactions, transaction_sum, num_transactions, write_to=False):
    """
    Takes a list of transaction dicts and converts to Sydbank compatible format.

    You must supply transaction_sum and num_transactions as verification.

    Transaction dictionary format:

    {
        'amount': 100, # 13 digits
        'from_account_number': '22330001033105', # 15 digits
        'to_reg_number': '7981', # 4 digits
        'to_account_number': '1046139', # 10 digits
        'to_text': 'This text is for their, # 35 chars
        'to_user_name': 'Kaj Nielsen', # 32 chars
        'bilagsnr': '324324', # 35 chars
        'date': '20141201', # 8 digits (optional)
        'currency': 'DKK' # 3 chars (optional)
    }
    """

    csvfile = StringIO.StringIO()
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    todaystring = today.strftime('%Y%m%d')
    tomorrowstring = tomorrow.strftime('%Y%m%d')

    start_row = [
        'IB000000000000',
        todaystring,
        blank_column(90),
        blank_column(255),
        blank_column(255),
        blank_column(255)
    ]

    writer.writerow(start_row)

    index = 0
    for transaction in transactions:
        index += 1
        row = [
            'IB030202000005',
            prepend_zeros('%d' % index, 4),  # index of transaction starting at 1
            prepend_zeros(transaction.get('date', tomorrowstring), 8),  # date
            prepend_zeros('%d+' % (transaction['amount'] * 100), 14),  # amount in ore (the 14 is to include the + symbol)
            append_spaces(transaction.get('currency', 'DKK'), 3), # currency
            '2',
            prepend_zeros(transaction['from_account_number'], 15),  # from account
            '2',
            transaction['to_reg_number'],  # to reg number
            prepend_zeros(transaction['to_account_number'], 10),  # to account number
            '0',
            append_spaces(transaction['to_text'], 35),  # text to customer statement
            append_spaces(transaction['to_user_name'], 32),  # customer name
            blank_column(32),
            blank_column(32),
            blank_column(4),
            blank_column(32),
            append_spaces(transaction['bilagsnr'], 35),  # our internal bilagsnr
            blank_column(35),
            blank_column(35),
            blank_column(35),
            blank_column(35),
            blank_column(35),
            blank_column(35),
            blank_column(35),
            blank_column(35),
            blank_column(35),
            blank_column(35),
            blank_column(1),
            blank_column(215)
        ]

        writer.writerow(row)

    end_row = [
        'IB999999999999',
        todaystring,
        prepend_zeros('%d' % num_transactions, 6),  # num transactions
        prepend_zeros('%d+' % (transaction_sum * 100), 14),  # sum of transaction values
        blank_column(64),
        blank_column(255),
        blank_column(255),
        blank_column(255)
    ]

    writer.writerow(end_row)

    if write_to:
        with open(write_to, 'wb') as f:
            csvfile.seek(0)
            f.write(csvfile.read())
            f.close()
    else:
        return csvfile
