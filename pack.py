#!/usr/local/env python
#! _*_ coding: utf-8 _*_
import argparse
from pkgutil import *
from fileutil import *
from netutil import *
__author__="quan.li"

conf  =  {}

def run():
    utoken = get_token(conf['user'],conf['passwd'])
    edition_wapper = fetch_edition_wapper(utoken,conf['editions'])
    compile_wapper = compile_edition_wapper(utoken,conf)
    wait_wapper = wait_complete_wapper(conf['user'],utoken)
    begin = 0 if not conf.has_key('from_pkg') else get_index(conf['from_pkg'],conf)
    end = len(conf['modules']) if not conf.has_key('to_pkg') else get_index(conf['to_pkg'],conf) + 1
    if begin > end:
        raise ValueError("起止包配置错误,end>begin")
    for index in range(begin,end):
        wait_wapper(map(compile_wapper,map(edition_wapper,conf['modules'][index])))

def load_conf():
    args = get_args()
    file_conf = load_conf_from_file(args.config)
    try:
        conf['from_pkg'] = args.from_pkg if args.from_pkg else file_conf['from_pkg'] if file_conf.has_key('from_pkg') else None
        conf['to_pkg'] = args.to_pkg if args.to_pkg else file_conf['to_pkg'] if file_conf.has_key('to_pkg') else None
        conf['user'] = args.user if args.user else file_conf['user']
        conf['passwd'] = args.passwd if args.passwd else file_conf['passwd']
        conf['editions'] = args.editions if args.editions else file_conf['editions'] if file_conf.has_key('editions') else None
        conf['progress'] = args.progress if args.progress is not None else file_conf['progress'] if file_conf.has_key('progress') else False
        conf['modules'] = file_conf['modules']
    except KeyError,e:
        raise ValueError("至少指定命令行或文件其中一种配置")

def get_args():
    parser  =  argparse.ArgumentParser(prog = "velapack",description = '''
    不需要点击，不需要等待，高度灵活可配置的
    vela自动打包，
    命令行参数会覆盖配置文件中相应参数，
    默认配置文件config.json，
    可以使用-c指定配置文件以应对多个项目的情况。
    详情见readme.txt
    ''') 
    parser.add_argument("-f","--from",dest = "from_pkg",help = "从哪个包开始")
    parser.add_argument("-t","--to",dest = "to_pkg",help = "到哪个包结束")
    parser.add_argument("-u","--user",help = "域账号用户名")
    parser.add_argument("-p","--passwd",help = "域账号密码")
    parser.add_argument("-e","--editions",help = "打包版本")
    parser.add_argument("-g","--progress",action = 'store_const',const=True,help = "是否推送打包进度，默认不推送")
    parser.add_argument("-c","--config",help = "配置文件路径",default = "config.json")
    return parser.parse_args()

if __name__  ==  "__main__":
    load_conf()
    run()
    push_alert(conf['user'],'打包完成')
