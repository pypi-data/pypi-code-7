# encoding: utf-8

from edo_client import OcClient, WoClient

def get_wo_client(oc_api, client_id, client_secret, account, instance, username, password):
    # 连接应用服务器
    oc_client= OcClient(oc_api, client_id, client_secret,
            account = account)

    #  获取认证
    oc_client.auth_with_password(username=username,
            password=password, account=account)
    #  获取服务
    wo_instance = oc_client.account.get_instance(account=account,
            application='workonline', instance=instance)

    #  获取连接
    wo_client = WoClient(wo_instance['api_url'], client_id,
            client_secret, account=account, instance=instance)

    #  获取认证
    wo_client.auth_with_token(oc_client.access_token)
    return wo_client
