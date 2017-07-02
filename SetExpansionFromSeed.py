# -*- coding: utf-8 -*-

conj_list1 = ['and','or',',','&','+','-','x','X','/','*','>','<','|','vs','VS','.',';','//']
conj_list2 = [' and ',' or ',' , ',' & ',' + ',' - ',' x ',' X ',' / ',' * ',' > ',' < ',' | ',' vs ',' VS ',' . ',' ; ',' // ']
prefix_list = [('@','#'),('@','@'),('#','#'),('#','@')]

import os,sys
import gensim
import random
#-----------Get the set from a scored set----------------------
def GetSetFromScoreToDict(score_set):
    candidate_set = {}
    for candidate in score_set:
        if candidate[0].lower() not in candidate_set:
            candidate_set[candidate[0].lower()] = candidate[1]
    candidate_set = sorted(candidate_set.items(),key = lambda d:d[1],reverse=True)
    for candidate in candidate_set:
        print candidate
    return candidate_set

#---------------EXTRACT SEED PAIRS FROM SEEDSETS----------------
def GenerateSeedPair(SeedSet):
    Pairs = []
    n = len(SeedSet)
    for i in range(0,n):
        for j in range(i+1,n):
            Pairs.append((SeedSet[i],SeedSet[j]))
    return Pairs

#-----------To get one seed's candidate entity set-------------
def GetSingleCandidateSet(seed,model,n):
    single_cand_list = model.most_similar(seed,topn = n)
    '''
    for element in single_cand_list:
        print element
    '''
    return single_cand_list
#------------Merge all the candidate lists and rank--------------
def MergeCandidateLists(cand_lists,SeedSet,model):
    candidate_rank_score = []
    seed_num = len(SeedSet)
    for list_set in cand_lists:
        for candidate in list_set:
            score = 0
            for seed in SeedSet:

                try:
                    capital_score = model.similarity(candidate[0],seed)
                except KeyError:
                    capital_score = 0
                try:
                    lowercase_score = model.similarity(candidate[0].lower(),seed.lower())
                except KeyError:
                    lowercase_score = 0
                seed_score = max(capital_score,lowercase_score)

                #seed_score = model.similarity(seed.lower(),candidate[0].lower())
                score += seed_score
            score /= seed_num
            candidate_rank_score.append((candidate[0],score))
    candidate_set = list(set(candidate_rank_score))
    candidate_set.sort(key = lambda x:x[1])
    #candidate_set = GetSetFromScoreToDict(candidate_rank_score)
    return candidate_set


#------------Expansion from seed with vector model and patterns------
def ExpandFromSeed(SeedSet,model):
    cand_lists = []
    for seed in SeedSet:
        single_cand_list = GetSingleCandidateSet(seed,model,2000)
        cand_lists.append(single_cand_list)
    candidate_set = MergeCandidateLists(cand_lists,SeedSet,model)
    return candidate_set


#---------------To get test every pattern and give them weights--------
def GetPatternWeight(SeedSet,source_dir):
    pattern_set = {}
    Pairs = GenerateSeedPair(SeedSet)
    for pair in Pairs:
        sentences = []
        for root, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                source_path = os.path.join(source_dir,filename)
                source_file = open(source_path,'r')
                for line in source_file:
                    if pair[0].lower() in line.lower() and pair[1].lower() in line.lower():
                        sentences.append(line)
        for sent in sentences:
            for conj in conj_list1:
                pattern1 = pair[0].lower()+conj+pair[1].lower()
                pattern2 = pair[1].lower()+conj+pair[0].lower()
                if pattern1 in sent.lower() or pattern2 in sent.lower():
                    if conj in pattern_set:
                        pattern_set[conj] += 1
                    else:
                        pattern_set[conj] = 1
            for conj in conj_list2:
                pattern1 = pair[0].lower()+conj+pair[1].lower()
                pattern2 = pair[1].lower() + conj + pair[0].lower()
                if pattern1 in sent.lower() or pattern2 in sent.lower():
                    if conj in pattern_set:
                        pattern_set[conj] += 1
                    else:
                        pattern_set[conj] = 1
    '''
    for (pattern,times) in pattern_set.items():
        print pattern,times
    '''
    times_sum = 0
    for (pattern,times) in pattern_set.items():
        times_sum += times
    for (pattern,times) in pattern_set.items():
        pattern_set[pattern] = float(times)/float(times_sum)
    return pattern_set

#--------------To test every pair of prefix and give them weight------
def GetPrefixWeight(SeedSet,source_dir):
    prefix_set = {}
    Pairs = GenerateSeedPair(SeedSet)
    for pair in Pairs:
        sentences = []
        for root, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                source_path = os.path.join(source_dir,filename)
                source_file = open(source_path,'r')
                for line in source_file:
                    if pair[0].lower() in line.lower() and pair[1].lower() in line.lower():
                        sentences.append(line)
        for sent in sentences:
            for prefix in prefix_list:
                pattern1 = prefix[0]+pair[0]
                pattern2 = prefix[1]+pair[1]
                if pattern1.lower() in sent.lower() and pattern2.lower() in sent.lower():
                    if prefix in prefix_set:
                        prefix_set[prefix] += 1
                    else:
                        prefix_set[prefix] = 1
    times_sum = 0
    for (prefix,times) in prefix_set.items():
        times_sum += times
    for (prefix,times) in prefix_set.items():
        prefix_set[prefix] = float(times)/float(times_sum)
    return prefix_set

