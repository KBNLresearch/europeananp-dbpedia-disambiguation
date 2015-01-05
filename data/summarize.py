import sys
from collections import defaultdict
ins = open( sys.argv[1], "r" )

d = defaultdict(list)
for line in ins:
	splitted=line.split (' ',1)
	d[splitted[0]].append(splitted[1].rstrip()[1:-1].replace("\\\"","\"\""))   
ins.close()

for key, value in d.iteritems():
  line=key+" "+"\""
  sepChar=""
  for label in value:
   line+=sepChar+label
   sepChar="|"
  line=line+"\""
  print line

