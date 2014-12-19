from blazeweb.routing import url_for
from webgrid import Column, LinkColumnBase, DateTimeColumn
from webgrid.blazeweb import Grid
from webhelpers.html.tags import link_to

from compstack.audit.model.entities import AuditRecord


class DiffColumn(LinkColumnBase):
    def create_url(self, record):
        return url_for(
            self.grid.diff_view,
            rev1=record.id,
        )


class AuditGrid(Grid):
    DateTimeColumn('Date', AuditRecord.createdts)
    Column('Comments', AuditRecord.comments)
    DiffColumn('Diff', AuditRecord.id, can_sort=False, link_label='Diff')

    def __init__(self, identifier=None, diff_view=None, **kwargs):
        self.audit_identifier = identifier
        self.diff_view = diff_view
        Grid.__init__(self, **kwargs)

    def query_base(self, has_sort, has_filters):
        query = Grid.query_base(self, has_sort, has_filters).add_columns(AuditRecord.id)

        return query.filter(
            AuditRecord.identifier == self.audit_identifier
        ) if self.audit_identifier else query
