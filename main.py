import csv
import time
import matplotlib.pyplot as plt
import feedparser
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx

import re
import string
import os

# Download the stopwords if not already downloaded
nltk.download('stopwords')
nltk.download('punkt')

# Variables to customize
num_keywords_shown = 25

# Read RSS feed URLs from CSV file
rss_feeds = []
with open('rssfeeds.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        rss_feed_url = row[0]
        rss_feeds.append(rss_feed_url)

# Parse the RSS feeds and collect post bodies
post_bodies = []
for rss_feed_url in rss_feeds:
    feed = feedparser.parse(rss_feed_url)
    for entry in feed.entries:
        post_body = entry.get('summary', '')
        post_bodies.append(post_body)

# Append the post bodies to the "post_bodies.csv" file
post_bodies_csv_filename = "post_bodies.csv"
file_exists = os.path.isfile(post_bodies_csv_filename)

with open(post_bodies_csv_filename, "a", newline="", encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    if not file_exists:  # Check if the file already exists
        writer.writerow(["Post Body"])  # Write the header if it's a new file
    writer.writerows([[body] for body in post_bodies])

print(f"Post bodies appended to {post_bodies_csv_filename}.")

# Wait for 5 seconds
time.sleep(5)

# Read keywords from CSV file
keywords_csv_filename = "keywords.csv"
keywords = []
with open(keywords_csv_filename, "r") as csv_file:
    reader = csv.reader(csv_file)
    next(reader)  # Skip header
    for row in reader:
        keyword = row[0]
        keywords.append(keyword.lower())

# Read post bodies from CSV file
post_bodies = []
with open(post_bodies_csv_filename, "r", encoding='utf-8') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        post_body = row[0]
        post_bodies.append(post_body)

# Split post bodies into words and apply filters
stopwords_set = set(stopwords.words('english'))
words = []
for post_body in post_bodies:
    tokens = word_tokenize(post_body.lower())
    for word in tokens:
        # Filter out stopwords, URLs, HTML tags, punctuation, and single characters
        if (
            word.isalpha() and
            word not in stopwords_set and
            len(word) > 1 and
            not re.match(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", word) and
            not re.match(r"<[a-zA-Z\/][^>]*>", word) and  # Exclude HTML tags
            not word.endswith("ing") and
            word not in string.punctuation  # Exclude common punctuation marks
        ):
            words.append(word)

# Filter words based on keywords
filtered_words = [word for word in words if word.lower() not in keywords]

# Count word frequencies
word_counts = Counter(filtered_words)

# Get the most common words and their frequencies
common_words = [word for word, count in word_counts.most_common(num_keywords_shown)]
word_frequencies = [count for word, count in word_counts.most_common(num_keywords_shown)]

# Generate bar chart
plt.figure(figsize=(10, 6))
plt.bar(common_words, word_frequencies)
plt.xlabel("Words")
plt.ylabel("Frequency")
plt.title(f"Most Common Words in Post Bodies (Filtered, Top {num_keywords_shown})")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Generate word cloud
wordcloud = WordCloud(width=800, height=400).generate(' '.join(common_words))

# Display the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# Generate the network graph
G = nx.Graph()
for word, frequency in zip(common_words, word_frequencies):
    G.add_node(word, label=word, frequency=frequency)

# Add edges between common words based on their co-occurrence
for i in range(len(common_words)):
    for j in range(i + 1, len(common_words)):
        word1 = common_words[i]
        word2 = common_words[j]
        if word1 != word2:
            G.add_edge(word1, word2)

# Set the positions of the nodes in the network graph
pos = nx.spring_layout(G)

# Get the frequencies of the nodes
node_frequencies = nx.get_node_attributes(G, 'frequency')

# Scale the node sizes for the graph
node_sizes = [1000 * node_frequencies[node] for node in G.nodes()]
max_node_size = max(node_sizes)
scaled_node_sizes = [size / max_node_size * 500 for size in node_sizes]  # Adjust the scaling factor (500) as desired

# Draw the network graph with modified attributes
plt.figure(figsize=(10, 6))
nx.draw_networkx(
    G,
    pos,
    with_labels=True,
    labels=nx.get_node_attributes(G, 'label'),
    node_color='skyblue',
    node_size=scaled_node_sizes,
    font_size=10,
    font_color='black',
    font_weight='bold',  # Set the label text to bold
    edge_color='lightgrey',  # Set the connection lines to grey
    width=1,
    alpha=0.7
)
plt.title("Network Graph of Common Words (Weighted by Frequency)")
plt.axis('off')
plt.tight_layout()
plt.show()
