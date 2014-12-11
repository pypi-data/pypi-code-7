#!/usr/bin/env python
# coding: utf-8

import ast
import os


class Connection(object):

    def __init__(self, database):
        self.database = database

    def get_sfr(self, query):
        """
        Return a dict for a standard SELECT-FROM-WHERE query
        """

        def get_select_fields(query):
            """
            Extracts the select fields from the query
            """
            return [field for field in query.split('FROM')[0][7:-1].split(', ')]

        def get_select_filter(query):
            """
            Extracts the filter values from the query
            """
            try:
                filter = query.split('WHERE')[1][1:]
                if filter.endswith(";"):
                    filter = filter[:-1]
            except:
                filter = None
            return filter

        def get_select_table(query):
            """
            Extracts the table from the query
            """
            select_filter = get_select_filter(query)
            if select_filter:
                length = len(select_filter) + 7
                return query.split('FROM')[1][1:-length]
            else:
                return query.split('FROM')[1][1:]

        return {'fields': (get_select_fields(query)),
                'table': (get_select_table(query)),
                'filter' :(get_select_filter(query))}


    def get_insert_values_table_fields(self, query):

        def get_insert_table(query):
            table = query.split("(")[0][12:-1]
            return table

        def get_insert_fields_and_values(query):
            len1 = len(query.split("(")[0]) + 1
            len2 = len(query.split(")")[0])
            fields = query[len1:len2]
            values = query.split("(")[2][:-1]
            fields_and_values = dict(zip(fields.split(", "), values.split(", ")))
            return fields_and_values


        return {'table': (get_insert_table(query)),
                'fields_and_values': (get_insert_fields_and_values(query))}

    def get_delete_lines(self, query):

        def get_line_data(query):
            line_data = {}
            filter = query.split("WHERE ")[1]
            line_data['key'] = filter.split('=')[0]
            line_data['value'] = filter.split('=')[1]
            table = query.split("FROM")[1][1:]
            table = table.split('WHERE')[0]
            line_data['table'] = table
            return line_data

        db_content = self.get_db_content()
        line_data = get_line_data(query)
        table_lines = []
        for line in db_content.split('\n'):
            if line.startswith(line_data['table']):
                table_lines.append(line)

        lines = []
        for line in table_lines:
            check_line = ast.literal_eval(line.split(" = ")[1])
            for key, value in check_line.items():
                if key == line_data['key'] and value == line_data['value']:
                    lines.append(line)
        return lines

    def get_update_line_data(self, query):
        line_data = {}
        filter = query.split("WHERE ")[1]
        line_data['key'] = filter.split('=')[0]
        line_data['value'] = filter.split('=')[1]
        table = query.split(" SET")[0][7:]
        table = table.split('WHERE')[0]
        line_data['table'] = table
        settings = query.split("SET ")[1].split(" WHERE")[0]
        line_data['settings'] = {}
        for item in settings.split(", "):
            line_data['settings'][item.split("=")[0]] = item.split("=")[1]
        return line_data

    def get_update_line(self, query):
        db_content = self.get_db_content()
        line_data = self.get_update_line_data(query)
        table_lines = []
        for line in db_content.split('\n'):
            if line.startswith(line_data['table']):
                table_lines.append(line)
        lines = []
        for line in table_lines:
            check_line = ast.literal_eval(line.split(" = ")[1])
            for key, value in check_line.items():
                if key == line_data['key'] and value == line_data['value']:
                    lines.append(line)
        return lines


    def execute(self, query):
        query = query.strip()

        class InvalidQuery(Exception):
            pass

        def select_query(self, query):

            filter = self.get_sfr(query)['filter']
            try:
                int(filter.split("=")[0])
                filter = None
            except:
                pass

            if filter:
                return self.select_by_fields_and_filter(
                                                  self.get_sfr(query)['table'],
                                                  self.get_sfr(query)['fields'],
                                                  filter)
            else:
                return self.get_all(self.get_sfr(query)['table'],
                                    self.get_sfr(query)['fields'],)

        def insert_query(self, query):
            data = self.get_insert_values_table_fields(query)
            id = self.get_max_id_for_table(data['table']) + 1
            data['fields_and_values']['id'] = str(id)
            line = "%s = %s\n" % (data['table'], data['fields_and_values'])
            db = open(self.database, 'a')
            db.writelines(line)
            return id

        def clean_lines():
            content = self.get_db_content()
            clean = ""
            for line in content.split('\n'):
                if line[:1]:
                    clean += line + "\n"
            self.save_db_content(clean)

        def update_query(self, query):
            data = self.get_update_line_data(query)
            lines = self.get_update_line(query)
            content = self.get_db_content()

            for line in lines:
                settings = ast.literal_eval(line.split(" = ")[1])
                for key, value in data['settings'].items():
                    settings[key] = value
                new_line = "%s = %s\n" % (data['table'], settings)
                content = content.replace(line, new_line)
            self.save_db_content(content)
            clean_lines()

        def delete_query(self, query):
            lines  = self.get_delete_lines(query)
            for line in lines:
                content = self.get_db_content()
                content = content.replace(line, "")
                self.save_db_content(content)
            clean_lines()

        query_type = query[:6].upper()

        if query_type == "SELECT":
            return select_query(self, query)
        elif query_type == "INSERT":
            return insert_query(self, query)
        elif query_type == "UPDATE":
            return update_query(self, query)
        elif query_type == "DELETE":
            return delete_query(self, query)
        else:
            raise InvalidQuery("Invalid SQL provided")

    def get_max_id_for_table(self, tablename):
        ids = self.get_all(tablename, fields=['id'])
        if ids:
            return max([int(id[0]) for id in ids])
        else:
            return 0

    def get_db_content(self):
        db = open(self.database, 'r')
        return db.read()

    def save_db_content(self, content):
        db = open(self.database, 'w')
        db.write(content)
        db.close()

    def get_table_as_dict(self, tablename):
        content = self.get_db_content()
        dict = {}
        count = 0
        for line in content.split('\n'):
            if line.startswith(tablename):
                dict[count] = ast.literal_eval(line.split(" = ")[1])
                count += 1
        return dict

    def get_all(self, tablename, fields):
        """
        Selects all database objects from one table
        """
        all = []

        for _object in self.get_table_as_dict(tablename).values():

            element = {}
            for key, value in _object.items():
                element[key] = value

            order = {}
            order_position = 0
            for field in fields:
                order[order_position] = field
                order_position += 1

            sorted_fields = []

            for key, value in order.items():
                sorted_fields.append((value, element[value]))

            element = []

            for item in sorted_fields:
                item = item[1]
                element.append(item)

            all.append(tuple(element))
        return all

    def select_by_fields_and_filter(self, tablename, fields, filter):
        """
        Selects database objects by fields and filter
        """
        try:
            filter_key = filter.split('=')[0]
            filter_value = filter.split('=')[1][1:-1]
        except:
            key = filter.split("=")[0]
            value = filter.split('=')[1]
            try:
                int(key) == int(value)
            except:
                raise InvalidQuery("Something went terriblly wrong")

        all = []
        filtered = []
        for _object in self.get_table_as_dict(tablename).values():

            if _object[filter_key] == filter_value:
                filtered.append(_object)

        for selected in filtered:
            element = {}
            for key, value in selected.items():
                element[key] = value

            order = {}
            order_position = 0
            for field in fields:
                order[order_position] = field
                order_position += 1

            sorted_fields = []
            for key, value in order.items():
                sorted_fields.append((value, element[value]))

            element = []
            for item in sorted_fields:
                item = item[1]
                element.append(item)

            all.append(tuple(element))
        return all

def connect(database):
    return Connection(database)


def console(database):
    con = connect(database)
    while True:
        query = raw_input('MyDb#: ')
        try:
            for item in con.execute(query):
                print ", ".join(item)
        except:
            pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('database')
    args = parser.parse_args()
    console(args.database)