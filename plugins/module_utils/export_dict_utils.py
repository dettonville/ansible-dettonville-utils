# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import io
import csv
import sys
import traceback
import codecs
import logging

_LOGLEVEL_DEFAULT = "INFO"

logging.basicConfig(
    level=_LOGLEVEL_DEFAULT
)


def get_headers_and_fields(column_list):
    fieldnames = [column["name"] for column in column_list]
    headers = [column["header"] for column in column_list]

    # just in case the headers were not specified
    if not headers:
        headers = fieldnames

    return headers, fieldnames


# ref: https://stackoverflow.com/questions/9157314/how-do-i-write-data-into-csv-format-as-string-not-file
def write_csv_string(export_list, column_list):
    (headers, fieldnames) = get_headers_and_fields(column_list)

    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n', fieldnames=fieldnames, extrasaction='ignore')

    header_row_dict = dict(zip(fieldnames, headers))

    # print('header_row_dict: %s' % header_row_dict)

    writer.writerow(header_row_dict)
    writer.writerows(export_list)

    # for row in list_of_rows:
    #     row_output = [row[column.name] for column in column_list]
    #     writer.writerow(row_output)

    return output.getvalue()


# ref: https://docs.python.org/3/library/csv.html
# ref: https://realpython.com/python-csv/
# ref: https://www.geeksforgeeks.org/writing-csv-files-in-python/
def write_csv_file(module, output_file, export_list, column_list):
    (headers, fieldnames) = get_headers_and_fields(column_list)

    try:
        with open(output_file, mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, lineterminator='\n', fieldnames=fieldnames, extrasaction='ignore')

            header_row_dict = dict(zip(fieldnames, headers))

            # print('header_row_dict: %s' % header_row_dict)

            writer.writerow(header_row_dict)
            writer.writerows(export_list)

            # for row in list_of_rows:
            #     row_output = [row[column.name] for column in column_list]
            #     writer.writerow(row_output)

    except IOError:
        module.fail_json(msg="Unable to create file %s", traceback=traceback.format_exc())

    result = dict(
        changed=True,
        message="The csv file has been created successfully at {0}".format(output_file)
    )

    return result


# ref: https://cppsecrets.com/users/1102811497104117108109111104116975048484864103109971051084699111109/Convert-a-CSV-file-to-a-table-in-a-markdown-file.php # noqa: E501 url size exceeds 120
def write_markdown_string(export_list, column_list):
    # print('column_list: %s' % column_list)
    (headers, fieldnames) = get_headers_and_fields(column_list)

    md_string = "|"
    for header in headers:
        md_string += " " + header + " |"

    md_string += "\n|"
    for i in range(len(headers)):
        md_string += " --- |"

    md_string += "\n"
    for row in export_list:
        logging.debug('row = %s' % str(row))
        md_string += "|"
        for column in column_list:
            if column['name'] in row:
                column_value = row[column['name']]
            else:
                column_value = ''
            logging.debug('column_value = %s' % str(column_value))
            md_string += " " + str(column_value) + " |"
        md_string += "\n"

    return md_string


def write_markdown_file(module, output_file, export_list, column_list):
    md_string = write_markdown_string(export_list, column_list)

    try:
        file = codecs.open(output_file, "w", encoding="utf-8")
        if sys.version_info >= (3, 6):
            file.write(md_string)
        else:
            file.write(md_string.decode('utf-8'))

        file.close()

    except IOError:
        module.fail_json(msg="Unable to create file %s", traceback=traceback.format_exc())

    result = dict(
        changed=True,
        message="The markdown file has been created successfully at {0}".format(output_file)
    )

    return result
