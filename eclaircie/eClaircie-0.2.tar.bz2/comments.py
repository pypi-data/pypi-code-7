import sys, os, locale
import email, email.header, email.utils
from datetime import date as Date
from datetime import datetime as DateTime

def decode_header(header): return str(email.header.make_header(email.header.decode_header(header)))

def update_comments(blog_dir, blog_name, translations, mail_dir, force = False):
  blog_name            = blog_name.replace(" ", "")
  last_update_filename = os.path.join(blog_dir, "last_comments_update")
  if (not force) and os.path.exists(last_update_filename): last_update_date = os.path.getmtime(last_update_filename)
  else:                                                    last_update_date = None
  filenames = [filename for filename in os.listdir(mail_dir) if not filename.startswith(".")]
  filenames.sort(key = lambda a: int(a))
  
  doc_name_2_comments = {}
  for filename in filenames:
    filename = os.path.join(mail_dir, filename)
    if last_update_date and (last_update_date > os.path.getmtime(filename)): continue
    
    print("comment  %s" % filename)
    doc_name, comments = parse_mail(blog_name, translations, filename)
    
    if doc_name:
      doc_name_2_comments[doc_name] = doc_name_2_comments.get(doc_name, "") + comments
  
  changed_doc_names = set()
  for doc_name, comments in doc_name_2_comments.items():
    changed_doc_names.add(doc_name)
    if last_update_date:
      f = open(os.path.join(blog_dir, doc_name[1:]) + "_comments.inc", "a")
    else:
      f = open(os.path.join(blog_dir, doc_name[1:]) + "_comments.inc", "w")
    f.write(comments)
  
  open(last_update_filename, "w")
  return changed_doc_names



def parse_mail(blog_name, translations, filename):
  mail     = email.message_from_file(open(filename))
  dest     = decode_header(mail["To"])
  if dest.startswith("'") or dest.startswith('"'): dest = dest[1:]
  if not dest.startswith(blog_name.replace(" ", "")):
    print("WARNING: non-comment email %s !" % filename)
    return None, None
  doc_name = dest[len(blog_name) + 1:].split()[0]
  doc_name, lang = doc_name.rsplit("_", 1)
  lang = lang[:2] # lang may ends with " or '
  
  address  = decode_header(mail["From"])
  if   "<" in address:
    sender = address.split("<")[0].strip().replace('"', "")
    if sender.startswith("'"): sender = sender.replace("'", "")
  elif address.count('"') >= 2:
    sender = address.split('"')[1]
  elif address.count("'") >= 2:
    sender = address.split("'")[1]
  else:
    sender = address.split("@")[0]

  datetime = email.utils.parsedate_to_datetime(mail["Date"])    
  text     = read_content(mail)
  
  import eclaircie
  locale.setlocale(locale.LC_ALL, eclaircie.LANGS[lang].locale)
  
  lang2 = lang
  #if lang == "en": lang2 = "all" # Hack in order to have english comment on french pages
  #else:            lang2 = lang
  
  return doc_name, """
.. lang:: %s

.. container:: comment

   .. container:: comment-title

      %s

   %s
""" % (lang2, translations[(lang, "comment_by")] % (sender, datetime.strftime("%c").strip()), text.replace("\n", "\n   "))


def read_content(mail):
  content_type = mail.get_content_type()
  if mail.is_multipart():
    for submail in mail.get_payload():
      text = read_content(submail)
      if not text is None: return text
      
  elif content_type == "text/plain":
    try:
      return mail.get_payload(decode = True).decode(mail.get_content_charset() or "latin")
    except UnicodeDecodeError:
      return mail.get_payload(decode = False)
    



