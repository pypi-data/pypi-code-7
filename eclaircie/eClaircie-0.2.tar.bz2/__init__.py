import sys, os, locale
import PIL, PIL.Image
from datetime import date as Date
from collections import defaultdict

from eclaircie.email_obfuscator import *

VERSION = "0.1"
EC_THEME_PATH = os.path.join(os.path.dirname(__file__), "themes")

def need_update(origs, deriveds):
  for i in range(len(deriveds)):
    if not os.path.lexists(deriveds[i]):
      deriveds[i] = "%s.empty" % os.path.splitext(deriveds[i])[0]
      if not os.path.lexists(deriveds[i]): return True
      
  orig_mtime    = max(os.path.getmtime(orig)    for orig    in origs if os.path.exists(orig))
  derived_mtime = min(os.path.getmtime(derived) for derived in deriveds)
  return orig_mtime > derived_mtime

def write_file(filename, s, lang = "--", touch = False):
  if isinstance(s, str): s = s.encode("utf8")
  if os.path.lexists(filename) and (len(s) == os.path.getsize(filename)):
    old_s = open(filename, "rb").read()
    if s == old_s:
      if touch:
        print("touch    %s" % filename)
        os.utime(filename)
        if BLOG and (filename.endswith(".rst") or filename.endswith(".inc")): BLOG.changed_rst_files.add(filename)
      return False

  print("write %s %s" % ("  " if (lang == "all") else lang, filename))
  open(filename, "wb").write(s)
  if BLOG and (filename.endswith(".rst") or filename.endswith(".inc")): BLOG.changed_rst_files.add(filename)
  return True

def reduce_image(filename, dest_filename, max_width = 200, max_height = 150, copy_if_already_small_enough = False):
  if need_update([filename], [dest_filename]):
    if not filename.endswith(".svg"):
      image = PIL.Image.open(filename)
      if (image.size[0] > max_width) or (image.size[1] > max_height):
        if image.size[0] * max_height > image.size[1] * max_width: image.thumbnail((max_width, int(image.size[1] * max_width / image.size[0])), 1)
        else:                                                      image.thumbnail((int(image.size[0] * max_height / image.size[1]), max_height), 1)
        print("create   %s" % dest_filename)
        image.save(dest_filename)
        return
        
    if copy_if_already_small_enough:
      print("create   %s" % dest_filename)
      data = open(filename, "rb").read()
      open(dest_filename, "wb").write(data)
      

class Doc(object):
  def __init__(self, blog, src_filename):
    self.blog           = blog
    self.src_filename   = src_filename
    self.categories     = []
    self.doc_name       = os.path.splitext(os.path.relpath(src_filename, blog.blog_dir))[0]
    self.filename       = os.path.join(blog.dirname, self.doc_name) + os.path.splitext(src_filename)[1]
    self.empty_filename = "%s.empty" % os.path.join(blog.dirname, self.doc_name)
    self.empty          = os.path.exists(self.empty_filename) and (os.path.getsize(self.empty_filename) == 0)
    self.build_result   = None
    blog.docs.append(self)

  def add_link(self, link_filename): raise ValueError("Symlink are supported only for posts.")
    
  def ready(self):
    if "/" in self.doc_name: self.categories = [self.blog.categories_dict[os.path.dirname(self.doc_name)]]
    else:                    self.categories = [self.blog.categories_dict[""]]
    
  def build(self, force = False):
    if not self.build_result is None: return self.build_result # For post in several categories
    if (not force) and self.is_up_to_date(): self.build_result = False; return False
    s, lang = self.build_str(self.get_source())
    self.save(s, lang)
    self.build_result = True; return True
    
  def is_up_to_date(self):
    #for changed_category in self.blog.changed_categories:
    #  if self.doc_name.startswith(changed_category): return False # Need to update because TOC has changed -- Sphinx does not do it ?!?!?
    return not need_update([self.src_filename], [self.filename])
    
  def get_source(self):
    print("read     %s" % self.src_filename)
    return open(self.src_filename).read()
    
  def build_str(self, s):
    lang_lines = []
    available_langs = set()
    for line in s.split("\n"):
      if line.startswith(".. lang::"):
        lang = line[len(".. lang::"):].strip()
        available_langs.add(lang)
        lang_lines.append((lang, []))
      else:
        if not lang_lines: lang_lines.append(("all", []))
        lang_lines[-1][1].append(line)
        
    available_langs.discard("all")
    if not available_langs: available_langs = set(LANGS.keys())
    l = [LANGS[lang] for lang in available_langs if lang in LANGS]
    l.sort(key = lambda x: x.priority)
    AVAILABLES_DOC_LANGS[self.doc_name] = l
    
    included_langs = self.blog.lang.langs
    for included_lang in included_langs:
      if included_lang in available_langs:
        result_lines = []
        for lang, lines in lang_lines:
          if (lang == included_lang) or (lang == "all"): result_lines.extend(lines)
        return "\n".join(result_lines), included_lang
    return "", "--" # Not found!
    
  def save(self, s, lang):
    self.empty = s == ""
    if self.empty: 
      if os.path.exists(self.filename): os.unlink(self.filename)
      write_file(self.empty_filename, "", touch = True)
    else:
      if os.path.exists(self.empty_filename): os.unlink(self.empty_filename)
      write_file(self.filename, s, lang, touch = True)
      
