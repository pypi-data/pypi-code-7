import codecs
import sugarcrm


#URL = "http://van-sugarcrm.pbs.local/service/v4_1/rest.php"
#USER = "Freddy"
#PASS = "password"

URL = "https://umtravel.sugarondemand.com/service/v4_1/rest.php"
USER = "Darryl"
PASS = "5a3767366132".decode('hex')

sugar = sugarcrm.API(URL, USER, PASS)


emails = {}
refs = {}

count = int(sugar.get_entries_count("Contacts", "", 1))
print "Extracting emails from %d Contacts" % count
for offset in range(22200, count, 100):
    print "Offset: %s, Emails: %d, Refs: %d" % (offset, len(emails), len(refs))
    contacts = sugar.get_entry_list("Contacts", "", [], 100, offset, 1)
    for contact in contacts:
        for field in dir(contact):
            if field.find("email") >= 0 and getattr(contact, field, "").find("@") >= 0:
                if getattr(contact, field, None):
                    if field.find("coborrower") >= 0  or field.find("ref") >= 0:
                        refs[getattr(contact, field).upper()] = (contact.first_name, contact.last_name)
                    else:
                        emails[getattr(contact, field).upper()] = (contact.first_name, contact.last_name)


count = int(sugar.get_entries_count("Leads", "", 1))
print "Extracting emails from %d Leads" % count
for offset in range(0, count, 100):
    print "Offset: %s, Emails: %d, Refs: %d" % (offset, len(emails), len(refs))
    leads = sugar.get_entry_list("Leads", "", [], 100, offset, 1)
    for lead in leads:
        for field in dir(lead):
            if field.find("email") >= 0 and getattr(lead, field, "").find("@") >= 0:
                if getattr(lead, field, None):
                    if field.find("coborrower") >= 0  or field.find("ref") >= 0:
                        refs[getattr(lead, field).upper()] = (lead.first_name, lead.last_name)
                    else:
                        emails[getattr(lead, field).upper()] = (lead.first_name, lead.last_name)


print "Total Contact/Lead emails found:", len(emails)
print "Total Co-Borrower/Reference emails found:", len(refs)


with codecs.open("emails.csv", "w", encoding='utf8') as out:
    out.write("email_address,first_name,last_name\n")
    for email, (first_name, last_name) in emails.items():
        out.write("%s,%s,%s\n" % (email, first_name, last_name))

with codecs.open("ref_emails.csv", "w", encoding='utf8') as out:
    out.write("email_address,first_name,last_name\n")
    for email, (first_name, last_name) in refs.items():
        out.write("%s,%s,%s\n" % (email, first_name, last_name))
