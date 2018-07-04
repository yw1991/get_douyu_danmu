import matplotlib.pyplot as plt  # 导入画图的库
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
import jieba  # jieba分词库
import numpy as np
from PIL import Image
import jieba.analyse

def my_ciyun(path):
    text = open(path, "r", encoding="utf-8").read(10000000)  # 打开所要分析的文本
    alice_coloring = np.array(Image.open("timg.jpg"))  # 传入图片
    wordlist = jieba.cut(text, cut_all=True)
    wl_space_split = " ".join(wordlist)  # 使用结巴进行分词并用空格隔开

    # jieba.load_userdict("userdict.txt")  # 导入自定义词典
    # jieba.analyse.set_stop_words("stopwords.txt")
    # ,allowPOS=('nb','n','nr', 'ns','a','ad','an','nt','nz','v','d')
    tags = jieba.analyse.extract_tags(text, topK=100, withWeight=True,
                                      allowPOS=('nb', 'n', 'nr', 'ns', 'a', 'ad', 'an', 'nt', 'nz', 'v', 'd'))  # 提取关键词

    wc = WordCloud(
        font_path=r"simkai.ttf",  # 修改默认字体库，我这里使用的是Windows里面的楷体，你也可以按这一路径选择喜欢的字体库或者去下载其他字体库
        width=1920,  # 宽
        height=1080,  # 高
        margin=6,
        background_color="white",  # 背景颜色
        max_words=200,  # 最大词量
        mask=alice_coloring,  # 设置背景图片
        max_font_size=130,  # 最大号字体
        # stopwords=STOPWORDS.add("一个")
    )
    # wc.generate(wl_space_split)
    for word, fre in tags:
        print(word, fre)

    keywords = dict(tags)
    wc.generate_from_frequencies(keywords)

    image_colors = ImageColorGenerator(alice_coloring)

    plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis("off")
    plt.show()  # 生成词云

if __name__ == '__main__':
    my_ciyun("result.txt")
