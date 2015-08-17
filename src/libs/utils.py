#!/usr/bin/env python
# -*- encoding: utf-8 -*-
try:
    import ujson as json
except:
    import json as json


__all__ = ['compose_ret', 'clean_bom']


def compose_ret(errno, data):
    return json.dumps({
        'errno': errno,
        'data': data,
    })


def clean_bom(ustr):
    ustr = ustr.replace(u'\ufeff', '')
    return ustr
