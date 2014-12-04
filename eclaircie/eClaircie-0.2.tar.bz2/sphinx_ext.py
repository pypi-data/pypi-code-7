import sys, os, os.path, locale, urllib, urllib.request, re, codecs
from datetime import date as Date

from docutils import nodes
from docutils.parsers.rst import Directive

from sphinx import addnodes
from sphinx.util.nodes import set_source_info
from sphinx.util.compat import Directive, make_admonition
from sphinx.environment import BuildEnvironment
from sphinx.util.nodes import clean_astext
from sphinx.util import copy_static_entry
from sphinx.util.osutil import SEP, os_path, relative_uri, ensuredir, movefile, ustrftime, copyfile

import sphinx.builders.html

import eclaircie, eclaircie.email_obfuscator

APP = None

def setup(app):
  global APP
  APP = app
  app.add_node(GalleryImageNode, html = (visit_gallery_image_html, depart_gallery_image_html))
  app.add_node(GalleryNode,      html = (visit_gallery_html,       depart_gallery_html))
  app.add_node(YoutubeNode,      html = (visit_youtube_html,       depart_youtube_html))
  app.add_node(AudioNode,        html = (visit_audio_html,         depart_audio_html))
  app.add_node(RedirectNode,     html = (visit_redirect_html,      depart_redirect_html))
  app.add_directive('gallery',  GalleryDirective)
  app.add_directive('youtube',  YoutubeDirective)
  app.add_directive('audio',    AudioDirective)
  app.add_directive('redirect', RedirectDirective)
  app.add_builder(EclaircieStandaloneHTMLBuilder)
  
  app.connect("builder-inited", on_builder_inited)
  app.connect("html-page-context", on_html_page_context)
  app.connect("html-collect-pages", on_html_collect_pages)
  app.connect("build-finished", on_build_finished)


class GalleryNode(nodes.General, nodes.Element): pass
class GalleryImageNode(nodes.image): pass

class GalleryDirective(Directive):
  has_content = True
  
  def run(self):
    images0 = (" ".join(self.content)).split()
    images = []
    for image0 in images0:
      filename = os.path.join(eclaircie.BLOG.blog_dir, "_images", image0)
      if os.path.isdir(filename):
        images.extend(sorted(os.path.join(image0, f)
                             for f in os.listdir(filename)
                             if (not f.startswith("miniature_")) and (f.lower().endswith(".png") or f.lower().endswith(".jpeg") or f.lower().endswith(".jpg") or f.lower().endswith(".svg") or f.lower().endswith(".gif"))))
      else:
        images.append(image0)
    r = []
    next_id = 0
    for image in images:
      if   image.startswith("/"):
        pass
      elif image.startswith("http://") or image.startswith("."):
        r.append(GalleryImageNode(gallery_id = next_id, uri = image, mini = next_id, big = next_id)); next_id += 1
      else:
        dirname = os.path.dirname(image)
        if dirname: dirname = "%s/" % dirname
        big  = "/_images/%s" % image
        mini = "/_images/%sminiature_%s" % (dirname, os.path.basename(image))
        
        if image.endswith(".svg"):
          r.append(GalleryImageNode(gallery_id = next_id, uri = big,  mini = next_id, big = next_id)); next_id += 1
        else:
          r.append(GalleryImageNode(gallery_id = next_id, uri = mini, mini = next_id,     big = next_id + 1)); next_id += 1
          r.append(GalleryImageNode(gallery_id = next_id, uri = big,  mini = next_id - 1, big = next_id)); next_id += 1
    node = GalleryNode()
    node.extend(r)
    return [node]
    
