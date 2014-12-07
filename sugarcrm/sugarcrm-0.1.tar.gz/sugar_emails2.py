import codecs
import csv
import sugarcrm


#URL = "http://van-sugarcrm.pbs.local/service/v4_1/rest.php"
#USER = "Freddy"
#PASS = "password"

URL = "https://umtravel.sugarondemand.com/service/v4_1/rest.php"
USER = "Darryl"
PASS = "5a3767366132".decode('hex')

sugar = sugarcrm.API(URL, USER, PASS)


old_emails = set()
for f in ["emails.csv", "ref_emails.csv", "emails2.csv", "ref_emails2.csv", "emails3.csv", "ref_emails3.csv"]:
    with open(f, 'r') as csvfile:
        for row in csv.reader(csvfile, delimiter=","):
            old_emails.add(row[0])
print "%d emails already exported." % len(old_emails)

emails = {}
refs = {}

q = lambda: 0
q.module = "Contacts"
q.query = "contacts.date_entered >= '2014-11-18 00:00:00'"

count = sugar.get_entries_count(q)
print "Extracting emails from %d new Contacts" % count
for offset in range(0, count, 100):
    print "Offset: %s, Emails: %d, Refs: %d" % (offset, len(emails), len(refs))
    contacts = sugar.get_entry_list(q, max_results=100, offset=offset, deleted=True)
    for contact in contacts:
        for field in dir(contact):
            if field.find("email") >= 0 and getattr(contact, field, "").find("@") >= 0:
                if getattr(contact, field, None) and getattr(contact, field).upper() not in old_emails:
                    if field.find("coborrower") >= 0  or field.find("ref") >= 0:
                        refs[getattr(contact, field).upper()] = (contact.first_name, contact.last_name)
                    else:
                        emails[getattr(contact, field).upper()] = (contact.first_name, contact.last_name)

q.module = "Leads"
q.query = "leads.date_entered >= '2014-11-18 00:00:00'"
count = sugar.get_entries_count(q)
print "Extracting emails from %d new Leads" % count
for offset in range(0, count, 100):
    print "Offset: %s, Emails: %d, Refs: %d" % (offset, len(emails), len(refs))
    leads = sugar.get_entry_list(q, max_results=100, offset=offset, deleted=True)
    for lead in leads:
        for field in dir(lead):
            if field.find("email") >= 0 and getattr(lead, field, "").find("@") >= 0:
                if getattr(lead, field, None) and getattr(lead, field).upper() not in old_emails:
                    if field.find("coborrower") >= 0  or field.find("ref") >= 0:
                        refs[getattr(lead, field).upper()] = (lead.first_name, lead.last_name)
                    else:
                        emails[getattr(lead, field).upper()] = (lead.first_name, lead.last_name)

print "Total Contact/Lead emails found:", len(emails)
print "Total Co-Borrower/Reference emails found:", len(refs)


with codecs.open("new_emails.csv", "w", encoding='utf8') as out:
    out.write("email_address,first_name,last_name\n")
    for email, (first_name, last_name) in emails.items():
        out.write("%s,%s,%s\n" % (email, first_name, last_name))

with codecs.open("new_ref_emails.csv", "w", encoding='utf8') as out:
    out.write("email_address,first_name,last_name\n")
    for email, (first_name, last_name) in refs.items():
        out.write("%s,%s,%s\n" % (email, first_name, last_name))
