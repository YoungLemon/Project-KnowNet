# 测试停用词表
vocabulary = {"h index": "h-index",
              "hirsch index": "h-index"}


class paper:

    def __init__(self):
        self.pt = ''  # 文献类型
        self.au = []  # 作者（简称）
        self.af = []  # 作者（全称）
        self.ti = ''  # 标题
        self.so = ''  # 来源
        self.dt = ''  # 类型
        self.de = []  # 关键词
        self.id = []  # 附加关键词
        self.ab = ''  # 摘要
        self.cr = dict()  # 参考文献
        self.nr = 0  # 引用的参考文献
        self.tc = 0  # 被引频次（wos核心合集内）
        self.pd = ''  # 出版月
        self.py = 0  # 出版年
        self.vl = 0  # 卷数
        self.IS = 0  # 期数
        self.bp = 0  # 开始页码
        self.ep = 0  # 结束页码
        self.doi = ''  # 文档唯一标识符
        self.sc = ''  # 研究方向

    def get_text(self):
        return self.ab

    def show_all_metadata(p):
        """展示论文的元数据"""
        if not isinstance(p, paper):
            print("参数不是paper数据结构！")
            return
        else:
            print("标题：", p.ti)
            print("DOI：", p.doi)
            print("作者：")
            for a, b in zip(p.au, p.af):
                print("\t", a, " (", b, ")", sep="")
            print("来源：", p.so)
            print("研究方向：", p.sc)
            print("关键词：", end="")
            for kw in p.de:
                print(kw, sep="", end=",")
            print()
            print("附加关键词：", end="")
            for kw in p.id:
                print(kw, sep="", end=",")
            print()
            print("摘要：", p.ab)
            print("参考文献（只收录有DOI的文献）：")
            for ref in p.cr:
                print("\t", ref, ":", p.cr[ref]["au"], p.cr[ref]["py"], p.cr[ref]["so"])
            print("参考文献数：", p.nr)
            print("被引频次（WOS核心合集）：", p.tc)
            print("出版月：", p.pd)
            print("出版年：", p.py)
            print("卷数：", p.vl)
            print("期数：", p.IS)
            print("起始页码：", p.bp)
            print("结束页码：", p.ep)
            print()

    def show_core_metadata(p):
        """展示论文的元数据"""
        if not isinstance(p, paper):
            print("参数不是paper数据结构！")
            return
        else:
            print("标题：", p.ti)
            print("作者：")
            for a, b in zip(p.au, p.af):
                print("\t", a, " (", b, ")", sep="")
            print("来源：", p.so)
            print("关键词：", end="")
            for kw in p.de:
                print(kw, sep="", end=",")
            print()
            print("附加关键词：", end="")
            for kw in p.id:
                print(kw, sep="", end=",")
            print()
            print("摘要：", p.ab)
            print("参考文献数：", p.nr)
            print("被引频次（WOS核心合集）：", p.tc)
            print()


def trim(item):
    return item[3:len(item)-1]


