#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.append('/home/aha/Other_Project/jieba/')
import jieba
import jieba.analyse
import psycopg2
jieba.set_dictionary('./dict/dict.txt.big')
jieba.load_userdict("./dict/user_dict.txt")


sentence = "獨立音樂需要大家一起來推廣，歡迎加入我們的行列！"
print "Input：", sentence
words = jieba.cut(sentence, cut_all=False)
print "Output 精確模式 Full Mode："
for word in words:
    print word

sentence = "独立音乐需要大家一起来推广，欢迎加入我们的行列！"
print "Input：", sentence
words = jieba.cut(sentence, cut_all=False)
print "Output 精確模式 Full Mode："
for word in words:
    print word
