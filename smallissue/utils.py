from django.db.models import Model


def isAscii(s):
  return s.isascii()


def get_or_none_if_pk_is_none(model: Model, pk):
    if pk is None:
        return None

    return model.objects.get(pk=pk)


from pydoc import locate

def get_classes_from_string(string_list):
    class_list = []
    for class_string in string_list:
        class_list.append(locate(class_string))
    class_list.reverse()
    return class_list
