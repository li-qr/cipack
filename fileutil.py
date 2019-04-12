#!/usr/local/env python
#! _*_ coding: utf-8 _*_
import json
__author__="quan.li"

def load_conf_from_file(path):
    '''
    从文件读取配置，文件路径可从命令-c指定。
    命令行配置高于文件配置。
    '''
    with open(path,"r") as f:
        try:
            return json.load(f,encoding='utf-8')
        except ValueError,e:
            raise ValueError("json读取出错，可能是格式不对")