def wos2paper(path, include_review=True):
    """将wos的纯文本引文数据转换成paper对象的列表"""
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    paperlist = []
    with open(path, 'r', encoding='utf-8') as f:
        p = paper()
        au_start = False
        af_start = False
        ti_start = False
        so_start = False
        cr_start = False
        for item in f.readlines():
            if item.startswith("FN") or item.startswith("VR"):      # WOS开头
                continue
            elif item.startswith("PT"):                             # 文献类型
                p.pt = trim(item)
            elif item.startswith("AU"):                             # 作者（简称）
                au_start = True
                p.au.append(trim(item))
            elif item.startswith("AF"):                             # 作者（全称）
                af_start = True
                p.af.append(trim(item))
            elif item.startswith("TI"):                             # 标题
                ti_start = True
                p.ti += (trim(item).lower())
            elif item.startswith("SO"):                             # 机构
                so_start = True
                p.so += (trim(item).lower())
            elif item.startswith("DT"):                             # 文献类型
                p.dt = (trim(item))
            elif item.startswith("DE"):                             # 关键词
                p.de = trim(item).lower().split("; ")
                p.de = [" ".join([lemmatizer.lemmatize(word) for word in kw.split()]) for kw in p.de]
                for i, word in enumerate(p.de):
                    if word in vocabulary:          # 词表同义词替换
                        p.de[i] = vocabulary[word]
                if p.de[-1][-1] == ";":
                    p.de[-1] = p.de[-1][:-1]
            elif item.startswith("ID"):                             # 附加关键词
                p.id = trim(item).lower().split("; ")
            elif item.startswith("AB"):                             # 摘要
                p.ab = trim(item)
            elif item.startswith("CR"):                             # 参考文献
                cr_start = True
                tmp = trim(item).split(", ")
                if tmp[-1].startswith("DOI"):
                    try:
                        pub_year = int(tmp[1])
                        reference = {"au": tmp[0],
                                     "py": pub_year,
                                     "so": tmp[2]}
                    except:
                        reference = {"au": tmp[0],
                                     "py": None,
                                     "so": tmp[1]}
                    p.cr[tmp[-1][4:]] = reference
            elif item.startswith("NR"):                             # 参考文献数
                p.nr = int(trim(item))
            elif item.startswith("TC"):                             # 被引频次（WOS核心合集内）
                p.tc = int(trim(item))
            elif item.startswith("PD"):                             # 出版月
                p.pd = trim(item)
            elif item.startswith("PY"):                             # 出版年
                p.py = int(trim(item))
            elif item.startswith("VL"):                             # 卷数
                try:
                    p.vl = int(trim(item))
                except:
                    p.vl = trim(item)
            elif item.startswith("IS"):                             # 期数
                try:
                    p.IS = int(trim(item))
                except:
                    p.IS = trim(item)
            elif item.startswith("BP"):                             # 开始页码
                try:
                    p.bp = int(trim(item))
                except:
                    p.bp = trim(item)
            elif item.startswith("EP"):                             # 结束页码
                try:
                    p.ep = int(trim(item))
                except:
                    p.ep = trim(item)
            elif item.startswith("DI"):                             # 文档唯一标识符
                p.doi = trim(item)
            elif item.startswith("SC"):                             # 科研方向
                p.sc = trim(item)

            elif item.startswith("ER"):                             # 单篇论文结尾
                if include_review == True or not p.dt == "Review":          # 清除综述
                    paperlist.append(p)
                p = paper()
            elif item.startswith("  "):                             # 空格开头情况的处理
                if au_start:            # 接续作者（简称）
                    p.au.append(trim(item))
                if af_start:            # 接续作者（全称）
                    p.af.append(trim(item))
                if ti_start:            # 接续标题
                    p.ti += (trim(item))
                if so_start:            # 接续机构
                    p.so += (trim(item))
                if cr_start:            # 接续参考文献
                    tmp = trim(item).split(", ")
                    if tmp[-1].startswith("DOI"):
                        try:
                            pub_year = int(tmp[1])
                            reference = {"au": tmp[0],
                                         "py": pub_year,
                                         "so": tmp[2]}
                        except:
                            reference = {"au": tmp[0],
                                         "py": None,
                                         "so": tmp[1]}
                        p.cr[tmp[-1][4:]] = (reference)

            if not (item.startswith("AU") or item.startswith("  ")) and au_start:       # 重置接续作者（简称）的标志
                au_start = False
            if not (item.startswith("AF") or item.startswith("  ")) and af_start:       # 重置接续作者（全称）的标志
                af_start = False
            if not (item.startswith("TI") or item.startswith("  ")) and ti_start:       # 重置标题的标志
                ti_start = False
            if not (item.startswith("SO") or item.startswith("  ")) and so_start:       # 重置标题的标志
                so_start = False
            if not (item.startswith("CR") or item.startswith("  ")) and cr_start:       # 重置标题的标志
                cr_start = False

    return paperlist


def clean_keyword(paperlist):
    """清洗关键词短语"""
    import clean_text
    for p in paperlist:
        tmp = ' '.join(p.de)
        p.de = clean_text.clean_token(tmp)
    return paperlist


def divide_keyword(paperlist):
    """将关键词短语切分成单个词"""
    from nltk.corpus import stopwords
    stoplist = stopwords.words('english')
    for p in paperlist:
        p.de = [word for kw in p.de for word in kw.split() if word not in stoplist]
        p.de = list(set(p.de))
    return paperlist


def ti2de(paperlist):
    """将标题切分成关键词，并替换原有关键词"""
    import clean_text
    for p in paperlist:
        p.de = clean_text.clean_token(p.ti)
    return paperlist


def ab2de(paperlist):
    """将摘要切分成关键词，并替换原有关键词"""
    import clean_text
    for p in paperlist:
        p.de = clean_text.clean_token(p.ab)
    return paperlist


def filter_paper_by_year(paperlist, year):
    """过滤出给定年份的论文"""
    return [paper for paper in paperlist if paper.py == year]


def paper_net(paperlist, node="paper", pt=None):
    import networkx

    if node == "paper":
        g = networkx.DiGraph()
        if pt:
            paperlist = [p for p in paperlist if p.pt == pt]
        g.add_nodes_from(paperlist)
        for p1 in g.nodes:
            for p2 in g.nodes:
                if p2.doi in p1.cr:
                    g.add_edge(p2, p1)

    elif node == "keyword":
        H = networkx.MultiGraph()
        if pt:
            paperlist = [p for p in paperlist if p.pt == pt]
        kwlist = list(set([kw for p in paperlist for kw in p.de]))
        H.add_nodes_from(kwlist)
        for p in paperlist:
            for kw1 in p.de:
                for kw2 in p.de:
                    if kw1 != kw2:
                        H.add_edge(kw1, kw2, weight=1)
        g = networkx.Graph()
        for u, v, d in H.edges(data=True):
            w = d['weight']
            if g.has_edge(u, v):
                g[u][v]['weight'] += w
            else:
                g.add_edge(u, v, weight=w)
    return g