class Conf(Doc): # conf.py
  pass

class Page(Doc):
  def ready(self):
    super().ready()
    for category in self.categories: category.pages.append(self)

class Archives(Page):
  def is_up_to_date(self):
    #for changed_category in self.blog.changed_categories:
    #  if self.doc_name.startswith(changed_category): return False # Need to update because TOC has changed -- Sphinx does not do it ?!?!?
    return not need_update([self.src_filename, os.path.join(os.path.dirname(self.filename), "ec_post_list.inc")], [self.filename])
    
class Include(Doc):
  def ready(self):
    super().ready()
    for category in self.categories: category.includes.append(self)

class CommentsInclude(Include):
  def build_str(self, s):
    lines          = []
    current_lang   = ""
    accepted_langs = set(self.blog.lang.langs)
    for line in s.split("\n"):
      if line.startswith(".. lang::"):
        current_lang = line[len(".. lang::"):].strip()
      else:
        if current_lang in accepted_langs:
          lines.append(line)
          
    return "\n".join(lines), "**"
    
class Post(Doc):
  def __init__(self, blog, src_filename, date):
    super().__init__(blog, src_filename)
    self.date = date
    self.link_filenames = []
    
  def formated_date(self): return self.date.strftime("%x")
  
  def is_up_to_date(self):
    #for changed_category in self.blog.changed_categories:
    #  if self.doc_name.startswith(changed_category): return False # Need to update because TOC has changed -- Sphinx does not do it ?!?!?
    return not need_update([self.src_filename, "%s_comments.inc" % self.src_filename[:-4]], [self.filename])
    
  def add_link(self, link_filename):
    self.link_filenames.append(link_filename)
    
  def ready(self):
    super().ready()
    
    for link_filename in self.link_filenames:
      link_doc_name = os.path.splitext(os.path.relpath(link_filename, self.blog.blog_dir))[0]
      if "/" in link_doc_name: self.categories.append(self.blog.categories_dict[os.path.dirname(link_doc_name)])
      else:                    self.categories.append(self.blog.categories_dict[""])
      
    ancestor_categories = set()
    for category in self.categories:
      category.posts.append(self)
      while category:
        ancestor_categories.add(category)
        if category.doc_name in self.blog.ec_dont_propagate_posts_for_categories: break
        category = category.categories[0]
        
    for ancestor_category in ancestor_categories: ancestor_category.posts_rec.append(self)
      
  def build_str(self, s):
    s, lang = super().build_str(s)
    s = s.lstrip()
    if not s: return "", "--"
    
    comments_include = "%s_comments" % self.doc_name
    has_comments = EC_HAS_COMMENTS and os.path.exists(self.filename.replace(".rst", "_comments.inc"))
    if EC_HAS_COMMENTS:
      add_comment_link = email_link(BLOG.author_email,
                                    "%s /%s_%s" % (BLOG.title.replace(" ", ""), self.doc_name, BLOG.lang.langs[0]),
                                    EC_TRANSLATIONS[BLOG.lang.langs[0], "add_comment"],
                                    localurl = "file://%s" % BLOG.blog_dir,
                                    url      = BLOG.url,
      )
      
    parts = s.split(".. more::", 1)
    if len(parts) == 2: label = EC_TRANSLATIONS[BLOG.lang.langs[0], "more"]
    else:               label = EC_TRANSLATIONS[BLOG.lang.langs[0], "comment"]
    title, underline, intro = parts[0].split("\n", 2)
    title = ":doc:`/%s`" % self.doc_name
    
    in_categories = []
    
    for ancestor in self.categories:
      in_category = ""
      while ancestor.categories[0]:
        if in_category: in_category = "/" + in_category
        in_category = ":doc:`/%s`" % ancestor.doc_name + in_category
        ancestor = ancestor.categories[0]
      if in_category: in_categories.append(in_category)
      
    in_categories = ", ".join(in_categories)
    if in_categories: in_categories = ".. container:: in-category\n\n   %s %s\n\n" % (EC_TRANSLATIONS[self.blog.lang.langs[0], "in_category"], in_categories)
    intro = ".. rst-class:: post-box\n\n%s\n%s\n\n.. container:: post-date\n\n   %s\n\n%s%s" % (title, underline[0] * len(title), self.formated_date(), in_categories, intro)
    if (len(parts) == 2) or has_comments:
      intro = """%s

.. container:: read-more

    :doc:`%s </%s>`
""" % (intro, label, self.doc_name)
    else:
      intro = """%s

.. container:: read-more

   .. raw:: html

      %s

""" % (intro, add_comment_link)
    if len(parts) == 2: s = parts[0] + parts[1]
    
    inc_filename = "%s.inc" % self.filename[:-4]
    write_file(inc_filename, intro, lang, touch = True)
    
    title, underline, s = s.split("\n", 2)
    if len(self.categories) < 2: in_categories = ""
    s = ".. rst-class:: post-box\n\n%s\n%s\n\n.. container:: post-date\n\n   %s\n\n%s%s" % (title, underline, self.formated_date(), in_categories, s)
    
    if has_comments:
      s += """\n\n.. include:: /%s.inc\n""" % comments_include
    
    if EC_HAS_COMMENTS:
      s += """

.. raw:: html

   %s""" % add_comment_link
    
    return s, lang
    
