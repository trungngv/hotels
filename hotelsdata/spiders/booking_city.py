import scrapy
import re
import math
from collections import Counter
from datetime import date
from hotelsdata.items import *

cityName = "Hanoi"
cityId = "-3714993"
nrows = 15 # how many hotels per page
nhotels = 607 # how many hotel in this city

def getOrElse(res, defaultValue = ""):
    """Get the first element of res if it is not empty,
    else return the defaultValue.
    """
    if len(res) > 0:
        return res[0]
    else:
        return defaultValue

patt = re.compile(r"(.*html)")
def getHotelUrl(relativeUrl):
    return "http://www.booking.com%s" % patt.findall(relativeUrl)[0]

def getStartUrls():
    # hanoi
    sourceUrl = "http://www.booking.com/searchresults.html?city=%s" % cityId
    return ["%s;rows=%d;offset=%d" % (sourceUrl, nrows, page * nrows)
         for page in range(0, (nhotels / nrows) + 1)]

class BookingCitySpider(scrapy.Spider):
    """Crawls a city for the list of its hotels.

    Requires the booking id of a city (see getStartUrls) and the number of properties.
    """
    name = "booking.city"
    allowed_domains = ["booking.com"]
    start_urls = getStartUrls()

    def parse(self, response):
        """Parse the search result page of a city to get the list of all properites.
        """
        item = UrlList()
        item['effectiveDate'] = str(date.today())

        urls = response.xpath("//a[@class='hotel_name_link url']/@href").extract()
        hotels = [getHotelUrl(url) for url in urls]
        print '-------------------------------------'
        print 'captured %s hotels' % len(hotels)
        print '-------------------------------------'

        item['urls'] = hotels
        yield item
