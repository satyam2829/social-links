from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from io import StringIO
import uvicorn
import pandas as pd
from basemodel import URL, NAME, TRADEMARK, APPSTORE, PLAYSTORE, LIGHTHOUSE
from fastapi.params import Body
import requests
from bs4 import BeautifulSoup
import re
import json

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to my API"}

@app.post("/website-details")
def get_website_details(data:URL):
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
    playstore_url = None
    appstore_url = None
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

        if "play.google.com" in link:
            playstore_url = link

        if "apps.apple.com" in link:
            appstore_url = link

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
        "PlayStore": playstore_url,
        "AppStore": appstore_url,
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

@app.post("/trademark-details")
def get_trademark_details(data: TRADEMARK):
    data = data.dict()
    
    company_name = data["company_name"]
    cin = data["company_cin"]

    zaubacorp_url = "https://www.zaubacorp.com/company-trademark/"
    url =  zaubacorp_url + data["company_name"] + "/" + data["company_cin"]

    trademark_data = dict()
    records = None
    trademark_details = list()
    total_pages = None
    name_and_class = list()
    trademark_date = list()
    trademark_status = list()

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'}

    company_trademark_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(company_trademark_page.content, "html.parser")

    details = soup.find("div", class_="container basic-cont")
    total_records = details.find("div", class_="col-xs-4 text-left")
    if total_records is not None:
        records = total_records.text
        records = " ".join(records.split())
        if "," in records:
            records = records.replace(",", "")
        records = int(re.findall("\d+", records)[0])

        if records % 10 == 0:
            total_pages = records // 10
        else:
            total_pages = (records // 10) + 1

        for page in range(1, total_pages + 1):
            trademark_details_list = list()
            new_url = zaubacorp_url + data["company_name"] + "/" + data["company_cin"] + "/page-" + str(page)

            new_trademark_page = requests.get(new_url, headers=headers)
            new_soup = BeautifulSoup(
            new_trademark_page.content, "html.parser")

            trademark_name_and_class = new_soup.find_all("span", class_="wordMark")
            for trademark in trademark_name_and_class:
                name = trademark.text
                name = name.replace("\xa0", "")
                name = name.replace("Class : ", "")
                name = name.replace("Trademark : ", "")
                name_and_class.append(name)

            trademark_name = list(
                [name_and_class[i] for i in range(len(name_and_class)) if i % 3 == 0])
            trademark_class = list(
                [int(ele) for ele in name_and_class if ele not in trademark_name])
            trademark_class = [trademark_class[i]
                                for i in range(len(trademark_class)) if i % 2 == 0]

            card = new_soup.find_all("div", class_="left-wrapper")
            for data in card:
                trademark_card = data.text.splitlines()
                trademark_card = [i for i in trademark_card if i]
                trademark_date.append(trademark_card[0])
                trademark_status.append(trademark_card[1])

                trademark_date = [sub.replace("\xa0", "")
                                  for sub in trademark_date]
                trademark_status = [sub.replace(
                    "\xa0", "") for sub in trademark_status]

                labels = ["name", "class", "date", "status"]

            for l in range(len(trademark_name)):
                trademark_data_dict = dict()
                trademark_data_dict.update({
                    "name": trademark_name[l],
                    "class": trademark_class[l],
                    "date": trademark_date[l][19:],
                    "status": trademark_status[l][9:]
                })

                trademark_details.append(trademark_data_dict)

        trademark_data.update({
                "Company": company_name,
                "CIN": cin,
                "records": records,
                "trademark_details": trademark_details
            })

    return trademark_data

@app.post("/appstore-ratings-and_reviews")
def get_appstore_data(data:APPSTORE):

    data = data.dict()
    appstore_page = requests.get(data["url"], timeout=15)
    soup = BeautifulSoup(appstore_page.content, "html.parser")

    average_rating = soup.find("span", class_="we-customer-ratings__averages__display")
    if average_rating is not None:
        average_rating = average_rating.text

    total_num_ratings = soup.find("div", class_="we-customer-ratings__count small-hide medium-show")
    if total_num_ratings is not None:
        total_num_ratings = total_num_ratings.text

    return {
        "average_rating": average_rating,
        "total_num_ratings": total_num_ratings,
    }


@app.post("/playstore-ratings-and_reviews")
def get_playstore_data(data:PLAYSTORE):
    data = data.dict()

    playstore_page = requests.get(data["url"], timeout=15)
    soup = BeautifulSoup(playstore_page.content, "html.parser")

    average_rating = soup.find("div", class_="K9wGie")
    if average_rating is not None:
        average_rating = average_rating.div.text

    total_num_ratings = soup.find("span", class_="AYi5wd TBRnV")
    if total_num_ratings is not None:
        total_num_ratings = total_num_ratings.span.text

    return {
        "average_rating": average_rating,
        "total_num_ratings": total_num_ratings,
    }

def __get_light_house_data__(light_house_results):
    light_house_data = dict()
    performance_score = None
    accessibility_score = None
    best_practices_score = None
    pwa_score = None
    seo_score = None

    _categories = light_house_results.get("categories")
    if _categories is not None:
        performance = _categories.get("performance")
        if performance is not None:
            performance_score = performance.get("score")
            if performance_score is not None:
                performance_score = round(performance_score * 100)

        accessibility = _categories.get("accessibility")
        if accessibility is not None:
            accessibility_score = accessibility.get("score")
            if accessibility_score is not None:
                accessibility_score = round(accessibility_score * 100)

        best_practices = _categories.get("best-practices")
        if best_practices is not None:
            best_practices_score = best_practices.get("score")
            if best_practices_score is not None:
                best_practices_score = round(best_practices_score * 100)

        pwa = _categories.get("pwa")
        if pwa is not None:
            pwa_score = pwa.get("score")
            if pwa_score is not None:
                pwa_score = round(pwa_score * 100)

            seo = _categories.get("seo")
            if seo is not None:
                seo_score = seo.get("score")
                if seo_score is not None:
                    seo_score = round(seo_score * 100)

    light_house_data.update(
        {
                "performance": performance_score,
                "accessibility": accessibility_score,
                "best_practices": best_practices_score,
                "pwa": pwa_score,
                "seo": seo_score,
        }
    )
    return light_house_data

@app.post("/lighthouse-results")
def get_light_house_results(data:LIGHTHOUSE):
    light_house_results = dict()

    data = data.dict()

    api_key = "AIzaSyDIFMcvo9kDayhTRGZgyyAEmzpMSdhtK5M"
    service_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    parameters = {
            "url": data["website"],
            "key": api_key,
            "strategy": data["version"],
            "category": [
                "PERFORMANCE",
                "ACCESSIBILITY",
                "BEST_PRACTICES",
                "SEO",
                "PWA",
            ],
        }
    light_house_response = requests.get(service_url, params=parameters)

    if light_house_response.status_code == 200:
        response_data = json.loads(light_house_response.text)
        response_data = response_data.get("lighthouseResult")

        if response_data is not None:
                light_house_results = __get_light_house_data__(response_data)
    
    light_house_results.update({"website": data["website"], "version": data["version"]})
    return light_house_results

@app.post("/llp-main-division")
def get_llp_main_division(data:TRADEMARK):
    data = data.dict()
    zaubacorp_url = "https://www.zaubacorp.com/company/"
    company_name = data["company_name"]
    llpin = data["company_cin"]

    url = zaubacorp_url + company_name + "/" + llpin

    table = pd.read_html(url)[0]
    main_division = table.iloc[3, 1]
    main_division_description = table.iloc[4, 1]

    main_division_results = {
        "Company": table.iloc[0,1],
        "LLPIN": llpin,
        "Main Division": main_division,
        "Description of Main Division": main_division_description
    }

    return main_division_results