class Category(Doc):
  def __init__(self, blog, src_filename):
    super().__init__(blog, src_filename)
    self.subcategories = []
    self.pages         = []
    self.includes      = []
    self.posts         = []
    self.posts_rec     = [] # Posts, including posts in subcategories
    if "/" in self.doc_name: self.category_name = self.doc_name.rsplit("/", 1)[0] # Remove "/index"
    else:                    self.category_name = "" # Root category
    if   "/" in self.category_name: self.categories = [blog.categories_dict[self.category_name.rsplit("/", 1)[0]]]
    elif self.category_name:        self.categories = [blog.categories_dict[""]]
    else:                           self.categories = [None]  # Root category
    if self.categories[0]: self.categories[0].subcategories.append(self)
    
    blog.categories_dict[self.category_name] = self
    if need_update([self.src_filename], [self.filename]) and (not self.empty):
      start = ("/%s" % self.doc_name).rsplit("/", 2)[0]
      if start and (start[0] == "/"): start = start[1:]
      blog.changed_categories.append(start)
      
  def ready(self): pass # Disable Doc's behavior
  
  def build(self, force = False):
    changed = force
    archives = []
    for doc in self.pages + self.includes + self.posts + self.subcategories:
      if isinstance(doc, Archives): archives.append(doc)
      else:
        if doc.build(force): changed = True
    
    changed = super().build(changed) or changed
    
    for doc in archives: # Archives page need to be built AFTER the index, not before, because it depends on it.
      if doc.build(force): changed = True
      
    return changed
    
  def build_str(self, s):
    self.subcategories.sort(key = lambda category: category.filename)
    self.pages        .sort(key = lambda page:     page.filename)
    self.posts        .sort(key = lambda post:     post.date)
    self.posts_rec    .sort(key = lambda post:     post.date)
    
    recent_posts = [[]]
    for post in reversed(self.posts_rec):
      if post.empty: continue
      recent_posts[-1].append(post)
      if len(recent_posts[-1]) >= self.blog.number_of_recent_post: recent_posts.append([])
    if not recent_posts[-1]: del recent_posts[-1]
    
    base = self.category_name
    if base: base += "/"
    tocdocs1 = ["%sec_recent_posts%s.rst" % (base, i + 2) for i in range(len(recent_posts) - 1)]
    tocdocs2 = [doc.doc_name for doc in (self.pages + self.subcategories) if not doc.empty]
    tocdocs2.sort()
    
    s, lang = super().build_str(s)
    if not s.strip(): return s, lang
    
    s = s + """

.. toctree::
   :hidden:
   :titlesonly:
   
%s

""" % ("\n".join("   /%s" % tocdoc for tocdoc in tocdocs1))
    
    s = s + """

.. rst-class:: localtoc

.. toctree::
   :maxdepth: 9
   :titlesonly:
   
%s

""" % ("\n".join("   /%s" % tocdoc for tocdoc in tocdocs2))
    
    if self.categories[0] is None: # Root category
      s = s + """
.. toctree::
   :maxdepth: 9
   :hidden:
   :titlesonly:
   
%s""" % ("\n".join("   /%s" % doc.doc_name for doc in self.posts_rec if not doc.empty))
    
    post_list = ""
    previous = None
    for post in self.posts_rec:
      if post.empty: continue
      if   (not previous) or (post.date.year != previous.date.year):
        post_list += """\n%s\n====\n""" % post.date.year
        previous = None
      if (not previous) or (post.date.month != previous.date.month):
        month = post.date.strftime("%B %Y")
        post_list += """\n%s\n%s\n\n""" % (month, "*" * len(month))
      post_list += """- %s :doc:`/%s`\n""" % (post.formated_date(), post.doc_name)
      previous = post
      
    title, title_chars = s.lstrip().split("\n", 2)[:2]
    pages = ["".join("""
.. include:: /%s.inc

""" % (post.doc_name) for post in posts) for posts in recent_posts]
    
    label = EC_TRANSLATIONS[BLOG.lang.langs[0], "comment_title"]
    if pages:
      s += "\n\n%s\n%s\n" % (label, "%" * len(label))
      s += pages[0]
    i = 2
    for page in pages[1:]:
      page_title = "%s (%s)" % (title, i)
      page = "%s\n%s\n" % (page_title, title_chars[0] * len(page_title)) + "\n\n%s\n%s\n" % (label, "%" * len(label)) + page
      write_file(os.path.join(os.path.dirname(self.filename), "ec_recent_posts%s.rst" % i), page, lang, touch = True)
      i += 1
      
    write_file(os.path.join(os.path.dirname(self.filename), "ec_post_list.inc"), post_list, lang, touch = True)
    return s, lang


