import proxy
import os
import re
import json
import shutil
from django.http import HttpResponse


class FileProxyFactory(object):
    """
    Class FileProxyFactory

    """
    def getFileProxy(self, pobjService, prequest):
        """
        Recupere le file proxy selon l'operation.

        Args:
            pobjService: Object service
            prequest: la requete
        Returns:
            Un file proxy
        """
        objFileProxy = FileGetProxy(pobjService, prequest)
        if self.isDownload(prequest):
            objFileProxy = FileDownloadProxy(pobjService, prequest)
        elif self.isView(prequest):
            objFileProxy = FileViewProxy(pobjService, prequest)
        elif self.isUpload(prequest):
            objFileProxy = FileUploadProxy(pobjService, prequest)
        elif self.isNewDir(prequest):
            objFileProxy = FileNewDirProxy(pobjService, prequest)
        elif self.isDelete(prequest):
            objFileProxy = FileDeleteProxy(pobjService, prequest)

        return objFileProxy

    def isDownload(self, prequest):
        """
        Verifie si l'operation est un download

        Args:
            prequest: La requete
        Returns:
            bool: True si l'operation est un download
        """
        return True if prequest.REQUEST.get('cmd') == 'download' and prequest.REQUEST.get('path') != '' else False

    def isView(self, prequest):
        """
        Verifie si l'operation est une vue

        Args:
            prequest: La requete
        Returns:
            bool: True si l'operation est une vue
        """
        return True if prequest.REQUEST.get('cmd') == 'view' and prequest.REQUEST.get('path') != '' else False

    def isUpload(self, prequest):
        """
        Verifie si l'operation est un upload

        Args:
            prequest: La requete
        Returns:
            bool: True si l'operation est un upload
        """
        return True if prequest.REQUEST.get('cmd') == 'upload' and prequest.REQUEST.get('path') != '' and prequest.FILES.get('x-filename') != '' and prequest.REQUEST.get('dir') != '' else False

    def isNewDir(self, prequest):
        """
        Verifie si l'operation est une creation d'un nouveau dossier

        Args:
            prequest: La requete
        Returns:
            bool: True si l'operation est une creation d'un nouveau dossier
        """
        return True if prequest.REQUEST.get('cmd') == 'newdir' and prequest.REQUEST.get('dir') != '' else False

    def isDelete(self, prequest):
        """
        Verifie si l'operation est une suppression

        Args:
            prequest: La requete
        Returns:
            bool: True si l'operation est une suppression
        """
        return True if prequest.REQUEST.get('cmd') == 'delete' and prequest.REQUEST.get('path') != '' else False


