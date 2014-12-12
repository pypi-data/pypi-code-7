from __future__ import unicode_literals
import datetime
import os
import multiprocessing
import shutil
import subprocess

from docutils.core import publish_parts as docutils_publish
from mako import exceptions

from .utils import OrderedDefaultdict


def render_rst(rst_path):
    with open(rst_path, 'r') as rst_file:
        rst_string = rst_file.read()
    return docutils_publish(rst_string, writer_name='html')['html_body']


class Build(object):

    def __init__(self, config):
        'Create config, build blog tree'
        self.config = config
        find = ['find', self.config.blogroot, '-name', '*.rst']
        self.posts = sorted(subprocess.check_output(find)
                                      .decode('utf-8')
                                      .split(),
                            reverse=True)
        self.blogtree = self._blogtree()

    def clean(self):
        'Carelessly wipe out the build dir'
        shutil.rmtree(self.config.build, ignore_errors=True)

    def render_err(self, name, context):
        'Render a template, with some debugging'
        template = self.config.template_lookup.get_template(name)
        try:
            return template.render(**context), None
        except:
            if self.config.debug:
                error_html = (exceptions.html_error_template()
                                        .render()
                                        .decode('utf-8'))
                return error_html, True
            raise

    def write_html(self, template, context, buildpath):
        html, err = self.render_err(template, context)
        htmldir = os.path.dirname(buildpath)
        if not os.path.exists(htmldir) and htmldir:
            os.makedirs(htmldir)
        with open(buildpath, 'w') as htmlfile:
            htmlfile.write(html)
        if err:
            print("Debug HTML written to: {0}".format(buildpath))
        else:
            print("Writing to: {0}".format(buildpath))

    def build_copy_dir(self, dir_):
        print
        shutil.copytree(dir_, os.path.join(self.config.build, dir_))

    def title_buildpath(self, root, rst_path):
        bare_path, ext = os.path.splitext(rst_path)
        slug = os.path.split(bare_path)[-1]
        title = ' '.join(slug.split('-')).capitalize()
        buildpath = (bare_path + '.html').replace(root or self.config.blogroot,
                                                  self.config.build)
        return title, buildpath

    def prev_next(self, rst_path):
        try:
            next_index = self.posts.index(rst_path) - 1
            if next_index < 0:
                nextpath = nexttitle = None
            else:
                nexttitle, nextpath = self.title_buildpath(None, self.posts[next_index])
                nextpath = nextpath.replace('_build', '')
        except IndexError:
            nextpath = nexttitle = None
        try:
            previoustitle, previouspath = self.title_buildpath(None, self.posts[self.posts.index(rst_path) + 1])
            previouspath = previouspath.replace('_build', '')
        except IndexError:
            previouspath = previoustitle = None
        return previouspath, previoustitle, nextpath, nexttitle

    def parse_meta(self, rst_path):
        title, buildpath = self.title_buildpath(None, rst_path)
        previouspath, previoustitle, nextpath, nexttitle = self.prev_next(rst_path)
        git_cmd = [
            'git',
            'log',
            '-n',
            '1',
            '--pretty=format:%h',
            '--',
            rst_path
        ]
        latest_commit = subprocess.check_output(git_cmd).decode('utf-8')
        return {
            'date': datetime.date(*map(int, rst_path.split(os.sep)[1:4])),
            'title': title,
            'buildpath': buildpath,
            'nextpath': nextpath,
            'nexttitle': nexttitle,
            'previouspath': previouspath,
            'previoustitle': previoustitle,
            'github': os.path.join(self.config.github,
                                   'blob',
                                   'master',
                                   rst_path),
            'commit': latest_commit,
        }

    def _blogtree(self):
        D = OrderedDefaultdict
        blogtree = D(lambda: D(list))
        for rst_path in self.posts:
            meta = self.parse_meta(rst_path)
            date = datetime.date(*map(int, rst_path.split(os.sep)[1:4]))
            meta['date'] = date
            blogtree[date.year][date.month].append(meta)
        return blogtree

    def build_page(self, rst_path):
        pageroot = os.path.dirname(rst_path)
        title, buildpath = self.title_buildpath(pageroot, rst_path)
        context = {
            'meta': {'index': self.blogtree, 'title': title},
            'content_html': render_rst(rst_path),
        }
        self.write_html('page.html', context, buildpath)

    def iter_posts(self, rst_path, direction):
        post_index = self.posts.index(rst_path)
        iter_to = post_index + direction
        if iter_to < 0:
            return None
        if iter_to == len(self.posts):
            return None
        return self.parse_meta(self.posts[iter_to])

    def build_post(self, rst_path):
        context = {
            'next_post': self.iter_posts(rst_path, -1),
            'previous_post': self.iter_posts(rst_path, +1),
            'blogtree': self.blogtree,
            'meta': self.parse_meta(rst_path),
            'content_html': render_rst(rst_path),
        }
        buildpath = context['meta']['buildpath']
        self.write_html('post.html', context, buildpath)

    def build_blog_page(self, blog_template):
        buildpath = (os.path.join(self.config.build, blog_template)
                            .replace('rst', 'html'))
        index_rst, _ = self.render_err(blog_template, {'index': self.blogtree})
        content_html = docutils_publish(index_rst, writer_name='html')['html_body']
        context = {
            'index': self.blogtree,
            'meta': {'title': 'Blog'},
            'content_html': content_html,
        }
        self.write_html('page.html', context, buildpath)

    def build_pages(self, pool):
        pool.map_async(self.build_page, self.config.pages)

    def build_posts(self, pool):
        pool.map_async(self.build_post, self.posts)

    def process_sass(self):
        subprocess.check_call(['sass', self.config.sasspath, '_build/assets/css'])

    def run(self):
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        if self.config.debug:
            pass
        pool.map_async = lambda fn, *it: list(map(fn, *it))
        pool.map_async(self.build_copy_dir, self.config.assetpaths)
        self.build_pages(pool)
        self.build_posts(pool)
        shutil.copy('templates/index.html', self.config.build)
        self.build_blog_page('blog.rst')

        pool.close()
        pool.join()
        subprocess.check_call([
            'sass',
            self.config.sassin,
            os.path.join(self.config.build, self.config.sassout)
        ])
        print('done.')