SPECIAL_DOCS = {}
BLOGS = {}
class TranslatedBlog(object):
  def __init__(self, blog_dir, dirname, lang, number_of_recent_post, ec_multiple_themes, title, author, author_email, url, ec_dont_propagate_posts_for_categories):
    BLOGS[lang]                = self
    self.blog_dir              = blog_dir
    self.dirname               = dirname
    self.lang                  = lang
    self.number_of_recent_post = number_of_recent_post
    self.ec_multiple_themes    = ec_multiple_themes
    self.docs                  = []
    self.categories_dict       = {}
    self.changed_categories    = []
    self.conf                  = Conf(self, os.path.join(blog_dir, "conf.py"))
    self.title                 = title
    self.author                = author
    self.author_email          = author_email
    self.url                   = url
    self.changed_rst_files     = set()
    self.src_filename_2_doc    = {}
    self.pending_links         = defaultdict(list)
    self.ec_dont_propagate_posts_for_categories = ec_dont_propagate_posts_for_categories
    
  def create_doc(self, src_filename):
    if os.path.islink(src_filename):
      link_target = os.readlink(src_filename)
      if link_target.startswith("."): link_target = os.path.join(os.path.dirname(src_filename), link_target)
      link_target = os.path.normpath(link_target)
      if link_target in self.src_filename_2_doc:
        self.src_filename_2_doc[link_target].add_link(src_filename)
        return
      else:
        self.pending_links[link_target].append(src_filename)
        return
        
    date = is_post(src_filename)
    doc  = None
    if   src_filename.endswith("_comments.inc"): doc = CommentsInclude(self, src_filename)
    elif src_filename.endswith(".inc"):          doc = Include        (self, src_filename) # Must be checked before posts, for comments includes
    elif date:                                   doc = Post           (self, src_filename, date)
    elif src_filename.endswith("archives.rst"):  doc = Archives       (self, src_filename)
    elif src_filename.endswith("index.rst"):     doc = Category       (self, src_filename)
    else:                                        doc = Page           (self, src_filename)
    if doc: self.src_filename_2_doc[src_filename] = doc
    
    if src_filename in self.pending_links:
      for pending_link in self.pending_links[src_filename]:
        doc.add_link(pending_link)
      del self.pending_links[src_filename]
      
  def build(self, force = False):
    for doc in self.docs: doc.ready()
    self.conf.build(force)
    self.categories_dict[""].build(force)

