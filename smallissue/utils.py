from django.db.models import Model


def isAscii(s):
  return s.isascii()


def get_or_none_if_pk_is_none(model: Model, pk):
    if pk is None:
        return None

    return model.objects.get(pk=pk)