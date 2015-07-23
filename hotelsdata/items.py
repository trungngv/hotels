# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Hotel(scrapy.Item):
  effectiveDate = scrapy.Field()
  name = scrapy.Field()
  starRating = scrapy.Field()
  latitude = scrapy.Field()
  longitude = scrapy.Field()
  country = scrapy.Field()
  state = scrapy.Field()
  city = scrapy.Field()
  suburb = scrapy.Field()
  street = scrapy.Field()
  streetnumber = scrapy.Field()
  roomCapacity = scrapy.Field()
  totalReviews = scrapy.Field()
  avgReviewScore = scrapy.Field()
  topNationNames = scrapy.Field()
  topNationCounts = scrapy.Field()

class UrlList(scrapy.Item):
  effectiveDate = scrapy.Field()
  urls = scrapy.Field()