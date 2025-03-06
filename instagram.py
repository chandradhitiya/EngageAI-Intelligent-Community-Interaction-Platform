import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
import datetime

# Prepare the data
data = {
    "hashtags": ["farmmadefoods", "yourightchoice", "freeerangeeggs", 
                 "freerange", "eggshells", "faqs"],
    "comment": {
        "text": "Why do I have gas and constipation problems after eating eggs?",
        "username": "albertheimer2024",
        "timestamp": "2025-02-24T17:19:22.000Z",
        "likes_count": 0,
        "replies_count": 0
    }
}

# Set style for better visuals
plt.style.use('seaborn')
sns.set_palette("husl")

# Create figure with subplots
fig = plt.figure(figsize=(15, 10))

# 1. Hashtag Frequency Bar Plot
plt.subplot(2, 2, 1)
hashtags = pd.Series(data['hashtags'])
hashtag_counts = hashtags.value_counts()
sns.barplot(x=hashtag_counts.values, y=hashtag_counts.index)
plt.title('Hashtag Distribution')
plt.xlabel('Count')
plt.ylabel('Hashtags')
for i, v in enumerate(hashtag_counts.values):
    plt.text(v + 0.1, i, str(v), va='center')

# 2. Word Cloud of Hashtags
plt.subplot(2, 2, 2)
wordcloud = WordCloud(width=400, height=300, 
                     background_color='white',
                     min_font_size=10).generate(' '.join(data['hashtags']))
plt.imshow(wordcloud)
plt.axis('off')
plt.title('Hashtag Word Cloud')

# 3. Comment Length Analysis
plt.subplot(2, 2, 3)
comment_length = len(data['comment']['text'].split())
plt.bar(['Comment'], [comment_length])
plt.title('Comment Word Count')
plt.ylabel('Number of Words')
plt.text(0, comment_length + 0.5, str(comment_length), ha='center')

# 4. Post Metadata Pie Chart
plt.subplot(2, 2, 4)
metadata = [data['comment']['likes_count'], 
           data['comment']['replies_count'],
           1]  # 1 for the comment itself
labels = ['Likes', 'Replies', 'Comment']
plt.pie(metadata, labels=labels, autopct='%1.1f%%')
plt.title('Engagement Distribution')

# Adjust layout and display
plt.tight_layout()
plt.suptitle('Social Media Post Visualization Insights', y=1.05, fontsize=16)
plt.show()

# Additional Time-based Analysis
timestamp = datetime.datetime.strptime(data['comment']['timestamp'], 
                                     '%Y-%m-%dT%H:%M:%S.%fZ')
hour = timestamp.hour

plt.figure(figsize=(8, 4))
plt.bar(['Post Hour'], [hour])
plt.title('Posting Time')
plt.ylabel('Hour (24h format)')
plt.text(0, hour + 0.5, f'{hour}:00', ha='center')
plt.ylim(0, 24)
plt.show()

# Print basic statistics
print(f"Number of hashtags: {len(data['hashtags'])}")
print(f"Comment length (words): {comment_length}")
print(f"Posting time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Engagement - Likes: {data['comment']['likes_count']}, Replies: {data['comment']['replies_count']}")