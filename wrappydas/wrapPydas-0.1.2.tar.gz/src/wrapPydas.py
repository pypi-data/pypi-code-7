import pydas
import os
import shutil
class wrapPydas(object):
    def __init__(self,email,token=None,url=None):
        self.__assetroot = "/usr/local/src/Midas3/data/assetstore/"
        self.email=email
        self.token = pydas.login(email,url=url,api_key=token)
        self.url = url
        self.createDriver()
        user = self.driver.get_user_by_email(self.email)
        self.writeRoot = os.path.join("/","tmp",user['uuid'])
        if( not os.path.exists(self.writeRoot) ):
            os.mkdir(self.writeRoot)
    def cleanUp(self):
        shutil.rmtree(self.writeRoot)
    def setAssetRoot(self,root):
        self.__assetroot = root
    def createDriver(self):
        self.driver = pydas.drivers.CoreDriver(url=self.url)
    def getFileName(self,community,directoryPath,fname):
        """
        community: name of the Midas community
        directoryPath: folder path separated with "/"
        fname: name of file on disk
        """
        self.community = self.driver.get_community_by_name(community,token=self.token)
        self.community_id = self.community['folder_id']
        self.folders = list(os.path.split(directoryPath))[::-1]
        self.item = self.findItemInPath(self.community_id,self.folders[:],fname)
        bs = self.__getBitstream(self.item['item_id'])
        bs_loc,checksum = self.__getBitstreamLocation(bs)
        readable_file = self.__createReadableFile(bs_loc,checksum,fname)
        return readable_file

    def findItemInCommunity(self):
        pass
    def findItemInPath(self,cid,folders,itemName):
        children = self.driver.folder_children(self.token,cid)
        if(not children ):
            return {}
        if( children['items'] ):
            for i in children['items']:
                if( i['name'] == itemName ):
                    return {'item_id':i['item_id'],'folder_id':cid}
        if( not folders ):
            return {}
        newFolder = folders.pop()

        if( children['folders'] ):
            for f in children['folders']:
                if( f['name'] == newFolder ):
                    return self.findItemInPath(f['folder_id'],folders,itemName)
        return {}
    def __getBitstream(self,item_id,revision=0):
        item = self.driver.item_get(self.token,item_id)
        rev = item['revisions'][revision]
        bitstreams = rev['bitstreams']
# for now just take first bitstreams
        bs = bitstreams[0]
        return bs
    def __getBitstreamLocation(self,bs):
        checksum = bs['checksum']
        d0 = checksum[0:2]
        d1 = checksum[2:4]
        fileLoc = os.path.join(self.__assetroot,d0,d1,checksum)
        return fileLoc,checksum
    def __createReadableFile(self,fileLoc,checksum,fname):
        fname_full = os.path.join(self.writeRoot,checksum+fname)
        if( not os.path.lexists(fname_full) ):
            os.symlink(fileLoc,fname_full)
        return fname_full
    def uploadDerivedFile(self,src='',dest='',description='',metadatapairs=None,privacy="Private"):
        """Upload a derived file to the parent directory."""
        if( metadatapairs == None ):
            metadatapairs = []
        if( dest == '' ):
            fparts = os.path.split(src)
            dest = fparts[1]
        newitem = self.driver.create_item(self.token,dest,
                                 self.item["folder_id"],
                                 description=description,
                                 privacy=privacy)
        uploadtoken = self.driver.generate_upload_token(self.token,
                          newitem['item_id'],
                          dest)
        self.upload_item = self.driver.perform_upload(uploadtoken,src,
                folderid = self.item['folder_id'])
        for meta in metadatapairs:
            self.driver.set_item_metadata(self.token,
                                          newitem['item_id'],
                                          meta[0],meta[1])











