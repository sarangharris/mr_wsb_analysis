from pyspark.sql import SparkSession
import couchdb
import math
from better_profanity import profanity
import pandas as pd
import re
import string
from operator import add
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


server = couchdb.Server('http://$USER:$USERPASS@129.114.27.39:30001/')

def main():
    words = preprocess()
    spark = SparkSession.builder.appName("WSB_Sentiment").getOrCreate()
    rdd = spark.sparkContext.parallelize(words)
    counts = rdd.map(lambda x: (x, 1)) \
                .reduceByKey(add)
    output = counts.collect()
    spark.stop()
    
    # sort by descending
    sorted_output = sorted(output, key = lambda x: -1*int(x[1]))
    
    # graph and send to db
    graph(sorted_output)
    write_to_db(sorted_output)

def preprocess():
    # Read from the file
    df = pd.read_csv("reddit_wsb.csv")
    data = df.dropna()
    titles = data.title
    bodies = data.body
    title_words = "\n".join(titles).lower()
    body_words = "\n".join(bodies).lower()
    all_words = title_words + body_words
    words = re.findall(r'\w+', all_words)
    
    # remove stop words and profanity
    stop_set = ['s','t', 'm', 'stock', 'going', 'know', 'https', 'will', 'don', 're', 'us', 'reddit', 'still'] + list(STOPWORDS)
    filtered_words = [word for word in words if word not in stop_set and word.isalpha() and not profanity.contains_profanity(word)]
    
    return filtered_words
    
def graph(data):
    word_dict = {}
    for word, count in data:
        word_dict[word] = count
    
    wordcloud = WordCloud(background_color='black', collocations=False, max_words=50)
    wordcloud.generate_from_frequencies(frequencies=word_dict)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title('Sentiment Analysis of WSB')
    plt.savefig("result.png")

def write_to_db(data):
    dbname = "sentiment_analysis"
    if dbname in server:
        db = server[dbname]
    else:
        db = server.create(dbname)
    for (word, count) in data:
        db[str(word)] = {'frequency': str(count)}

if __name__ == '__main__':
    main()
