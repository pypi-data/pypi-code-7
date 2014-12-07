from __future__ import print_function
import sugarcrm


URL = "http://van-sugarcrm.pbs.local/service/v4_1/rest.php"
USER = "Freddy"
PASS = "password"


session = sugarcrm.Session(URL, USER, PASS)

contact = session.get_entry("Contacts", "f3339b4e-bb65-de7a-5c1f-5474da774425")
print(contact.first_name, contact.last_name)

#note = sugarcrm.Note("Python Attachment Test Note")
#sugar.set_entry(note)
#print note.fields

#result = sugar.set_note_attachment(note, "README.rst")
#print result

#results = session.get_entries("Notes", "f0c78aab-e051-174a-12aa-5439a7146977")
#print len(results)
#print results

#q = sugarcrm.Note("Python%")
#results = sugar.get_entry_list(q)
#print results


#op = sugar.get_entry("Opportunities", "82f72939-735e-53a2-0944-5418c4edae2a")
#user = sugar.get_entry("Users", op.assigned_user_id)
#print user.email1


#o = sugarcrm.Opportunity()
#o.id = "82f72939-735e-53a2-0944-5418c4edae2a"
#o.sales_stage = "Turndown"
#sugar.set_entry(o)

#c = sugarcrm.Contact(first_name="Mylee")
#results = sugar.get_entry_list(c)
#print results

#results = sugar.get_available_modules()
#for m in results:
#    print m.module_key

#result = sugar.get_entry("Users", "3904589034850934905")
#print result
#
#result = sugar.get_entries("Users", ["2349230942","234283489234","2342893489"])
#print result
#
#q = sugarcrm.Note(name="Notfound%")
#results = sugar.get_entry_list(q)
#print results

#doc = sugarcrm.Document()
#doc.document_name = "Document Test"
#doc.revision = 1
#sugar.set_entry(doc)
#print doc.id
#print sugar.set_document_revision(doc, "../../work/optionpayportal/templates/pdf/ach_authorization.pdf")
#o = sugar.get_entry("Opportunities", "5b671886-cfe4-36f5-fa9d-5418a24e4aca")
#print o.id
#print sugar.set_relationship(o, doc)


# Extract all non-empty email fields from all Contacts in SugarCRM
#emails = set()
#contact_query = sugarcrm.Contact()  # No filters provider finds all objects
#contact_count = sugar.get_entries_count(contact_query, deleted=True)
#print "Extracting emails from %d Contacts" % contact_count
## Grab 100 Contact objects at a time from SugarCRM
#for offset in range(0, 500, 100):
#    contacts = sugar.get_entry_list(contact_query, deleted=True,
#                                    max_results=100, offset=offset)
#    for contact in contacts:
#        for field in dir(contact):
#            if field.find("email") >= 0 and getattr(contact, field, "").find("@") >= 0:
#                emails.add(getattr(contact, field).lower())
#print "Found %d emails" % len(emails)



#c = sugar.get_entry("Contacts", "4705da45-d8ef-d72c-cf95-53f50111d72d")


#q = sugarcrm.Lead()
#leads = sugar.get_entry_list(q, max_results=300)


## Get a list of contact id's attached to a lead
#links = {"Contacts": ['id', 'first_name', 'last_name']}
##links=[{'name': "contacts", 'value': ['id', 'first_name', 'last_name']}]
#note = sugar.get_entry("Leads", "d7dac88d-ce33-d98a-da8b-5418bba9e664", links=links)
#print note.contacts



#links = {"contact": ['id', 'first_name', 'last_name']}

#q = sugarcrm.Opportunity()
#q.module = "Opportunities"
#q.query = "opportunities.date_entered > '2014-09-01'"
#opps = sugar.get_entry_list(q, links=links, max_results=5)

#lead = sugar.get_entry("Leads", "a31ac8af-d971-aa4a-3bde-546e464f9153", links=links)