def visit_gallery_html(self, node):
  self.body.append(self.starttag(node, 'div', **{"class" : "gallery"}))
  id_2_node = [child for child in node.children]
  
  big_images = [image.attributes["uri"] for image in id_2_node if image.attributes["gallery_id"] == image.attributes["big"]]
  big_images = "[%s]" % ",".join("'%s'" % url for url in big_images)
  
  big_images = []
  for image in id_2_node:
    if image.attributes["gallery_id"] == image.attributes["big"]:
      big = image.attributes["uri"]
      if not(big .startswith("http://") or big .startswith(".") or big .startswith("/")): big  = big.replace("_images/", APP.builder.imgpath + "/")
      big_images.append("'%s'" % big)
  big_images = "[%s]" % ",".join(big_images)
      
  i = 0
  for image in id_2_node:
    if image.attributes["gallery_id"] == image.attributes["mini"]:
      mini = image.attributes["uri"]
      if not(mini.startswith("http://") or mini.startswith(".") or mini.startswith("/")): mini = mini.replace("_images/", APP.builder.imgpath + "/")
      if mini.endswith(".svg"):
        extra = ' style="height:auto; width:auto; max-width:200px; max-height:150px;"'
      else:
        extra = ""
      self.body.append("""<img class="gallery-img" src="%s" onClick="show_imageviewer(%s, %s);"%s/>\n""" % (mini, big_images, i, extra))
      i += 1

def depart_gallery_html(self, node):
  self.body.append('</div>')

def visit_gallery_image_html (self, node): pass
def depart_gallery_image_html(self, node): pass


class YoutubeNode(nodes.General, nodes.Element): pass

class YoutubeDirective(Directive):
  has_content = True
  
  def run(self):
    node = YoutubeNode()
    node.attributes["youtube_id"] = " ".join(self.content).strip()
    return [node]

def visit_youtube_html(self, node):
  youtube_id = node.attributes["youtube_id"]
  preview_filename = os.path.join(eclaircie.BLOG.blog_dir, "_images", "youtube_preview_%s.jpeg" % youtube_id)
  if not os.path.exists(preview_filename):
    s = urllib.request.urlopen("http://www.youtube.com/embed/%s" % youtube_id).read()
    s = s.decode("utf8")
    preview_url = re.findall('"iurlsd"\s*:\s*"(.*?)"', s)[0].replace("\\", "")
    s = urllib.request.urlopen(preview_url).read()
    open(preview_filename, "wb").write(s)
    
  self.body.append(self.starttag(node, 'div',
    style = """background-image: url("%s/youtube_preview_%s.jpeg");""" % (APP.builder.imgpath, youtube_id),
    onclick="""this.innerHTML="<iframe width='640' height='480' src='http://www.youtube.com/embed/%s?autoplay=1' frameborder='0' allowfullscreen='1'></iframe>";""" % youtube_id,
    **{"class" : "video"}))
  self.body.append(self.starttag(node, 'div', **{"class" : "video-read"}))
  self.body.append(' &gt; ')
  self.body.append('</div>')
  
def depart_youtube_html(self, node):
  self.body.append('</div>')


class AudioNode(nodes.General, nodes.Element): pass

class AudioDirective(Directive):
  has_content = True
  
  def run(self):
    node = AudioNode()
    node.attributes["filenames"] = [filename.strip() for filename in " ".join(self.content).split()]
    return [node]

EXT_2_MIME = { "ogg" : "audio/ogg", "mp3" : "audio/mpeg" }

def visit_audio_html(self, node):
  filenames = node.attributes["filenames"]
  
  self.body.append(self.starttag(node, 'audio', controls = "1"))
  for filename in filenames:
    self.body.append(self.starttag(node, 'source',
      src = "%s/%s" % (APP.builder.dlpath, filename),
      type = EXT_2_MIME[filename.rsplit(".")[-1].lower()]))
    self.body.append('</source>')
  self.body.append('Please update your browser for HTML5 audio support.')
  self.body.append('</audio>')
  
  for filename in filenames:
    self.body.append(self.starttag(node, 'p'))
    self.body.append(self.starttag(node, 'a', href = "%s/%s" % (APP.builder.dlpath, filename), **{"class" : "reference download internal"}))
    self.body.append(self.starttag(node, 'tt', **{"class" : "xref download docutils literal"}))
    self.body.append(self.starttag(node, 'span', **{"class" : "pre"}))
    self.body.append('%s</span></tt></a></p>' % filename)
  
