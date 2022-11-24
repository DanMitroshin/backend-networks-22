class NullClass:
    pass

null = NullClass()


def aggregate(
    values,
    aggregate_func,
    aggregate_by,
    group_by=None,
    sort=True,
):
    if group_by is not None:
        # Values should be sorted by group_by field, if provided
        if sort:
            values.sort(key=lambda elem: elem[group_by])
        # Checking for incorrect inputs
        try:
            current_group = []
            current_group_value = values[0][group_by]
        except IndexError:
            return []
        except KeyError:
            raise KeyError('Group_by field is not present in values')
        # Aggregating by group
        result = []
        for value in values + [{group_by: null}]:
            if value[group_by] == current_group_value:
                current_group.append(value)
            else:
                result.append({
                    'value': aggregate(current_group, aggregate_func, aggregate_by),
                    'name': current_group_value,
                })
                current_group = [value]
                current_group_value = value[group_by]
        return result
    else:
        try:
            return aggregate_func([item[aggregate_by] for item in values])
        except KeyError:
            raise KeyError('Aggregate_by field is not present in values')


def popularity():
    return ...
