from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from io import StringIO
import uvicorn
import pandas as pd
from basemodel import URL, NAME
from fastapi.params import Body
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to my API"}

@app.post("/sociallinks")
def get_social_media_links(data:URL):
    data = data.dict()
    facebook_url = None
    linkedin_url = None
    twitter_url = None
    instagram_url = None
    youtube_url = None
    producthunt_url = None
    github_url = None
    whatsapp_url = None
    status_code = None
    cin = list()
    gstin = list()
    email = list()
    phones = list()
    fssai = list()

    webpage = requests.get(data["url"], timeout=15)
    soup = BeautifulSoup(webpage.content, "html.parser")

    all_links = [link['href'] for link in soup.find_all('a', href = True)]

    for link in all_links:
        if "linkedin.com/company" in link:
            linkedin_url = link

        if "facebook.com" in link:
            facebook_url = link

        if "twitter.com" in link:
            twitter_url = link

        if "instagram.com" in link:
            instagram_url = link

        if "youtube.com/channel" in link:
            youtube_url = link

        if "product.com" in link:
            producthunt_url = link

        if "github.com" in link:
            github_url = link

        if "wa.me/" in link:
            whatsapp_url = link

        cin_regex = r"([A-Z]{1}\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6})"
        cin = list(set(re.findall(cin_regex, webpage.text)))

        gst_regex = r"(\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[A-Z]{2})"
        gstin = list(set(re.findall(gst_regex, webpage.text)))

        email_regex = r"[\w\.-]+@[\w\.-]+"
        email = list(set(re.findall(email_regex, webpage.text)))

        phone_regex = r"\+91?\d[\d -]{8,12}\d"
        phones = list(set(re.findall(phone_regex, webpage.text)))

        fssai_regex = r"(\d{14})"
        fssai = list(set(re.findall(fssai_regex, webpage.text)))

    links = {
        "Website": data["url"],
        "Facebook": facebook_url,
        "Twitter": twitter_url,
        "LinkedIn": linkedin_url,
        "Instagram": instagram_url,
        "Youtube": youtube_url,
        "Whatsapp": whatsapp_url,
        "ProductHunt": producthunt_url,
        "GitHub": github_url,
        "CIN": cin,
        "GSTIN": gstin,
        "Email": email,
        "Phone": phones,
        "Fssai" : fssai,
        "Status Code": webpage.status_code
    }

    return links

@app.post("/google-ratings-and-reviews")
def get_google_ratings_and_reviews(data: NAME):
    data = data.dict()
    ratings = None
    votes = None

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}

    search_url = "https://www.google.com/search?q="
    url = search_url + data["name"]

    webpage = requests.get(url, headers=headers)
    soup = BeautifulSoup(webpage.content, "html.parser")

    rating_element = soup.find("span", class_ = "Aq14fc")
    if rating_element is not None:
        ratings = rating_element.text

    votes_element = soup.find("span", class_ = "hqzQac")
    if votes_element is not None:
        votes = votes_element.a.span.text
        votes = votes.split(" ")[0]

    google_business_data = {
        "Company": data["name"],
        "Ratings": ratings,
        "Reviews": votes,
        "Status": webpage.status_code
    }

    return google_business_data
