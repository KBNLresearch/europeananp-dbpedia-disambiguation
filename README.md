# Entity disambiguation for [Europeana Newspapers](http://www.europeana-newspapers.eu/)

A simple Python library and webservice, that allows named entity disambiguation against a label database. 
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

Download dumps from DBPedia (nt-format) from `http://wiki.dbpedia.org/Downloads2014` and put dem in `data/rawdata`


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

## Start Webservice

## ALTO processing 


