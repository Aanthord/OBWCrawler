# OBWCrawler
# YouTube Video Crawler

This Python script allows you to search for videos on YouTube based on specified keywords and recursively explore related videos up to a specified depth. The script implements exponential backoff and rate limiting to handle errors and comply with YouTube's API usage guidelines.

## Inspiration

This project was inspired by the [noisy](https://github.com/1tayH/noisy) project by [1tayH](https://github.com/1tayH), which showcases techniques for programmatically browsing the web while handling various challenges such as dynamic content and JavaScript rendering.

## Responsible Usage

This script is provided for educational and personal use purposes only. It is your responsibility to ensure that your use of this script complies with all applicable laws, regulations, and terms of service. The authors and contributors of this script assume no liability for any misuse, violation of terms, or unintended consequences resulting from the use of this script.

Please note that any attempt to manipulate platforms, bypass security measures, or engage in activities that violate the terms of service or applicable laws could result in severe consequences, including but not limited to legal action, account suspension, or service termination.

By using this script, you acknowledge and agree that you are solely responsible for your actions and any consequences that may arise from the use or misuse of this script.

## Features

- Search for videos on YouTube by keyword
- Recursively explore related videos based on video titles and descriptions
- Implement exponential backoff and rate limiting for API requests
- Save search results to a flat file for further processing
- Customizable configuration options
- Logging for better visibility and debugging

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Obtain a YouTube Data API key from the Google Developers Console and add it to the `config.json` file.

## Usage

1. Configure the desired settings in the `config.json` file, such as keywords, maximum results per keyword, rate limiting, and depth of exploration.
2. Run the script using `python your_script.py`.
3. The script will search for videos based on the specified keywords and recursively explore related videos up to the configured depth.
4. The search results will be logged to the console and saved to a file named `search_results.txt`.

## Configuration

The `config.json` file contains the following configurable options:

- `api_key`: Your YouTube Data API key (required)
- `keywords`: A list of keywords to search for on YouTube
- `max_results_per_keyword`: The maximum number of search results to fetch for each keyword
- `requests_per_second`: The maximum number of API requests per second
- `max_depth`: The maximum depth for exploring related videos
- `max_retries`: The maximum number of retry attempts for each search query
- `default_timeout`: The initial timeout value (in seconds) for the exponential backoff calculation

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
