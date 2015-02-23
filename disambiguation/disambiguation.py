import solr
import sys
import json
import re
import fuzzycomp
import locale
import math

LANG = "en"

s = solr.SolrConnection('http://localhost:8984/solr/dbpedia_' + LANG)

CUTOFF_RELEVANCY = 0.0
CUTOFF_SIMILARITY = 0.6
CUTOFF_TOTAL_SCORE = 0.02


def _escapeQueryString(toEscape):
    replaceCharacter = ["+", "-", "&&", "||", "!", "(", ")", "{",
                        "}", "[", "]", "^", "\"", "~", "*", "?", ":"]

    cleaned = toEscape.rstrip().lstrip()
    for c in replaceCharacter:
        cleaned = cleaned.replace(c, '\\' + c)
    return cleaned


def _cleanedLabel(label):
    '''remove information in parenthesis, lowercase'''
    return re.sub(r'\(.*\)', '', label.lower()).rstrip().lstrip()


def _stringSimilarity(a, b):
    '''adapted string similarity: combines jaro-winkler distance with
       number of common terms in both strings '''

    if a and b and len(a) > 0 and len(b) > 0:
        sa = set(''.join([c for c in a.split(" ")]))
        sb = set(''.join([c for c in b.split(" ")]))

        intersect = sa.intersection(sb)
        if (sa and sb and len(sa) > 0 and len(sb) > 0):
            jaro = fuzzycomp.jaro_winkler(a.encode('utf-8'),
                                          b.encode('utf-8'), 0.1)
            jaro *= (float(len(intersect)) / float(max(len(sa), len(sb))))
            return jaro
        else:
            return 0.0
    else:
        return 0.0


def disambiguateList(entityStrings):
    result = dict()
    for s in set(entityStrings):
        result[s] = linkEntity(s)
    return result


def linkEntity(namedEntityString):
    cleaned = _escapeQueryString(unicode(namedEntityString.decode('utf-8').lower()))
    labelQuery = "label_" + LANG + ":\"" + cleaned + "\"^2000 " + " ".join(["label_" + LANG + ":" + elt for elt in cleaned.split(" ")])
    redirectLabelQuery="redirectLabel:\"" +cleaned + "\"^2000 " + " ".join(["redirectLabel:"+elt for elt in cleaned.split(" ")])
    try:
        result = s.raw_query(q="\
  		(("+labelQuery+") OR ("+redirectLabelQuery+")) \
                AND _val_:inlinks^10 \
                AND (schemaorgtype:Person^10 OR schemaorgtype:Place OR schemaorgtype:Organization)",
                fq="schemaorgtype:Person OR schemaorgtype:Place OR schemaorgtype:Organization",
                fl="* score",
                rows=5,
                indent="on",
                wt="json")
    except Exception, e:
        print e
        return None

    bestMatch = None
    bestMatchMainLabel = None

    jsonResult = json.loads(result)
    maxScore = jsonResult["response"]["maxScore"]

    score = -1.0
    sumScore = 0.0

    sumLabels = dict()
    mainLabels = dict()

    for d in jsonResult["response"]["docs"]:
        if (d.get("score")/maxScore) > CUTOFF_RELEVANCY:
            sumScore += d.get("score")
            labels = d.get("redirectLabel")

            if labels is None:
                labels = []

            mainLabels[d.get("id")] = d.get("label_" + LANG)
            sumLabels[d.get("id")] = [(_cleanedLabel(d.get("label_" + LANG)),
                                      d.get("score"))]

        for l in labels:
            sumLabels[d.get("id")].append((_cleanedLabel(l), d.get("score")))

    for d in sumLabels.keys():
        for l in sumLabels.get(d):
            similarityScore = _stringSimilarity(cleaned, l[0])

            if similarityScore > CUTOFF_SIMILARITY:
                relativeRelevancyScore = l[1] / sumScore
                labelScore = similarityScore * math.sqrt(relativeRelevancyScore)

                if labelScore > score:
                    bestMatch = d
                    bestMatchMainLabel=mainLabels[d]
                    score=labelScore

    if score > CUTOFF_TOTAL_SCORE:
        return bestMatch, score, bestMatchMainLabel
    else:
        return None, -1.0, bestMatchMainLabel

if __name__ == '__main__':
    print linkEntity(sys.argv[1])
