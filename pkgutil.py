#!/usr/local/env python
#! _*_ coding: utf-8 _*_
from netutil import *
import time
__author__="quan.li"

def max_edition(editions):
    '''
    在未指定版本的时候获取最新版本号
    '''
    editions.sort(key=lambda x:tuple(int(v) for v in x['version'].split(".")))
    return editions[-1]["id"]

def fetch_edition_wapper(token,edition=""):
    '''
    获取一个打包的版本号
    '''
    def fetch_edition(module):
        editions = get_editions(module['module_id'],token)
        if module.has_key('edition'):
            for e in editions:
                if e['version']==module['edition']:
                    return {"module":module,"edition":e['id']}
        elif edition:
            for e in editions:
                if e['version']==edition:
                    return {"module":module,"edition":e['id']}
        else:
            return {"module":module,"edition":max_edition(editions)}
    return fetch_edition


def wait_complete_wapper(user,token):
    def wait_complete(tasks):
        for task in tasks:
            while True:
                progress = fetch_progress(task['module'],task['complite'],token)
                if progress['status'] == '编译中...':
                    time.sleep(2)
                elif progress['status'] == '编译失败':
                    if progress['info'] == '等待ci返回':
                        push_alert(user,'未捕获异常，移步vela：http://vela.corp.elong.com')
                        pass
                    else:
                        err_info = '打包失败，详情链接：' + progress['info']+'\n'
                        err_info += fetch_errors(progress['info'])
                        push_alert(user,err_info)
                    raise ValueError("打包失败")
                    break
                elif progress['status'] == '编译成功':
                    break
    return wait_complete


def get_index(module_name,conf):
    '''
    获取打包范围
    '''
    index=0
    for a in conf['modules']:
        for b in a:
            if b['module'] == module_name:
                return index
        index += 1
