import json
import logging
import logging.config
import os
import random
import re
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

def load_config():
    """
    Loads the config file containing search keywords, rate limiting settings,
    API key, and other preferences.
    """
    try:
        logging.info('Loading configuration from config.json')
        with open('config.json', 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        logging.error('Configuration file "config.json" not found')
        raise
    except json.JSONDecodeError:
        logging.error('Error decoding the configuration file: Invalid JSON format')
        raise
    except Exception as e:
        logging.error(f'Error loading configuration file: {e}')
        raise

    api_key = config.get('api_key')
    if not api_key:
        logging.error('API key not found in the config file')
        raise ValueError('API key is required')

    required_keys = ['keywords', 'max_results_per_keyword', 'requests_per_second', 'max_depth']
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        logging.error(f'Missing required keys in the config file: {", ".join(missing_keys)}')
        raise ValueError('Configuration file is missing required keys')

    return config

def validate_config(config):
    """
    Validates the configuration values.
    """
    api_key = config.get('api_key')
    if not api_key or not isinstance(api_key, str):
        raise ValueError('API key must be a non-empty string')

    keywords = config.get('keywords')
    if not keywords or not isinstance(keywords, list):
        raise ValueError('Keywords must be a non-empty list')

    max_results_per_keyword = config.get('max_results_per_keyword')
    if not isinstance(max_results_per_keyword, int) or max_results_per_keyword < 1:
        raise ValueError('Max results per keyword must be a positive integer')

    requests_per_second = config.get('requests_per_second')
    if not isinstance(requests_per_second, (int, float)) or requests_per_second < 0:
        raise ValueError('Requests per second must be a non-negative number')

    max_depth = config.get('max_depth')
    if not isinstance(max_depth, int) or max_depth < 1:
        raise ValueError('Max depth must be a positive integer')

    max_retries = config.get('max_retries')
    if not isinstance(max_retries, int) or max_retries < 1:
        raise ValueError('Max retries must be a positive integer')

    default_timeout = config.get('default_timeout')
    if not isinstance(default_timeout, (int, float)) or default_timeout < 0:
        raise ValueError('Default timeout must be a non-negative number')

def search_videos_by_keyword(keyword, max_results=10, depth=0, max_depth=2, api_key=None, max_retries=5, default_timeout=1):
    """
    Search for videos on YouTube by a keyword, implementing exponential backoff
    for error handling. Recursively searches for related videos up to the specified depth.
    """
    if not api_key:
        logging.error('API key is required')
        raise ValueError('API key is required')

    youtube = build('youtube', 'v3', developerKey=api_key)

    logging.info(f'Searching for videos related to "{keyword}" at depth {depth}')
    videos = []

    for n in range(max_retries):
        try:
            # Execute the search query and retrieve the results
            logging.debug(f'Executing search query for "{keyword}"')
            search_response = youtube.search().list(
                q=keyword,
                part='id,snippet',
                maxResults=max_results,
                type='video'
            ).execute()

            # Process the search results
            for search_result in search_response.get('items', []):
                # Create a dictionary with video metadata
                video_metadata = {
                    'title': search_result['snippet']['title'],
                    'url': f"https://www.youtube.com/watch?v={search_result['id']['videoId']}",
                    'channel': search_result['snippet']['channelTitle'],
                    'description': search_result['snippet'].get('description', ''),  # Handle missing description
                    'depth': depth
                }
                videos.append(video_metadata)

                # Recursively search for related videos if depth is not exceeded
                if depth < max_depth:
                    related_keywords = extract_related_keywords(video_metadata)
                    if related_keywords:
                        logging.debug(f'Searching for related videos using keywords: {", ".join(related_keywords)}')
                        for keyword in related_keywords:
                            videos.extend(search_videos_by_keyword(keyword, max_results, depth + 1, max_depth, api_key, max_retries, default_timeout))

            logging.info(f'Found {len(videos)} videos for "{keyword}" and related topics')
            return videos

        except HttpError as e:
            if e.resp.status == 403 and 'quotaExceeded' in str(e.content):
                logging.warning(f"API quota exceeded for '{keyword}'. Skipping this keyword...")
                break
            elif e.resp.status in [403, 500, 503]:
                # Implement exponential backoff for retryable errors
                sleep_time = (default_timeout * (2 ** n)) + (random.randint(0, 1000) / 1000)  # Exponential backoff + jitter
                logging.warning(f"Waiting {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
            else:
                logging.error("Non-retryable error occurred, skipping this keyword...")
                break
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            break

    logging.warning(f'No videos found for "{keyword}" and related topics')
    return videos

def extract_related_keywords(video_metadata):
    """
    Extracts related keywords from the video title and description.
    If the description is not available, it returns an empty list to skip depth spidering.
    """
    title = video_metadata['title']
    description = video_metadata['description']

    # If the description is not available, skip depth spidering
    if not description:
        logging.debug(f'Skipping depth spidering for "{title}" due to missing description')
        return []

    # Extract keywords from the title
    title_keywords = re.findall(r'\w+', title.lower())

    # Extract keywords from the description
    description_keywords = re.findall(r'\w+', description.lower())

    # Combine the keywords from title and description, and remove duplicates
    all_keywords = list(set(title_keywords + description_keywords))

    logging.debug(f'Extracted keywords for "{title}": {", ".join(all_keywords)}')
    return all_keywords

def main():
    # Load the configuration file
    config = load_config()

    # Validate the configuration
    try:
        validate_config(config)
    except ValueError as e:
        logging.error(f'Invalid configuration: {e}')
        return

    keywords = config['keywords']
    max_results = config['max_results_per_keyword']
    requests_per_second = config['requests_per_second']
    max_depth = config['max_depth']
    api_key = config['api_key']
    max_retries = config.get('max_retries', 5)
    default_timeout = config.get('default_timeout', 1)
    sleep_time = 1 / requests_per_second

    # Create a list to store videos from all searches
    all_videos = []

    # Iterate over the keywords in the config
    for keyword in keywords:
        logging.info(f"Searching for: {keyword}")
        videos = search_videos_by_keyword(keyword, max_results, max_depth=max_depth, api_key=api_key, max_retries=max_retries, default_timeout=default_timeout)
        all_videos.extend(videos)

        # Print the video details
        for video in videos:
            logging.info(f"Title: {video['title']}")
            logging.info(f"URL: {video['url']}")
            logging.info(f"Channel: {video['channel']}")
            logging.info(f"Description: {video['description']}")
            logging.info(f"Depth: {video['depth']}")
            logging.info("-" * 30)

        logging.info("\n")
        time.sleep(sleep_time)  # Basic rate limiting

    # Save the list of all videos to a flat file
    logging.info(f"Saving search results for {len(all_videos)} videos to 'search_results.txt'")
    with open('search_results.txt', 'w', encoding='utf-8') as file:
        for video in all_videos:
            file.write(json.dumps(video) + '\n')

    logging.info("Script execution completed successfully.")

if __name__ == "__main__":
    main()