class FileProxy(proxy.Proxy):
    """
    Class FileProxy

    """
    def __init__(self, pobjService, prequest):
        """
        Constructeur

        Args:
            pobjService: Object service
            prequest: La requete
        """
        super(FileProxy, self).__init__(pobjService, prequest)

    def getLayer(self):
        """
        Recupere une couche dans le path de la requete

        Returns:
            Le path vers la couche
            "" si null
        """
        if self.m_objRequest.REQUEST.get('path') != "":
            path = re.sub('/^root\/?/', '', self.m_objRequest.REQUEST.get('path'))
            return path.replace('\\', '/')
        else:
            return ''

    def getLayers(self):
        """
        Recupere les couches

        Returns:
            Un tableau de couches
        """
        objArrayLayers = []
        strLayer = self.getLayer()
        if strLayer is not "":
            objArrayLayers.append(strLayer)
        return objArrayLayers

    def validateLayersFromRequest(self, pobjService=None, pobjArrayResources=None, pobjArrayLayers=None):
        """
        Valide les couches de la requete

        Args:
            pobjService: Object service
            pobjArrayResources: Object resource
            pobjArrayLayers: Tableau de couches
        Raise:
            Exception: Not Authorized by Datastore layer
        """
        if pobjService is None:
            objService = self.m_objService
        else:
            objService = pobjService
        if pobjArrayResources is None:
            objArrayResources = self.m_objResource
        else:
            objArrayResources = pobjArrayResources
        if pobjArrayLayers is None:
            objArrayLayers = self.getLayers()
        else:
            objArrayLayers = pobjArrayLayers

        bAllAuthorized = True
        for strLayer in objArrayLayers:
            bIsAuthorized = False
            for objResource in self.m_objResource:
                objDatastore = objResource.datastores.filter(service=objService)
                if self.isAuthorizedLayer(objDatastore, strLayer):
                    bIsAuthorized = True
                    break
            if not bIsAuthorized:
                bAllAuthorized = False
                break
        if not bAllAuthorized:
            raise Exception('Not Authorized by Datastore layer')

    def isAuthorizedLayer(self, pobjDatastore, pstrLayer):
        """
        Valide si une couche est valide

        Args:
            pobjDatastore: Object datastore
            pstrLayer: couche
        Returns:
            bool: selon l'authorisation
        """
        objArrayDSLayers = pobjDatastore.values("layers")[0].get("layers")
        bAuthorized = False
        for strDSLayer in objArrayDSLayers:
            if strDSLayer[-1] == '/':
                strDSLayer = strDSLayer[0, -1]
            objArrayDSPath = strDSLayer.split('/')
            objArrayLayerPath = pstrLayer.split('/')
            iNumDSPathNode = objArrayDSPath.__len__()
            iNumLayerPathNode = objArrayLayerPath.__len__()
            iNumPathNode = min(iNumDSPathNode, iNumLayerPathNode)
            for iIter in (0, iNumLayerPathNode):
                if objArrayDSPath[iIter] != objArrayLayerPath[iIter]:
                    break
                if iIter+1 >= iNumDSPathNode:
                    bAuthorized = True
            if bAuthorized:
                break
        return bAuthorized


