from scss import Scss
from csscompressor import compress
from sassy_coffee import utils
from slimit import minify
import sassin, os, coffeescript, sassy_coffee

def compile_files():
    ftc = sassy_coffee.formats_to_compile
    exc = sassy_coffee.exclusions
    print 'Compiling files with formats ' + str(ftc) + ' and'
    print 'exclusions ' + str(exc)

    if 'sass' in ftc:
        compile_sass_files(exc)
    if 'scss' in ftc:
        compile_scss_file(exc)
    if 'coffee' in ftc:
        compile_coffeescript(exc)

def compile_sass_files(exclusions=list()):
    matches = utils.locate_files_to_compile('*.sass', exclusions)

    for path, f, name in matches:
        scss = sassin.compile_from_file(os.path.join(sassy_coffee.DJANGO_PATH, f))
        compressed_css = compile_and_compress_scss(scss, path, name)
        utils.write_to_file('css', name, path, compressed_css)

def compile_scss_file(exclusions=list()):
    matches = utils.locate_files_to_compile('*.scss', exclusions)

    for path, f, name in matches:
        with open(os.path.join(sassy_coffee.DJANGO_PATH, f), 'r') as scss_file:
            compressed_css = compile_and_compress_scss(scss_file.read(), path, name)
            utils.write_to_file('css', name, path, compressed_css)

def compile_and_compress_scss(scss, path, name):
    scss_compiler = Scss()
    css = scss_compiler.compile(scss)
    return compress(css)

def compile_coffeescript(exclusions=list()):
    matches = utils.locate_files_to_compile('*.coffee', exclusions)

    for path, f, name in matches:
        js = coffeescript.compile_file(os.path.join(sassy_coffee.DJANGO_PATH, f), bare=True)
        compressed_js = minify(js)
        utils.write_to_file('js', name, path, compressed_js)
