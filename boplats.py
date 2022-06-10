#!/usr/bin/env python3

import json
import sys
import requests
import re
from bs4 import BeautifulSoup


def run():
    listings = getListings()
    data = []

    for listing in listings:
        data.append(processListing(listing))

    writeToFile(json.dumps(data, sort_keys=True))


def getListings():
    url = "https://nya.boplats.se/sok?types=1hand"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    listings = soup.find_all("div", class_="search-result-item item imageitem")

    return listings


def processListing(listing):
    dict = {}
    dict["url"] = listing.find("a", class_="search-result-link")["href"]

    dict["area"] = listing.find(
        "div", class_="search-result-area-name").getText().replace("\n", "").strip()

    address = listing.find(
        "div", class_="search-result-address").getText().replace("\n", "").strip()

    try:
        match = re.search(
            r'(\D+)\s*(\d*)', address, re.IGNORECASE).groups()

        dict["street"] = match[0].strip()
        dict["streetNumber"] = match[1]

    except KeyboardInterrupt:
        sys.exit()

    except:
        pass

    dict["price"] = listing.find(
        "div", class_="search-result-price").getText().replace("\n", "").strip()

    dict["price"] = removeNonNumbers(dict["price"])

    listingText = listing.get_text()

    try:
        dict["rooms"] = re.search(
            r'([0-9])\s*rum', listingText, re.IGNORECASE).group(1)
    except KeyboardInterrupt:
        sys.exit()
    except:
        pass

    try:
        dict["size"] = re.search(
            r'([0-9,.]+)\s*m²', listingText, re.IGNORECASE).group(1)
    except KeyboardInterrupt:
        sys.exit()
    except:
        pass


    publText = listing.find(
        "div", class_="publ-date").getText().replace("\n", "").strip()

    try:
        dict["publ"] = re.search(
            r'publ.\s*(.*)', publText, re.IGNORECASE).group(1)
    except KeyboardInterrupt:
        sys.exit()
    except:
        pass
    

    try:
        coords = getCoordsFor(
            dict["url"], dict["street"], dict["streetNumber"])
        dict["lat"] = coords[0]
        dict["lon"] = coords[1]
    except KeyboardInterrupt:
        sys.exit()
    except:
        pass

    return dict


def getCoordsFor(url, street, streetNumber):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    try:
        coord_div = soup.find("div", {"tabindex": "1"})
        return (coord_div["data-latitude"], coord_div["data-longitude"])

    except KeyboardInterrupt:
        sys.exit()
    except:
        return geNominatimCoordsFor(street, streetNumber)


def geNominatimCoordsFor(street, streetNumber):
    url = f'https://nominatim.openstreetmap.org/search/?city=Gothenburg&street={streetNumber}+{street}&format=json'
    r = requests.get(url)
    res = r.json()

    try:
        place = res[0]
        return (place["lat"], place["lon"])
    except:
        return None


def removeNonNumbers(string):
    return re.sub(r'\D', "", string)

def writeToFile(listings):
    path = "./res.js"

    with open(path, 'w') as file:
        file.write("let listings = " + listings)


run()
