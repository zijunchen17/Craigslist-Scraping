import scrapy
from scrapy.http import Request
from scrapy_splash import SplashRequest

# shell: scrapy shell "http://localhost:8050/render.html?url=https://newyork.craigslist.org/search/egr"
# cmd: docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash --max-timeout 36


class JobsSpider(scrapy.Spider):
	name = 'jobs'
	allowed_domains = ['newyork.craigslist.org']
	start_urls = ['https://newyork.craigslist.org/search/egr']


	def start_requests(self):
		for url in self.start_urls:
			yield SplashRequest(url, callback=self.parse)
			# yield Request(url, callback=self.parse)


	def parse(self, response):
		# listings = response.xpath('//a[@class="result-title hdrlnk"]/text()').extract()
		# for listing in listings:
		# 	yield {'Listing': listing}
		
		listings = response.xpath('//li[@class="result-row"]')
		for listing in listings:
			date = listing.xpath('.//*[@class="result-date"]/@datetime').extract_first()
			link = listing.xpath('.//a[@class="result-title hdrlnk"]/@href').extract_first()
			text = listing.xpath('.//a[@class="result-title hdrlnk"]/text()').extract_first()

			yield{'date': date,
				'link': link,
				'text': text}
			yield SplashRequest(link,
								callback=self.parse_listing,
								meta={'date': date,
								'link': link,
								'text': text})


		next_page_url = response.xpath('//a[text()="next > "]/@href').extract_first()
		if next_page_url:
			yield SplashRequest(response.urljoin(next_page_url), callback=self.parse)



	def parse_listing(self, response):
		
		date = response.meta['date']
		link = response.meta['link']
		text = response.meta['text']

		compensation =  response.xpath('//*[@class="attrgroup"]/span[1]/b/text()').extract_first()
		job_type = response.xpath('//*[@class="attrgroup"]/span[2]/b/text()').extract_first()

		images = response.xpath('//*[@id="thumbs"]//@src').extract()
		images = [image.replace('50x50c', '600x450') for image in images]

		address = response.xpath('//*[@id="postingbody"]/text()').extract()

		yield{'date': date,
			'link': link,
			'text': text,
			'compensation': compensation,
			'job_type': job_type,
			'images': images,
			'address': address
		}
