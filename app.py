import streamlit as st
import time
import pandas as pd
import time
import pickle
import numpy as np
from selenium import webdriver
path = "C:\Program Files (x86)\chromedriver.exe"
from selenium.webdriver.common.by import By
import os
import sys
import pandas as pd
from nordvpn_switcher import initialize_VPN, rotate_VPN
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

with open("dico.pkl", "rb") as f:
    dico = pickle.load(f)

def crawling_match_url(path, region_number, tournaments_number, season_number, api_delay_term=5):
    rotate_VPN()
    bar = st.progress(0)
    # activate webdriver
    url = 'https://www.whoscored.com/Regions/'+str(region_number)+'/Tournaments/'
    url = url+str(tournaments_number)+'/Seasons/'+str(season_number)+'/Fixtures'
    driver = webdriver.Chrome(path)
    driver.get(url)

    # wait get league team datas
    match_link= []
    for i in range(40):
        time.sleep(api_delay_term)
        elements = driver.find_elements_by_css_selector('a.result-1.rc')
        for element in elements:
            match_link.append(element.get_attribute('href'))

            # click
        try : 
            button = driver.find_element_by_css_selector('a.previous.button.ui-state-default.rc-l.is-default')
            driver.execute_script("arguments[0].click();", button)
            bar.progress(i*2)
            
        except : 
            bar.progress(80)
            break

        time.sleep(2)
            
    
    driver.close()
    del driver
    ids = []
    for url in list(set(match_link)):
        ids.append(url.split("Matches/")[1].split("/Live")[0])
    bar.progress(100)
    return ids

def get_data(soup):

    script = soup.find_all("script")
    for i in range(30,45): 
        
        try:
            data = str(script[i])
            data = data.split('<script>\n        require.config.params["args"] = ')[1]
            data = data.split(';\n    </script>')[0]
            data = data.replace("matchId", '"matchId"')
            data = data.replace("matchCentreData", '"matchCentreData"')
            data = data.replace("matchCentreEventTypeJson", '"matchCentreEventTypeJson:"')
            data = data.replace("formationIdNameMappings", '"formationIdNameMappings"')
            return data
        except:
            pass
    return -1



def parse_file(html):
    soup = BeautifulSoup(html, "html.parser")
    return get_data(soup)
    

def scraper_json(region, tournament, savedFile, links):
    links = [int(link) for link in links]
    bar = st.progress(0)
    error_count = 0
    dico = {"id":[], "data":[]} # Initialisation du dictionnaire
    index = 0 
    len_ = len(links)
    for link in links: 
        if index%10 == 0:
            rotate_VPN()  
        index +=1
        bar.progress(index/len_) 
        cond_ = 0
        while cond_ < 4:
            try:
                driver = webdriver.Chrome(path)
                driver.get(f"https://fr.whoscored.com/Matches/{link}/live/")
                html = driver.page_source
                data = parse_file(html)
                if data  == -1:
                    cond_ += 1
                else:
                    dico["id"].append(link)
                    dico["data"].append(data)
                    cond_ = 4
            except Exception as e:
                error_count +=1
                print(f"> [Error] {e}")
                rotate_VPN()
                cond_ += 1
        
    driver.close()
    del driver
    dico = pd.DataFrame(dico)
    try:
        dico.to_csv(f"C:/Users/Simon/Desktop/Travail/whoscored_data/{region}/{tournament}/{savedFile}.csv")
    except:
        print("> Error for saving!")
    st.write(f"> Number errors = {error_count}")
    
initialize_VPN(save=1,area_input=["Norway", "Australia", "Canada", "Taiwan", "Brazil", "United States", "Mexico"])

st.sidebar.header("Input parameter")
with st.sidebar.form(key="my_form"):
    region_input = st.selectbox("Select region ...", ("Allemagne", "Angleterre", "Italie", "Espagne", "France"))
    region = dico[region_input]["region"] 
    tournament_input = st.selectbox("Select tournament ...", ("Bundesliga", "Premier League", "Serie A", "LaLiga", "Ligue 1"))
    tournament = dico[region_input][tournament_input]["tournament"] 
    season_input1 = st.selectbox("Select season ...", ("2021/2022", "2020/2021", "2019/2020", "2018/2019", "2017/2018", "2016/2017", "2015/2016", "2014/2015", "2013/2014", "2012/2013", "2011/2012", "2010/2011", "2009/2010"), key="one")
    season1 = dico[region_input][tournament_input][season_input1] 
    file_name1 = st.text_input("Enter the name of the file 1 ...")
    #season_input2 = st.selectbox("Select season ...", ("2021/2022", "2020/2021", "2019/2020", "2018/2019", "2017/2018", "2016/2017", "2015/2016", "2014/2015", "2013/2014", "2012/2013", "2011/2012", "2010/2011", "2009/2010"), key="two")
    #season2 = dico[region_input][tournament_input][season_input2] 
    #file_name2 = st.text_input("Enter the name of the file 2 ...")
    #season_input3 = st.selectbox("Select season ...", ("2021/2022", "2020/2021", "2019/2020", "2018/2019", "2017/2018", "2016/2017", "2015/2016", "2014/2015", "2013/2014", "2012/2013", "2011/2012", "2010/2011", "2009/2010"), key="three")
    #season3 = dico[region_input][tournament_input][season_input3] 
    #file_name3 = st.text_input("Enter the name of the file 3 ...")
    #season_input4 = st.selectbox("Select season ...", ("2021/2022", "2020/2021", "2019/2020", "2018/2019", "2017/2018", "2016/2017", "2015/2016", "2014/2015", "2013/2014", "2012/2013", "2011/2012", "2010/2011", "2009/2010"), key="four")
    #season4 = dico[region_input][tournament_input][season_input4] 
    #file_name4 = st.text_input("Enter the name of the file 4 ...")
    submit_button = st.form_submit_button(label="submit")

st.markdown("# Scraper WhoScored?com")
if submit_button:
    st.markdown("## Step 1: Retrieve matchs URLs")
    ids = crawling_match_url(path, region, tournament, season1)
    st.markdown("## Step 2: Retrieve matchs Json")
    scraper_json(region_input, tournament_input, file_name1, ids)
    st.markdown("## Step 3: Save data")
    #st.markdown("## Step 1: Retrieve matchs URLs")
    #ids = crawling_match_url(path, region, tournament, season2)
    #st.markdown("## Step 2: Retrieve matchs Json")
    #scraper_json(region_input, tournament_input, file_name2, ids)
    #st.markdown("## Step 3: Save data")
    #st.markdown("## Step 1: Retrieve matchs URLs")
    #ids = crawling_match_url(path, region, tournament, season3)
    #st.markdown("## Step 2: Retrieve matchs Json")
    #scraper_json(region_input, tournament_input, file_name3, ids)
    #st.markdown("## Step 3: Save data")
    #st.markdown("## Step 1: Retrieve matchs URLs")
    #ids = crawling_match_url(path, region, tournament, season4)
    #st.markdown("## Step 2: Retrieve matchs Json")
    #scraper_json(region_input, tournament_input, file_name4, ids)
    #st.markdown("## Step 3: Save data")
   
    
    
   

