import requests
import time

LINODE_MGMT_URL = "https://api.linode.com/"


class LinodeException(Exception):
    def __init__(self, message):
        super(LinodeException, self).__init__(message)


class LinodeApi(object):
    """api for linode"""
    def __init__(self, key):
        self.linode_api_key = key
        
    def call_api(self, action, params):
        def call_api_internal():
            params.update(dict(
                api_key = self.linode_api_key,
                api_action = action,
                ))
            r = requests.get(
                LINODE_MGMT_URL,
                params = params,
                timeout = 60,
                )
            try:
                rdict = r.json()
                rerrors = rdict["ERRORARRAY"]
                if len(rerrors) > 0:
                    raise Exception("Linode API server returned error: {}".format(rerrors[0]["ERRORMESSAGE"]))
                return rdict
            except ValueError:
                raise LinodeException("Linode API server response: {}".format(r.text))

        upload_exception = None
        for _ in range(3):
            try:
                results = call_api_internal()
                return results
            except Exception as e:
                upload_exception = e
                time.sleep(7)
                continue
        if upload_exception is not None:
            raise upload_exception


    def get_domainid(self, domainname):
        domains = self.call_api("domain.list", {})["DATA"]
        for domain in domains:
            if domain["DOMAIN"] == domainname:
                return domain["DOMAINID"]
        raise Exception("Linode domain `{}` not found".format(domainname))


    def create_cname(self, fullname, target):
        resourcename, domainname = fullname.split(".", 1)
        domainid = self.get_domainid(domainname)
        self.call_api(
            "domain.resource.create", 
            dict(
                domainid = domainid,
                type = "CNAME",
                name = resourcename,
                target = target,
                ),
            )


    def create_a(self, fullname, target):
        resourcename, domainname = fullname.split(".", 1)
        domainid = self.get_domainid(domainname)
        self.call_api(
            "domain.resource.create", 
            dict(
                domainid = domainid,
                type = "A",
                name = resourcename,
                target = target,
                ),
            )


    def get_domainid_resourceid(self, fullname):
        resourcename, domainname = fullname.split(".", 1)
        domainid = self.get_domainid(domainname)
        resources = self.call_api("domain.resource.list", dict(domainid=domainid))["DATA"]
        for resource in resources:
            if str(resource["NAME"]) == resourcename:
                return domainid, resource["RESOURCEID"]
        raise Exception("Linode domain resource `{}` not found".format(resourcename))


    def get_cname_target(self, fullname):
        domainid, resourceid = self.get_domainid_resourceid(fullname)
        data = self.call_api(
            "domain.resource.list", 
            dict(
                domainid = domainid,
                resourceid = resourceid,
                ),
            )["DATA"]
        if len(data) > 1:
            raise Exception("Linode API server returned more than one record for name `{}`".format(fullname))
        data = data[0]
        if data["TYPE"].lower() != "cname":
            raise Exception("Linode tells that `{}` is not a CNAME".format(fullname))
        return data["TARGET"]


    def update_cname(self, fullname, target):
        resourcename, domainname = fullname.split(".", 1)
        domainid, resourceid = self.get_domainid_resourceid(fullname)
        self.call_api(
            "domain.resource.update", 
            dict(
                domainid = domainid,
                resourceid = resourceid,
                target = target,
                ),
            )


    def update_or_create_cname(self, fullname, target):
        resourcename, domainname = fullname.split(".", 1)
        try:
            self.get_domainid_resourceid(fullname)
            self.update_cname(fullname, target)
        except Exception:
            self.create_cname(fullname, target)


    def delete_cname(self, fullname):
        # just check that fullname is a CNAME with get_cname_target
        self.get_cname_target(fullname)
        domainid, resourceid = self.get_domainid_resourceid(fullname)
        self.call_api(
            "domain.resource.delete",
            dict(
                domainid = domainid,
                resourceid = resourceid,
                ),
            )
