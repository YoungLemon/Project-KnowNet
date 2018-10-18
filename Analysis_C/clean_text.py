import nltk
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer() # 词干提取器


def clean_token(text):

    colloc_list = []
    entity_names = []

    tagger = nltk.tag.perceptron.PerceptronTagger()
    tagged = []

    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [tagger.tag(sentence) for sentence in tokenized_sentences]

    # '''获取命名实体名称'''
    # for sentence in tagged_sentences:
    #     tagged.extend(sentence)
    # chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
    # for tree in chunked_sentences:
    #     entity_names.extend(extract_entity_names(tree))
    # entity_names = set(entity_names)
    # # print(entity_names)
    #
    # '''获取常用语名称'''
    # bigram_measures = nltk.collocations.BigramAssocMeasures()
    # finder = nltk.collocations.BigramCollocationFinder.from_words(tagged)
    # finder.apply_freq_filter(3)
    # colloc_list = finder.nbest(bigram_measures.pmi, 20)
    # # print(colloc_list)

    '''预处理'''
    tagged = []
    terms = {"h index": "h-index",
            "hirsch index": "h-index"}

    sents = nltk.sent_tokenize(text)
    tok_sents = [nltk.word_tokenize(sent) for sent in sents]
    tagged_sents = [tagger.tag(sent) for sent in tok_sents]
    tagged_sents = [join_term(sent, terms) for sent in tagged_sents]
    # tagged_sents = [joincolloc(sent, colloc_list) for sent in tagged_sents]
    # tagged_sents = [joincollocbi(sent, colloc_list) for sent in tagged_sents]
    # tagged_sents = [groupne2(sent, entity_names) for sent in tagged_sents]
    # tagged_sents = [groupne3(sent, entity_names) for sent in tagged_sents]
    tagged_sents = [filter_for_tags(sent) for sent in tagged_sents]
    tagged_sents = [normalize_tags(sent) for sent in tagged_sents]
    tagged_sents = [normalize(sent) for sent in tagged_sents]
    tagged_sents = [filter_numbers(sent) for sent in tagged_sents]
    tagged_sents = [lowercase(sent) for sent in tagged_sents]
    tagged_sents = [lemmatize(sent) for sent in tagged_sents]
    tagged_sents = [rstopwords(sent) for sent in tagged_sents]
    for sent in tagged_sents:
        tagged.extend(sent)
    sentences = [item[0] for item in tagged]
    return sentences


def join_term(tagged, term=None):
    """把分离的专有名词短语合并"""

    tagged1 = []
    sw = 0

    for i in range(len(tagged) - 1):
        if sw == 1:
            sw = 0
            continue
        tmp = ' '.join([tagged[i][0], tagged[i + 1][0]])
        if tmp in term:
            sw = 1
            tagged1.append((term[tmp], 'NN'))
        else:
            tagged1.append(tagged[i])
    if len(tagged) > 0:
        tagged1.append(tagged[len(tagged) - 1])

    return tagged1


def filter_for_tags(tagged):
    '''过滤非名词词汇'''
    tags = ['NN', 'NNPS', 'NNP', 'NNS']
    return [item for item in tagged if item[1] in tags]


def filter_numbers(tagged):
    '''过滤过短的标点及数字'''
    return [item for item in tagged if len(item[0]) > 2 and not item[0].isdigit()]


def normalize(tagged):
    '''去掉词汇中可能的标点'''
    return [(item[0].replace('.', ''), item[1]) for item in tagged]


def normalize_tags(tagged):
    '''词性标准化为前两个字符，如NN'''
    return [(item[0], item[1][0:1]) for item in tagged]


def lowercase(tagged):
    '''词汇小写化'''
    return [(w.lower(), t) for (w, t) in tagged]


def rstopwords(tagged):
    '''去除停用词'''
    sw = nltk.corpus.stopwords.words('english') + ['method', 'research', 'approach', 'study', 'analysis',
                                                   'problem', 'issue', 'ltd', 'elsevier', 'right']
    return [(w, t) for (w, t) in tagged if not w in sw]


def lemmatize(tagged):
    '''提取词干'''
    return [(wnl.lemmatize(item[0]), item[1]) if not ' ' in item[0] else (item[0], item[1]) for item in tagged]


