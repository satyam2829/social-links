from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from io import StringIO
import uvicorn
import pandas as pd
from basemodel import URL
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

    data = {
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

    return data