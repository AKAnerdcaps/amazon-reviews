import time
import logging
import pandas as pd
from requests_html import HTMLSession

class AmazonReviewScraper:
    def __init__(self, asin):
        self.asin = asin
        self.session = HTMLSession()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        self.base_url = f'https://www.amazon.com/product-reviews/{self.asin}/ref=cm_cr_arp_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber='

    def fetch_reviews(self, page):
        try:
            url = self.base_url + str(page)
            response = self.session.get(url)
            response.html.render(sleep=1)

            review_elements = response.html.find('div[data-hook=review]')
            if not review_elements:
                return None
            return review_elements
        except Exception as e:
            logging.error(f"Error fetching reviews for page {page}: {str(e)}")
            return None

    def parse_reviews(self, review_elements):
        reviews_data = []
        for review in review_elements:
            title = review.find('a[data-hook=review-title] span')[2].text
            # title = title_element[1].text if len(title_element) > 1 else ''

            rating_element = review.find('i[data-hook=review-star-rating] span', first=True)
            rating = rating_element.text if rating_element else ''

            body_element = review.find('span[data-hook=review-body] span', first=True)
            body = body_element.text.replace('\n', '').strip() if body_element else ''

            review_data = {
                'Title': title,
                'Rating': rating,
                'Body': body
            }
            reviews_data.append(review_data)
        return reviews_data

    def save_to_file(self, results):
        try:
            filename = f'data/{self.asin}-reviews.csv'
            df = pd.DataFrame(results)
            df.to_csv(filename, index=False)
            logging.info(f'Reviews saved to {filename}')
        except Exception as e:
            logging.error(f"Error saving to CSV file: {str(e)}")

if __name__ == '__main__':
    logging.basicConfig(filename='amazon_review_scraper.log', level=logging.INFO)
    asin = 'B09DFCB66S'
    scraper = AmazonReviewScraper(asin)
    results = []

    for page in range(1, 20):
        logging.info(f"Getting page: {page}")
        time.sleep(0.5)
        reviews = scraper.fetch_reviews(page)
        if reviews is not None:
            results.extend(scraper.parse_reviews(reviews))
        else:
            logging.info('No more pages!')
            break

    scraper.save_to_file(results)
