from prettytable import PrettyTable
import proso.geography.user as user
import proso.geography.success as success
import numpy
import scipy.stats


def answers_per_user(output, answers, group_column, group_name_mapping=None):
    _header(output, "Answers per User")

    table = PrettyTable([
        'Group', 'Size', 'Mean', "Std.", "Log Mean", 'Median', '25 Perc.', '75 Perc.', 'Mean Success'])
    table.align['Group'] = 'l'
    for group_name, group_data in answers.groupby(group_column):
        numbers = user.answers_per_user(group_data).values()
        table.add_row([
            group_name if group_name_mapping is None else group_name_mapping[group_name],
            len(numbers),
            numpy.round(numpy.mean(numbers), 2),
            numpy.round(numpy.std(numbers), 2),
            numpy.round(2 ** numpy.mean(numpy.log2(numbers)), 2),
            numpy.median(numbers),
            numpy.round(numpy.percentile(numbers, 25), 2),
            numpy.round(numpy.percentile(numbers, 75), 2),
            numpy.round(numpy.mean(success.success_per_user(group_data).values()), 2)])
    output.write(table.get_string(sortby="Group"))
    output.write("\n")


def answers_per_user_pvalues(output, answers, group_column, group_name_mapping=None):
    _header(output, "Answers per User - P Values (log)")
    numbers = {}
    for group_name, group_data in answers.groupby(group_column):
        g_name = group_name if group_name_mapping is None else group_name_mapping[group_name]
        numbers[g_name] = numpy.log(user.answers_per_user(group_data).values())
    table = PrettyTable(["Group"] + sorted(numbers.keys()))
    table.align['Group'] = 'l'
    numbers = sorted(numbers.items())
    for g_name1, ns1 in numbers:
        pvalues = []
        for g_name2, ns2 in numbers:
            tstat, pvalue = scipy.stats.ttest_ind(ns1, ns2)
            pvalues.append(numpy.round(pvalue, 2))
        table.add_row([g_name1] + pvalues)
    output.write(table.get_string())
    output.write("\n")


def user_ratio(output, answers, group_column, group_name_mapping=None):
    _header(output, "User Ratios")

    table = PrettyTable(['Group', '20 answers', "50 answers", "100 answers", '2 sessions'])
    table.align['Group'] = 'l'
    for group_name, group_data in answers.groupby(group_column):
        cell_ans_num_20 = user.user_ratio(group_data, answer_number_min=20)
        cell_ans_num_50 = user.user_ratio(group_data, answer_number_min=50)
        cell_ans_num_100 = user.user_ratio(group_data, answer_number_min=100)
        cell_sess_num_2 = user.user_ratio(group_data, session_number=2)
        table.add_row([
            group_name if group_name_mapping is None else group_name_mapping[group_name],
            numpy.round(cell_ans_num_20[0] / float(cell_ans_num_20[1]), 2),
            numpy.round(cell_ans_num_50[0] / float(cell_ans_num_50[1]), 2),
            numpy.round(cell_ans_num_100[0] / float(cell_ans_num_100[1]), 2),
            numpy.round(cell_sess_num_2[0] / float(cell_sess_num_2[1]), 2)])
    output.write(table.get_string(sortby="Group"))
    output.write("\n")


def _header(output, text):
    output.write("----------------------------------------------------------------------\n")
    output.write("  " + text + "\n")
    output.write("----------------------------------------------------------------------\n")
