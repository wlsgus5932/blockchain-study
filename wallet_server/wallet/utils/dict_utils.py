import collections

def sorted_dict_by_key(unsorted_dict: dict):

#     return collections.OrderedDict(
#             sorted(unsorted_dict.items()), key=lambda keys: keys[0]
#     )
        return dict(sorted(unsorted_dict.items()))