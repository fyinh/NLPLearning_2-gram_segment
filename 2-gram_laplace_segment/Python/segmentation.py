# coding: utf-8

import pickle
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import math


# 判断一个unicode是否是一个汉字
def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

# 判断数字
def is_number(uchar):
    if uchar >= u'\u0030' and uchar <= u'\u0039' or (uchar >= '０' and uchar <= '９'):
        return True
    else:
        return False

# 判断英文字母
def is_alphabet(uchar):
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

# 判断标点符号
def is_other(uchar):
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


# 获得词数组
def getWList():
    f = open('corpus_for_ass2train.txt')
    words = []
    new_words = []
    for line in f.readlines():
        wordlist = line.split()
        words.extend(wordlist)
    for i in range(0, len(words)):
        if is_other(words[i]):
            if i!=0 and words[i-1] == 'S':
                words[i] = '#'
            else:
                words[i] = 'S'
                new_words.append(words[i])
        else:
            new_words.append(words[i])
    f.close()
    return new_words
#
# words = getWList()
# for i in words:
#     print(i)

def get_dic(n, word_list):
    word_dic = {}
    count = 0
    for i in range(len(word_list)):
        if word_list[i] not in word_dic:
            word_dic[word_list[i]] = {}
            word_dic[word_list[i]][word_list[i]] = 1 + word_dic[word_list[i]].setdefault(word_list[i], 0)
            print(word_dic[word_list[i]][word_list[i]])
        if i != len(word_list) - 1:
            word_dic[word_list[i]][word_list[i+1]] = 1 + word_dic[word_list[i]].setdefault(word_list[i+1], 0)
            print(word_dic[word_list[i]][word_list[i+1]])
    for key in word_dic.keys():
        count += len(word_dic[key].keys()) - 1
    return word_dic, count

# word_dic ,count = get_dic(2, words)
# print(word_dic)
# print(count)

# 得到一个句子的所有的词
def get_words(sen, max_length = 4):
    all_words = []
    for i in range(len(sen)):
        all_words.append([sen[i],i,i])
        for j in range(1, max_length + 1):
            if i+j < len(sen):
                if sen[i:i+j+1] in corpus:
                    print("aaa")
                    all_words.append([sen[i:i+j+1],i,i+j])
    return all_words

def get_sen_result(sen):
    all_words = get_words(sen)
    seg_result = []
    i = 0
    flag = 0
    while (i < len(all_words)):
        word = all_words[i]
        if word[1] == 0 and word[2] != len(sen) - 1:
            j = word[2] + 1
            if j <= len(sen) - 1:
                for word_later in all_words:
                    if word_later[1] == j:
                        word_new = word[0] + " " + word_later[0]
                        max_p = max_prob(word_new)
                        for word_old in all_words:
                            if word_old[1] == word[1] and word_old[2] == word_later[2] and word_old[0] != word_new:
                                if max_prob(word_old[0]) >= max_p:
                                    max_p = max_prob(word_old[0])
                                else:
                                    all_words.remove(word_old)
                            if word_old[1] > word[1]:
                                break
                        if max_p == max_prob(word_new) and [word_new, word[1], word_later[2]] not in all_words:
                            all_words.insert(flag,[word_new, word[1], word_later[2]])
                    elif word_later[1] > j:
                        break
                all_words.remove(word)
                i = flag

        elif word[1] == 0 and word[2] == len(sen) - 1:
            if word[0] not in seg_result:
                seg_result.append(word[0])
            flag += 1
            i = flag

        elif word[1] != 0:
            break

    return seg_result


def max_prob(sen_one_result):
    prob = 0
    word_list = sen_one_result.split(' ')
    word_list.insert(0,'#')
    for i in range(1,len(word_list)):
        if word_list[i-1] in word_dic:
            denominator = word_dic[word_list[i-1]][word_list[i-1]]
        else:denominator = 0
        if denominator == 0:
            numerator = 0
        else:
            numerator = word_dic[word_list[i-1]].get(word_list[i], 0)
        p = math.log((numerator + 0.3)/(denominator + count * 0.3))
        prob += p
    return prob

def best_cut(sen):
    seg_all_result = get_sen_result(sen)
    best_prob = float('-Inf')
    best_seg = ''
    for seg_one_result in seg_all_result:
        prob = max_prob(seg_one_result)
        if prob > best_prob:
            best_prob = prob
            best_seg = seg_one_result
    return best_seg

def sentence_split(s):
    result = []
    pre = ''
    word = ''
    number = ''
    alpha = ''
    for c in s:
        # print(c)
        if is_other(c):
            if is_number(pre):
                result.append(number)
                number = ''
            elif is_alphabet(pre):
                result.append(alpha)
                alpha = ''
            elif is_chinese(pre):
                word = best_cut(word)
                result.append(word)
                word = ''
            result.append(c)
        elif is_number(c):
            number += c
            if is_alphabet(pre):
                result.append(alpha)
                alpha = ''
            elif is_chinese(pre):
                word = best_cut(word)
                result.append(word)
                word = ''
        elif is_alphabet(c):
            alpha += c
            if is_number(pre):
                result.append(number)
                number = ''
            elif is_chinese(pre):
                word = best_cut(word)
                result.append(word)
                word = ''
        else:
            word += c
            if is_number(pre):
                result.append(number)
                number = ''
            elif is_alphabet(pre):
                result.append(alpha)
                alpha = ''
        pre = c
    if number != '':
        result.append(number)
    elif alpha != '':
        result.append(alpha)
    elif word != '':
        word = best_cut(word)
        result.append(word)
    return result

if __name__ == "__main__":
    global corpus, word_dic, count
    corpus = getWList()
    word_dic, count = get_dic(2,corpus)
    # print(word_dic)
    # sentence = sentence_split("本报讯春节临近，全国各地积极开展走访慰问困难企业和特困职工的送温暖活动，并广泛动员社会各方面的力量。".decode('utf-8'))
    # str = '  '.join(sentence)
    # print(str)
    f = open('corpus_for_ass2test.txt','r')
    fw = open('result.txt', 'w') #写入文件
    for line in f.readlines():
        sentence = sentence_split(line.decode('utf-8'))
        str = '  '.join(sentence)
        print(str)
        fw.write(str)
        print("yes")
    fw.close()

