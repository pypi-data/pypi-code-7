from bise.catalogueindexer.adapters.basic import PACDocumentCataloguer
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest


class FactsheetCataloguer(PACDocumentCataloguer):

    def get_values_to_index(self):
        request = getRequest()
        items = super(FactsheetCataloguer, self).get_values_to_index()
        view = getMultiAdapter((self.context, request), name='view')
        contents = u''
        for item in view.facts():
            for fact in item.get('facts'):
                contents += getMultiAdapter(
                    (fact.getObject(), request),
                    name='factrenderview')()

        items['article[content]'] = contents
        targets = []
        for target in self.context.targets:
            targets.append(target)
        items['article[target_list]'] = u','.join(targets)
        actions = []
        for action in self.context.actions:
            actions.append(action)
        items['article[action_list]'] = u','.join(actions)
        tags = []
        for tag in self.context.cataloguetags:
            tagid, tagname = tag.split('-')
            tags.append(tagname)
        items['article[tag_list]'] = u','.join(tags)        

        return items
