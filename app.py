from flask import Flask, jsonify, render_template_string
import requests
import openai
from mailchimp3 import MailChimp
import os
from dotenv import load_dotenv
import re
from datetime import datetime, timedelta
import pytz
from pytz import timezone
from dateutil.parser import parse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger


load_dotenv()
news_api_key = os.getenv("NEWS_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
mailchimp_api_key = os.getenv("MAILCHIMP_API_KEY")
mailchimp_list_id = os.getenv("MAILCHIMP_LIST_ID")


def send_email_daily():
    response = fetch_news(news_api_key)
    news = response.get("results", [])

    summarized_news = []
    for article in news:
        text = f"{article['title']}\n{article['content']}"
        # Extract the first 3 and last 3 sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        if len(sentences) > 6:
            text = " ".join(sentences[:3] + sentences[-3:])
        summary = generate_summary(openai_api_key, text)
        if is_incomplete_sentence(summary):
            summary = revise_summary(openai_api_key, summary)
        summarized_news.append(summary)

    send_daily_dose_email(summarized_news)


def send_daily_dose_email(summarized_news):

    with open("email_template/index.html", "r") as file:
        html_template = file.read()

    client = MailChimp(mc_api=mailchimp_api_key)

    # Create a new campaign
    campaign = client.campaigns.create({
        'type': 'regular',
        'recipients': {
            'list_id': mailchimp_list_id
        },
        'settings': {
            'subject_line': 'Your Daily Dose',
            'title': 'Daily Dose Campaign-7',
            'from_name': 'The Daily Dose',
            'reply_to': 'jordan@getthedailydose.com'
        }
    })

    # Set the campaign's content with the AI-generated summaries
    html_content = "<ul>" + "".join(f"<li>{summary}</li>" for summary in summarized_news) + "</ul>"
    final_html = html_template.replace("{content}", html_content)
    client.campaigns.content.update(campaign['id'], {
        'html': final_html
    })

    client.campaigns.actions.send(campaign['id'])

    # Schedule the campaign to be sent
    # next_7am_cst = get_next_7am_cst().astimezone(pytz.timezone('UTC'))
    # client.campaigns.actions.schedule(campaign['id'], {
    #     'schedule_time': next_7am_cst
    # })

def get_next_7am_cst():
    now = datetime.now(pytz.timezone('US/Central'))
    next_7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if next_7am <= now:
        next_7am += timedelta(days=1)
    return next_7am

def is_incomplete_sentence(summary):
    last_char = summary[-1]
    return last_char not in {".", "!", "?"}

def generate_summary(api_key, text, model="gpt-3.5-turbo", max_length=100):
    openai.api_key = api_key

    prompt = f"Please provide a concise summary (in about {max_length} words) of the following news article that includes all important information and does not cut off:\n\n{text}\n\nSummary:"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_length,
        temperature=0.5,
    )

    return response['choices'][0]['message']['content'].strip()

def revise_summary(api_key, initial_summary, model="gpt-3.5-turbo", max_length=100):
    openai.api_key = api_key

    prompt = f"The following summary has some incomplete sentences. Please rephrase and complete the sentences to provide a coherent and concise summary:\n\n{initial_summary}\n\nRevised summary:"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_length,
        temperature=0.5,
    )

    return response['choices'][0]['message']['content'].strip()

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, world!'

@app.route('/fetch_news')
def get_news():
    news = fetch_news(news_api_key)
    return jsonify(news)

def fetch_news(api_key, language="en", query="top"):
    url = "https://newsdata.io/api/1/news"
    params = {
        "language": language,
        "q": query,
        "apikey": api_key,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None


summarized_news = []

# summarized_news = ["Imran Khan, the chairman of the Pakistan Tehreek-e-Insaf (PTI) party, has stated that his team may participate in talks focused on holding elections, but he himself will not negotiate with what he considers to be corrupt officials. Instead, he has instructed his party leaders to reach out to other political parties and civil society groups to gain support for the Supreme Court. The PTI's Vice-Chair will likely be involved in any negotiations that take place."]

@app.route('/fetch_summarized_news')
def get_summarized_news():
    response = fetch_news(news_api_key)
    news = response.get("results", [])


    if len(summarized_news)==0:
        for article in news:
            text = f"{article['title']}\n{article['content']}"
            # Extract the first 3 and last 3 sentences
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
            if len(sentences)>6:
                text = " ".join(sentences[:3] + sentences[-3:])
            summary = generate_summary(openai_api_key, text)
            if is_incomplete_sentence(summary):
                # print(summary)
                summary = revise_summary(openai_api_key, summary)
            summarized_news.append(summary)

    # send_daily_dose_email(summarized_news)
    # Create an HTML list for better readability in the browser
    html_list = "<ul>" + "".join(f"<li>{summary}</li>" for summary in summarized_news) + "</ul>"
    return render_template_string(html_list)


scheduler = BackgroundScheduler(timezone=timezone('US/Central'))

# scheduler.add_job(send_email_daily, 'cron', hour=7)
# scheduler.start()

if __name__ == '__main__':
    print("Scheduling email sending job")
    scheduler.add_job(send_email_daily, 'cron', hour=7)
    scheduler.start()
    test_time = datetime.now() + timedelta(minutes=2)  # Schedule the job to run 2 minutes from now
    # scheduler.add_job(send_email_daily, DateTrigger(test_time))
    # scheduler.start()

    app.run(host='0.0.0.0', debug=False, port=3000)