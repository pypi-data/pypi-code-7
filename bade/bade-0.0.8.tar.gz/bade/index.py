import os
import subprocess

from . import utils


class BadeIndex(object):

    def __init__(self, config):
        self.config = config
        self.pages, self.nav = self.page_indexes()
        self.posts = self.posts_index()
        self.blogtree = self._blogtree()

    def page_indexes(self):
        pages = dict()
        nav = [{'title': 'Home', 'path': '/'}]
        found_blog = False
        for page in self.config.pages:
            if isinstance(page, str):
                page_meta = {
                    'title': utils.rst_title(page),
                    'path': self.page_path(page),
                }
                nav.append(page_meta)
                page_meta.update({
                    'build': self.page_build(page),
                })
                pages[page] = page_meta
            elif isinstance(page, dict):
                title, path = page.popitem()
                nav.append({'title': title, 'path': path})
                if title.lower() == 'blog':
                    found_blog = True
        if found_blog is not True:
            nav.append({'title': 'Blog', 'path': '/blog.html'})
        return pages, nav

    def posts_index(self):
        return_dict = dict()
        find = ['find', self.config.blogroot, '-name', '*.rst']
        try:
            paths_list = (subprocess.check_output(find,
                                                  stderr=subprocess.STDOUT)
                                    .decode('utf-8')
                                    .split())
        except subprocess.CalledProcessError:
            paths_list = list()
        for idx, rst_path in enumerate(paths_list):
            if idx == 0:
                prev_post = None
            else:
                prev_post = {
                    'title': utils.rst_title(paths_list[idx - 1]),
                    'path': self.post_path(paths_list[idx - 1]),
                }
            if idx == (len(paths_list) - 1):
                next_post = None
            else:
                next_post = {
                    'title': utils.rst_title(paths_list[idx + 1]),
                    'path': self.post_path(paths_list[idx + 1]),
                }
            return_dict[rst_path] = {
                'date': utils.post_date(rst_path),
                'title': utils.rst_title(rst_path),
                'build': self.post_build(rst_path),
                'path': self.post_path(rst_path),
                'next_post': next_post,
                'prev_post': prev_post,
            }
        return return_dict

    def _blogtree(self):
        'Monthly dict of posts'
        D = utils.OrderedDefaultdict
        blogtree = D(lambda: D(list))
        for postpath in self.posts:
            date = utils.post_date(postpath)
            blogtree[date.year][date.month].append({
                'title': utils.rst_title(postpath),
                'path': self.post_path(postpath),
            })
        return blogtree

    def navigation(self):
        'Return index of all pages and posts'
        return {'blogtree': self.blogtree, 'pages': self.pages}

    def page_build(self, rst_path):
        'Return the page to write a rendered post'
        _, page_name = os.path.split(rst_path)
        return os.path.join(self.config.build, page_name + '.html')

    def page_path(self, rst_path):
        'Return the path for href to page'
        return self.page_build(rst_path).replace(self.config.build, '')

    def post_build(self, rst_path):
        'Return the path to write a rendered post'
        return (rst_path[:-4] + '.html').replace(self.config.blogroot,
                                                 self.config.build)

    def post_path(self, rst_path):
        'Return the path for href to post'
        return self.post_build(rst_path).replace(self.config.build, '')

    def fresh_context(self):
        'Return a fresh context with references to nav, blogtree'
        return {
            'nav': self.nav,
            'blogtree': self.blogtree,
        }

    def page_context(self, rst_path):
        'Template context for a page'
        context = self.fresh_context()
        context.update(self.pages[rst_path])
        return context, self.page_build(rst_path)

    def post_context(self, rst_path):
        'Template context for a post'
        context = self.fresh_context()
        context.update(self.posts[rst_path])
        return context, self.post_build(rst_path)
