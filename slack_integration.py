import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack Bot Token and Channel ID
SLACK_BOT_TOKEN = "xoxb-8510734922882-8512814576514-NY7ELHsuIv0dIlHreAQLqhB8"
CHANNEL_ID = "C08EMEEKQPR"

# Initialize Slack Client
client = WebClient(token=SLACK_BOT_TOKEN)

# Function to send a question and answer
def send_message(question, answer):
    message = f"❓ *Question:* {question}\n✅ *Answer:* {answer}\n\n📝 Reply with 'approve' or suggest a change."
    try:
        response = client.chat_postMessage(channel=CHANNEL_ID, text=message)
        print("✅ Message sent successfully.")
        return response["ts"]  # Return message timestamp for tracking replies
    except SlackApiError as e:
        print(f"❌ Error sending message: {e.response['error']}")
        return None

# Function to check for customer replies
def check_replies(timestamp, max_retries=10, interval=5):
    """Continuously checks for replies at intervals until max retries"""
    retries = 0
    while retries < max_retries:
        try:
            response = client.conversations_replies(channel=CHANNEL_ID, ts=timestamp)
            messages = response.get("messages", [])

            if len(messages) > 1:  # If there are replies
                for msg in messages[1:]:  # Skip the original bot message
                    user = msg.get("user", "Unknown User")
                    text = msg.get("text", "").strip()
                    print(f"📩 Customer Response from {user}: {text}")

                    if text.lower() == "approve":
                        print("✅ Approved")
                        return "approved"
                    else:
                        print(f"✏️ Suggested Change: {text}")
                        return text

            print("⏳ No replies yet... Checking again.")
            time.sleep(interval)  # Wait before checking again
            retries += 1

        except SlackApiError as e:
            print(f"❌ Error fetching replies: {e.response['error']}")
            break  # Stop checking if an error occurs

    print("❌ No response received within the given time.")
    return None

# Example Usage
if __name__ == "__main__":
    question = "What is the capital of India?"
    answer = "New Delhi"

    ts = send_message(question, answer)  # Send the message

    if ts:
        time.sleep(40)  # Allow Slack to process the message
        response = check_replies(ts)  # Start checking for replies

        if response:
            print(f"✅ Final Response: {response}")
        else:
            print("❌ No valid response received.")
