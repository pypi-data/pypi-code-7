from blazeweb.utils import abort
import difflib
import re

from compstack.audit.model.entities import AuditRecord


class AuditDiffMixin(object):
    def init(self, ident_mask=None, page_title=None, extend_from=None):
        self.extend_from = extend_from
        self.page_title = page_title or 'Change History'
        self.ident_mask = re.compile('{0}-\d+'.format(ident_mask))
        self._auth_calculated = False

    def auth_calculate(self, rev1, rev2=None):
        # this could be a secure view, so call parent's method
        #   if not, _auth_calculated will make sure this gets processed
        try:
            super(AuditDiffMixin, self).auth_calculate()
        except AttributeError:
            pass

        self.ar = AuditRecord.get(rev1)
        if not self.ar:
            abort(404)
        if not re.match(self.ident_mask, self.ar.identifier):
            abort(400)
        self._auth_calculated = True

    def default(self, rev1, rev2=None):
        if not self._auth_calculated:
            self.auth_calculate(rev1, rev2)

        prev_ar = AuditRecord.get(rev2) if rev2 else self.ar.get_previous_record()

        diff_text = []
        a = prev_ar.full_text.splitlines(True) if prev_ar else []
        b = self.ar.full_text.splitlines(True)
        diff = difflib.SequenceMatcher(None, a, b)
        # op is tuple: (opcode, prev_ar_begin, prev_ar_end, ar_begin, ar_end)
        for op in diff.get_opcodes():
            if op[0] == "replace":
                diff_text.append(
                    '<del class="audit">' + ''.join(a[op[1]:op[2]]) +
                    '</del><ins class="audit">' + ''.join(b[op[3]:op[4]]) +
                    '</ins>'
                )
            elif op[0] == "delete":
                diff_text.append('<del class="audit">' + ''.join(a[op[1]:op[2]]) + '</del>')
            elif op[0] == "insert":
                diff_text.append('<ins class="audit">' + ''.join(b[op[3]:op[4]]) + '</ins>')
            elif op[0] == "equal":
                diff_text.append(''.join(b[op[3]:op[4]]))

        self.assign('diff_text', ''.join(diff_text))
        self.assign('extend_from', self.extend_from)
        self.assign('page_title', self.page_title)
        self.assign('old_rev_ts', prev_ar.createdts if prev_ar else None)
        self.assign('new_rev_ts', self.ar.createdts)
        self.render_endpoint('audit:audit_diff.html')
