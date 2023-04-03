# The Daily Dose News App

The Daily Dose News App is a Flask application that fetches news articles from an API, summarizes them using the OpenAI GPT-3.5 Turbo model, and sends out a daily email digest at 7 AM CST.

## Features

- Fetches news articles using the NewsData API
- Summarizes news articles with OpenAI GPT-3.5 Turbo model
- Schedules and sends a daily email digest with Mailchimp

## Installation

1. Clone the repository:

```bash 
git clone https://github.com/yourusername/daily_dose_news_app.git
```

2. Change into the project directory:
 ```bash
 cd daily_dose_news_app
 ```

3. Create a virtual environment:

```bash
python -m venv venv
```


4. Activate the virtual environment:

- On Linux/macOS:

```bash
source venv/bin/activate
```


- On Windows:

```bash
venv\Scripts\activate
```


5. Install the required packages:
```bash
pip3 install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root directory and set the following environment variables:

```bash
NEWS_API_KEY=<your_newsdata_api_key>
OPENAI_API_KEY=<your_openai_api_key>
MAILCHIMP_API_KEY=<your_mailchimp_api_key>
MAILCHIMP_LIST_ID=<your_mailchimp_list_id>
```


Replace `<your_*_api_key>` with the respective API keys.

2. Make sure the `email_template/index.html` file is in place with the correct format.

## Usage

1. Run the Flask application:

```bash
python app.py
```


2. Visit the following routes in your web browser or with a tool like `curl`:

- `http://localhost:3000/`: The application's homepage
- `http://localhost:3000/fetch_news`: Fetches news articles and returns them in JSON format
- `http://localhost:3000/fetch_summarized_news`: Fetches summarized news articles and displays them in an HTML list

The application will automatically send out the daily email digest at 7 AM CST.

## Dependencies

- Flask
- requests
- openai
- mailchimp3
- python-dotenv
- re
- datetime
- pytz
- dateutil
- APScheduler

## License

This project is released under the [MIT License](LICENSE).
