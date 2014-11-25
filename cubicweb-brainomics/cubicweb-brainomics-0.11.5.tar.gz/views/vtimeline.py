"""cubicweb-vtimeline views/forms/actions/components for web ui"""
import json
from itertools import chain

from logilab.common.date import ustrftime

from cubicweb.utils import json_dumps
from cubicweb.predicates import is_instance

try:
    from cubes.vtimeline.views import VeriteCoTimelineJsonDataView, VeriteCoTimelineView
except ImportError:
    pass
else:
    class SubjectVeriteCoTimelineView(VeriteCoTimelineView):
        __select__ = is_instance('Subject')

        def js_story_factory(self, settings):
            return u'''$("a[href$=\'#entity-timeline-tab\']").on('shown.bs.tab', function() {
            if (cw.cubes.brainomics.timelineLoaded === undefined) {
                createStoryJS(%s);
                cw.cubes.brainomics.timelineLoaded = true;}});
            ''' % json_dumps(settings)


    class VeriteCoTimelineJsonDataView(VeriteCoTimelineJsonDataView):
        __select__ = is_instance('Subject')

        def call(self):
            dates = []
            # Date format is %Y,%m,%d for vtimeline sake
            d = {'timeline': {'headline': '', 'type': 'default', 'text': '', 'date': dates}}
            for entity in self.cw_rset.entities():
                # Subject dates
                for admission in entity.reverse_admission_of:
                    study = admission.admission_in[0]
                    for date, label in ((admission.admission_date, self._cw._('Admission in')),
                                        (admission.admission_end_date, self._cw._('Out of'))):
                        if not date:
                            continue
                        text = u'<p>%s - %s</p>' % (label, study.view('incontext'))
                        dates.append({'startDate': ustrftime(date, '%Y,%m,%d'),
                                      'headline': label,
                                      'text': text})
                    # Steps
                    for step in admission.reverse_step_of:
                        if step.step_date:
                            dates.append({'startDate': ustrftime(step.step_date, '%Y,%m,%d'),
                                          'headline': step.name,
                                          'text': u'<p>%s</p>' % study.view('incontext')})
                # Measures
                for measure in entity.reverse_concerns:
                    calendarable = measure.cw_adapt_to('ICalendarable')
                    # Measure adapter
                    if calendarable and calendarable.start:
                        dates.append({'startDate': ustrftime(calendarable.start, '%Y,%m,%d'),
                                      'headline': measure.view('incontext')})
                    # Fallback to assessment
                    elif measure.reverse_generates:
                        calendarable = measure.reverse_generates[0].cw_adapt_to('ICalendarable')
                        if calendarable and calendarable.start:
                            dates.append({'startDate': ustrftime(calendarable.start, '%Y,%m,%d'),
                                          'headline': measure.view('incontext')})
                # Diagnostics/Therapies
                for e in chain(entity.related_diagnostics, entity.related_therapies):
                    calendarable = e.cw_adapt_to('ICalendarable')
                    # Measure adapter
                    if calendarable and calendarable.start:
                        dates.append({'startDate': ustrftime(calendarable.start, '%Y,%m,%d'),
                                      'headline': e.view('incontext')})
                    # Drugtake
                    if e.cw_etype == 'Therapy':
                        for drugtake in e.reverse_taken_in_therapy:
                            date = drugtake.start_taking_date
                            if date:
                                dates.append({'startDate': ustrftime(date, '%Y,%m,%d'),
                                              'headline': drugtake.view('incontext')})
                # SurvivalData
                for surv in entity.reverse_survival_of:
                    if surv.lastnews_date:
                        title = []
                        for attr in ('state_at_lastnews', 'deceased', 'relapse_date'):
                            if getattr(surv, attr) is not None:
                                title.append('%s - %s' % (self._cw._(attr), getattr(surv, attr)))
                        dates.append({'startDate': ustrftime(surv.lastnews_date, '%Y,%m,%d'),
                                      'headline': '<br/>'.join(title)})
                # Add additional data
                self.additional_infos(entity, d)
            self.w(json.dumps(d))

        def additional_infos(self, entity, d):
            """ Allow to override this view with specific infos """
            pass


    def registration_callback(vreg):
        vreg.register(VeriteCoTimelineJsonDataView)
        vreg.register_and_replace(SubjectVeriteCoTimelineView, VeriteCoTimelineView)
