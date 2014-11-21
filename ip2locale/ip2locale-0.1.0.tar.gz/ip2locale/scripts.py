# -*- coding: utf-8 -*-


from ip2locale.Provider.taobao import TaoBaoProvider

def get_ip2locale(ip):
    ret = []
    providers = [
        TaoBaoProvider,
    ]
    for each_provider in providers:
        ret.append(
            each_provider().query(ip)
        )
    return ret
