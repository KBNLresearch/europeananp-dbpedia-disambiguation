import solr
import sys
import json
import re
import fuzzycomp
import locale
import math

s = solr.SolrConnection('http://localhost:8983/solr/dbpedia')

CUTOFF_RELEVANCY=0.0
CUTOFF_SIMILARITY=0.6
CUTOFF_TOTAL_SCORE=0.02

def _lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = \
                    max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return result

def _escapeQueryString(toEscape):
  replaceCharacter=["+","-","&&","||","!","(",")","{","}","[","]","^","\"","~","*","?",":"]

  cleaned=toEscape.rstrip().lstrip()
  for c in replaceCharacter:
  	cleaned=cleaned.replace(c,'\\'+c)
  return cleaned

#remove information in parenthesis, lowercase
def _cleanedLabel(label):
	return re.sub(r'\(.*\)','',label.lower()).rstrip().lstrip()


#adapted string similarity: combines jaro-winkler distance with number of common terms in both strings 
def _stringSimilarity(a,b):
	if a and b and len(a)>0 and len(b)>0:
		sa=set(u''.join([c for c in a.split(" ")]))
		sb=set(u''.join([c for c in b.split(" ")]))
		intersect=sa.intersection(sb)
		if (sa and sb and len(sa)>0 and len(sb)>0):
			return fuzzycomp.jaro_winkler(a.encode('utf-8'),b.encode('utf-8'),0.1)*(float(len(intersect))/float(max(len(sa),len(sb))))
		else:
			return 0.0
	else:
		return 0.0

def disambiguateList(entityStrings):
  result=dict()
  for s in entityStrings:
      result[s]=linkEntity(s)
  return result

def linkEntity(namedEntityString):

  cleaned=_escapeQueryString(unicode(namedEntityString.lower()))
  labelQuery="label_en:\""+cleaned+"\"^2000 "+" ".join(["label_en:"+elt for elt in cleaned.split(" ")])
  redirectLabelQuery="redirectLabel:\""+cleaned+"\"^2000 "+" ".join(["redirectLabel:"+elt for elt in cleaned.split(" ")])
  try:
  	result=s.raw_query(q="\
  		(("+labelQuery+") OR ("+redirectLabelQuery+")) \
  		AND _val_:inlinks^4 \
  		AND (schemaorgtype:Person^10 OR schemaorgtype:Place OR schemaorgtype:Organization)",
  		fq="schemaorgtype:Person OR schemaorgtype:Place OR schemaorgtype:Organization",
  		fl="* score",
  		rows=5,
  		indent="on",
  		wt="json")
  except Exception, e:
  	print e
  	return None
  jsonResult=json.loads(result)
  bestMatch=None
  score=-1.0
  maxScore=jsonResult["response"]["maxScore"]
  sumScore=0.0
  sumLabels=dict()
  for d in jsonResult["response"]["docs"]:

  	if (d.get("score")/maxScore) > CUTOFF_RELEVANCY:
  		sumScore+=d.get("score")
  		labels=d.get("redirectLabel")
  		if labels is None:
  			labels=[]
  		sumLabels[d.get("id")]=[(_cleanedLabel(d.get("label_en")),d.get("score"))]
  		for l in labels:
  			sumLabels[d.get("id")].append((_cleanedLabel(l),d.get("score"))) 

  for d in sumLabels.keys():
  	 for l in sumLabels.get(d):
  	 	similarityScore=_stringSimilarity(cleaned,l[0])
  	 	if (similarityScore>CUTOFF_SIMILARITY):
  	 		relativeRelevancyScore=l[1]/sumScore
  	 		labelScore=similarityScore*math.sqrt(relativeRelevancyScore)
  	 		if labelScore>score:
  	 			bestMatch=d
  	 			score=labelScore
  if score > CUTOFF_TOTAL_SCORE:
  	return bestMatch,score
  else:
  	return None, -1.0

if __name__ == '__main__':
	print linkEntity(sys.argv[1])