def is_post(src_filename):  
  try:
    year, month, day, title = os.path.basename(src_filename).split("_", 3)
    return Date(int(year), int(month), int(day))
  except: return None

def lang_split(src_dir, langs, dest_dirs_langss, ignored_dirs):
  """lang_split(src_dir, [lang1, lang2,...], [(dest_dir1, [lang1, lang2,...]), (dest_dir2, [lang2,...]),...])"""
  dest_dirs    = { dest_dir for (dest_dir, langs) in dest_dirs_langss }
  
  for dirpath, dirnames, filenames in os.walk(src_dir):
    if dirpath in ignored_dirs: dirnames[:] = []; continue
    
    for dest_dir, lang in dest_dirs_langss:
      dest_dirpath = os.path.join(dest_dir, dirpath[len(src_dir) + 1:])
      os.makedirs(dest_dirpath, exist_ok = True)
      
      blog = BLOGS[lang]
      for filename in filenames:
        if   filename in SPECIAL_DOCS: pass
        elif filename.endswith(".rst") or filename.endswith(".inc"):
          blog.create_doc(os.path.join(dirpath, filename))
        elif os.path.samefile(os.path.join(dirpath, filename), os.path.join(src_dir, "conf.py")): pass
        else: symlink(os.path.join(dirpath, filename), os.path.join(dest_dirpath, filename))
        
def symlink(src, dest):
  if os.path.lexists(dest):
    if os.path.islink(dest):
      dest_link = os.path.join(os.path.dirname(dest), os.readlink(dest))
      if os.path.samefile(dest_link, src): return
    os.unlink(dest)
  print("link  %s" % dest)
  os.symlink(src, dest)

def do(s):
  print("\n%s" % s)
  if os.system(s) != 0:
    print("\nÉCHEC!")
    sys.exit()

LANGS = {}
class _Language(object):
  def __init__(self, name, locale, *langs):
    self.name     = name
    self.locale   = locale
    self.langs    = langs
    self.priority = len(LANGS) + 1
    LANGS[langs[0]] = self
def Language(name, locale, *langs):
  if langs[0] in LANGS: return LANGS[langs[0]]
  return _Language(name, locale, *langs)

AVAILABLES_DOC_LANGS = {}
def get_available_doc_langs(doc_name):
  if not doc_name in AVAILABLES_DOC_LANGS:
    langs = set()
    src_filename = os.path.join(BLOG.blog_dir, "%s.rst" % doc_name)
    if os.path.exists(src_filename):
      print("readlang %s" % src_filename)
      s = open(src_filename).read()
      for line in s.split("\n"):
        if line.startswith(".. lang::"):
          lang = LANGS.get(line[len(".. lang::"):].strip())
          if lang: langs.add(lang)
    else: langs = LANGS.values() # Search page, etc
    AVAILABLES_DOC_LANGS[doc_name] = sorted(langs, key = lambda x: x.priority)
  return AVAILABLES_DOC_LANGS[doc_name]

#RENAMED_FILES = [".buildinfo", "objects.inv", "searchindex.js"]
RENAMED_FILES = {
  ".buildinfo"     : ".%s_buildinfo",
  "objects.inv"    : "objects_%s.inv",
  "searchindex.js" : "searchindex_%s.js",
}

