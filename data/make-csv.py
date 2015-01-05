from collections import defaultdict
xstr = lambda s: s or ""
xzero = lambda s: s or "0"

ins = open( "page_links_count.txt", "r" )
pagecount = dict()
for line in ins:
	splitted=line.lstrip().split(' ',2)
        pagecount[splitted[1]]=splitted[0]
ins.close() 
ins = open( "redirect-labels-summed.txt", "r" )
redirectlabels=dict()
for line in ins:
        splitted=line.rstrip().split(' ',1)
        redirectlabels[splitted[0]]=splitted[1]
ins.close()


labels=dict()
ins = open( "labels.txt", "r" )
for line in ins:
	splitted=line.split (' ',1)
	labels[splitted[0]]=splitted[1].rstrip().lstrip()
ins.close()

schemaorgtypes=dict()
ins = open( "schemaorgtypes-summed.txt", "r" )
for line in ins:
	splitted=line.split (' ',1)
	schemaorgtypes[splitted[0]]=splitted[1].rstrip().lstrip()
ins.close()

ins = open( "abstracts.txt", "r" )
for line in ins:
	splitted=line.split (' ',1)
	print "\""+splitted[0].replace("\"","\\\"")+"\","+xstr(labels.get(splitted[0]))+","+xstr(schemaorgtypes.get(splitted[0]))+",\""+xstr(splitted[1]).rstrip().lstrip().replace("\"","")+"\","+xstr(redirectlabels.get(splitted[0]))+","+xzero(pagecount.get(splitted[0]))    
ins.close()


