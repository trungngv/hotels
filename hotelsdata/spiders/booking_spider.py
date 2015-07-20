import scrapy
import re
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
    patt = re.compile(r"(\d+) ([a-zA-Z\s]+), ([a-zA-Z\s]+), ([a-zA-Z\s]+), ([a-zA-Z\s]+)")
    parts = patt.findall(address)
    if len(parts) > 0 and len(parts[0]) == 5:
        (streetnumber, street, suburb, city, country) = parts[0]
        return (country, "", city, suburb, street, streetnumber)
    else:
        return ("", "", "", "", "", "")        

def getRoomCapacity(summary):
    patt = re.compile(r"Hotel Rooms: (\d+)")
    return getOrElse(patt.findall(summary))

# TODO: start_ulrs is the page for a city
class BookingSpider(scrapy.Spider):
    name = "booking.com"
    allowed_domains = ["booking.com"]
    start_urls = [
        "http://www.booking.com/hotel/vn/sofitelmetropole.html",
    ]

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
        print "addres = ", val

        (hotel['country'], hotel['state'], hotel['city'],
         hotel['suburb'], hotel['street'], hotel['streetnumber']) = parseAddress(val) 

        val = getOrElse(response.xpath("//p[@class='summary ']/text()").extract()).strip()
        hotel['roomCapacity'] = int(getRoomCapacity(val))
        
        #totalReviews = scrapy.Field()
        #avgReviewScore = scrapy.Field()
        #guestNationalities = scrapy.Field()

        yield hotel
