# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 15:41:22 2017

@author: dell
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 18:31:51 2016

@author: dell
"""

 
import logging
import os
import sys
import multiprocessing

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
 
if __name__ == '__main__':

    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
 
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))
    
    # check and process input arguments

    data_source = sys.argv[1]
    chunk_file_source = os.path.join(data_source,"chunk_file")
    target_path = os.path.join(data_source,"mix_chunk_file")
    
    model_path = "./tweets.model"
    vector_path = "./tweets.vector"
    
    target_file = open(target_path,'w')
    for root,dirnames,filenames in os.walk(chunk_file_source):
        for filename in filenames:
            path = os.path.join(root,filename)
            source_file = open(path,'r')
            s = source_file.read()
            target_file.write(s)
            source_file.close()
    target_file.close()

    sentences = LineSentence(target_path)
    #model = Word2Vec.load(model_path)
    #model.train(sentences)
    model = Word2Vec(sentences, size=200, window=5, min_count=5,workers=multiprocessing.cpu_count())
    # trim unneeded model memory = use(much) less RAM
    #model.init_sims(replace=True)
    model.save(model_path)   
    model.wv.save_word2vec_format(vector_path, binary=False)

#python TrainVectorModel.py data_source_path
