# Entity disambiguation for [Europeana Newspapers](http://www.europeana-newspapers.eu/)

A simple Python library and webservice, that allows named entity disambiguation against a label database. 
The idea is to use a Solr query to filter possible candidates and use the more detailed analysis on string similarity, number of inlinks and entity type to select the "best" candidate.
It contains code to handle (multi-lingual) DBpedia dumps and load them into a Solr backend.
It also contains helper code for the annotation of ALTO 2.1 files that are used in the context of the Europeana Newspapers project.

## Startup Solr

This project needs a Solr 4 instance. A script to install a local instance is here:
```
 init\install-solr.sh
```

If you use this way, you can use the 
```
./start-solr.sh
```
to start up a local instance with the right configuration


## Processing dumps

Download dumps from DBPedia (nt-format) from `http://wiki.dbpedia.org/Downloads2014` and put them in `data/rawdata`


For an English label database you need:
```
instance_types_en.nt.bz2	
page_links_en.nt.bz2		
short_abstracts_en.nt.bz2
labels_en.nt.bz2		
redirects_en.nt.bz2
```

Run
```
cd data
./prepare-solr-input.sh
```

This will take a while and generate a `final.csv`, which is the input

To index the CSV file into the default Solr, use

```
./index-in-solr.sh 
```

## Webservice

There is a webservice, that currently only support DBpedia link resolution for a named entity
It has a built-in webserver. 
To start
```
python disambiugation/web.py
```

It will listen on port 5000

To test it:
```
http://localhost:5000/link?ne=einstein
```

Results in:
```
  {
	"p": 0.4927993981146857,
	"link": "http://dbpedia.org/resource/Albert_Einstein",
	"ne": "einstein",
	"name": "Albert Einstein"
 }
```

It uses the Bottle framework, so it should be possible to use the class also in a WSGI environment (Apache). See documentation from the Bottle project.

## ALTO processing 

There is a script that processes a directory of ALTO files, checks the annotations and adds an 'URI' argument to that annotation if it finds a DBpedia link for that named entity and writes the XML file to an output directory.

For example
```
python disambiguation/process-alto.py SOURCE-DIRECTORY-TREE OUTPUT-DIRECTORY-TREE en
```

