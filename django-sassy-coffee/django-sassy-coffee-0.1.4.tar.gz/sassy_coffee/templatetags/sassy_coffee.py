from django import template

register = template.Library()

@register.tag
def sass(parser, token):
	nodelist = parser.parse(('endsass'),)
	parser.delete_first_token();
	return SassNode(nodelist)

class SassNode(template.Node):
	def __init__(self, nodelist):
		self.nodelist = nodelist

	def render(self, context):
		output = self.nodelist.render(context)
		output = output.replace('sass', 'css')
		return output

@register.tag
def scss(parser, token):
    nodelist = parser.parse(('endcoffee'),)
    parser.delete_first_token();
    return ScssNode(nodelist)

class ScssNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        output = output.replace('scss', 'css')
        return output

@register.tag
def coffee(parser, token):
    nodelist = parser.parse(('endcoffee'),)
    parser.delete_first_token();
    return CoffeeNode(nodelist)

class CoffeeNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        output = output.replace('coffee', 'js')
        return output