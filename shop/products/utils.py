from django.http import QueryDict
import json
import os
from rest_framework import parsers


def primary_image_upload_to(instance, filename, *args, **kwargs):
    return os.path.join(*[
        'products',
        instance.name,
        'primary_image',
        filename,
    ])


def products_image_upload_to(instance, filename, *args, **kwargs):
    return os.path.join(*[
        'products',
        instance.product.name,
        'more_images',
        filename,
    ])


def category_image_upload_to(instance, filename, *args, **kwargs):
    return os.path.join(*[
        'categories',
        instance.name,
        filename,
    ])


def offers_image_upload_to(instance, filename, *args, **kwargs):
    return os.path.join(*[
        'offers',
        instance.offer.name,
        filename,
    ])


class MultipartJsonParser(parsers.MultiPartParser):

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context
        )
        data = {}
        # print('IN-PARSER:', result.data)
        # data = json.loads(result.data["data"])
        # print({"products": data})

        # for case1 with nested serializers
        # parse each field with json
        print('*'*5, 'IN-PARSER', '*'*5)
        for key, value in result.data.items():
            print(type(value), value)
            if type(value) != str:
                data[key] = value
                continue
            if '{' in value or "[" in value:
                try:
                    # print(type(json.loads(value)), json.loads(value))
                    data[key] = json.loads(value)
                    # print()
                except ValueError:
                    data[key] = value
            else:
                data[key] = value

        qdict = QueryDict('', mutable=True)
        qdict.update(data)
        return parsers.DataAndFiles(qdict, result.files)
