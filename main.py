import time
import json
import requests
import re
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import google.generativeai as genai
import streamlit as st
import pandas as pd

# Slack Bot Token and Channel ID
SLACK_BOT_TOKEN = "xoxb-8510734922882-8512814576514-NY7ELHsuIv0dIlHreAQLqhB8"
CHANNEL_ID = "C08EMEEKQPR"

# Initialize Slack Client
client = WebClient(token=SLACK_BOT_TOKEN)

# Configure Gemini AI
genai.configure(api_key="AIzaSyDK_65-5M677JjChV-Ockv9v8HNpWExj4o")
model = genai.GenerativeModel("gemini-1.5-pro")

# List of URLs to fetch content from
WEBSITE_URLS = [
    'https://farmmadefoods.com/collections/free-range-eggs?customer_posted=true',
    'https://farmmadefoods.com/products/farm-made-foods-free-range-eggs-6',
    'https://farmmadefoods.com/products/natural-coconut-sugar',
    'https://farmmadefoods.com/products/coconut-sugar-delights',
    'https://farmmadefoods.com/blogs/recipe/sunny-side-up-eggs',
    'https://farmmadefoods.com/blogs/recipe/mixed-herbs-omelette-easy-healthy-breakfast-recipe',
    'https://farmmadefoods.com/blogs/recipe/english-breakfast-recipe-easy-guide',
    'https://farmmadefoods.com/blogs/recipe/eggcellent-zesty-delight',
    'https://farmmadefoods.com/blogs/recipe/scrambled-eggs-recipe',
    'https://www.medicalnewstoday.com/articles/327423#nutritional-differences',
    'https://en.wikipedia.org/wiki/Free-range_eggs',
    'https://www.healthline.com/nutrition/coconut-sugar#TOC_TITLE_HDR_6',
    'https://en.wikipedia.org/wiki/Coconut_sugar'
]

# Load extracted Reddit dataset
with open('reddit_data.json', 'r', encoding='utf-8') as f:
    market_data = json.load(f)

# Define keywords to filter questions
keywords = ["farm made eggs", "free range", "farm fresh", "organic eggs", "local farm"]

def is_question(text):
    return text.strip().endswith('?')

def contains_keywords(text, keywords):
    return any(keyword.lower() in text.lower() for keyword in keywords)

# Extract and sort relevant questions
question_posts = [post for post in market_data if is_question(post['title']) and contains_keywords(post['title'], keywords)]
question_posts_sorted = sorted(question_posts, key=lambda x: x['engagement_score'], reverse=True)

def get_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Error: Unable to fetch {url}. Status code: {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.text for p in soup.find_all("p")]
        return " ".join(paragraphs)[:2000]
    except Exception as e:
        return f"Error: {str(e)}"

def get_combined_web_content():
    combined_text = ""
    for url in WEBSITE_URLS:
        extracted_text = get_text_from_url(url)
        if "Error:" not in extracted_text:
            combined_text += extracted_text + "\n\n"
    return combined_text[:4000]

def ask_gemini(question):
    webpage_text = get_combined_web_content()
    prompt = f"Based on the following webpage content, answer the question concisely in under 400 characters:\n\n{webpage_text}\n\nQuestion: {question}"
    response = model.generate_content(prompt)
    answer = response.text.strip()[:400]
    if "I don't know" in answer or len(answer) < 50:
        return "Sorry, we will get back to you later."
    return answer

def send_message(question, answer):
    message = f"❓ *Question:* {question}\n✅ *Answer:* {answer}\n\n📝 Reply with 'approve' or suggest a change."
    try:
        response = client.chat_postMessage(channel=CHANNEL_ID, text=message)
        return response["ts"]
    except SlackApiError as e:
        return f"Error: {e.response['error']}"

def check_replies(timestamp, max_retries=10, interval=5):
    retries = 0
    while retries < max_retries:
        try:
            response = client.conversations_replies(channel=CHANNEL_ID, ts=timestamp)
            messages = response.get("messages", [])
            if len(messages) > 1:
                for msg in messages[1:]:
                    user = msg.get("user", "Unknown User")
                    text = msg.get("text", "").strip()
                    if text.lower() == "approve":
                        return "approved"
                    else:
                        return text
            time.sleep(interval)
            retries += 1
        except SlackApiError as e:
            return f"Error: {e.response['error']}"
    return "No valid response received."

# Streamlit frontend
st.title("Automated Reddit Q&A with Gemini AI and Slack Bot")

# Display extracted content in Excel-like table format
st.subheader("Extracted Web Content from Multiple Sources")

# Create a dataframe for the extracted content (Excel-like table)
extracted_content = []
for url in WEBSITE_URLS:
    extracted_content.append({
        "URL": url,
        "Extracted Text": get_text_from_url(url)
    })

# Display content as a table
content_df = pd.DataFrame(extracted_content)
st.dataframe(content_df)

# Display the top 10 Reddit Questions in a table format
if question_posts_sorted:
    top_questions = question_posts_sorted[:10]
    question_df = pd.DataFrame([{
        "Title": post['title'],
        "Engagement Score": post['engagement_score'],
        "URL": post['url']
    } for post in top_questions])

    st.subheader("Top 10 Reddit Questions")
    st.table(question_df)

    # User selects a question to process
    selected_question = st.selectbox("Select a Question to Process", options=top_questions, format_func=lambda x: x['title'])

    if selected_question:
        st.write(f"Processing selected question: {selected_question['title']}")
        
        # Display Web Content
        st.subheader("Web Content Extraction")
        combined_content = get_combined_web_content()
        st.text_area("Extracted Web Content", combined_content, height=200)
        time.sleep(10)

        # Ask Gemini AI
        st.subheader("Gemini AI Response")
        answer = ask_gemini(selected_question['title'])
        st.write(answer)
        time.sleep(10)

        # Send message to Slack
        st.subheader("Sending Message to Slack")
        ts = send_message(selected_question['title'], answer)
        if isinstance(ts, str) and ts.startswith("Error"):
            st.error(f"❌ Error sending message to Slack: {ts}")
        else:
            st.success("✅ Message sent to Slack!")
        time.sleep(10)

        # Check for replies
        st.subheader("Checking for Slack Replies")
        response = check_replies(ts)
        if response == "approved":
            st.success("✅ Final Response: Approved")
        elif response:
            st.write(f"✏️ Suggested Change: {response}")
        else:
            st.error("❌ No valid response received.")
        
        time.sleep(10)

else:
    st.write("No relevant Reddit questions found.")

# Loop functionality for processed comments
while True:
    if question_posts_sorted:
        # Re-run the process for the next set of questions
        selected_question = question_posts_sorted[0]
        st.write(f"Re-processing the first question: {selected_question['title']}")
        # Re-execute the process similar to above without duplicating data output
        # Rest of the logic...
    time.sleep(60)  # Pause for 1 minute
