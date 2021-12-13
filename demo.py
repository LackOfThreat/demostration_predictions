import streamlit as st
from datetime import datetime, timedelta
import pytz
import requests
import pandas as pd
import io


def download_file_from_google_drive(id):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    return response    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


if __name__ == "__main__":
    link = "https://drive.google.com/file/d/1ClclhYTpwez6Dmf2eiG_M7TFmed85OPr/view?usp=sharing"
    file = download_file_from_google_drive("1ClclhYTpwez6Dmf2eiG_M7TFmed85OPr").content
    data = pd.read_csv(io.StringIO(file.decode('utf-8'))).drop("Unnamed: 0", axis=1)
    data["time"] = pd.to_datetime(data.time)
    
    # tz = pytz.timezone('Europe/Kiev')
    tz = pytz.timezone('US/Alaska')
    kiev_now = datetime.now(tz)
    kiev_now_str = "%s-%s-%s %s:00:00" % (kiev_now.year, kiev_now.month, \
        kiev_now.day, kiev_now.hour)
    kiev_now_datetime = pd.to_datetime(kiev_now_str)
    kiev_one_hour_more_str = str(kiev_now_datetime+timedelta(hours=1))
    data = data.sort_values(by=['not_changed'], ascending=False)
    st.title("Предсказание заказов - Багато Лосося")
    st.write("Текущий временной промежуток:", kiev_now_str, " -" ,kiev_one_hour_more_str)
    
    if len(data[data["time"]==kiev_now_datetime]) == 0:
        st.write("**На это время нет вероятных заказов**")
    else:
        st.write("**Нужно приготовить:**")

    for index, row in data[data["time"]==kiev_now_datetime].iterrows():
        st.write("*",row[1])



