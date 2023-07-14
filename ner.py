import json
import os

import openai
import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
openai.api_key = os.getenv("OPENAI_SECRET_KEY")

st.header("Extract Financial Information")

# your_story_article = "Anil Goteti, former Senior Vice President of ﻿Flipkart﻿and a consumer tech veteran, has launched a credit card and travel rewards platform—Scapia, marking his venture into the fintech space.  The Bengaluru-based startup offers a digital credit card to travellers, in partnership with the Federal Bank, and allows them to earn reward on each transaction in the form of Scapia coins. These coins can then be redeemed on the app itself in the form of discounts for flights and hotel bookings across countries. Customers can use the credit card, which is based on the VISA network, in across 150 countries, and access their transactions in real time within the app. In the last two-three years, the popularity of co-branded credit cards has seen immense traction. From ecommerce platform like ﻿Amazon﻿ and ﻿Flipkart﻿, to airlines and aggregators, companies have been tying up with banks to offer their own credit cards.   According to PwC, a study of popular co-brand cards in India reveals ‘travel’ as the prominent use case among various use cases followed by fuel, e-tail, and retail shopping. In the segment itself, airlines like Vistara and Air India have come up with co-branded cards in partnership with Axis Bank and SBI, while aggregators like MakeMyTrip and EaseMyTrip offer the same to their customers with ICICI Bank and Standard Chartered.  In fact, non-branded credit cards also offer rewards to customers that can be redeemed across travel websites for flights, lounge services, hotels, etc, individually or on their now in-house apps (Example HDFC Smartbuy platform).  Goteti, a travel enthusiast himself, terms Scapia as an exclusive platform for travellers that brings together both digital credit card offering and travel rewards for better experience. “The entire value that we give to customers is very high, plus the whole experience. We are not restricted to a particular airline or a hotel for rewards redemption like other co-branded credit cards. Our lounge access benefit is not restricted, the forex markup is zero, there are no hidden charges, and so on,” Goteti told YourStory.   While the founder did not divulge on the funding details, sources say the company, which was operating in stealth since January last year, has already raised funding from a clutch of investors.  What the card offers? The in-house app allows customers to track their credit card spending, as well as offers coins, which can be redeemed in the form of hotel and flight booking on the same app.  The platform has integrated the APIs of various aggregators (for hotels) and airlines to offer the same. Each transaction comes with a 10% reward in the form of Scapia coins. Five Scapia coins equal Rs 1. Further, 20% reward is offered on every hotel stay and flight booked from within the app. In addition, it claims to have no joining fee as of now, zero forex markup on international spends, with unlimited domestic lounge access, along with a no-cost EMI option.  Scapia earns revenue via its co-branded partnership with the Federal Bank, depending on the revenue sharing agreement, and fees from partner brand on bookings.  Besides individual co-branded credit cards, the platform is in direct completion with Cred, which also allows its users to redeem their coins for travel bookings within the app (Cred Escapes). Second entrepreneurial innings  Scapia is Goteti’s second entrepreneurial innings since his exit from Flipkart in 2020. He had previously launched a digital solutions startup, ﻿Protonn﻿, along with his colleague Mausam Bhatt. The platform allowed independent professionals, including lawyers, graphic designers, and nutritionists, to launch their own business online, create videos, conduct live sessions, generate payment links, and track their performances.  However, the Matrix Partners India-backed venture shut shop in less than a year of raising funds. 021 Capital, Tanglin Venture Partners, along with angel investors like Binny Bansal (Flipkart), Kalyan Krishnamurthy (Flipkart), Neeraj Arora (WhatsApp), Sujeet Kumar (﻿Udaan﻿), and Kunal Shah (﻿CRED﻿) had also placed their bet.  “It (startup) wasn’t going according to the plans. It was where the market was peaking at that point of time, but we did the right thing by returning the money to the investors. I took a break and the discovery process during that break led to Scapia,”the founder said.  Speaking about the failure of his first venture and building a new one, Goteti said,“When you want to leave a legacy and build something exciting, which serves millions of customers, everything will not be hunky dory. There will be ups and downs. You spend time in the industry and learn how to take things in your stride. Is it disappointing, yes! But you don’t think about the failures, but the larger vision and what excites you.”"
# your_story_response = {"startup_name": "Scapia", "startup_description": "Scapia offers a digital credit card, in partnership with Federal Bank, allowing users to earn reward on each transaction in the form of Scapia coins, which can be redeemed for travel bookings within the app itself. The Bengaluru-based startup offers a digital credit card  to travellers, in partnership with the Federal Bank, and allows them to earn reward on each transaction in the form of Scapia coins. These coins can then be redeemed on the app itself in the form of discounts for flights and hotel bookings across countries. Customers can use the credit card, which is based on the VISA network, in across 150 countries, and access their transactions in real time within the app.", "startup_location": "Bengaluru", "founded_date": "not specified", "founders": "Anil Goteti (former Senior Vice President of Flipkart)", "vc_investors": "Matrix Partners India, 021 Capital, Tanglin Venture Partners", "angel_investors": "Binny Bansal (Flipkart), Kalyan Krishnamurthy (Flipkart), Neeraj Arora (WhatsApp), Sujeet Kumar (Udaan), and Kunal Shah (CRED)", "funding_type": "not specified", "funding_date": "not_specified", "funding_amount": "not specified", "valuation": "not specified"}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

instruction = "Identify the following feilds from the below given news article\n\n1. startup name\n2. startup location\n3. founders \n4. funding amount\n5. funding round date\n6. VC Investors\n7. Angel Investors\n8. funding type\n9. Founded Date\n10. Article heading\n11. Article date\n\n"
financial_instruction = "Extract key financial information (revenue, profit/loss, expenses)\n\n"

def get_cleaned_document(url):

    webpage = requests.get(url, headers=headers)
    soup = BeautifulSoup(webpage.content, "html.parser")
    website_body = soup.find("body")
    input = website_body.get_text()
    return input

url = st.text_input("Enter the URL")

if st.button("SUBMIT"):

    input = get_cleaned_document(url)

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. "},
            {"role": "user", "content": instruction + "\n" + input},
            {"role": "user", "content": "format the result as json object."},
            {"role": "user", "content": "feild names should be in lower case combined with under score"},
            {"role": "user", "content": "In case of multiple startups, use startup name as key"}
        ],
    )

    financial_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. "},
            {"role": "user", "content": financial_instruction + "\n" + input},
            {"role": "user", "content": "format the result as table."},
            {"role": "user", "content": "feild names should be in lower case combined with under score"},
            {"role": "user", "content": "In case of financial from multiple year, use year as the key"}
        ],
    )

    response = completion.choices[0].message.content
    financial_response = financial_completion.choices[0].message.content
    st.json(response)
    st.success(financial_response)