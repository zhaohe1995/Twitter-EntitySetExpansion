# Twitter-EntitySetExpansion #
A tool to do entity set expansion on Twitter corpus. From a set of initial seeds the program  can return more semantic similar entities.

### Environment Configuration ###
To run the source code, you should have following setting installed on your linux:    
- python 2.7  
- gensim > 0.13.3

### Data Preprocessing ###
The Twitter data source is stored in the dir ‘/home/Twitter/data’, and all the file should ends with '.gz'
  
    cd /Twitter-EntitySetExpansion
	export TWITTER_NLP=./Twitter	
	python PreProcessAndChunk.py /home/Twitter/data

### Train Word2Vec Model ###
    
	python TrainVectorModel.py /home/Twitter/data

### Set Expansion with Several Seeds ###

	python SetExpansionFromSeeds.py /home/Twitter/data seed1 seed2 seed3