class FileTree(object):
    """
    Class FileTree

    """
    def __init__(self, pstrRootPath=""):
        """
        Constructeur

        Args:
            pstrRootPath: le path de base pour le listing
        """
        if pstrRootPath is not "" and os.path.isdir(pstrRootPath):
            self.setRootPath(pstrRootPath)

    def get(self, pstrFilePath, pobjArrayFileList=[], pobjArrayResources=[]):
        """
        Lit le contenu d'un file path return un JSON de celui-ci

        Args:
            pstrFilePath: Le path du fichier
            pobjArrayFileList: Liste de fichiers
            pobjArrayResources: Tableau de resources

        Returns:
            JSON
        """
        strFilePath = self.m_strRootPath+'/'+pstrFilePath
        if not self.m_strRootPath or not os.path.isdir(self.m_strRootPath) or os.path.isfile(strFilePath) or not os.path.isdir(strFilePath):
            return '[]'
        if pobjArrayFileList.__len__() <= 0:
            pobjArrayFileList = self.getFileList(strFilePath)
        objArrayDirectoryToJSON = []
        for strEntry in pobjArrayFileList:
            if strEntry[0, 1] is not '.':
                objArrayDirectoryToJSON = self.getFileJSON(strFilePath, strEntry, pobjArrayResources)
        return '['+objArrayDirectoryToJSON.join(',')+']'

    def download(self, pstrFilePath, pbForceDownload=True):
        """
        Lit le contenu d'un file path et le return au browser

        Args:
            pstrFilePath: le path du fichier
            pbForceDownload: Pour forcer le telechargement du fichier
        """
        responce = HttpResponse()
        strFilePath = self.m_strRootPath+'/'+pstrFilePath
        if not self.m_strRootPath or not os.path.isdir(self.m_strRootPath) or not os.path.isfile(strFilePath):
            return
        if pbForceDownload is not False:
            responce['Content-type'] = "application/force-download"
            responce['Content-disposition'] = "attachement; filename=\""+os.path.basename(strFilePath)+"\""
        else:
            strExt = strFilePath.lower().split('.')[-1]
            if strExt == "pdf":
                strCType = "application/pdf"
            elif strExt == "docx" or strExt == "doc":
                strCType = "application/msword"
            elif strExt == "xlsx" or strExt == "xls":
                strCType = "application/vnd.ms-excel"
            elif strExt == "pptx" or strExt == "ppt":
                strCType = "application/vnd.ms-powerpoint"
            elif strExt == "gif":
                strCType = "image/gif"
            elif strExt == "png":
                strCType = "image/png"
            elif strExt == "jpeg" or strExt == "jpg":
                strCType = "image/jpg"
            else:
                strCType = "application/force-download"
            responce['Content-type'] = strCType
            responce['Content-disposition'] = "inline; filename=\""+os.path.basename(strFilePath)+"\""
        responce['Content-Transfert-Encoding'] = "Binary"
        responce['Content-length'] = os.path.getsize(strFilePath)
        responce.write(open(strFilePath, 'r').read())
        return responce

    def getFileJSON(self, pstrPath, pstrFile, pobjArrayResources):
        """
        Recupere un fichier JSON

        Args:
            pstrPath: le path du fichier
            pstrFileL: Le nom du fichier
            pobjArrayResources: Object resource
        Returns:
            JSON
        """
        if pstrPath[-1] is not '/':
            pstrPath += '/'
        objFileDescription = {'text': pstrFile,
                              'disabled': False,
                              'leaf': False if os.path.isdir(pstrPath+pstrFile) else True,
                              'qtip': 'Size: '+os.path.getsize(pstrPath+pstrFile)+' bytes' if os.path.isfile(pstrPath+pstrFile) else ''}

        if os.path.isdir(pstrPath+pstrFile):
            objFileDescription['cls'] = 'folder'
        elif pstrFile.rfind('.'):
            objFileDescription['iconCls'] = 'file-'+pstrFile[pstrFile.rfind('.')+1].lower()

        if pobjArrayResources[pstrFile]:
            objFileDescription['osmresource'] = pobjArrayResources[pstrFile]

        return json.dumps(objFileDescription)

    def getFileList(self, pstrFilePath):
        """
        Recupere une liste de fichier

        Args:
            pstrFilePath: le path du fichier
        Returns:
            Un tableau
        """
        strFilePath = self.m_strRootPath+'/'+pstrFilePath
        objArrayFileList = []
        if not os.path.isdir(strFilePath):
            return objArrayFileList
        objDirectory = os.listdir(strFilePath)
        for strEntry in objDirectory:
            if strEntry[0, 1] != '.':
                objArrayFileList.append(strEntry)
        return objArrayFileList

    def getRootPath(self):
        """
        Recupere la racine du path

        Returns:
            String
        """
        return self.m_strRootPath

    def setRootPath(self, pstrRootPath):
        """
        Definie la racine du path

        Args:
            pstrRootPath: La racine a definir
        """
        if pstrRootPath[-1] is '/':
            pstrRootPath = pstrRootPath[0, -1]
        self.m_strRootPath = pstrRootPath

    def getUploadedItem(self, prequest):
        """
        Retourne l'element uploader

        Args:
            prequest: La requete
        Returns:
            L'element
        """
        return prequest.FILES.get('x-filename')

    def upload(self, pstrBasePath):
        """
        Upload un fichier utilisant l'element uploade

        Args:
            pstrBasePath: Le path vers le fichier a uploader
        Returns:
            String
            JSON
        """
        objResponse = False
        strBasePath = os.path.realpath(self.getRootPath()+'/'+pstrBasePath)
        if not self.m_strRootPath or not os.path.isdir(self.m_strRootPath) or not os.path.isdir(strBasePath):
            return
        objArrayUploadedItem = self.getUploadedItem()
        strFilePath = strBasePath+'/'+objArrayUploadedItem['name']
        if os.path.isfile(strFilePath):
            objResponse = {'success': False,
                           'errors': {'message': "File already exists"}}
        if objResponse is False and objArrayUploadedItem['error'] is not UPLOAD_ERR_OK:
            objResponse = {'success': False,
                           'errors': {'message': self.getFileUploadErrorMessage(objArrayUploadedItem['error'])}}
        if objResponse is False:
            bMoved = shutil.move(objArrayUploadedItem['tmp_name'], strFilePath)
            if bMoved:
                objResponse = {'success': True}
            else:
                objResponse = {'success': False,
                               'errors': {'message': 'Could not upload file'}}
        return json.dumps(objResponse)

    def createDirectory(self, pstrPath):
        """
        Cree un nouveau repertoire

        Args:
            pstrPath: Le path du repertoire a creer
        Returns:
            JSON
        """
        strPath = self.getRootPath()+'/'+pstrPath
        if os.mkdir(strPath):
            objResponse = {'success': True}
        else:
            objResponse = {'success': False,
                           'errors': {'message': 'Could not create directory'}}
        return json.dumps(objResponse)

    def getFileUploadErrorMessage(self, piErrorCode):
        """
        Retourne le message d'erreur utilisant le code d'erreur

        Args:
            piErrorCode: Le code d'erreur
        Returns:
            Le message d'erreur
        """
        strMessage = ''
        if piErrorCode is UPLOAD_ERR_INI_SIZE:
            strMessage = 'The uploaded file exceeds the upload_max_filesize directive in php.ini'
        elif piErrorCode is UPLOAD_ERR_FORM_SIZE:
            strMessage = 'The uploaded file exceeds the MAX_FILE_SIZE directive that was specified in the HTML form'
        elif piErrorCode is UPLOAD_ERR_PARTIAL:
            strMessage = 'The uploaded file was only partially uploaded'
        elif piErrorCode is UPLOAD_ERR_NO_FILE:
            strMessage = 'No file was uploaded'
        elif piErrorCode is UPLOAD_ERR_NO_TMP_DIR:
            strMessage = 'Missing a temporary folder'
        elif piErrorCode is UPLOAD_ERR_CANT_WRITE:
            strMessage = 'Failed to write file to disk'
        elif piErrorCode is UPLOAD_ERR_EXTENSION:
            strMessage = 'File upload stopped by extension'
        else:
            strMessage = 'Unknown upload error'
        return strMessage

    def delete(self, pstrFilePath):
        """
        Supprime un fichier

        Args:
            pstrFilePath: Le path vers le fichier a supprimer
        Returns:
            JSON
        """
        strRootPath = self.m_strRootPath
        strFilePath = self.getRootPath()+'/'+pstrFilePath

        if os.path.isfile(strFilePath):
            if os.remove(strFilePath):
                objResponse = {'success': True}
            else:
                objResponse = {'success': False,
                               'errors': {'message': 'Could not delete file'}}
        elif os.path.isdir(strFilePath):
            if os.rmdir(strFilePath):
                objResponse = {'success': True}
            else:
                objResponse = {'success': False,
                               'errors': {'message': 'Could not delete folder. Is it empty?'}}
        else:
            objResponse = {'success': False,
                           'errors': {'message': 'File or folder does not exists'}}
        return json.dumps(objResponse)