def depart_audio_html(self, node): pass


class RedirectNode(nodes.General, nodes.Element): pass

class RedirectDirective(Directive):
  has_content = True
  
  def run(self):
    node = RedirectNode()
    node.attributes["redirect_url"] = " ".join(self.content).strip()
    return [node]

def visit_redirect_html(self, node):
  self.body.append(self.starttag(node, 'script'))
  self.body.append('window.location="%s";</script>' % node.attributes["redirect_url"])
  
def depart_redirect_html(self, node): pass


def init_env_globals(app):
  globals = app.builder.templates.environment.globals
  globals["ec_is_post"]    = ec_is_post
  globals["ec_toctree"]    = ec_toctree
  globals["ec_rellinks"]   = ec_rellinks
  globals["ec_lang_for"]   = ec_lang_for
  globals["ec_reparents"]  = ec_reparents
  globals["ec_email_link"] = eclaircie.email_obfuscator.email_link(eclaircie.BLOG.author_email, localurl = "file://%s" % eclaircie.BLOG.blog_dir, url = eclaircie.BLOG.url)

def on_builder_inited(app):
  init_env_globals(app)
  
  # Disable file copy, because Sphinx always copy all files, inclduing unchanged ones!
  app.builder.copy_download_files = lambda: None
  app.builder.copy_image_files    = lambda: None
  global USED_THEMES, DEFAULT_THEME
  USED_THEMES = {}
  DEFAULT_THEME = app.builder.config.html_theme
  

def on_env_updated(app, env):
  pass

def on_doctree_read(app, doctree):
  pass

def on_doctree_resolved(app, doctree, docname):
  pass

def is_post(docname):
  try:
    year, month, day, title = docname.rsplit("/", 1)[-1].split("_", 3)
    date = Date(int(year), int(month), int(day))
  except: return False
  return True
ec_is_post = is_post

def ec_toctree(docname):
  post = is_post(docname)
  if post: docname = "%s/index" % docname.rsplit("/", 1)[0]
  
  result = APP.env.get_toctree_for(docname, APP.builder, collapse = True, titles_only = True, includehidden = False)
  
  if result:
    for refnode in result.traverse(nodes.reference):
      if refnode["anchorname"]: # only keep the FIRST title of the page (1 page = 1 entry)
        refnode.replace_self([])
      elif post and (refnode['refuri'] == ""): # For post, the link in the TOC points to the parent category, not to the post itself
        refnode['refuri'] = "index_%s.html" % eclaircie.BLOG.lang.langs[0]
  return APP.builder.render_partial(result)['fragment']

def ec_lang_for(docname):
  l = [(lang.langs[0], lang.name) for lang in eclaircie.get_available_doc_langs(docname)]
  if len(l) <= 1: return []
  return l

def ec_reparents(docname, parents):
  if is_post(docname):
    parents = []
    parentdocs = docname.split("/")[:-1]
    for i in range(len(parentdocs)):
      title = clean_astext(APP.env.titles["/".join(parentdocs[:i + 1]) + "/index"])
      if len(eclaircie.LANGS) > 1:
        parents.append({"link" : ("../" * (len(parentdocs) - i - 1)) + "index_%s.html" % eclaircie.BLOG.lang.langs[0], "title" : title})
      else:
        parents.append({"link" : ("../" * (len(parentdocs) - i - 1)) + "index.html", "title" : title})
  return parents

