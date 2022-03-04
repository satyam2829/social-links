from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from io import StringIO
import uvicorn
import pandas as pd
from basemodel import URL
from fastapi.params import Body
import requests
from bs4 import BeautifulSoup

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
    status_code = None

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

    data = {
        "Website": data["url"],
        "Facebook": facebook_url,
        "Twitter": twitter_url,
        "LinkedIn": linkedin_url,
        "Instagram": instagram_url,
        "Youtube": youtube_url,
        "ProductHunt": producthunt_url,
        "GitHub": github_url,
        "Status Code": webpage.status_code
    }

    return data

# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     return {"filename": file.filename}

# @app.post("/files/")
# async def create_file(file: bytes = File(...)):
#     return {"file_size": len(file)}

@app.post("/uploadfile")
def read_csv(data_file: UploadFile):
    
    df = pd.read_excel(StringIO(str(data_file.file.read())), engine='openpyxl')
    stream = StringIO()
    df.to_csv(stream, index = False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response