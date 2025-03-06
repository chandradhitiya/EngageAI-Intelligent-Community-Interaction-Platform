import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configure API key
genai.configure(api_key="AIzaSyDK_65-5M677JjChV-Ockv9v8HNpWExj4o")

# Create a custom Gemini model instance
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
    'https://farmmadefoods.com/pages/contact',
    'https://farmmadefoods.com/pages/about-us',
    'https://farmmadefoods.com/pages/refund-policy',
    'https://www.medicalnewstoday.com/articles/327423#nutritional-differences',
    'https://en.wikipedia.org/wiki/Free-range_eggs',
    'https://www.healthline.com/nutrition/coconut-sugar#TOC_TITLE_HDR_6',
    'https://en.wikipedia.org/wiki/Coconut_sugar',
    'https://www.eater.com/2019/7/17/20696498/whats-the-difference-cage-free-free-range-pasture-raised-eggs',
    'https://www.soilassociation.org/take-action/organic-living/what-is-organic/organic-eggs/',
    'https://www.egginfo.co.uk/egg-facts-and-figures/production/free-range-egg',
    'https://www.heritagepinesfarm.com/farm-blog/free-range-eggs-faqs/',
    'https://www.thespruceeats.com/whats-cracking-with-organic-eggs-1708923',
    'https://www.usda.gov/about-usda/news/blog/eggstra-eggstra-learn-all-about-them',
    'https://www.teagasc.ie/rural-economy/rural-development/diversification/free-range-egg-production/',
    'https://www.allrecipes.com/is-it-safe-to-eat-eggs-with-blood-spots-11684973'
]

# Function to extract text from a webpage
def get_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Error: Unable to fetch {url}. Status code: {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.text for p in soup.find_all("p")]
        return " ".join(paragraphs)[:2000]  # Limit text from each website to 2000 chars

    except Exception as e:
        return f"Error: {str(e)}"

# Function to merge content from multiple websites
def get_combined_web_content():
    combined_text = ""
    for url in WEBSITE_URLS:
        extracted_text = get_text_from_url(url)
        if "Error:" not in extracted_text:
            combined_text += extracted_text + "\n\n"

    return combined_text[:4000]

# Function to generate answers using Gemini with fallback
def ask_gemini(question):
    webpage_text = get_combined_web_content()

    try:
        # Try to answer using custom data
        prompt = f"Based on the following webpage content, answer the question concisely in under 400 characters:\n\n{webpage_text}\n\nQuestion: {question}"
        response = model.generate_content(prompt)
        answer = response.text.strip()[:400]

        # If no relevant answer found, use normal Gemini model
        if "I don't know" in answer or len(answer) < 50:
            # Create a normal Gemini model instance
            normal_model = genai.GenerativeModel("gemini-1.5-flash")  # Use a suitable model name

            # Generate answer using normal model
            normal_response = normal_model.generate_content(question)
            normal_answer = normal_response.text.strip()[:400]

            return normal_answer

        return answer

    except Exception as e:
        print(f"Error occurred: {e}")
        return "Sorry, an error occurred while processing your request."

# Dynamic Question Input
if __name__ == "__main__":
    while True:
        question = input("\nEnter your question (or type 'exit' to quit): ").strip()
        if question.lower() == "exit":
            print("Exiting...")
            break

        answer = ask_gemini(question)
        print("\nAnswer:", answer)
