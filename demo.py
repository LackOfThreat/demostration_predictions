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
    st.set_page_config(page_title="Ресторан",
                   page_icon="💸",
                   layout="wide")
    link = "https://drive.google.com/file/d/1e0ZT4bhQF2gCcjxwAJxEXADkMvdipgw-/view?usp=sharing"
    file = download_file_from_google_drive("1e0ZT4bhQF2gCcjxwAJxEXADkMvdipgw-").content
    data = pd.read_csv(io.StringIO(file.decode('utf-8'))).drop("Unnamed: 0", axis=1)
    # data['date'] = pd.to_datetime(data.time, format="%Y-%m-%d")
    data["ds"] = pd.to_datetime(data.ds)
    
    tz = pytz.timezone('Europe/Kiev')
    kiev_now = datetime.now(tz)

    kiev_now = datetime.fromtimestamp(1639216152)

    kiev_now_str = "%s-%s-%s %s:00:00" % (kiev_now.year, kiev_now.month, \
        kiev_now.day, kiev_now.hour)
    kiev_today_str = "%s-%s-%s" % (kiev_now.year, kiev_now.month, \
        kiev_now.day)
    kiev_now_datetime = pd.to_datetime(kiev_now_str)
    kiev_one_hour_more_str = str(kiev_now_datetime+timedelta(hours=1))
    data = data.sort_values(by=['yhat'], ascending=False)
    # st.write(data[data["date"]])
    st.title("Предсказание заказов - Ресторан")
    spot = st.selectbox("Точка", ['Січових Стрільців'])
    #data = data[data['spot'] == spot]
    st.write("Предсказания на сегодняшний день:", kiev_today_str)
    chart_container = st.container()
    # if len(data[data["time"]==kiev_now_datetime]) == 0:
    #     st.write("**На это время нет вероятных заказов**")
    # else:
    #     st.write("**Нужно приготовить:**")
    hist_data = {"index": [], 'amount': []}

    for i in range(1, 24):
        kiev_one_hour_more_str = str(kiev_now_datetime+timedelta(hours=1))
        st.write("Нужно приготовить с:", "**",str(kiev_now_datetime)[:-3],"**", "до", '**', kiev_one_hour_more_str[:-3], '**')
        time = (str(kiev_now_datetime))
        amount = 0
        
        # st.dataframe(data[data["time"]==kiev_now_datetime])
        for index, row in data[data["ds"]==kiev_now_datetime].iterrows():
            st.write("*",row[0], f"{int(row[2])}x")
            amount += int(row[2])
        kiev_now_datetime = kiev_now_datetime+timedelta(hours=1)
        hist_data['index'].append(time[10:-3])
        hist_data['amount'].append(amount)
        st.markdown("""---""")

    hist_data = pd.DataFrame(hist_data).set_index('index')
    chart_container.bar_chart(hist_data['amount'])