BLOG = None
EC_TRANSLATIONS = None
EC_HAS_COMMENTS = False
def run(conf_filename, force = False):
  global EC_TRANSLATIONS, EC_HAS_COMMENTS, BLOG
  d = {}
  s = open(conf_filename).read().split("\n")
  s = "\n".join(l for l in s if not l.startswith(".. lang::"))
  exec(s, d)
  blog_dir                 = os.path.dirname(conf_filename)
  number_of_recent_post    = d["number_of_recent_post"]
  EC_TRANSLATIONS          = d["ec_translations"]
  title                    = d["project"]
  author                   = d["author"]
  author_email             = d["author_email"]
  url                      = d["url"]
  comments_mail_dir        = d["comments_mail_dir"]
  gallery_miniature_width  = d["gallery_miniature_width"]
  gallery_miniature_height = d["gallery_miniature_height"]
  gallery_import_width     = d["gallery_import_width"]
  gallery_import_height    = d["gallery_import_height"]
  ec_dont_propagate_posts_for_categories = d["ec_dont_propagate_posts_for_categories"]
  
  d = {}
  s = open(os.path.join(blog_dir, "themes.conf")).read().split("\n")
  s = "\n".join(l for l in s if not l.startswith(".. lang::"))
  exec(s, d)
  ec_multiple_themes = d["ec_multiple_themes"]
  ec_multiple_themes = list(ec_multiple_themes.items())
  ec_multiple_themes.sort(key = lambda category_theme: len(category_theme[0]), reverse = True)
  
  if comments_mail_dir:
    EC_HAS_COMMENTS = True
    import eclaircie.comments
    comments_changed_doc_names = eclaircie.comments.update_comments(blog_dir, title, EC_TRANSLATIONS, comments_mail_dir, force)
    
  for dirpath, dirnames, filenames in os.walk(os.path.join(blog_dir, "_images")):
    for filename in filenames:
      if filename.startswith("miniature_"): continue
      if filename.startswith("youtube_preview_"): continue
      reduce_image(os.path.join(dirpath, filename), os.path.join(dirpath, "miniature_%s" % filename), gallery_miniature_width, gallery_miniature_height)
      
  langs            = sorted(LANGS.values(), key = lambda lang: 0 if lang.langs[0] == "en" else 1) # Start by English since it does not require translation in Sphinx
  dest_dirs_langss = [(os.path.join(blog_dir, "_%s" % lang.langs[0]), lang) for lang in langs]
  for dest_dir, lang in dest_dirs_langss:
    blog = TranslatedBlog(blog_dir, dest_dir, lang, number_of_recent_post, ec_multiple_themes, title, author, author_email, url, ec_dont_propagate_posts_for_categories)
    for doc_name in comments_changed_doc_names:
      blog.changed_rst_files.add("%s%s.rst" % (dest_dir, doc_name))
      

  ignored_dirs = { os.path.join(blog_dir, "html"), os.path.join(blog_dir, "_static"), os.path.join(blog_dir, "_images"), os.path.join(blog_dir, "_downloads") } | { dest_dir for (dest_dir, langs) in dest_dirs_langss }
  
  for dirpath, dirnames, filenames in os.walk(os.path.join(blog_dir)):
    if dirpath in ignored_dirs: dirnames[:] = []; continue
    for filename in filenames:
      if filename.endswith(".py") and (filename != "conf.py"):
        filename = os.path.join(dirpath, filename)
        print("running  %s..." % filename)
        py = open(filename).read()
        exec(py, globals(), { "__file__" : filename } )
        
  lang_split(blog_dir, [lang.langs[0] for lang in LANGS.values()], dest_dirs_langss, ignored_dirs)
  
  for dest_dir, lang in dest_dirs_langss:
    symlink(os.path.join(blog_dir, "_static"),    os.path.join(dest_dir, "_static"))
    symlink(os.path.join(blog_dir, "_images"),    os.path.join(dest_dir, "_images"))
    symlink(os.path.join(blog_dir, "_downloads"), os.path.join(dest_dir, "_downloads"))
    
  for dest_dir, lang in dest_dirs_langss:
    locale.setlocale(locale.LC_ALL, lang.locale)
    print("  **** eClaircie -- language '%s'****""" % lang.name)
    BLOG = BLOGS[lang]
    BLOG.build(force)
    
    # Hack .buildinfo & co, since Sphinx does not allow to specify its filename, and we need a different
    # .buildinfo & co for each lang
    if len(LANGS) > 1:
      for sphinx_filename, ec_filename in RENAMED_FILES.items():
        ec_filename = ec_filename % lang.langs[0]
        if os.path.exists(os.path.join(blog_dir, "html", ec_filename)):
          #do("cd %s; cp --force %s %s" % (os.path.join(blog_dir, "html"), ec_filename, sphinx_filename))
          do("cd %s; mv --force %s %s" % (os.path.join(blog_dir, "html"), ec_filename, sphinx_filename))
          
    # Run Sphinx!
    if BLOG.changed_rst_files:
      #print(BLOG.changed_rst_files)
      
      run_sphinx(dest_dir, os.path.join(blog_dir, "html"), os.path.join(dest_dir, "_doctree"), False, BLOG.changed_rst_files)
      
      #run_sphinx(dest_dir, os.path.join(blog_dir, "html"), os.path.join(dest_dir, "_doctree"), False)
      
    # Re-hack
    if len(LANGS) > 1:
      for sphinx_filename, ec_filename in RENAMED_FILES.items():
        ec_filename = ec_filename % lang.langs[0]
        #do("cd %s; cp --force %s %s" % (os.path.join(blog_dir, "html"), sphinx_filename, ec_filename))
        do("cd %s; mv --force %s %s" % (os.path.join(blog_dir, "html"), sphinx_filename, ec_filename))
        
      # Hack search index
      search_filename = os.path.join(blog_dir, "html", "search_%s.html" % lang.langs[0])
      print("fix %s" % search_filename)
      s = open(search_filename).read().replace("searchindex.js", "searchindex_%s.js" % lang.langs[0])
      open(search_filename, "w").write(s)
    
    # Rename RSS files
    if len(LANGS) > 1:
      if os.path.exists(os.path.join(blog_dir, "html", "news_%s.html" % lang.langs[0])):
        do("cd %s; mv --force news_%s.html news_%s.rss" % (os.path.join(blog_dir, "html"), lang.langs[0], lang.langs[0]))
    else:
      if os.path.exists(os.path.join(blog_dir, "html", "news.html")):
        do("cd %s; mv --force news.html news.rss" % os.path.join(blog_dir, "html"))
        
    print()
    
  symlink(os.path.join(blog_dir, "_images"),    os.path.join(blog_dir, "html", "_images"))
  symlink(os.path.join(blog_dir, "_downloads"), os.path.join(blog_dir, "html", "_downloads"))

  if len(LANGS) > 1:
    index_filename = os.path.join(blog_dir, "html", "index.html")
    if not os.path.exists(index_filename):
      s = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<body>