class FileGetProxy(FileProxy):
    """
    Class FileGetProxy quand la requete est un get

    """

    def getAction(self):
        return self.CRUD_READ

    def process(self):
        """
        Traite l'information a retourner

        Returns:
            HttpResponce
        """
        strFilePath = self.getLayer()
        objFileTree = FileTree(self.m_objService.source)
        return HttpResponse(objFileTree.get(strFilePath, self.m_objArrayAvailableLayers, self.m_objArrayAvailableResources))

    def getInlineLayers(self):
        """
        Retourne la liste des couches accedees par la requete

        Returns:
            Un tableau de couches
        """
        objArrayLayers = []
        strFilePath = self.getLayer()
        objFileTree = FileTree(self.m_objService.source)
        objArrayLayers = objFileTree.getFileList(strFilePath)
        return objArrayLayers

    def getResourcesFromRequest(self, pobjConfig, pobjRequest=None):
        """
        Valide si les resources sont accessible par la requete

        Args:
            pobjConfig: Object de configuration
            pobjReques: La requete optionnel
        Returns:
            Un tableau de resource
        """
        if pobjRequest:
            objRequest = pobjRequest
        else:
            objRequest = pobjConfig

        if objRequest.get('service_slug') is None:
            raise Exception("osmservice param is missing")

        objArrayResource = []
        if objRequest.get('resource_slug') is list:
            pass
        else:
            objArrayResource.append(Resource.objects.getResource(objRequest.get('resource_slug')))
        return objArrayResource

    def validateLayersFromRequest(self, pobjService=None, pobjArrayResources=None, pobjArrayLayers=None):
        """
        Valide si les couches sont accessible par le requete

        Args:
            pobjService: Object service optionnel
            pobjArrayResources: Object resource optionnel
            pobjArrayLayers: Tableau de couches optionnel
        Raise:
            Exception: Not Authorized by Datastore layer
        """
        if pobjService is None:
            objService = self.m_objService
        else:
            objService = pobjService

        if pobjArrayResources is None:
            objArrayResource = self.m_objResource
        else:
            objArrayResource = pobjArrayResources

        if pobjArrayLayers is None:
            objArraylayers = self.getLayers()
        else:
            objArraylayers = pobjArrayLayers
        strFilePath = self.getLayer()
        if strFilePath[-1] is not '/' and len(strFilePath) > 0:
            strFilePath += '/'

        bAllAuthorized = True
        for strLayer in objArraylayers:
            bIsAuthorized = False
            for objResource in self.m_objResource:
                objDatastore = objResource.datastores.filter(service=objService)
                if self.isAuthorizedLayer(objDatastore, strFilePath+strLayer):
                    self.m_objArrayAvailableLayers.append(strLayer)
                    self.m_objArrayAvailableResources[strLayer] = self.m_objResource.name
                    break

        if self.m_objArrayAvailableLayers.__len__() <= 0:
            raise Exception('Not Authorized by Datastore layer')


