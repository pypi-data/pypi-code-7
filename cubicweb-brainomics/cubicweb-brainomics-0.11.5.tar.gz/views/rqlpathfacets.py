"""
Backport from CW 3.19 (0509880fec01)
This should be removed once SuiviMP switch to 3.19 (currently 3.18)
"""

from rql import nodes
from cubicweb.web.facet import RQLPathFacet, DateRangeFacet, cleanup_select, _get_var


class AbstractRangeRQLPathFacet(RQLPathFacet):
    """
    The :class:`AbstractRangeRQLPathFacet` is the base class for
    RQLPathFacet-type facets allowing the use of RangeWidgets-like
    widgets (such as (:class:`FacetRangeWidget`,
    class:`DateFacetRangeWidget`) on the parent :class:`RQLPathFacet`
    target attribute.
    """
    __abstract__ = True
    dynamic_facet = False

    def vocabulary(self):
        """return vocabulary for this facet, eg a list of (label,
        value)"""
        select = self.select
        select.save_state()
        try:
            filtered_variable = self.filtered_variable
            cleanup_select(select, filtered_variable)
            varmap, restrvar = self.add_path_to_select()
            if self.label_variable:
                attrvar = varmap[self.label_variable]
            else:
                attrvar = restrvar
            # start RangeRQLPathFacet
            minf = nodes.Function('MIN')
            minf.append(nodes.VariableRef(restrvar))
            select.add_selected(minf)
            maxf = nodes.Function('MAX')
            maxf.append(nodes.VariableRef(restrvar))
            select.add_selected(maxf)
            # add is restriction if necessary
            if filtered_variable.stinfo['typerel'] is None:
                etypes = frozenset(sol[filtered_variable.name] for sol in select.solutions)
                select.add_type_restriction(filtered_variable, etypes)
            # end RangeRQLPathFacet
            try:
                # this line is to be reported in cw 3.19.0
                args = self.cw_rset.args if self.cw_rset else None
                rset = self.rqlexec(select.as_string(), args)
            except Exception:
                self.exception('error while getting vocabulary for %s, rql: %s',
                               self, select.as_string())
                return ()
        finally:
            select.recover()
        # don't call rset_vocabulary on empty result set, it may be an empty
        # *list* (see rqlexec implementation)
        if rset:
            minv, maxv = rset[0]
            return [(unicode(minv), minv), (unicode(maxv), maxv)]
        return []


    def possible_values(self):
        """return a list of possible values (as string since it's used to
        compare to a form value in javascript) for this facet
        """
        return [strval for strval, val in self.vocabulary()]

    def add_rql_restrictions(self):
        infvalue = self.infvalue()
        supvalue = self.supvalue()
        if infvalue is None or supvalue is None: # nothing sent
            return
        varmap, restrvar = self.add_path_to_select(
            skiplabel=True, skipattrfilter=True)
        restrel = None
        for part in self.path:
            if isinstance(part, basestring):
                part = part.split()
            subject, rtype, object = part
            if object == self.filter_variable:
                restrel = rtype
        assert restrel
        # when a value is equal to one of the limit, don't add the restriction,
        # else we filter out NULL values implicitly
        if infvalue != self.infvalue(min=True):
            self._add_restriction(infvalue, '>=', restrvar, restrel)
        if supvalue != self.supvalue(max=True):
            self._add_restriction(supvalue, '<=', restrvar, restrel)

    def _add_restriction(self, value, operator, restrvar, restrel):
        self.select.add_constant_restriction(restrvar,
                                             restrel,
                                             self.formatvalue(value),
                                             self.target_attr_type, operator)

    def add_path_to_select(self, skiplabel=False, skipattrfilter=False):
        varmap = {'X': self.filtered_variable}
        actual_filter_variable = None
        for part in self.path:
            if isinstance(part, basestring):
                part = part.split()
            subject, rtype, object = part
            if skiplabel and object == self.label_variable:
                continue
            if object == self.filter_variable:
                rschema = self._cw.vreg.schema.rschema(rtype)
                if rschema.final:
                    # filter variable is an attribute variable
                    if self.restr_attr is None:
                        self.restr_attr = rtype
                    if self.restr_attr_type is None:
                        attrtypes = set(obj for subj,obj in rschema.rdefs)
                        if len(attrtypes) > 1:
                            raise Exception('ambigous attribute %s, specify attrtype on %s'
                                            % (rtype, self.__class__))
                        self.restr_attr_type = iter(attrtypes).next()
                    if skipattrfilter:
                        actual_filter_variable = subject
                        continue
            subjvar = _get_var(self.select, subject, varmap)
            if rtype == 'eid' and self.dynamic_facet:
                # Keep eid restriction for dynamic variable
                rel = nodes.make_constant_restriction(subjvar, 'eid', object, 'Int')
            else:
                objvar = _get_var(self.select, object, varmap)
                rel = nodes.make_relation(subjvar, rtype, (objvar,),
                                          nodes.VariableRef)
            self.select.add_restriction(rel)
        if self.restr_attr is None:
            self.restr_attr = 'eid'
        if self.restr_attr_type is None:
            self.restr_attr_type = 'Int'
        if actual_filter_variable:
            restrvar = varmap[actual_filter_variable]
        else:
            restrvar = varmap[self.filter_variable]
        return varmap, restrvar


class RangeRQLPathFacet(AbstractRangeRQLPathFacet, RQLPathFacet):
    """
    The :class:`RangeRQLPathFacet` uses the :class:`FacetRangeWidget`
    on the :class:`AbstractRangeRQLPathFacet` target attribute
    """
    pass


class DateRangeRQLPathFacet(AbstractRangeRQLPathFacet, DateRangeFacet):
    """
    The :class:`DateRangeRQLPathFacet` uses the
    :class:`DateFacetRangeWidget` on the
    :class:`AbstractRangeRQLPathFacet` target attribute
    """
    pass
