from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import authenticate, logout, login
import tweepy,sys,jsonpickle
from .models import Post, Result, Tweet
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
# from django.core.files.storage import FileSystemStorage
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import re, string

try:
    import json
except:
    import simplejson as json




def home(request):
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
	return render(request, 'blog/home.html', {'posts': posts})

def crawling(request):
	return render(request, 'blog/crawling.html',)

def logout_view(request):
	logout(request)
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
	return render(request, 'blog/home.html', {'posts': posts})

def classify(request):
	return render(request, 'blog/classify.html')

def about(request):
	return render(request, 'blog/about.html',)

def login(request):
	return render(request, 'blog/login.html',)

def get_tweets(request):
    if request.POST:
        Result.objects.all().delete()
        Tweet.objects.all().delete()
        #global pos_count, neg_count, net_count
        pos_count = 0
        neg_count = 0
        net_count = 0
        import nltk

        training_data = "D:/klasifikasi/corpus/data_training.txt"

        def load_corpus(fileName):
            corpus = []
            all_words = []

            input = open(fileName, "r")
            for line in input:
                # '#' is the delimiter
                parts = line.split("#")
                label = int(parts[0])
                words = parts[1].split(" ")
                corpus.append((words, label))

                for word in words:
                    all_words.append(word)

            input.close()
            return (corpus, all_words)

        corpus, all_words = load_corpus(training_data)

        words_freqs = nltk.FreqDist(w.lower() for w in all_words)
        word_features = list(words_freqs)[:1200]

        def unigram_features(doc):
            doc_words = set([w.lower() for w in doc])
            features = {}

            for word in word_features:
                if (word in doc_words):
                    features['has({})'.format(word)] = 1
                else:
                    features['has({})'.format(word)] = 0

            return features

        feature_functions = [unigram_features]

        def doc_features(doc):
            features = {}
            for func in feature_functions:
                features.update(func(doc))
            return features

        train_set_features = [(doc_features(d), c) for (d, c) in corpus]
        classifier = nltk.NaiveBayesClassifier.train(train_set_features)

        import tweepy, sys, jsonpickle

        consumer_key = 'Sn1LZiIAudlvCPsxRZnMfGXl7'
        consumer_secret = 'Wuqt6ezDQIuxDO2556l22rjMRbim8D850AiLBFNnuUZPWwCRYm'

        qry = '@gojekindonesia -filter:retweets AND -filter:replies'
        maxTweets = 500
        tweetsPerQry = 100

        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        if (not api):
            sys.exit('Autentikasi gagal, mohon cek "Consumer Key" & "Consumer Secret" Twitter anda')

        sinceId = None
        max_id = -1
        tweetCount = 0

        while tweetCount < maxTweets:
            try:
                if (max_id <= 0):
                    if (not sinceId):
                        new_tweets = api.search(q=qry, count=tweetsPerQry, tweet_mode='extended')
                    else:
                        new_tweets = api.search(q=qry, count=tweetsPerQry, since_id=sinceId, tweet_mode='extended')
                else:
                    if (not sinceId):
                        new_tweets = api.search(q=qry, count=tweetsPerQry, max_id=str(max_id - 1), tweet_mode='extended')
                    else:
                        new_tweets = api.search(q=qry, count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId, tweet_mode='extended')
                if not new_tweets:
                    break
                for tweet in new_tweets:
                    if (tweet._json['user']["name"] != "Transportasi Jakarta" and tweet._json['user']["name"] != "tahuberita" and tweet._json['user']["name"] != "sapikecil" and tweet._json['user']["name"] != "DEMOKRASI" and tweet._json['user']["name"] != "teropongsenayan.com" and tweet._json['user']["name"] != "Infonitas.com" and
                                tweet._json['user']["name"] != "97,5 FM Motion Radio" and "?" not in tweet._json["full_text"] and tweet._json['metadata']["iso_language_code"] == "in"):
                        text = jsonpickle.encode(tweet._json["full_text"], unpicklable=False)
                        created_at = jsonpickle.encode(tweet._json["created_at"], unpicklable=False)

                        text = re.sub(r"(?:\@|#|https? | https?|https?| \://)\S+", " ", text)
                        text = re.sub(r"\n", "", text)

                        character = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                                         'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                        punctuations = '''!()-[]{};:'"\,<>./?#$%^&*_~'''
                        no_pun = " "
                        for char in text:
                            if char not in punctuations:
                                no_pun = no_pun + char
                        text = no_pun

                        for i in range(len(character)):
                            charac_long = 5
                            while charac_long >= 2:
                                char = character[i] * charac_long
                                text = text.replace(char, character[i])
                                charac_long -= 1

                        text = ' '.join(word.strip(string.punctuation) for word in text.split())
                        obj, created = Tweet.objects.get_or_create(created_date=created_at, tweet_text=text)

                        sentence = text
                        result = classifier.classify(doc_features(sentence.split()))

                        if (result == 2):
                            classify_result = 'Positif'
                            pos_count += 1
                        elif (result == 0):
                            classify_result = 'Negatif'
                            neg_count += 1
                        else:
                            classify_result = 'Netral'
                            net_count += 1

                        sentiment2 = Result(sentiment=text.lower(), classification=classify_result)
                        sentiment2.save()

                tweetCount += len(new_tweets)
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                print("some error : " + str(e));
                break

        """messages.add_message(request, messages.INFO, 'Tweets telah tersimpan pada filename: {1}'.format(tweetCount, fname))
        messages.add_message(request, messages.INFO, 'Jumlah Tweets telah tersimpan: %.0f' % tweetCount)
        fo = open(fname + '.json', 'r')
        fw = open(fname + '.txt', 'w')

        for line in fo:
            try:
                tweet = json.loads(line)
                text = re.sub(r"(?:\@ | @|@|https?| https?|https? \://)\S+", "", tweet['full_text'])
                text = re.sub(r"\n", "", text)
                fw.write(text + "\n")
            except:
                continue"""

        """import nltk

        training_data = "C:/Users/Achmad/PycharmProjects/Sentiment_Analysis/corpus/data_training.txt"

        def load_corpus(fileName):
            corpus = []
            all_words = []

            input = open(fileName, "r")
            for line in input:
                # '#' is the delimiter
                parts = line.split("#")
                label = int(parts[0])
                words = parts[1].split(" ")
                corpus.append((words, label))

                for word in words:
                    all_words.append(word)

            input.close()
            return (corpus, all_words)

        corpus, all_words = load_corpus(training_data)

        words_freqs = nltk.FreqDist(w.lower() for w in all_words)
        word_features = list(words_freqs)[:1200]

        def unigram_features(doc):
            doc_words = set([w.lower() for w in doc])
            features = {}

            for word in word_features:
                if (word in doc_words):
                    features['has({})'.format(word)] = 1
                else:
                    features['has({})'.format(word)] = 0

            return features

        feature_functions = [unigram_features]

        def doc_features(doc):
            features = {}
            for func in feature_functions:
                features.update(func(doc))
            return features

        train_set_features = [(doc_features(d), c) for (d, c) in corpus]
        classifier = nltk.NaiveBayesClassifier.train(train_set_features)"""

        # fo = open(fname + '.txt', 'r')
        """Result.objects.all().delete()
        global pos_count, neg_count, net_count
        pos_count = 0
        neg_count = 0
        net_count = 0
        for line in fo:
            sentence = line
            result = classifier.classify(doc_features(sentence.split()))

            if (result == 2):
                classify_result = 'Positive'
                pos_count += 1
            elif (result == 0):
                classify_result = 'Negative'
                neg_count += 1
            else :
                classify_result = 'Neutral'
                net_count += 1

            sentiment2 = Result(sentiment=sentence, classification=classify_result)
            sentiment2.save()"""

        #classifier.show_most_informative_features()

        #test_corpus, _ = load_corpus(testing_data)
        #test_set_features = [(doc_features(d), c) for (d, c) in test_corpus]

        #print(nltk.classify.accuracy(classifier, test_set_features))

    return render(request, 'blog/classify.html', {'obj': Result.objects.all()})