class FileDownloadProxy(FileProxy):
    """
    Class FileDownloadProxy quand la requete est un download

    """

    def getAction(self):
        return self.CRUD_READ

    def process(self):
        """
        Traite l'information a retourner

        """
        strFilePath = self.getLayer()
        objFileTree = FileTree(self.m_objService.source)
        return objFileTree.download(strFilePath)


class FileViewProxy(FileProxy):
    """
    Class FileViewProxy quand la requete est une vue

    """

    def getAction(self):
        return self.CRUD_READ

    def process(self):
        """
        Traite l'information a retourner

        """
        strFilePath = self.getLayer()
        objFileTree = FileTree(self.m_objService.source)
        objFileTree.download(strFilePath, False)


class FileUploadProxy(FileProxy):
    """
    Class FileUploadProxy quand la requete est un upload

    """

    def getAction(self):
        return self.CRUD_CREATE

    def process(self):
        """
        Traite l'information a retourner

        """
        strBasePath = self.getLayer()
        objFileTree = FileTree(self.m_objService.source)
        HttpResponse(objFileTree.upload(strBasePath))


class FileNewDirProxy(FileProxy):
    """
    Class FileNewDirProxy quand la requete est uen creation de dossier

    """

    def getAction(self):
        return self.CRUD_CREATE

    def process(self):
        """
        Traite l'information a retourner

        """
        strPath = self.getLayer()
        objFileTree = FileTree(self.m_objService.source)
        HttpResponse(objFileTree.createDirectory(strPath))

    def getLayer(self):
        """
        Recupere une couche

        Returns:
            Une couche
            '' si null
        """
        if self.m_objRequest.REQUEST.get('dir'):
            path = re.sub('/^root\/?/', '', self.m_objRequest.REQUEST.get('dir'))
            return path.replace('\\', '/')
        else:
            return ''


class FileDeleteProxy(FileProxy):
    """
    Class FileDeleteProxy quand la requete est une suppression

    """

    def getAction(self):
        return self.CRUD_DELETE

    def process(self):
        """
        Traite l'information a retourner

        """
        strFilePath = self.getLayer()
        objFileTree = FileTree(self.m_objService.source)
        HttpResponse(objFileTree.delete(strFilePath))









