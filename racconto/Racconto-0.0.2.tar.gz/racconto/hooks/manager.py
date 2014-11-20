class HooksManager(object):

    after_all_hooks = []
    before_all_hooks = []
    after_each_hooks = []
    before_each_hooks = []

    @classmethod
    def run_after_all_hooks(cls, pages, posts):
        for func in cls.after_all_hooks:
            func(pages, posts)

    @classmethod
    def run_before_all_hooks(cls, pages, posts):
        for func in cls.before_all_hooks:
            func(pages, posts)

    @classmethod
    def run_before_each_hooks(cls, page_or_post):
        for func in cls.before_each_hooks:
            func(page_or_post)

    @classmethod
    def run_after_each_hooks(cls, page_or_post):
        for func in cls.after_each_hooks:
            func(page_or_post)

    @classmethod
    def register_after_all_hook(cls, func=None):
        """ Registers function as an after all hook """
        if hasattr(func, '__call__'):
            cls.after_all_hooks.append(func)
        return func

    @classmethod
    def register_after_each_hook(cls, func=None):
        """ Registers function as an after each hook """
        if hasattr(func, '__call__'):
            cls.after_each_hooks.append(func)
        return func

    @classmethod
    def register_before_each_hook(cls, func=None):
        """ Registers function as an after each hook """
        if hasattr(func, '__call__'):
            cls.before_each_hooks.append(func)
        return func

    @classmethod
    def register_before_all_hook(cls, func=None):
        """ Registers function as an before all hook """
        if hasattr(func, '__call__'):
            cls.before_all_hooks.append(func)
        return func
