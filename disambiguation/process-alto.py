import os
import sys
import xml.etree.ElementTree as ET
import collections
import disambiguation
# Usage python SOURCE-DIRECTORY-WITH-ALTOS OUTPUT-DIRECTORY LANGUAGE


def processDir(sourceDir, targetDir, language="en"):
    ET.register_namespace('', 'http://www.loc.gov/standards/alto/ns-v2#')
    for subdir, dirs, files in os.walk(sourceDir):
        for file in files:
            fname = os.path.join(subdir, file)
            outputfname = os.path.join(
                targetDir, os.path.relpath(fname, sourceDir))
            if not os.path.exists(os.path.dirname(outputfname)):
                os.makedirs(os.path.dirname(outputfname))
            print fname
            print outputfname
            tree = ET.parse(fname)
            entities = dict()
            for t in tree.getroot().iter(tag="{http://www.loc.gov/standards/alto/ns-v2#}NamedEntityTag"):
                if entities.get(t.attrib.get('LABEL')) is None:
                    entities[t.attrib.get('LABEL')] = []
                entities.get(t.attrib.get('LABEL')).append(t)

            result = disambiguation.disambiguateList(entities.keys())
            for key in result.keys():
                if result.get(key) is not None and result.get(key)[0] is not None:
                    for tag in entities[key]:
                        tag.set("URI", result[key][0][1:-1])
            tree.write(
                outputfname, xml_declaration=True, encoding='utf-8', method='xml')

if __name__ == '__main__':
    processDir(sys.argv[1], sys.argv[2], sys.argv[3])
