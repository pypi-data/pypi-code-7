import os.path as p
import os, sys
from pyPdf import PdfFileReader
import shutil
import re
#from Config import *
from yesno import query_yes_no

#######
#Set the paths in the Paths class!!
#
# regex tv: http://regex101.com/r/bI8vC1/6
# regex movie: http://regex101.com/r/tJ1dO0/6
# trackt: http://pytrakt.readthedocs.org/en/latest/index.html
# tvdb: https://github.com/dbr/tvdb_api
#######

def ext(st):
    return p.splitext(st)[1][1:]

class Media(object):
    def __init__(self, path):
        path = p.abspath(path)
        if not p.exists(path):
            raise Exception("File not exists")
        self.path = path
        self.original = path
        self.store_pos = None
    
    @property
    def newpath(self):
        if self.store_pos is None:
            self.set_newpath()
        return self.store_pos


    def set_newpath(self):
        if self.__class__ == Media:
            self.store_pos = Paths.storepath() + "unknown/" + self.name
        else:
            self.store_pos = Paths.storepath() + MediaType.media[self.__class__.__name__]["storepath"] + self.name
    

    @property
    def name(self):
        return p.basename(self.path)

    @property
    def position(self):
        return p.dirname(self.path)

    @property
    def orig_name(self):
        return p.basename(self.original)

    @property
    def orig_position(self):
        return p.dirname(self.original)

    @property
    def store_position(self):
        return p.dirname(self.newpath)

    @property
    def store_name(self):
        return p.basename(self.newpath)


    @classmethod
    def create(cls, path):
        return cls(path)

    def info(self):
        if self.__class__ == Media:
            return
        if p.isfile(self.newpath):
            print "\n" + self.newpath + " already exists."
            return
        print "\n--->" + self.store_name + ":"
        print self.original
        print self.newpath

    def store(self):
        if self.__class__ == Media:
            return
        if p.isfile(self.newpath):
            #print "\n" + self.newpath + " already exists."
            return
        Paths.ensure_dir(p.dirname(self.store_pos))
        shutil.move(self.path, self.store_pos)
        self.path = self.store_pos
        try:
            tr = self.orig_position
            for i in range(100):
                os.rmdir(tr)#usare rmdirs, ma bisogna utilizzare il comando os.chdir()
                tr = p.dirname(tr)
            print self.orig_position + "(folder deleted)"
        except OSError as ex:
            pass

class Video(Media):
    def __init__(self, path):
        super(Video, self).__init__(path)

    @classmethod
    def create(cls, path):
        titles = TvSeries.regexp.search(p.basename(path))
        if titles:
            return TvSeries(path, titles.groups())
        else:
            titles = Movie.regexp.search(p.basename(path))
            if titles:
                return Movie(path, titles.groups())
            else:
                return Video(path)

class TvSeries(Video):
    
    regexp = re.compile(r"^(.+?)[-. ]{0,3}s?(\d?\d)[ex](\d?\d)[-. ]{0,3}(.*?)(?:[-. ](?=pulcione|eng|ita|\w+Mux|\w+[-.]?dl|\d+p|XviD|NovaRip).+)?\.([\w]{2,3})$", re.I | re.M)

    def __init__(self, path, sd):
        self.series = sd[0].replace('.', ' ')
        if len(sd[1]) == 1:
            self.season = "0" + sd[1]
        else:
            self.season = sd[1]
        if len(sd[2]) == 1:
            self.episode = "0" + sd[2]
        else:
            self.episode = sd[2]
        self.episode = sd[2]
        self.title = sd[3].replace('.', ' ')
        super(TvSeries, self).__init__(path)

    def set_newpath(self):
        sk="Serie TV/&s/ST &sea/&s &seax&e &t." + ext(self.name) #pattern of the save location in storepath
        sk = sk.replace("&sea", self.season).replace("&s", self.series).replace("&e", self.episode).replace("&t", self.title)
        self.store_pos = Paths.storepath() + sk

class Movie(Video):
    #import tmdb
    #tmdb.configure(tmdb_key)
    
    regexp = re.compile(r"^(?!\d\d?[ex]\d\d?)(?:\[(?:[-\w\s]+)*\] )?(.*?)[-_. ]?(?:[\{\(\[]?(?:dvdrip|[-._\b]ita|[-._\b]eng|xvid| cd\d|dvdscr|\w{1,5}rip|divx|\d+p|(\d{4})).*?)?\.([\w]{2,3})$", re.I | re.M)

    def __init__(self, path, sd):
        if sd[1] is not None:
            self.year = " (" + sd[1] + ")"
        else:
            self.year = ""
        self.title = sd[0]+self.year
        self.title = self.title.replace('.', ' ') + "." + sd[2]
        super(Movie, self).__init__(path)

    def set_newpath(self):
        sk="Film/" + self.title
        self.store_pos = Paths.storepath() + sk
        

class Document(Media):
    def __init__(self, path):
       super(Document, self).__init__(path)
    

    def set_newpath(self):
        titolo = '/Title'
        try:
            pdf_toread = PdfFileReader(file(self.path, "rb"))
            pdf_info = pdf_toread.getDocumentInfo()
            if len(pdf_info[titolo]) < 2:
                raise Exception()
            self.store_pos = Paths.storepath() + "libri/" + pdf_info[titolo].replace('/', '-') + ".pdf"    
            self.store_pos = self.store_pos.encode('utf8')
        except Exception:
            super(Document, self).set_newpath()

