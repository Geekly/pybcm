import pandas as pd

# read the entire file into a python array
with open('legocolors.json', 'r') as f:
    data = f.read().replace('\n', '')

jdata = pd.read_json(data)

print(jdata)

jdata.sort_values('colorid', inplace=True)
print(jdata)
# for key in sorted(mydict.iterkeys()):
#     print "%s: %s" % (key, mydict[key])

fullcolor = ''
for row in jdata.itertuples():
    colorid = row.colorid
    name = str(row.colorname)
    fullcolor = fullcolor + "{0:d}: '{1}',\n".format(colorid, name)
print(fullcolor)

with open('colordict.txt', 'wt') as out:
    out.write(fullcolor)



# colors = {1:  'White',
#               2:  'Tan',
#               49: 'Very Light Gray',