def ec_rellinks(pagename, rellinks):
  docname     = pagename.rsplit("/", 1)[-1]
  doc_is_post = is_post(docname)
  rellinks2   = []
  previous    = None
  next        = None
  for rellink in rellinks: # For post, we need to reverse prev and next links -- index page must use the reverse order
    if   rellink[2] == "P":
      if doc_is_post: next     = (rellink[0], rellink[1], rellink[2], eclaircie.EC_TRANSLATIONS[eclaircie.BLOG.lang.langs[0], "older_posts"])
      else:           previous = (rellink[0], rellink[1], rellink[2], eclaircie.EC_TRANSLATIONS[eclaircie.BLOG.lang.langs[0], "newer_posts"])
    elif rellink[2] == "N":
      if doc_is_post: previous = (rellink[0], rellink[1], rellink[2], eclaircie.EC_TRANSLATIONS[eclaircie.BLOG.lang.langs[0], "newer_posts"])
      else:           next     = (rellink[0], rellink[1], rellink[2], eclaircie.EC_TRANSLATIONS[eclaircie.BLOG.lang.langs[0], "older_posts"])
    else: rellinks2.append(rellink)
  
  if previous:
    if doc_is_post:
      if is_post(previous[0].rsplit("/", 1)[-1]): rellinks2.insert(0, previous)
    else:
      if docname.startswith("ec_recent_posts"): rellinks2.insert(0, previous)
      
  rellinks2.append(("archives", "", "", "archives"))
  
  if next:
    if doc_is_post:
      rellinks2.append(next)
    else:
      if next[0].rsplit("/", 1)[-1].startswith("ec_recent_posts"): rellinks2.append(next)
    
  return rellinks2
  

USED_THEMES = {}
DEFAULT_THEME = ""
def on_html_page_context(app, pagename, templatename, context, doctree):
  new_theme = DEFAULT_THEME
  for category, theme in eclaircie.BLOG.ec_multiple_themes:
    if pagename.startswith(category):
      new_theme = theme
      break
      
  if "sourcename" in context: # Add language code in sourcename
    filename, ext = os.path.splitext(context["sourcename"])
    context["sourcename"] = "%s_%s%s" % (filename, eclaircie.BLOG.lang.langs[0], ext)

  USED_THEMES[app.builder.config.html_theme] = app.builder.theme
  if app.builder.config.html_theme != new_theme:
      app.builder.config.html_theme = new_theme
      app.builder.init_templates()
      context["style"] = app.builder.globalcontext["style"] = app.builder.theme.get_confstr('theme', 'stylesheet')
      init_env_globals(app) # Need to be re-inited

# Hack index_page to change source filenames

def _fix_filename(filename): return "%s_%s" % (filename, eclaircie.BLOG.lang.langs[0])
class LangSpecificIndexBuilder(sphinx.search.IndexBuilder):
  def prune(self, filenames):
    super().prune({ _fix_filename(filename) for filename in filenames })
  def feed(self, filename, title, doctree):
    super().feed(_fix_filename(filename), title, doctree)

def on_html_collect_pages(app):
  posts = [docname for docname in app.env.found_docs if eclaircie.is_post(docname)]
  posts.sort(key = lambda docname: os.path.basename(docname), reverse = 1)
  posts = posts[:eclaircie.BLOG.number_of_recent_post]
  
  locale.setlocale(locale.LC_ALL, "C") # For strftime(); RSS need dates in english :-(
  
  context = {
    "items"    : [],
    "title"    : app.config.project,
    "link"     : eclaircie.BLOG.url,
    "language" : eclaircie.BLOG.lang.langs[0],
  }
  
  for docname in posts:
    doctree = app.env.get_doctree(docname)
    description = clean_astext(doctree)
    description = description.split("\n", 4)[-1]
    description = "%s\n..." % description.strip()[:500]
    context["items"].append({
      "title": app.env.titles[docname].astext(),
      "link": "%s/%s_%s.html" % (eclaircie.BLOG.url, docname, eclaircie.BLOG.lang.langs[0]),
      "description": description,
      "categories": [os.path.dirname(docname)],
      "pubDate": eclaircie.is_post(docname).strftime(u"%a, %d %b %Y %H:%M:%S +0000"),
    })
  if context["items"]:
    context["pubDate"] = context["items"][0]["pubDate"]
    
  locale.setlocale(locale.LC_ALL, eclaircie.BLOG.lang.locale) # Reset locale
  
  yield ("news", context, "rss.html")


      
