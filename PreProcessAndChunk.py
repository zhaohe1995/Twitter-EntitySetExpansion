#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 12:00:41 2017

@author: zhaohe
"""

"""
Process the original twitter dataset.
Extract the 'created_at' and 'text' from dataset.
Output these information into new files.
"""
import os,sys
import gzip
import json

def DeleteSpace(infile,outfile):
      inf = open(infile,'r')
      outf = open(outfile,'w')
      lines = inf.readlines()
      for line in lines:
            if line.split():
                  outf.writelines(line)
      inf.close()
      outf.close()
      os.remove(infile)

def ExtractTweets(source_dir,target_dir):
      for root,dirnames,filenames in os.walk(source_dir):
            for filename in filenames:
                  if not filename.endswith('.gz'):
                        continue
                  print "Extracting text from:",filename
                  
                  source_path = os.path.join(source_dir,filename)
                  target_path = os.path.join(target_dir,filename[:-3]+'.txt')
                  nospace_path = os.path.join(target_dir,filename[:-3])
                  
                  source_file = gzip.open(source_path,'r')
                  target_file = open(target_path,'w')
                  
                  for line in source_file:
                        tweet = json.loads(line)
                        try:
                              language = tweet['lang']
                        except KeyError:
                              continue
                        if language == 'en':
                              text = tweet['text']
                              time = tweet['created_at']
                              line_to_write = text+'\n'
                              #line = '{\"created_at\":\"'+e[1]+'\",\"text\":\"'+e[0]+'\"}\n'
                              try:
                                    target_file.write(line_to_write)
                              except UnicodeEncodeError:
                                    continue
                  source_file.close()
                  target_file.close()
                  DeleteSpace(target_path,nospace_path)

def TagTweets(source_dir,target_dir):
      for root,dirnames,filenames in os.walk(source_dir):
            for filename in filenames:
                  print "Tagging:",filename
                  
                  source_path = os.path.join(source_dir,filename)
                  target_path = os.path.join(target_dir,filename)
                  
                  twitter_nlp = './twitter_nlp-master'
                  chunk_program = twitter_nlp+'/python/ner/extractEntities.py'
                  os.system('export TWITTER_NLP='+twitter_nlp+'/')
                  os.system('python '+chunk_program+' -k '+source_path+' -o '+target_path)
                  os.remove(source_path)
                  
ENTITY = []
def ChunkTweets(source_dir,target_dir):
      for root,dirnames,filenames in os.walk(source_dir):
            for filename in filenames:
                  print "Chunking:",filename
                  
                  source_path = os.path.join(source_dir,filename)
                  target_path = os.path.join(target_dir,filename+'.txt')
                  
                  source_file = open(source_path,'r')
                  target_file = open(target_path,'w')
                  for line in source_file:
                        tokens = line.split(' ')
                        new_tokens = []
                        flag = 0
                        entity = []
                        for token in tokens:
                              if token[-2:] == '/O':
                                    token = token[:-2]
                                    if flag == 1:
                                          ENTITY.append('_'.join(entity))
                                          new_tokens.append(''.join(entity))
                                          flag = 0
                                          entity = []
                                    new_tokens.append(token)
                              elif token[-3:] == '/O\n':
                                    token = token[:-3]+'\n'
                                    if flag == 1:
                                          ENTITY.append('_'.join(entity))
                                          new_tokens.append(''.join(entity))
                                          flag = 0
                                          entity = []
                                    new_tokens.append(token)
                              elif '/B-ENTITY' in token or '/I-ENTITY' in token:
                                    flag = 1
                                    if token[-1] == '\n':
                                          entity.append(token[:-10]+'\n')
                                    else:
                                          entity.append(token[:-9])
                        target_file.write(' '.join(new_tokens))
                  source_file.close()
                  target_file.close()
                  os.remove(source_path)
                              
if __name__ == '__main__':
      program = os.path.basename(sys.argv[0])
      data_path = sys.argv[1]

      twitter_data_dir = data_path
      tweets_file_dir = os.path.join(data_path,"tweets_file")
      tag_file_dir = os.path.join(data_path,"tag_file")
      chunk_file_dir = os.path.join(data_path,"chunk_file")
      try:
            os.mkdir(tweets_file_dir)
            os.mkdir(tag_file_dir)
            os.mkdir(chunk_file_dir)
      except OSError as e:
            pass
      ExtractTweets(twitter_data_dir,tweets_file_dir)
      TagTweets(tweets_file_dir,tag_file_dir)
      ChunkTweets(tag_file_dir,chunk_file_dir)