class Picture(Media):
    def __init__(self, path):
       super(Picture, self).__init__(path)

class Image(Media):
    def __init__(self, path):
       super(Image, self).__init__(path)

class Music(Media):
    def __init__(self, path):
       super(Music, self).__init__(path)

class Subtitles(Media):
    def __init__(self, path):
       super(Subtitles, self).__init__(path)

class Archives(Media):
    def __init__(self, path):
       super(Archives, self).__init__(path)

class Ignore(Media):
    def __init__(self, path):
        super(Ignore, self).__init__(path)

    def set_newpath(self):
        self.store_pos = self.orig_position
        
    def store(self):
        pass

class Draft(Media):
    def __init__(self, path):
       super(Draft, self).__init__(path)

class Comic(Media):
    def __init__(self, path):
       super(Comic, self).__init__(path)


class MediaFactory(object):
    elem=[]  

    @staticmethod
    def scan():
        files = []
        for pa in Paths.rootpath():
            files.extend([p.join(dp, f) for dp, dn, filenames in os.walk(pa) for f in filenames])
        return files


    @staticmethod
    def createMedia(path):
        #import pdb; pdb.set_trace()
        exts = ext(path).lower()
        for mt in MediaType.media.values():
            if exts in mt['ext']:
                return mt['class'].create(path)
        return Media(path)

    @staticmethod
    def createObjects(print_info=True):
        s_ign = ['^'+Paths.storepath()+"*", "*part$", "*.temp", "*.mobi", "*.DS_Store"]
        ignores = re.compile('|'.join(s_ign).replace('.', '\.').replace('*', '.*'))
        for i in MediaFactory.scan():
            if ignores.match(i):
                continue
            h=MediaFactory.createMedia(i)
            MediaFactory.elem.append(h)
            if print_info:
                h.info()

    @staticmethod
    def moveAll():
        for i in MediaFactory.elem:
            i.store()
    
    @staticmethod
    def printInfo():
        for i in MediaFactory.elem:
            i.info()
    
    @staticmethod
    def sortAll():
        MediaFactory.createObjects()

        if query_yes_no("\n---!!!---\nLeggere attentamente le righe precedenti! Procedere allo spostamento?", "no"):
            MediaFactory.moveAll()
            print "%d elementi spostati." % len(MediaFactory.elem)
        else:
            print "Nessun elemento e' stato spostato."
            

    @staticmethod
    def sortUnknown():
        for i in [os.path.join(dp, f) for dp, dn, filenames in os.walk(Paths.storepath() + "unknown/") for f in filenames]:
            h=MediaFactory.createMedia(i)
            h.info()
    
    @staticmethod
    def resort():
        for i in [os.path.join(dp, f) for dp, dn, filenames in os.walk(Paths.storepath()) for f in filenames]:
            h=MediaFactory.createMedia(i)
            h.info()


class Paths(object):
    __storepath = ''
    __rootpath = []
    
    @staticmethod
    def storepath():
        return Paths.__storepath

    @staticmethod
    def rootpath():
        return Paths.__rootpath

    @staticmethod
    def addRoot(paths):
        for path in paths:
            if p.isdir(path):
                if not path[-1] == '/':
                    path=path+'/'
                Paths.__rootpath.append(p.expanduser(path))
            else:
                raise IOError('Cartella non esistente %s' % path)

    @staticmethod
    def setStore(path):
        if p.isdir(path):
            if not path[-1] == '/':
                    path=path+'/'
            Paths.__storepath=p.expanduser(path)
        else:
            raise IOError('Cartella non esistente %s' % path)

            
        
    @staticmethod
    def ensure_dir(directory):
        if not p.exists(directory):
            os.makedirs(directory)
        return directory


class MediaType(object):
    media = {
            "Video" : {"ext": ["flv", "avi", "mkv", "mp4", 'srt'], "class": Video, "storepath": "Video/"},
            "Document" : {"ext": ["pdf", "chm", "epub"], "class": Document, "storepath": "Documenti/"},
            "Image" : {"ext": ["dmg", "iso", "mdf"], "class": Image,  "storepath": "Immagini disco/"},
            "Picture" : {"ext": ["jpg", "png", "gif", "jpeg"], "class": Picture,  "storepath": "Foto/"},
            "Music" : {"ext": ["mp3", "flac"], "class": Music,  "storepath": "Musica/"},
            #"Subtitles": {"ext": ["srt"], "class": Video, "storepath": "Video/"},
            "Archives": {"ext": ["7z", "zip", "rar"], "class": Archives, "storepath": "Archivi/"},
            "Ignore": {"ext": ["utpart", "DS_Store", ""], "class": Ignore, "storepath": "ignorati/"},
            "Draft": {"ext": ["nfo", "txt", "diz"], "class": Draft, "storepath": "monnezza/"},
            "Comic": {"ext": ["cbr", "cbz"], "class": Comic, "storepath": "Fumetti/"}
            }


medias = [Media, Video, Image, Picture, TvSeries, Archives, Document, Ignore, Draft, Comic, Music]


if __name__ == "__main__":
    sort(sys.argv)

def sort():
    argv= sys.argv
    #Config.loadConfig()
    if len(argv) < 2:
        print "Utilizzo: [nome cartella di origine]* nome cartella di destinazione"
        exit()
    
    if len(argv) == 2:
        paths = ['.']
    else:
        paths = argv[1:-1]
    
    
    Paths.addRoot(paths)
    Paths.setStore(argv[-1])
    MediaFactory.sortAll()