def on_build_finished(app, exception):
  if exception: return
  if not hasattr(APP.builder, "globalcontext"): return # Nothing built
  ctx = APP.builder.globalcontext.copy()
  ctx.update(APP.builder.indexer.context_for_searchtool())
  
  for theme in USED_THEMES.values():
    if theme is APP.builder.theme: continue # Already done by builder
    themeentries = [os.path.join(themepath, 'static')
                    for themepath in theme.get_dirchain()[::-1]]
    for entry in themeentries:
      copy_static_entry(entry, os.path.join(APP.builder.outdir, '_static'), APP.builder, ctx)
    



class EclaircieStandaloneHTMLBuilder(sphinx.builders.html.StandaloneHTMLBuilder):
    name = "ec_html"
    
    def handle_page(self, pagename, addctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        ctx = self.globalcontext.copy()
        # current_page_name is backwards compatibility
        ctx['pagename'] = ctx['current_page_name'] = pagename
        default_baseuri = self.get_target_uri(pagename)
        # in the singlehtml builder, default_baseuri still contains an #anchor
        # part, which relative_uri doesn't really like...
        default_baseuri = default_baseuri.rsplit('#', 1)[0]

        def pathto(otheruri, resource=False, baseuri=default_baseuri):
            if resource and '://' in otheruri:
                # allow non-local resources given by scheme
                return otheruri
            elif not resource:
                otheruri = self.get_target_uri(otheruri)
            uri = relative_uri(baseuri, otheruri) or '#'
            return uri
        ctx['pathto'] = pathto
        ctx['hasdoc'] = lambda name: name in self.env.all_docs
        if self.name != 'htmlhelp':
            ctx['encoding'] = encoding = self.config.html_output_encoding
        else:
            ctx['encoding'] = encoding = self.encoding
        ctx['toctree'] = lambda **kw: self._get_local_toctree(pagename, **kw)
        self.add_sidebars(pagename, ctx)
        ctx.update(addctx)

        self.app.emit('html-page-context', pagename, templatename,
                      ctx, event_arg)

        try:
            output = self.templates.render(templatename, ctx)
        except UnicodeError:
            self.warn("a Unicode error occurred when rendering the page %s. "
                      "Please make sure all config values that contain "
                      "non-ASCII content are Unicode strings." % pagename)
            return

        if not outfilename:
            outfilename = self.get_outfilename(pagename)
        # outfilename's path is in general different from self.outdir
        ensuredir(os.path.dirname(outfilename))
        try:
            s = codecs.encode(output, encoding, 'xmlcharrefreplace')
            eclaircie.write_file(outfilename, s)
              
            #f = codecs.open(outfilename, 'w', encoding, 'xmlcharrefreplace')
            #try:
            #    f.write(output)
            #finally:
            #    f.close()
        except (IOError, OSError) as err:
            self.warn("error writing file %s: %s" % (outfilename, err))
        if self.copysource and ctx.get('sourcename'):
            # copy the source file for the "show source" link
            source_name = os.path.join(self.outdir, '_sources',
                                    os_path(ctx['sourcename']))
            ensuredir(os.path.dirname(source_name))
            #copyfile(self.env.doc2path(pagename), source_name)
            s = open(self.env.doc2path(pagename), "rb").read()
            eclaircie.write_file(source_name, s)
            
            
    def load_indexer(self, docnames):
        self.indexer.__class__ = LangSpecificIndexBuilder
        return super().load_indexer(docnames)