<script language="javascript"><!--
var language = window.navigator.userLanguage || window.navigator.language;
language = language.slice(0,2);
"""
      for lang in LANGS.values():
        s += """if (language == "%s") document.location.href="index_%s.html";\n""" % (lang.langs[0], lang.langs[0])
      s += """else document.location.href="index_en.html";
//--></script>
<p>This site is available in several languages:</p>\n"""
      for lang in LANGS.values():
        s += """<a href="index_%s.html">%s</a><br/>\n""" % (lang.langs[0], lang.name)
      s += """</body></html>"""
      open(index_filename, "w").write(s)
    
from sphinx.application import Sphinx
from sphinx.util import Tee, format_exception_cut_frames, save_traceback
from sphinx.util.console import red, nocolor, color_terminal
from sphinx.util.osutil import abspath, fs_encoding
from sphinx.util.pycompat import terminal_safe, bytes

def run_sphinx(src_dir, out_dir, doctree_dir, force = False, filenames = []):
  builder_name   = "ec_html"
  force_all      = force
  freshenv       = force
  warningiserror = False
  verbosity      = 1
  parallel       = 0
  status         = sys.stdout
  warning        = sys.stderr
  tags           = []
  confoverrides  = {}
  app = Sphinx(src_dir, src_dir, out_dir, doctree_dir, builder_name, confoverrides, status, warning,
               freshenv, warningiserror, tags, verbosity, parallel)
  app.build(force_all, filenames)
  
