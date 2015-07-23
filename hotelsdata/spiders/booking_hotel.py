import scrapy
import re
import math
import json
from collections import Counter
from datetime import date
from hotelsdata.items import Hotel

def getOrElse(res, defaultValue = ""):
    """Get the first element of res if it is not empty,
    else return the defaultValue.
    """
    if len(res) > 0:
        return res[0]
    else:
        return defaultValue

# for Vietnamese address
def parseAddress(address):
    """
    Returns (country, state, city, suburb, street, streetnumber).
    """
    patt = re.compile(r"(\d+/?\d+) ([a-zA-Z\s]+), ([a-zA-Z\s]+), ([a-zA-Z\s]+), ([a-zA-Z\s]+)")
    parts = patt.findall(address)
    if len(parts) > 0 and len(parts[0]) == 5:
        (streetnumber, street, suburb, state, country) = parts[0]
        return (country, state, "", suburb, street, streetnumber)
    else:
        return ("", "", "", "", "", "")        

def getRoomCapacity(summary):
    patt = re.compile(r"Hotel Rooms: (\d+)")
    return getOrElse(patt.findall(summary))

def getReviewPage(hotelUrl, page=1):
    """Construct url of the review page of a hotel.
    """
    patt = re.compile(r".*/hotel/([a-zA-Z]+)/(.*)")
    (country, html) = patt.findall(hotelUrl)[0]
    return "http://www.booking.com/reviews/%s/hotel/%s?r_lang=all&page=%d" % (country, html, page)

def getTotalReviews(title):
    patt = re.compile(r"^(\d+)")
    return int(getOrElse(patt.findall(title), 0))

def getTopNations(nationCounter, top=15):
    c = nationCounter.most_common(top)
    names = []
    counts = []
    for (name, count) in c:
        names.append(name.strip())
        counts.append(count)
    return (",".join(names), str(counts))

def getStartUrls():
    with open('hanoi.json', 'r') as f:
        items = json.load(f)
        urls = []
        for item in items:
            urls.extend(item['urls'])
        return urls

class BookingHotelSpider(scrapy.Spider):
    """
    Crawls information of a hotel together with statistics of its reviews.
    """
    name = "booking.hotel"
    allowed_domains = ["booking.com"]
    #TODO read from file
    start_urls = getStartUrls()

    def parse(self, response):
        """Parse a hotel website to extract information about the hotel.
        """
        # TODO call back page to parse reviews
        hotel = Hotel()
        hotel['effectiveDate'] = str(date.today())
        
        val = response.xpath("//span[@id='hp_hotel_name']/text()").extract()
        hotel['name'] = getOrElse(val).strip()

        val = response.xpath("//span[@class='hp__hotel_ratings__stars hp__hotel_ratings__stars__clarification_track']/i/@title").extract()
        hotel['starRating'] = getOrElse(val)

        val = getOrElse(response.xpath("//span[@id='hp_address_subtitle']/@data-coords").extract())
        if val != "":
            coords = val.split(",")
            hotel['latitude'] = float(coords[0])
            hotel['longitude'] = float(coords[1])

        val = response.xpath("//span[@id='hp_address_subtitle']/text()").extract()
        val = getOrElse(val).strip()

        (hotel['country'], hotel['state'], hotel['city'],
         hotel['suburb'], hotel['street'], hotel['streetnumber']) = parseAddress(val) 

        val = getOrElse(response.xpath("//p[@class='summary ']/text()").extract()).strip()
        hotel['roomCapacity'] = int(getRoomCapacity(val))
        
        print '-----------------------'
        print hotel
        print '---------------'

        reviewUrl = getReviewPage(response.url)
        yield scrapy.Request(reviewUrl, 
            meta={'hotel': hotel, 'nations': Counter(),
                'baseUrl': response.url, 'page': 1}, 
            callback=self.parseReviews)

    def parseReviews(self, response):
        """Follow review pages until there is no more page, then yield hotel.
        """
        print "crawling", response.url

        hotel = response.meta['hotel']
        
        if not hotel.get('totalReviews'):
            title = response.xpath("//title/text()").extract()[0]
            hotel['totalReviews'] = getTotalReviews(title)

        if not hotel.get('avgReviewScore'):
            hotel['avgReviewScore'] = getOrElse(response.xpath("//div/@data-total").extract())

        nations = response.meta['nations']
        countries = response.xpath("//span[@class='reviewer_country']/text()").extract()
        nations.update(countries)
        npages = int(math.ceil(hotel['totalReviews'] / 75.0))
        page = response.meta['page']
        if page < npages:
            nextUrl = getReviewPage(response.meta['baseUrl'], page + 1)
            print "url---------------------------------", nextUrl
            yield scrapy.Request(nextUrl, 
                meta={'hotel': hotel, 'nations': nations,
                    'baseUrl': response.meta['baseUrl'], 'page': page + 1},
                callback=self.parseReviews)
        else:
            nations.pop('\n')                
            (hotel['topNationNames'], hotel['topNationCounts']) = getTopNations(nations)
            yield hotel

