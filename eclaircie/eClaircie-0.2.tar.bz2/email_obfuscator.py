

def hash_link(s):
  return s.replace("<", "").replace(">", "").replace(" ", "").replace("@", "").replace(".", "").replace("/", "")

def email_link(email, name = "", label = "", localurl = None, url = None):
  if localurl == "auto":
    import eclaircie
    localurl = eclaircie.BLOG.blog_dir
  if url == "auto":
    import eclaircie
    url = eclaircie.BLOG.url
    
  if not label: label = email
  if name: email = "%s <%s>" % (name, email)
  div_id = "email_%s" % hash_link(email)
  email_link = """<a href="mailto:%s">%s</a>""" % (email, label)
  s  = """<div id="%s"></div><script>var x=document.getElementById('%s');""" % (div_id, div_id)
  if url:
    s += "if ((window.location.href.slice(0, %s)=='%s') | (window.location.href.slice(0, %s)=='%s')) { " % (len(localurl), localurl, len(url), url)
  s += "var y = '';"
  s += "".join("""y += '%s';""" % email_link[i*6:i*6+6] for i in range(len(email_link)//6+1))
  s += "x.innerHTML = y;"
  if url:
    s += "} else {x.innerHTML = '(hidden - not original page!)';}"
  s += """</script>"""
  return s.replace("@", "&#64") #.replace(".", "&#46")
