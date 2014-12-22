#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date, time


class NonvalidYearException(Exception):  # Exceptionを継承
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MewCalc:
    def __init__(self):
        """
        初期化
        """
        pass

    def calculate_by_year(self, year):
        """
        人間の歳で猫の年齢計算する
        :param year: 人間の歳
        :return: 猫の年齢
        """
        if year <= 0:
            raise NonvalidYearException("year is not valid")
        return 24 + (year - 2) * 4

    def calculate_human_age(self, born):
        """
        普通に人間的な年齢を計算する
        :param born: date型の日付
        :return: 猫の年齢
        """
        today = date.today()
        try:
            birthday = born.replace(year=today.year)
        except ValueError:  # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=today.year, month=born.month + 1, day=1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year


    def calc_less_than_zero(self, born):
        """
        TODO: 2年目までの計算をする
        :param born:
        """
        pass

    def calculate(self, born):
        """
        猫の年齢を計算する
        :param born:
        :return: 猫の年齢
        """
        if type(born) == int:
            return self.calculate_by_year(born)
        else:
            # 人間の年齢計算して
            age = self.calculate_human_age(born)
            if age < 1:
                self.calc_less_than_zero(born)
            # 猫の年齢計算する
            return self.calculate_by_year(age)
