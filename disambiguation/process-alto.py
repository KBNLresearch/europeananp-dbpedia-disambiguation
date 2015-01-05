import os,sys
import xml.etree.ElementTree as ET
import collections
import disambiguation

def processDir(sourceDir,targetDir,language):
	for subdir, dirs, files in os.walk(sourceDir):
		for file in files:
			fname=os.path.join(subdir, file)
			print fname
			tree = ET.parse(fname)
			entities=dict()
			for t in tree.getroot().iter(tag="{http://www.loc.gov/standards/alto/ns-v2#}NamedEntityTag"):
				if entities.get(t.attrib.get('LABEL')) is None:
					entities[t.attrib.get('LABEL')]=[]
				entities.get(t.attrib.get('LABEL')).append(t)
	
			print disambiguation.disambiguateList(entities.keys())				
if __name__ == '__main__':
	processDir(sys.argv[1],sys.argv[2],sys.argv[3])
