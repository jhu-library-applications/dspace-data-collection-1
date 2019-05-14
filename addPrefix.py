import csv
f=csv.writer(open('newprefix.csv', 'w'))
f.writerow(['fileName'])

with open('metadataWithDates.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        fileIdentifier = row['fileIdentifier'].strip()
        fileIdentifierNew = 'jhu_rg-14-195_'+fileIdentifier
        f.writerow([fileIdentifierNew])
