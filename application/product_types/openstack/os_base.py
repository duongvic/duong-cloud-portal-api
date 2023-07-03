#
# Copyright (c) 2020 FTI-CAS
#

import munch

from foxcloud import client as fox_client


DEFAULT_SORT_BY = (('updated_at', 'asc'), ('created_at', 'asc'))


class OSBaseMixin(object):

    def __init__(self, cluster, os_config=None, engine='console', services=None, **kwargs):
        self.cluster = cluster
        self.os_config = os_config
        params = {
            'os_auth': os_config['auth'],
            **kwargs
        }
        self.client = fox_client.Client(version='1', engine=engine, services=services, **params)

    def ok(self, data):
        return None, data

    def fail(self, error):
        return error, None

    def parse(self, obj, fields=None, extra_fields=None, extra_field_getter=None, **paging):
        if isinstance(obj, list):
            objects = [self.to_dict(o) for o in obj]
            if 'page_size' in paging:
                page_data = self.paginate(objects, **paging)
                objects = page_data['data']
            else:
                page_data = None

            objects_ = []
            for o in objects:
                err, item = self.parse_i(o, fields=fields, extra_fields=extra_fields,
                                         extra_field_getter=extra_field_getter)
                if err:
                    return self.fail(err)
                objects_.append(item)

            if page_data:
                page_data['data'] = objects_
                return None, page_data
            else:
                return None, objects_

        return self.parse_i(obj, fields=fields, extra_fields=extra_fields,
                            extra_field_getter=extra_field_getter)

    def parse_i(self, obj, fields=None, extra_fields=None, extra_field_getter=None):
        obj_dict = self.to_dict(obj)
        if not obj_dict:
            return None, obj

        ret = obj_dict
        if extra_fields and extra_field_getter:
            for f in extra_fields:
                err, data = extra_field_getter(obj_dict, f)
                if err:
                    return self.fail(err)
                ret[f] = data

        if fields:
            if extra_fields:
                fields = fields + extra_fields
            ret = self.filter_fields(ret, fields)

        return None, ret

    def to_dict(self, obj):
        """
        Convert obj to dict.
        :param obj:
        :return:
        """
        if not obj:
            return obj

        if isinstance(obj, dict):
            return obj
        else:
            obj_dict = None
            if isinstance(obj, munch.Munch):
                obj_dict = obj.toDict()
            else:
                to_dict = getattr(obj, 'to_dict', None)
                if to_dict:  # TODO: Check type if function
                    obj_dict = obj.to_dict()

            return obj_dict if obj_dict is not None else obj

    def paginate(self, objects, page, page_size, sort_by=None, **kw):
        """
        Paginate data.
        :param objects:
        :param page:
        :param page_size:
        :param sort_by:
        :return:
        """
        # Python sorted is stable sort, so we can call it multiple times
        # to sort by multiple fields. Performance may be an issue.
        # See: https://stackoverflow.com/questions/5212870/sorting-a-python-list-by-two-fields

        if page_size is None:
            return objects

        if sort_by is None:
            sort_by = DEFAULT_SORT_BY

        for sort in sort_by:
            reverse = sort[1] == 'desc'
            objects = sorted(objects, key=lambda x: x.get(sort[0], 0), reverse=reverse)

        count = len(objects)
        page = page or 1
        start = min((page - 1) * page_size, count)
        end = min(start + page_size, count)
        data = objects[start:end] if start < end else []
        return {
            'data': data,
            'has_more': end < count,
            'next_page': page + 1 if end < count else None,
            'prev_page': page - 1 if page > 1 else None,
        }

    def filter_fields(self, objects, fields):
        """
        Filter fields for objects.
        :param objects:
        :param fields:
        :return:
        """
        if fields is None:
            return objects

        if isinstance(objects, dict):
            result = {}
            for f in fields:
                result[f] = objects.get(f)
        else:
            result = []
            for obj in objects:
                obj_data = {}
                for f in fields:
                    obj_data[f] = obj.get(f)
                result.append(obj_data)

        return result
