from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName
from bika.health.config import MENSTRUAL_STATUSES
import json


class CaseMenstrualStatusWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/casemenstrualstatuswidget",
        'helper_js': ("bika_health_widgets/casemenstrualstatuswidget.js",
                      "bika_health_widgets/patientmenstrualstatuswidget.js"),
        'helper_css': ("bika_health_widgets/casemenstrualstatuswidget.css",),
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        outvalues = []
        values = form.get(field.getName(), empty_marker)
        for value in values:
            outvalues.append({'FirstDayOfLastMenses': value.get('FirstDayOfLastMenses', ''),
                              'MenstrualCycleType': value.get('MenstrualCycleType', ''),
                              'Pregnant': bool(value.get('Pregnant', False)),
                              'MonthOfPregnancy': value.get('MonthOfPregnancy', '')})

        # Save patient's MenstrualStatus
        if 'PatientID' in form:
            patient = self.aq_parent.Schema()['Patient'].get(self.aq_parent)
            if patient:
                patient.Schema()['MenstrualStatus'].set(patient, [{
                  'Hysterectomy': bool(values[0].get('Hysterectomy', False)),
                  'HysterectomyYear': values[0].get('HysterectomyYear', ''),
                  'OvariesRemoved': bool(values[0].get('OvariesRemoved', False)),
                  'OvariesRemovedNum': int(value.get('OvariesRemovedNum', 0)),
                  'OvariesRemovedYear': values[0].get('OvariesRemovedYear', '')
                  }]
                )

        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)

    def getMenstrualStatusesList(self):
        statuses = {}
        for key in MENSTRUAL_STATUSES.keys():
            statuses[key] = MENSTRUAL_STATUSES.getValue(key)
        return statuses

    def getPatientsGender(self):
        gender = 'dk'
        patient = self.aq_parent.Schema()['Patient'].get(self.aq_parent)
        if patient:
            gender = patient.Schema()['Gender'].get(patient)
        return gender

    def getMenstrualStatus(self):

        statuses = {'FirstDayOfLastMenses':'',
                     'MenstrualCycleType': MENSTRUAL_STATUSES.keys()[0],
                     'Pregnant':False,
                     'MonthOfPregnancy':0,
                     'Hysterectomy': False,
                     'HysterectomyYear': '',
                     'OvariesRemoved': False,
                     'OvariesRemovedNum': 0,
                     'OvariesRemovedYear': ''}

        # Fill with patient's Menstrual status info
        patient = self.aq_parent.Schema()['Patient'].get(self.aq_parent)
        if patient:
            pms = self.aq_parent.Schema()['MenstrualStatus'].get(self.aq_parent)
            if pms:
                statuses = dict(statuses.items() + pms[0].items())

        cms = self.aq_parent.Schema()['MenstrualStatus'].get(self.aq_parent)
        if cms:
            statuses = dict(statuses.items() + cms[0].items())

        return [statuses]

registerWidget(CaseMenstrualStatusWidget,
               title='CaseMenstrualStatusWidget',
               description='Menstrual status information',
               )
