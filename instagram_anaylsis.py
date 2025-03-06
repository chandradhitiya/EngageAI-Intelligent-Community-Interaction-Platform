import json
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from wordcloud import WordCloud

# Load the JSON data
with open('processed_instagram_dataset.json', 'r') as f:
    data = json.load(f)

posts = data['posts']

# 1. Time Series Analysis of Post Engagement
def time_series_engagement(posts):
    """Creates time series plots of likes, comments, and engagement score."""
    df = pd.DataFrame(posts)
    # Extract timestamp from post data directly instead of URL
    df['timestamp'] = pd.to_datetime([post.get('timestamp', None) for post in posts])
    df = df.dropna(subset=['timestamp'])
    df = df.set_index('timestamp')
    df = df[['likesCount', 'commentsCount', 'engagement_score']].sort_index()

    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    df['likesCount'].plot(ax=axes[0], title='Likes Over Time', color='blue')
    axes[0].set_ylabel('Number of Likes')
    
    df['commentsCount'].plot(ax=axes[1], title='Comments Over Time', color='green') 
    axes[1].set_ylabel('Number of Comments')
    
    df['engagement_score'].plot(ax=axes[2], title='Engagement Score Over Time', color='red')
    axes[2].set_ylabel('Engagement Score')

    plt.tight_layout()
    plt.show()

# 2. Scatter Plot: Engagement Score vs. Caption Sentiment
def scatter_engagement_vs_sentiment(posts):
    """Creates a scatter plot of engagement score vs. caption sentiment."""
    df = pd.DataFrame(posts)
    df = df.dropna(subset=['engagement_score', 'caption_sentiment'])

    plt.figure(figsize=(10, 8))
    plt.scatter(df['caption_sentiment'], df['engagement_score'], alpha=0.6, c='blue')
    
    # Add trend line
    z = np.polyfit(df['caption_sentiment'], df['engagement_score'], 1)
    p = np.poly1d(z)
    plt.plot(df['caption_sentiment'], p(df['caption_sentiment']), "r--", alpha=0.8)
    
    plt.title('Engagement Score vs. Caption Sentiment')
    plt.xlabel('Caption Sentiment')
    plt.ylabel('Engagement Score')
    plt.grid(True, alpha=0.3)
    plt.show()

# 3. Bar Chart: Average Comment Sentiment by Post
def bar_chart_comment_sentiment(posts):
    """Creates a bar chart of average comment sentiment by post."""
    df = pd.DataFrame([{
        'url': post['url'],
        'avg_sentiment': post['comment_stats']['avg_sentiment']
    } for post in posts])
    
    df = df.sort_values('avg_sentiment', ascending=False).head(15)  # Show top 15 posts

    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(df)), df['avg_sentiment'], color='skyblue')
    plt.xticks(range(len(df)), [f"Post {i+1}" for i in range(len(df))], rotation=45)
    plt.title('Average Comment Sentiment by Post (Top 15)')
    plt.xlabel('Posts')
    plt.ylabel('Average Sentiment')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()

# 4. Word Cloud: Most Frequent Hashtags
def wordcloud_hashtags(posts):
    """Creates a word cloud of the most frequent hashtags."""
    all_hashtags = []
    for post in posts:
        if 'hashtags' in post and post['hashtags']:
            all_hashtags.extend(post['hashtags'])

    if not all_hashtags:
        print("No hashtags found in the dataset")
        return

    hashtag_counts = Counter(all_hashtags)
    wordcloud = WordCloud(
        width=1200, 
        height=600,
        background_color='white',
        colormap='viridis',
        max_words=100
    ).generate_from_frequencies(hashtag_counts)

    plt.figure(figsize=(15, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Most Frequent Hashtags', pad=20, size=15)
    plt.show()

# 5. Bar Chart: Engagement by Category
def bar_chart_engagement_by_category(posts):
    """Creates a bar chart of average likes and comments by engagement category."""
    df = pd.DataFrame(posts)
    category_stats = df.groupby('engagement_category').agg({
        'likesCount': 'mean',
        'commentsCount': 'mean'
    }).reindex(['low', 'medium', 'high'])

    x = np.arange(len(category_stats.index))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 8))
    rects1 = ax.bar(x - width/2, category_stats['likesCount'], width, 
                    label='Average Likes', color='lightblue')
    rects2 = ax.bar(x + width/2, category_stats['commentsCount'], width,
                    label='Average Comments', color='lightgreen')

    ax.set_ylabel('Count')
    ax.set_title('Average Engagement Metrics by Category')
    ax.set_xticks(x)
    ax.set_xticklabels(category_stats.index.str.capitalize())
    ax.legend()

    # Add value labels
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.0f}',
                       xy=(rect.get_x() + rect.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Run the visualizations
    time_series_engagement(posts)
    scatter_engagement_vs_sentiment(posts)
    bar_chart_comment_sentiment(posts)
    wordcloud_hashtags(posts)
    bar_chart_engagement_by_category(posts)
