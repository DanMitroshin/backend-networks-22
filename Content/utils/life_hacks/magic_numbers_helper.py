#!/usr/bin/env python
# coding: utf-8


# Функция обработки запроса пользователя для отправки в алгоритм
# return: 1. str of numbers if amount of numbers no more than 10
#         2. "-1" otherwise
def parse_request_to_str_of_numbers(user_str):
    try:
        if len(user_str) > 40:
            return "-1"
        answer = user_str.replace(' ', ',').replace('-', ',').replace('.', ',').split(',')
        def check_norm_symbols(mass):
            new_mass = []
            for elem in mass:
                if len(elem) == 0:
                    continue
                if elem == "января" or elem == "январь":
                    new_mass += ['1']
                elif elem == "февраля" or elem == "февраль":
                    new_mass += ['2']
                elif elem == "марта" or elem == "март":
                    new_mass += ['3']
                elif elem == "апреля" or elem == "апрель":
                    new_mass += ['4']
                elif elem == "мая" or elem == "май":
                    new_mass += ['5']
                elif elem == "июня" or elem == "июнь":
                    new_mass += ['6']
                elif elem == "июля" or elem == "июль":
                    new_mass += ['7']
                elif elem == "августа" or elem == "август":
                    new_mass += ['8']
                elif elem == "сентября" or elem == "сентябрь":
                    new_mass += ['9']
                elif elem == "октября" or elem == "октябрь":
                    new_mass += ['10']
                elif elem == "ноября" or elem == "ноябрь":
                    new_mass += ['11']
                elif elem == "декабря" or elem == "декабрь":
                    new_mass += ['12']
                else:
                    new_elem = ""
                    for i, e in enumerate(elem):
                        if e in "0123456789":
                            new_elem += e
                    if new_elem != "":
                        new_mass += [new_elem]
            return new_mass
        answer = check_norm_symbols(answer)
        ans = ""
        for a in answer:
            ans += a
        if len(ans) > 10:
            return "-1"
        if ans == '':
            return "-1"
        return ans
    except:
        return "-1"

### tests
#print(parse_request_to_str_of_numbers("uhuhuhy"))
#print(type(parse_request_to_str_of_numbers("13 ноября 1988 - 18")))



