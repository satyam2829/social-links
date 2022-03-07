import pandas as pd
import streamlit as st
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from stqdm import stqdm

df = pd.DataFrame(columns=["ID", "Website", "LinkedIn", "Facebook", "Twitter", "Instagram", "Youtube", "ProductHunt", 
                            "Github", "StatusCode"])

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    rows = st.number_input("Enter no. of websites", min_value=5, max_value=1000)

    ids = data["ID"]
    website = data["Website"].head(rows)

    for i in stqdm(range(len(website))):

        facebook_url = None
        linkedin_url = None
        twitter_url = None
        instagram_url = None
        youtube_url = None
        producthunt_url = None
        github_url = None
        status_code = None
    
        try:
            webpage = requests.get(website[i], timeout=15)
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

            df.loc[df.shape[0]] = [ids[i], website[i], linkedin_url, facebook_url, twitter_url, instagram_url, youtube_url,
                                producthunt_url, github_url, webpage.status_code]

        except:
            df.loc[df.shape[0]] = [ids[i], website[i], linkedin_url, facebook_url, twitter_url, instagram_url, youtube_url,
                                producthunt_url, github_url, webpage.status_code]


def convert_df(df):
     return df.to_csv().encode('utf-8')

csv = convert_df(df)

st.download_button(label="Download Results", data=csv, file_name='links.csv', mime='text/csv')