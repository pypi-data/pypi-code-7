from datetime import date
import sugarcrm
import sys


if len(sys.argv) == 1:
    print "Enter some dates."
    exit()


class Lead:
    def __init__(self, lead):
        self.first_name = lead.first_name
        self.last_name = lead.last_name
        self.num_leads = 1
        self.status = lead.status
        self.contact_app = not bool(int(lead.phone_app_c) + int(lead.online_app_c))
        self.phone_app = bool(int(lead.phone_app_c))
        self.credit_app = bool(int(lead.online_app_c))
        self.contact_id = ""
        self.contact_number = ""
        self.mfs_opportunity = ""
        self.mfs_source = ""
        self.mfs_status = ""
        self.mfs_amount = 0.00
        self.mcs_opportunity = ""
        self.mcs_source = ""
        self.mcs_status = ""
        self.mcs_amount = 0.00
        self.other_opportunity = ""
        self.other_source = ""
        self.other_status = ""
        self.other_amount = 0.00
        if getattr(lead, 'contacts', False):
            self.contact_id = lead.contacts[0].id
            self.contact_number = lead.contacts[0].contact_nice_number_c
            qo = sugarcrm.Opportunity()
            t = lead.contacts[0].contact_nice_number_c
            qo.query = ("opportunities_cstm.contact_number_opp_c='%s' OR "
                        "opportunities_cstm.contact_number_opp_c='%s'"
                        % (t, "%s,%s" % (t[:len(t)-3], t[-3:])))
            for opp in sugar.get_entry_list(qo):
                print "Opportunity: %s (%s) $%.2f" % (opp.name, opp.sales_stage, float(opp.amount or 0.00))
                if opp.name.find("MFS") >= 0:
                    self.mfs_opportunity = opp.name
                    self.mfs_source = opp.lead_source
                    self.mfs_status = opp.sales_stage
                    self.mfs_amount = float(opp.amount or 0.00)
                elif opp.name.find("MCS") >= 0:
                    self.mcs_opportunity = opp.name
                    self.mcs_source = opp.lead_source
                    self.mcs_status = opp.sales_stage
                    self.mcs_amount = float(opp.amount or 0.00)
                else:
                    self.other_opportunity = opp.name
                    self.other_source = opp.lead_source
                    self.other_status = opp.sales_stage
                    self.other_amount = float(opp.amount or 0.00)

    def update(self, lead):
        self.first_name = lead.first_name
        self.last_name = lead.last_name
        self.num_leads += 1
        if lead.status == "Converted":
            self.status = lead.status
        elif lead.status == "Active" and self.status != "Converted":
            self.status = lead.status
        self.contact_app = int(self.contact_app) or not bool(int(lead.phone_app_c) + int(lead.online_app_c))
        self.phone_app = int(self.phone_app) or bool(int(lead.phone_app_c))
        self.credit_app = int(self.credit_app) or bool(int(lead.online_app_c))
        if getattr(lead, 'contacts', False):
            self.contact_id = lead.contacts[0].id
            self.contact_number = lead.contacts[0].contact_nice_number_c
            qo = sugarcrm.Opportunity()
            t = lead.contacts[0].contact_nice_number_c
            qo.query = ("opportunities_cstm.contact_number_opp_c='%s' OR "
                        "opportunities_cstm.contact_number_opp_c='%s'"
                        % (t, "%s,%s" % (t[:len(t)-3], t[-3:])))
            for opp in sugar.get_entry_list(qo):
                print "Opportunity: %s (%s) $%.2f" % (opp.name, opp.sales_stage, float(opp.amount or 0.00))
                if opp.name.find("MFS") >= 0 and float(opp.amount or 0.00) >= self.mfs_amount:
                    self.mfs_opportunity = opp.name
                    self.mfs_source = opp.lead_source
                    self.mfs_status = opp.sales_stage
                    self.mfs_amount = float(opp.amount or 0.00)
                elif opp.name.find("MCS") >= 0 and float(opp.amount or 0.00) >= self.mcs_amount:
                    self.mcs_opportunity = opp.name
                    self.mcs_source = opp.lead_source
                    self.mcs_status = opp.sales_stage
                    self.mcs_amount = float(opp.amount or 0.00)
                elif opp.amount >= float(self.other_amount or 0.00):
                    self.other_opportunity = opp.name
                    self.other_source = opp.lead_source
                    self.other_status = opp.sales_stage
                    self.other_amount = float(opp.amount or 0.00)


URL = "https://umtravel.sugarondemand.com/service/v4_1/rest.php"
USER = "Darryl"
PASS = "5a3767366132".decode('hex')

sugar = sugarcrm.API(URL, USER, PASS)

leads = {}

q = sugarcrm.Lead()
q.query = "leads.date_entered > '%s' and leads.date_modified <= '%s'" \
          % (sys.argv[1], sys.argv[2])

count = sugar.get_entries_count(q)
print "Querying %d leads between '%s' and '%s'" % (count, sys.argv[1], sys.argv[2])
links = {"Contacts": ['id', 'contact_nice_number_c']}
for offset in range(0, count, 100):
    results = sugar.get_entry_list(q, links=links, max_results=100, offset=offset)
    for lead in results:
        key = "%s_%s" % (lead.last_name.lower(), lead.first_name.lower())
        if key in leads:
            print "Duplicate Lead: %s, %s (%s)" % (lead.last_name, lead.first_name, lead.status)
            leads[key].update(lead)
        else:
            print "New Lead: %s, %s (%s)" % (lead.last_name, lead.first_name, lead.status)
            leads[key] = Lead(lead)


with open ("lead_data_%s_to_%s_on_%s.csv" % (sys.argv[1], sys.argv[2], str(date.today())), 'w') as out:
    out.write("first_name,last_name,lead_status,"
              "num_leads,contact_app,phone_app,credit_app,"
              "contact_id,contact_number,"
              "mfs_opportunity,mfs_source,mfs_status,mfs_amount,"
              "mcs_opportunity,mcs_source,mcs_status,mcs_amount,"
              "other_opportunity,other_source,other_status,other_amount\n")
    for lead in leads.values():
        out.write("%s,%s,%s,%d,%d,%d,%d,%s,%s,%s,%s,%s,%.2f,%s,%s,%s,%.2f,%s,%s,%s,%.2f\n"
                  % (lead.first_name, lead.last_name, lead.status,
                     lead.num_leads,lead.contact_app, lead.phone_app, lead.credit_app,
                     lead.contact_id, lead.contact_number,
                     lead.mfs_opportunity, lead.mfs_source, lead.mfs_status, lead.mfs_amount,
                     lead.mcs_opportunity, lead.mcs_source, lead.mcs_status, lead.mcs_amount,
                     lead.other_opportunity, lead.other_source, lead.other_status, lead.other_amount))