#--------------Rerank candidate_set with pattern informance------------
def RankCandWithPattern(candidate_set,SeedSet,source_dir,pattern_set,prefix_set):
    pattern_cand_set = []
    #Initial for each seeds
    seed_tweet_dict = {}
    for seed in SeedSet:
        seed_tweet_dict[seed] = []

    #Map the lines to each seeds' set
    for root, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            source_path = os.path.join(source_dir,filename)
            source_file = open(source_path,'r')
            for line in source_file:
                for seed in SeedSet:
                    if seed.lower() in line.lower():
                        seed_tweet_dict[seed].append(line)
    #Based on co-occurrence
    for candidate in candidate_set:
        cand = candidate[0].lower()
        pattern_score = {}
        prefix_score = {}
        pattern_value = 0
        prefix_value = 0

        for seed in SeedSet:
            sent_list = []
            for sentence in seed_tweet_dict[seed]:
                if cand in sentence.lower():
                    sent_list.append(sentence)
            for sent in sent_list:
                for pattern in pattern_set:
                    pattern1 = cand+pattern+seed.lower()
                    pattern2 = seed.lower()+pattern+cand
                    if pattern1 in sent.lower() or pattern2 in sent.lower():
                        if pattern in pattern_score:
                            pattern_score[pattern] += 1
                        else:
                            pattern_score[pattern] = 1
                for prefix in prefix_set:
                    prefix1 = prefix[0]+cand
                    prefix2 = prefix[1]+seed.lower()
                    if prefix1 in sent.lower() and prefix2 in sent.lower():
                        if prefix in prefix_score:
                            prefix_score[prefix] += 1
                        else:
                            prefix_score[prefix] = 1

        for (pattern,times) in pattern_score.items():
            pattern_score[pattern] = times * pattern_set[pattern]
            pattern_value += pattern_score[pattern]
        for (prefix,times) in prefix_score.items():
            prefix_score[prefix] = times * prefix_set[prefix]
            prefix_value += prefix_score[prefix]
        pattern_cand_set.append((candidate[0],candidate[1],pattern_value,prefix_value))
    return pattern_cand_set

#------------------Rank the candidate set------------------------------------
def RankCandidateSet(candidate_set,rank_model):
    ranked_set = []
    for candidate in candidate_set:
        item_name = candidate[0]
        f1_value = candidate[1]
        f2_value = candidate[2]
        f3_value = candidate[3]
        f_score =0.0
        ranked_set.append([item_name,f1_value,f2_value,f3_value,f_score])

    n = len(ranked_set)
    ranked_set.sort(key = lambda x:x[1],reverse=True)
    ranked_set[0][1] = 1
    for i in range(1,n):
        if ranked_set[i][1] < ranked_set[i-1][1]:
            ranked_set[i][1] = ranked_set[i-1][1]+1
        else:
            ranked_set[i][1] = ranked_set[i - 1][1]

    ranked_set.sort(key = lambda x:x[2],reverse=True)
    ranked_set[0][2] = 1
    for i in range(1,n):
        if ranked_set[i][2] < ranked_set[i-1][2]:
            ranked_set[i][2] = ranked_set[i-1][2]+1
        else:
            ranked_set[i][2] = ranked_set[i - 1][2]

    ranked_set.sort(key = lambda x:x[3],reverse=True)
    ranked_set[0][3] = 1
    for i in range(1,n):
        if ranked_set[i][3] < ranked_set[i-1][3]:
            ranked_set[i][3] = ranked_set[i-1][3]+1
        else:
            ranked_set[i][3] = ranked_set[i - 1][3]

    for item in ranked_set:
        item[4] = rank_model[0]*item[1]+rank_model[1]*item[2]+rank_model[2]*item[3]
    ranked_set.sort(key=lambda x:x[4])
    return ranked_set


#------------------Refine the evaluate ranked set----------------------------
def RefineRankSet(candidate_set):
    refined_set = []
    lower_refined_set = []
    for candidate in candidate_set:
        entity = candidate[0]
        if entity[0] == '@' or entity[0] == '#':
            continue
        elif entity[:4] == 'http':
            continue
        elif entity.isdigit()==True:
            continue
        elif entity.lower() in lower_refined_set:
            continue
        else:
            lower_refined_set.append(entity.lower())
            refined_set.append(entity)
    return refined_set



#--------------------Get all the seed sets from file-------------------
def ExpandFromSeedSet(seed_set,model):
    candidate_set = ExpandFromSeed(seed_set,model)
    pattern_set = GetPatternWeight(seed_set,chunk_file_dir)
    prefix_set = GetPrefixWeight(seed_set,chunk_file_dir)  
    pattern_cand_set = RankCandWithPattern(candidate_set,seed_set,chunk_file_dir,pattern_set,prefix_set)
    ranked_set = RankCandidateSet(pattern_cand_set,rank_model)
    refined_set = RefineRankSet(ranked_set)
    
    print 'The ranked entity list is:'
    for entity in refined_set[:150]:
          print entity
    

if __name__ == '__main__':

    model_path = r'./tweets.vector'
    model = gensim.models.KeyedVectors.load_word2vec_format(model_path, binary=False)

    data_source = sys.argv[1]
    chunk_file_dir = os.path.join(data_source,"chunk_file")
    
    seed_set = [sys.argv[2],sys.argv[3],sys.argv[4]]

    rank_model = [0.75327364,0.17832751,0.06839885]
    ExpandFromSeedSet(seed_set,model)

#python SetExpansion.py data_source_path seed1 seed2 seed3