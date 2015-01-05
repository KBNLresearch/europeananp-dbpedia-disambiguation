#!/bin/bash
#Creates a Solr compatible CSV file

echo "Extract entities..."
bzcat rawdata/short_abstracts_en.nt.bz2  | awk '/^\s*[^#]/ { print $1 }' | sort > entities-sorted.txt

echo "Extract labels..."
bzcat rawdata/labels_en.nt.bz2 | awk '/^\s*[^#]/ { ORS=""; print $1 " ";for (i=3;i<=NF-1;i++) print $i " "; print "\n" }' | sort | rev | cut -c5- | rev | native2ascii -encoding UTF-8 -reverse > labels.txt

echo "Extract short abstracts..."
bzcat rawdata/short_abstracts_en.nt.bz2 | awk '/^\s*[^#]/ { ORS=""; print $1 " ";for (i=3;i<=NF-1;i++) print $i " "; print "\n" }' | rev | cut -c5- | rev | sed "s/\\\\\"/\"\"/g" | native2ascii -encoding UTF-8 -reverse > abstracts.txt

echo "Extract schema.org types..."
bzcat rawdata/instance_types_en.nt.bz2 | grep "http://schema.org" | cut -d " " -f 1,3 | sed "s/http:\/\/schema\.org\///g"  >schemaorgtypes.txt 
python summarize.py schemaorgtypes.txt > schemaorgtypes-summed.txt 

echo "Extract page link count..."
bzcat rawdata/page_links_en.nt.bz2| awk '/^\s*[^#]/ { ORS=""; for (i=3;i<=NF-1;i++) print $i " "; print "\n" }' | sort | uniq -c > page_links_count.txt

echo "Extract redirect labels..."
bzcat rawdata/redirects_en.nt.bz2 | cut -d " " -f 1,3 |  sort | join - labels.txt | cut -d " " -f 2,3- >redirect-labels.txt
python summarize.py redirect-labels.txt > redirect-labels-summed.txt 

echo "Make final csv..."
python make-csv.py | sed "s/|\"/| \"/g" | sed "s/,\"\"\"/,\" \"\"/g" > final.csv
