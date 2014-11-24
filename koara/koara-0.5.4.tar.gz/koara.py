import re

class Koara:

	class Html5Renderer:
		def render_blockquote(self, body, nested):
 			out = ''
 			if(nested):
 				out += "\n\n";
 			return out + "<blockquote>" + body + "</blockquote>\n\n"
 		
 		def render_code_span(self, text):
 			return "<code>" + text + "</code>"
	
 		def render_del(self, text):
 			return "<del>" + text + "</del>"
 
 		def render_em(self, text):
 			return "<em>" + text + "</em>"
 		
		def render_fenced_code_blocks(self, code, lang):
			block = "<pre><code"
			if(len(lang) > 0):
				block += " class=\"" + lang + "\""
			return block + ">" + code + "</code></pre>\n" 
 		
		def render_header(self, text, level):
			tag = "h" + `level`
			return '<' + tag + '>' + text + '</' + tag + '>\n\n';

		def render_hr(self):
 			return "<hr>\n";
 		
 		def render_html(self, html, nested, i):
 			if(i==0 and nested):
 				return "\n" + re.sub(r'(?m)^(?!$)', '    ', html)
 			else:
 				return html;

		def render_image(self, src, title, alt):
			image = "<img src=\"" + src + "\" alt=\"" + alt + "\"" 
			if title is not None:
				image += " title=\"" +  title + "\""
			return image + ">"
 		
		def render_line_break(self):
 			return "<br>\n"
 		
		def render_link(self, url, title, text):
			link = "<a href=\"" + re.sub(r' ', "%20", url) + "\"";
			if title is not None:
				link += " title=\"" + title + "\""
			return link + ">" + text + "</a>"
		
 		def render_list(self, body, nested, ordered):
 			tag = "ol" if ordered else "ul"
 			list = "\n<" + tag + ">\n" + re.sub(r'(?m)^(?!$)', '    ', body) + "</" + tag + ">\n"
 			return list if nested else (list + "\n")
