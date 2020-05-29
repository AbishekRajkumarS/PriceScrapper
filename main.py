import os
import crochet
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time

from Amazon.Amazon.spiders.amazon_spider import AmazonSpider
from Flipkart.Flipkart.spiders.flipkart_spider import FlipkartSpider

crochet.setup()

app = Flask(__name__)

output_data = []
crawl_runner = CrawlerRunner()


# By Deafult Flask will come into this when we run the file
@app.route('/')
def index():
    return render_template("index.html")  # Returns index.html file in templates folder.


# After clicking the Submit Button FLASK will come into this
@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        s = request.form['url']  # Getting the Input Amazon Product URL
        global product
        product = s.replace(" ", "+")[:-1]

        # This will remove any existing file with the same name so that the scrapy will not append the data to any
        # previous file.
        # if os.path.exists("D:\Projects\Python\Amazon\outputfile.json"):
        #     os.remove("D:\Projects\Python\Amazon\outputfile.json")
        #
        # if os.path.exists("D:\Projects\Python\Flipkart\outputfile.json"):
        #     os.remove("D:\Projects\Python\Flipkart\outputfile.json")

        return redirect(url_for('amazon_scrape'))  # Passing to the Scrape function


@app.route("/amazon")
def amazon_scrape():
    scrape_with_crochet(product_name=product, spider=AmazonSpider)  # Passing that URL to our Scraping Function

    time.sleep(20)  # Pause the function while the scrapy spider is running

    return redirect(url_for('flipkart_scrape'))


@app.route("/flipkart")
def flipkart_scrape():
    scrape_with_crochet(product_name=product, spider=FlipkartSpider)  # Passing that URL to our Scraping Function

    time.sleep(10)  # Pause the function while the scrapy spider is running

    return redirect(url_for('scrape'))


@app.route("/scrape")
def scrape():
    time.sleep(10)
    return jsonify(output_data)


@crochet.run_in_reactor
def scrape_with_crochet(product_name, spider):
    # This will connect to the dispatcher that will kind of loop the code between these two functions.
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)

    # This will connect to the Spider function in our scrapy file and after each yield will pass to the
    # crawler_result function.
    eventual = crawl_runner.crawl(spider, category=product_name)
    return eventual


# This will append the data to the output data list.
def _crawler_result(item, response, spider):
    output_data.append(dict(item))
    print(output_data)


if __name__ == "__main__":
    app.run(debug=True)
