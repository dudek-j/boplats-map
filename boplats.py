#!/usr/bin/env python3

import json
import re
import sys

import requests
from bs4 import BeautifulSoup


def run():
    listings = getListings()
    data = []

    for idx, listing in enumerate(listings):
        progress_bar(idx + 1, len(listings))
        data.append(processListing(listing))

    writeToFile(json.dumps(data, sort_keys=True))


def getListings():
    url = "https://nya.boplats.se/sok?types=1hand"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    listings = soup.find_all("div", class_="search-result-item item imageitem")

    return listings


def processListing(listing):
    dict = {}
    dict["url"] = listing.find("a", class_="search-result-link")["href"]

    ## Area
    dict["area"] = (
        listing.find("div", class_="search-result-area-name")
        .getText()
        .replace("\n", "")
        .strip()
    )

    address = (
        listing.find("div", class_="search-result-address")
        .getText()
        .replace("\n", "")
        .strip()
    )

    ## Adress
    try:
        addressMatch = re.search(r"(\D+)\s*(\d*)", address, re.IGNORECASE).groups()

        dict["street"] = addressMatch[0].strip()
        dict["streetNumber"] = addressMatch[1]
    except IndexError:
        pass

    ## Price
    dict["price"] = (
        listing.find("div", class_="search-result-price")
        .getText()
        .replace("\n", "")
        .strip()
    )

    dict["price"] = removeNonNumbers(dict["price"])

    listingText = listing.get_text()

    ## Rooms
    try:
        dict["rooms"] = re.search(r"([0-9])\s*rum", listingText, re.IGNORECASE).group(1)
    except IndexError:
        pass

    ## Size
    try:
        dict["size"] = re.search(r"([0-9,.]+)\s*m²", listingText, re.IGNORECASE).group(
            1
        )
    except IndexError:
        pass

    ## Publ date
    publText = (
        listing.find("div", class_="publ-date").getText().replace("\n", "").strip()
    )

    try:
        dict["publ"] = re.search(r"publ.\s*(.*)", publText, re.IGNORECASE).groups(1)
    except IndexError:
        pass

    ## Coordinates
    try:
        coords = getCoordsFor(dict["url"], dict["street"], dict["streetNumber"])
        dict["lat"] = coords[0]
        dict["lon"] = coords[1]
    except IndexError:
        pass

    return dict


def getCoordsFor(url, street, streetNumber):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    try:
        coord_div = soup.find("div", {"id": "karta"})
        if coord_div:
            return (coord_div["data-latitude"], coord_div["data-longitude"])
        else:
            return ()
    except KeyError:
        return geNominatimCoordsFor(street, streetNumber)


def geNominatimCoordsFor(street, streetNumber):
    url = f"https://nominatim.openstreetmap.org/search/?city=Gothenburg&street={streetNumber}+{street}&format=json"
    r = requests.get(url)
    res = r.json()

    try:
        place = res[0]
        return (place["lat"], place["lon"])
    except KeyError:
        return ()


def removeNonNumbers(string):
    return re.sub(r"\D", "", string)


def progress_bar(current, total, bar_length=20):
    fraction = current / total

    arrow = int(fraction * bar_length - 1) * "-" + ">"
    padding = int(bar_length - len(arrow)) * " "

    ending = "\n" if current == total else "\r"

    print(f"Progress: [{arrow}{padding}] {int(fraction*100)}%", end=ending)


def writeToFile(listings):
    path = "./res.js"

    with open(path, "w") as file:
        file.write("let listings = " + listings)


try:
    run()
except KeyboardInterrupt:
    print("\n")
    print("Interrupted")
    sys.exit(0)