# 		
 		def render_list_item(self, text):
 			return "<li>" + text + "</li>\n";
 		
		def render_paragraph(self, body):
			return "<p>" + body + "</p>"
 		
		def render_strong(self, text):
 			return "<strong>" + text + "</strong>"
 		
 		def render_table(self, head, body):
 			return "<table>\n    <thead>\n" + head + "    </thead>\n    <tbody>\n" + body + "    </tbody>\n</table>\n"
 		
 		def render_table_row(self, text):
 			return "        <tr>\n" + re.sub(r'(?m)^(?!$)', '            ', text) + "        </tr>\n"

 		def render_table_cell(self, text, header, align):
 			tag = "th" if header else "td"
 			if(align is not None):
 			   return "<" + tag + " style=\"text-align: " + align + ";\">" + text + "</" + tag + ">\n"
 			return "<" + tag + ">" + text + "</" + tag + ">\n"

	def __init__(self, extensions=[]):
	    self.extensions = extensions
	
	def parse(self, text, renderer=Html5Renderer()):
		self.renderer = renderer
		self.inlineHash = {}
		self.inlineHashCount = 0
		self.htmlHash = {}
		self.linkUrls = {}
		self.linkTitles = {}
		
		text = re.sub(r'\r\n|\r', "\n", text)
		text = re.sub(r'\t', "    ", text)
		text = re.sub(r'(?m)[ \t]+$', '', text)
		text = self.do_fenced_code_blocks(text)
		text = self.hash_html_blocks(text);
		text = self.strip_link_definitions(text);
		text = self.do_block_elements(text, False);
		text = self.unescape_special_chars(text);
		return re.sub(r'(?m)^[ \t]*$', '', text)
	
	def do_fenced_code_blocks(self, text):
	    return re.sub(r'(?m)^`{3}(.*)\n([\s\S]+?)`{3}', 
					lambda m: self.renderer.render_fenced_code_blocks(self.encode_code(m.group(2).strip()), m.group(1)), text)
					
	def hash_html_blocks(self, text):
		def protect_html(m):
	    	 return "\n" + self.hash_html(m.group()) + "\n\n"
		text = re.sub(r'(?mi)<!--[\s\S]+?-->', protect_html, text)
		text = re.sub(r'(?mi)^<(div|table|a|blockquote|code|d[ltd]|h[1-6]|ol|p|pre|ul|kbd)\b(.+\n)\n*[ \t]{4}[\s\S]+?^<\/\1>', protect_html, text)
		text = re.sub(r'(?mi)^[ ]*<(div|table|a|blockquote|code|d[ltd]|h[1-6]|ol|p|pre|ul|kbd)\b([\s\S]+?<\/\1>(?=\n{2,})|[\s\S]+?<\/\1>$)', protect_html, text)
		text = re.sub(r'(?mi)^<(br|hr|img).*>', protect_html, text)
		return text
	
	def strip_link_definitions(self, text):
		def replace(m):
			id = m.group(1).lower()
			self.linkUrls[id] = m.group(2)
			self.linkTitles[id] = m.group(3)
			return ""
		return re.sub(r'(?m)^[ \t]*\[([^\[]+)\]:[ \t]*\n?[ \t]*<?[\[]?(\S+?)[\]]?>?[ \t]*\n?[ \t]*(?:[\"(](.+?)[\")][ \t]*)?(?:\n+)', replace, text);
		
	
	def do_block_elements(self, text, nested):
 		text = self.do_blockquotes(text, nested);   
 		text = self.do_fenced_code_blocks(text);
 		text = self.do_headers(text)
 		text = self.do_tables(text)
		text = re.sub(r'(?m)^[ \t]{0,3}(-[ ]?){3,}[ \t]*$', self.renderer.render_hr(), text)
 		text = self.do_unordered_lists(text, nested)
 		text = self.do_ordered_lists(text, nested)	
 		text = self.hash_html_blocks(text)
		return self.form_paragraphs(text, nested)
	
	def do_blockquotes(self, text, nested):
		def replace(m):
			body = self.do_block_elements(re.sub(r'(?m)^[ \t]*>[ \t]*', '', m.group()), True)
			return self.renderer.render_blockquote(body, nested);
		return re.sub(r'(?m)^>[ \t]*(([\s\S]+?)(?=\n[^>])|[\s\S]+$)', replace, text)
	
	def do_headers(self, text):
		def replace(m):
	    	 return self.renderer.render_header(self.do_span_elements(m.group(2).strip()), len(m.group(1)))
   		return re.sub(r'(?m)^[ \t]*(\#{1,6})[ \t]+([^\n]+?)[ \t]*$', replace, text)
	
	def do_tables(self, text):
		if('tables' in self.extensions):
			text = re.sub('\\\\\\|', self.hash_inline('|'), text)
			text = re.sub('(?m)^[ ]{0,3}[|](.+)\n[ ]{0,3}[|]([ ]*[-:]+[-| :]*)\n(([ ]*[|].*\n)*)(?=\n|$)', lambda m: self.do_table(m.group(0), m.group(1), m.group(2), m.group(3)), text)
			text = re.sub('(?m)^[ ]{0,3}(\S.*[|].*)\n[ ]{0,3}([-:]+[ ]*[|][-| :]*)\n((.*[|].*\n)*)(?=\n|$)', lambda m: self.do_table(m.group(0), m.group(1), m.group(2), m.group(3)), text)
		return text
	
	def do_table(self, table, head, underline, content):
		content = re.sub('(?m)^\||\|$', '', content)
		headers = head.split("|")
 		cols = underline.split("|");
 		attributes = self.do_table_attributes(cols);
 		rows = content.split("\n");
		return self.renderer.render_table(self.do_table_head(attributes, headers), self.do_table_body(attributes, rows))
		
	def do_table_attributes(self, cols):
		attributes = [None] * (len(cols))
		for i in range(len(cols)):
 			alignment = cols[i].strip()
 			if(re.match('^-+:$', alignment)):
 				attributes[i] = "right"
 			elif(re.match('^:-+:$', alignment)):
 				attributes[i] = "center"
 			elif(re.match('^:-+$', alignment)):
 				attributes[i] = "left"
		return attributes
	
	def do_table_head(self, attributes, headers):
		th = ""
		for i in range(len(headers)):
 			h = headers[i].strip()
 			if(h):
 				th += self.renderer.render_table_cell(self.do_span_elements(h), True, attributes[i])
		return self.renderer.render_table_row(th)
	
	def do_table_body(self, attributes, rows):
		output = ""
		for i in range(len(rows) - 1):
			cells = rows[i].split("|")
			td = ""
			for j in range(len(cells)):
				text = self.do_span_elements(cells[j].strip())
				td += self.renderer.render_table_cell(text, False, attributes[j]);
			output += self.renderer.render_table_row(td);
		return output
	    
	def do_unordered_lists(self, text, nested):
	    return re.sub(r'(?m)^[ \t]{0,3}((\*[ \t]+[\s\S]+?)(?=\n{3,}|\n{2}[^\*\s]|\n+\d[.])|\*[ \t]+[\s\S]+$)', 
					lambda m: self.renderer.render_list(self.do_list_items(m.group(1)), nested, False), text);
		  
	def do_ordered_lists(self, text, nested):
	   		    return re.sub(r'(?m)^[ \t]{0,3}((\d+[.][\s\S]+?)(?=\n{3}|\n{2}<ul>|\n{2}[^(\d\s)]|\n{2}\d[^.])|\d+[.][\s\S]+$)', 
					lambda m: self.renderer.render_list(self.do_list_items(m.group(1)), nested, True), text);


	def do_list_items(self, list):
		def replace(m):
			return self.renderer.render_list_item(self.do_block_elements(re.sub(r'(?m)^[ \t]{0,4}', '', m.group(1)), True))
		return re.sub(r'(?m)^[ \t]{0,3}(?:\*|\d+[.])[ \t]*([\s\S]+?(?=^[ \t]{0,3}\*|^[ \t]{0,3}\d+[.])|[\s\S]*$)', replace, list)

	def form_paragraphs(self, text, nested):
		paragraphs = re.split('\n{2,}', text.strip())
		for i in range(len(paragraphs)):
			p = paragraphs[i].strip()
			if(p in self.htmlHash):
				paragraphs[i] = self.renderer.render_html(self.htmlHash.get(p), nested, i)
			else:
				p = self.do_span_elements(p)	
				if not p.startswith('| '):
					p = re.sub(r'\n', self.renderer.render_line_break(), p)
				else: 
					p = re.sub(r'^\|[ ]+', '', p, 1)
					p = re.sub(r'\n\|[ ]+', self.renderer.render_line_break(), p)
				if i == 0 and nested:
					paragraphs[i] = p;
					if len(paragraphs) == 1:
						return p
				elif not p == "":
					paragraphs[i] = self.renderer.render_paragraph(p)
			if i > 0 and nested:
				paragraphs[i] = re.sub(r'(?m)^', '    ', paragraphs[i])
		return '\n\n'.join(str(p) for p in paragraphs) + "\n"

	def do_span_elements(self, text):
 		text = self.do_code_spans(text);
 		text = self.encode_backslash_escapes(text);
		text = self.do_images(text);
 		text = self.do_links(text);
 		text = self.do_auto_links(text);
 		text = self.do_formatting(text);
 		text = self.encode_amps_and_angles(text);
		return text

	def do_code_spans(self, text):
		text = re.sub(r'(?<!\\\\)(`+)(.+?)(?<!`)\1(?!`)', lambda m: 
					self.hash_inline(self.renderer.render_code_span(self.encode_code(m.group(2).strip()))), text)
		return re.sub('(?m)<code>.*</code>', lambda m: self.hash_inline(m.group()), text)

	def encode_backslash_escapes(self, text):
		text = re.sub(r'\\\\', lambda m: self.hash_inline('\\'), text)
		text = re.sub(r'\\\[', lambda m: self.hash_inline('['), text)
		text = re.sub(r'\\\]', lambda m: self.hash_inline(']'), text)
		text = re.sub(r'\\\!', lambda m: self.hash_inline('!'), text)
		text = re.sub(r'\\\(', lambda m: self.hash_inline('('), text)
		text = re.sub(r'\\\)', lambda m: self.hash_inline(')'), text)
		text = re.sub(r'\\\#', lambda m: self.hash_inline('#'), text)
		text = re.sub(r'\\\*', lambda m: self.hash_inline('*'), text)
		text = re.sub(r'\\\~', lambda m: self.hash_inline('~'), text)
		text = re.sub(r'\\\_', lambda m: self.hash_inline('_'), text)
		text = re.sub(r'\\\-', lambda m: self.hash_inline('-'), text)
		text = re.sub(r'\\\.', lambda m: self.hash_inline('.'), text)
		text = re.sub(r'\\\`', lambda m: self.hash_inline('`'), text)
		text = re.sub(r'\\\!', lambda m: self.hash_inline('!'), text)
		return text
	    
	def do_images(self, text):
		def replace_referenced_images(m):
			alt = m.group(1)
			id = m.group(2).lower()
			if id is None:
				id = alt.lower()
			if(id in self.linkUrls):
				return self.renderer.render_image(self.linkUrls[id], self.linkTitles[id], alt)
			return m.group()
		
		text = re.sub(r'!\[(.+)\][ ]?\((\S+)[ ]*\"(.*)\"[ ]*\)', 
					lambda m: self.renderer.render_image(m.group(2), m.group(3), m.group(1)), text)
		text = re.sub(r'!\[(.+)\][ ]?\((.+)\)', 
					lambda m: self.renderer.render_image(m.group(2), None, self.hash_inline(m.group(1))), text)
		return re.sub(r'[!]\[(.*?)\][ ]?(?:\n[ ]*)?\[(.*?)\]', replace_referenced_images, text)

	def do_links(self, text):
		def replace_reference_links(m):
			linkText = m.group(1)
			id = m.group(2).lower()
			if(id == ""):
				id = linkText.lower()
			if(id in self.linkUrls):
				return self.renderer.render_link(self.linkUrls[id], self.linkTitles[id], linkText)
			return m.group()
		text = re.sub(r'\[([^\[]*?)\][ ]?(?:\n[ ]*)?\[(.*?)\]', replace_reference_links, text);
		
		return re.sub(r'(\[(.*?)\][ ]?\([ \t]*<?(.+?)>?[ \t]*(([\'\"])(.*?)\5)?\))', 
					lambda m: self.renderer.render_link(m.group(3), m.group(6), m.group(2)), text);
	
	def do_auto_links(self, text):
	   if('autolinks' in self.extensions):
	   		text = re.sub(r'(?m)(\()?((https?|ftp):\/\/[\w./&;]*)\b(?=\s|$)', 
					lambda m: self.renderer.render_link(m.group(2), None, m.group(2)), text)
	   		text = re.sub(r'(?m)\b([-.\w]+\@[-a-z0-9]+(\.[-a-z0-9]+)*\.[a-z]+)\b(?=\s|$)', 
					lambda m: self.renderer.render_link("mailto:" + m.group(1), None, m.group(1)), text)
	   return text    

	def do_formatting(self, text):
	   text = re.sub(r'(^|\W)\_(.+?)\_(?=\W|$)', lambda m: m.group(1) + self.renderer.render_em(m.group(2)), text);
	   text = re.sub(r'(^|\W)\*(.+?)\*(?=\W|$)', lambda m: m.group(1) + self.renderer.render_strong(m.group(2)), text);
	   return re.sub(r'(^|\W)\~(.+?)\~(?=\W|$)', lambda m: m.group(1) + self.renderer.render_del(m.group(2)), text);

	def encode_amps_and_angles(self, text):
		text = re.sub(r'&(?!\#?[xX]?(?:[0-9a-fA-F]+|\w+);)', '&amp;', text)
		text = re.sub(r'<(?![a-z\/?\$!])', '&lt;', text)
		text = re.sub(r'(?<![a-z\/?\"\$!-])>', '&gt;', text)
		text = re.sub(r'\$', '&#036;', text)
		return text

	def encode_code(self, text):
 		text = re.sub(r'\\\`', self.hash_inline('`'), text)
 		text = re.sub(r'<', '&lt;', text)
 		text = re.sub(r'>', '&gt;', text)
 		text = re.sub(r'\$', '&#036;', text)
		return text	    

	def hash_html(self, literal):
	    hash = "===KOARA_HTML~" + `len(self.htmlHash)` + "===";
	    self.htmlHash[hash] = literal
	    return hash	    

	def hash_inline(self, literal):
	   	hash = "===KOARA_INLINE~" + `len(self.inlineHash)` + "===";	
	   	self.inlineHash[hash] = literal
	   	return hash	    

	def unescape_special_chars(self, text):
		for hash in self.inlineHash:
			text = re.sub(hash, re.sub("\\\\", "\\\\\\\\", self.inlineHash[hash]), text)
		return text
	    	    