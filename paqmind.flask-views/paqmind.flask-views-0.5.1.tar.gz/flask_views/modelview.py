import re
import datetime
import simplejson as json
import copy

from collections import OrderedDict
from jinja2 import TemplateNotFound
from paqforms import variable_decode
from flask import g, request, Response, abort, render_template
from flask.ext.routes import route

from .view import View
from .utils import dashify, Paginator


class ModelView(View):
    # BASE
    model_name = None
    public_index = 'index'
    private_index = 'index'
    perpage = 20
    filterform = None
    sortform = None
    get_filters = None
    get_sorts = None
    create_form_class = None
    edit_form_class = None

    # TEMPLATES
    templates = {
        # Custom by default
        'index': '{model}/index.html',
        'card': '{model}/card.html',
        'create': '{model}/form.html',
        'edit': '{model}/form.html',
        'detail': '{model}/detail.html',
        'pdf': '{model}/pdf.html',
        'txt': '{model}/txt.html',

        # General by default
        'index_or_detail': 'model/index-or-detail.html',
        'tab_filters': 'model/tab.filters.html',
        'tab_sorts': 'model/tab.sorts.html',
        'tab_perpage': 'model/tab.perpage.html',
        'tab_create': 'model/tab.create.html',
        'filters': 'model/filters.html',
        'loop': 'model/loop.html',
        'pagination': 'model/pagination.html',
    }


    def __init__(self, bp):
        View.__init__(self, bp)

        self.model_name = dashify(self.model_name or re.sub('View$', '', self.__class__.__name__))

        self.coreattrs = dict(
            endpoint = self.endpoint,
            model = self.model_name
        )
        self.coreattrs['bp'] = self.bp.name

        self.templates = {
            key: value.format(**self.coreattrs)
            if value else value for (key, value)
            in self.templates.items()
        }


    # ROUTES -------------------------------------------------------------------
    @route('/', endpoint='{view}:index', methods=('GET', 'POST'))
    @route('/index.json', endpoint='{view}:index_json', methods=('GET', 'POST'))
    @route('/index.html', endpoint='{view}:index_html', methods=('GET', 'POST'))
    def index(self):
        return self._index('index')


    @route('/<id:id>/detail', endpoint='{view}:detail')
    @route('/<id:id>/detail.json', endpoint='{view}:detail_json')
    @route('/<id:id>/detail.pdf', endpoint='{view}:detail_pdf')
    @route('/<id:id>/detail.txt', endpoint='{view}:detail_txt')
    @route('/<id:id>/detail.html', endpoint='{view}:detail_html')
    @route('/<id:id>/card.html', endpoint='{view}:card_html')
    def detail(self, id):
        return self._detail(id)


    @route('/create', methods=('GET', 'POST'))
    def create(self):
        return self._create()


    @route('/<id:id>/edit', methods=('GET', 'POST'))
    def edit(self, id):
        return self._edit(id)


    @route('/delete', methods=('POST',))
    @route('/<id:id>/delete', methods=('POST',))
    def delete(self, id=None):
        return self._delete(id)


    @route('/archive', methods=('POST',))
    @route('/<id:id>/archive', methods=('POST',))
    def archive(self, id):
        return self._archive(id)


    # ACTIONS (ROUTES + IMPLEMENTATIONS) ---------------------------------------
    @route('/set-continue', methods=('POST',))
    def set_continue(self):
        self.session['continue'] = request.form.get('value', 'edit')
        return Response(status=204)


    # IMPLEMENTATIONS ----------------------------------------------------------
    def _index(self, index):
        if not self.allows(index):
            raise abort(403)

        filters, filterform = self.do_filter(self.filterform, index)
        sorts, sortform = self.do_sort(self.sortform, index)
        cursor = self.do_cursor(filters, sorts)
        paginator, redirect = self.do_paginate(cursor, index)
        if redirect:
            return redirect
        data = self.after_paginate(paginator, index)

        try:
            if request.path.endswith('.json'):
                models = [model for model in paginator.models if self.allows('detail', model)]
                return self.jsonify(
                    models = models,
                    total = paginator.total,
                    **data
                )
            elif request.path.endswith('.html'):
                return self.jsonify(
                    total = paginator.total,
                    tab_html = self.render('tab_sorts',
                        index = index,
                        sortform = sortform,
                        **data
                    ),
                    data_html = self.render('loop',
                        index = index,
                        filterform = filterform,
                        sortform = sortform,
                        paginator = paginator,
                        **data
                    ),
                    flash_html = '',
                    redirect = None,
                )
            else:
                return self.render('index',
                    index = index,
                    filterform = filterform,
                    sortform = sortform,
                    paginator = paginator,
                    **data
                )
        except TemplateNotFound as e:
            self.bp.logger.warn(
                '[{method} {path}]: template {template!r} is not found'.format(
                    method=request.method, path=request.path, template=str(e)
                )
            )
            raise abort(404)


    def _detail(self, id):
        model, data = self.detail_model(id)
        if not self.allows('detail', model):
            raise abort(403)

        try:
            if request.path.endswith('.json'):
                return self.jsonify(
                    model = model
                )
            elif request.path.endswith('.pdf'):
                    return self.render('pdf',
                        model = model,
                        **data
                    )
            elif request.path.endswith('.txt'):
                return self.render('txt',
                    model = model,
                    **data
                )
            elif request.path.endswith('.html'):
                data_html = self.render('card',
                    model = model,
                    **data
                )
                return self.jsonify(
                    data_html = data_html,
                    flash_html = '',
                    redirect = None
                )
            else:
                return self.render('detail',
                    model = model,
                    **data
                )
        except TemplateNotFound as e:
            self.bp.logger.warn(
                '[{method} {path}]: template {template!r} is not found'.format(
                    method=request.method, path=request.path, template=str(e)
                )
            )
            raise abort(404)


    def _create(self):
        model, data = self.create_model()
        if not self.allows('create', model):
            raise abort(403)

        form = self.create_form_class(model, request.form)
        if form.ok:
            self.do_create(model, form)
            return self.autoredirect(model.id)

        return self.render('create',
            model = model,
            form = form,
            **data
        )


    def _edit(self, id):
        model, data = self.edit_model(id)
        if not self.allows('edit', model):
            raise abort(403)

        form = self.edit_form_class(model, request.form)
        if form.ok:
            self.do_edit(model, form)
            return self.autoredirect(model.id)

        return self.render('edit',
            model = model,
            form = form,
            **data
        )


    def _delete(self, id):
        model, _ = self.detail_model(id=id)
        if not self.allows('delete', model):
            raise abort(403)
        self.do_delete([model])
        flash_html = render_template('alerts.html')
        redirect = request.args.get('redirect')

        return self.jsonify(
            data_html = '',
            flash_html = flash_html,
            redirect = redirect
        )


    def _archive(self, id):
        model, _ = self.detail_model(id)
        if not g.user.allowed(self.endpoint + '.archive', model):
            raise abort(403)
        self.do_archive([model])
        flash_html = render_template('alerts.html')
        redirect = request.args.get('redirect')

        return self.jsonify(
            data_html = '',
            flash_html = flash_html,
            redirect = redirect
        )


    # HOOKS --------------------------------------------------------------------
    def do_filter(self, form, index):
        if form:
            form_class = form.__class__
            default_value = copy.deepcopy(form.feed_value)

            action = request.form.get('action') or request.args.get('action')
            inputfilters = variable_decode(request.args).get('filters', {})
            inputfilters.update(variable_decode(request.form).get('filters', {}))

            if action == 'filters.apply':
                form = form_class({}, inputfilters, submit=True)
                if not form.has_error:
                    self.session.setdefault(index, {})['filters'] = inputfilters
            elif action == 'filters.reset':
                form = form_class(default_value, submit=False)
                try: del self.session[index]['filters']
                except: pass
            elif inputfilters:
                form = form_class({}, inputfilters)
            else:
                # Use session
                data = self.session.get(index, {}).get('filters', default_value)
                form = form_class({}, data)

            filters = {} if form.has_error else self.get_filters(form)
        else:
            filters = {}
            form = None

        return filters, form


    def do_sort(self, form, index):
        if form:
            form_class = form.__class__
            default_value = copy.deepcopy(form.feed_value)

            action = request.form.get('action') or request.args.get('action')
            inputsorts = variable_decode(request.args).get('sorts', {})
            inputsorts.update(variable_decode(request.form).get('sorts', {}))
            fields = request.form.get('fields') or request.args.get('fields')

            if action == 'sorts.apply':
                form = form_class({}, inputsorts, submit=True)
                if request.form.get('fields'):
                    form.fields = OrderedDict([(name, form.fields[name]) for name in request.form.get('fields').split(' ')])
                if not form.has_error:
                    self.session.setdefault(index, {})['sorts'] = inputsorts
                    self.session[index]['fields'] = fields
            elif action == 'sorts.reset':
                form = form_class(default_value)
                try: del self.session[index]['sorts']
                except: pass
                try: del self.session[index]['fields'];
                except: pass
            elif inputsorts:
                form = form_class({}, inputsorts)
            else:
                # Use session
                data = self.session.get(index, {}).get('sorts', default_value)
                form = form_class({}, data)
                if self.session.get(index, {}).get('fields'):
                    form.fields = OrderedDict([(name, form.fields[name]) for name in self.session.get(index, {}).get('fields').split(' ')])

            sorts = [] if form.has_error else self.get_sorts(form)
        else:
            sorts = []
            form = None

        return sorts, form


    def force_filters(self, index, filters):
        pass


    def do_cursor(self, filters, sorts):
        raise Exception('Define `{}.do_cursor` method'.format(self.__class__.__name__))


    def do_paginate(self, cursor, index):
        page = request.args.get('page', type=int)
        if page is None:
            page = 1
        elif page == 1 and not request.is_xhr:
            return None, self.redirect(index)

        action = request.form.get('action') or request.args.get('action')
        if request.is_xhr and request.path.endswith('.json'):
            perpage = request.form.get('perpage', type=int) or request.args.get('perpage', type=int) or 999
        else:
            perpage = request.form.get('perpage', type=int) or request.args.get('perpage', type=int) or self.perpage
        limit = request.form.get('limit', False, type=bool) or request.args.get('perpage', type=bool)

        if action == 'paginate':
            if perpage:
                self.session['perpage'] = perpage
            elif perpage == 0:
                self.session.pop('perpage')
        else:
            # Use session
            perpage = self.session.get('perpage', perpage)

        paginator = Paginator(cursor, page, perpage)
        if limit:
            paginator.show = False

        if paginator.pages and page > paginator.pages:
            return None, self.redirect(index, page=paginator.pages)
        return paginator, None


    def after_paginate(self, paginator, index):
        return {}


    def detail_model(self, id):
        raise Exception('Define `{}.detail_model` method'.format(self.__class__.__name__))


    def create_model(self):
        raise Exception('Define `{}.create_model` method'.format(self.__class__.__name__))


    def edit_model(self, id):
        raise Exception('Define `{}.edit_model` method'.format(self.__class__.__name__))


    def do_create(self, model, form):
        raise Exception('Define `{}.do_create` method'.format(self.__class__.__name__))


    def do_edit(self, model, form):
        raise Exception('Define `{}.do_edit` method'.format(self.__class__.__name__))


    def do_delete(self, models):
        raise Exception('Define `{}.do_delete` method'.format(self.__class__.__name__))


    def do_archive(self, models):
        raise Exception('Define `{}.do_archive` method'.format(self.__class__.__name__))


    # HELPERS ------------------------------------------------------------------
    def allows(self, action, models=[], with_filters=True):
        if hasattr(self, action) and getattr(self, action) and getattr(getattr(self, action), 'routable', False):
            return g.user.allowed(
                '{}.{}'.format(self.endpoint, action), models, with_filters=with_filters
            )
        else:
            return False


    def autoredirect(self, model_id):
        continue_ = request.form.get('continue') or request.args.get('continue') or self.session.get('continue') or 'edit'
        if continue_ == 'edit':
            return self.redirect('edit', id=model_id)
        elif continue_ == 'create':
            return self.redirect('create')
        elif continue_ == 'index':
            index = self.private_index or self.public_index or 'home'
            return self.redirect(index)
        else:
            raise RuntimeError('Unknown `continue` value {!r}'.format(_continue))


    def jsonify(self, *args, **kwargs):
        return Response(
            json.dumps(dict(*args, **kwargs)), mimetype='application/json'
        )