def extract_entity_names(t):
    '''抽取实体名称'''
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
    return entity_names


def joincolloc(tagged, colloc_list):

    tagged1 = []
    sw = 0

    for i in range(len(tagged) - 1):
        if sw == 1:
            sw = 0
            continue
        if (tagged[i], tagged[i + 1]) in colloc_list:
            sw = 1
            if tagged[i][1].startswith('NN') or tagged[i + 1][1].startswith('NN'):
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], 'NN'))
            elif tagged[i][1] == 'RB' or tagged[i + 1][1] == 'RB':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], 'RB'))
            else:
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], tagged[i][1]))
        else:
            tagged1.append(tagged[i])
    if len(tagged) > 0:
        tagged1.append(tagged[len(tagged) - 1])

    return tagged1


def joincollocbi(tagged, colloc_list):

    tagged1 = []
    sw = 0

    for i in range(len(tagged) - 1):
        if sw == 1:
            sw = 0
            continue
        if ' ' in tagged[i][0]:
            t1 = (tagged[i][0][tagged[i][0].find(' '):].strip(), tagged[i][1])
        else:
            t1 = (tagged[i][0], tagged[i][1])
        if ' ' in tagged[i + 1][0]:
            t2 = (tagged[i + 1][0][:tagged[i + 1][0].find(' ')].strip(), tagged[i][1])
        else:
            t2 = (tagged[i + 1][0], tagged[i + 1][1])
        if (t1, t2) in colloc_list:
            sw = 1
            if tagged[i][1] == 'NNP' or tagged[i + 1][1] == 'NNP':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], 'NNP'))
            elif tagged[i][1] == 'NN' or tagged[i + 1][1] == 'NN':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], 'NN'))
            elif tagged[i][1] == 'RB' or tagged[i + 1][1] == 'RB':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], 'RB'))
            else:
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], tagged[i][1]))
        else:
            tagged1.append(tagged[i])
    if len(tagged) > 0:
        tagged1.append(tagged[len(tagged) - 1])

    return tagged1


def groupne2(tagged, entity_names):

    tagged1 = []
    sw = 0

    for i in range(len(tagged) - 1):
        if sw == 1:
            sw = 0
            continue
        if (tagged[i][0] + ' ' + tagged[i + 1][0]) in entity_names:
            sw = 1
            if tagged[i][1] == 'NNP' or tagged[i + 1][1] == 'NNP':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], 'NNP'))
            elif tagged[i][1] == 'NN' or tagged[i + 1][1] == 'NN':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], 'NN'))
            elif tagged[i][1] == 'RB' or tagged[i + 1][1] == 'RB':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], 'RB'))
            else:
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0], tagged[i][1]))
        else:
            tagged1.append(tagged[i])
    if len(tagged) > 0:
      tagged1.append(tagged[len(tagged) - 1])

    return tagged1


def groupne3(tagged, entity_names):
    tagged1 = []
    sw = 0
    for i in range(len(tagged) - 2):
        if sw == 1:
            sw = 0
            continue
        if (tagged[i][0] + ' ' + tagged[i + 1][0] + ' ' + tagged[i + 2][0]) in entity_names:
            sw = 1
            if tagged[i][1] == 'NNP' or tagged[i + 1][1] == 'NNP' or tagged[i + 2][1] == 'NNP':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0] + ' ' + tagged[i + 2][0], 'NNP'))
            elif tagged[i][1] == 'NN' or tagged[i + 1][1] == 'NN' or tagged[i + 2][1] == 'NNP':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0] + ' ' + tagged[i + 2][0], 'NN'))
            elif tagged[i][1] == 'RB' or tagged[i + 1][1] == 'RB' or tagged[i + 2][1] == 'NNP':
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0] + ' ' + tagged[i + 2][0], 'RB'))
            else:
                tagged1.append((tagged[i][0] + ' ' + tagged[i + 1][0] + ' ' + tagged[i + 2][0], tagged[i][1]))
        else:
            tagged1.append(tagged[i])
    if len(tagged) > 1:
        tagged1.append(tagged[len(tagged) - 2])
        tagged1.append(tagged[len(tagged) - 1])
    elif len(tagged) == 1:
        tagged1.append(tagged[len(tagged) - 1])
    return tagged1
