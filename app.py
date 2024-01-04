import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
from elastic_api import search_index, get_total_price, search_index2, remove_content
from streamlit_js_eval import streamlit_js_eval

def format_currency(value):
    return f"{int(value):,}원"

def set_summary(month, total_profit, total_loss):
    st.text(f"{month}월 총 수입: {format_currency(total_profit)}")
    st.text(f"{month}월 총 지출: {format_currency(total_loss)}")
    if total_profit > abs(total_loss):
        st.text("=> 수입이 지출보다 많네요. 잘 하고 계세요!")
    else:
        st.text("=> 지출을 좀 줄이셔야 할 것 같습니다..")

def set_plot():
    date_sum=df.groupby('날짜')[['금액']].sum()
    fig1 = px.line(date_sum)
    payment=df[df.타입=='지출']
    payment.금액=abs(payment.금액)
    payment_sum=payment.groupby('대분류')[['금액']].sum()
    payment_sum.reset_index(inplace=True)
    fig2=px.pie(payment_sum, values='금액', names='대분류')

    col1, col2, = st.columns(2)
    with col1:
        st.subheader('일별 수입/지출')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.subheader('대분류별 소비 비중')
        st.plotly_chart(fig2, use_container_width=True)

def set_table(df):
    st.subheader(f"전체 거래 내역")
    st.dataframe(df)
    print(df)

st.header("월 별 가계부")
month = st.selectbox("월을 선택해 주세요", list(range(1, 13)))
result = search_index(month)
if result:
    combined_data = []
    for entry in result.to_dict()["hits"]["hits"]:
        source = entry["_source"]  # _source 데이터
        source["_id"] = entry["_id"]  # _index 추가
        combined_data.append(source)

    # DataFrame 생성
    df = pd.DataFrame(combined_data)

    selected_columns = ['_id', '대분류', '내용', '날짜', '금액', '결제수단', '소분류', '타입']
    df_selected = df[selected_columns]

    total_profit, total_loss = get_total_price(month)
    set_summary(month, total_profit, total_loss)
    set_plot()
    set_table(df_selected)    
else:
    st.text(f"{month}월에는 입력된 데이터가 없어요")

# 삽입
with st.sidebar:
    # 가계부 표에 있는 변수 순서대로 데이터를 입력하고 '삽입' 버튼을 누르면
    # 가계부 표 밑에 새로운 소비 데이터가 추가됨
    transection_date = st.date_input("거래가 발생한 날짜를 입력해 주세요")
    transection_type = st.selectbox("타입을 선택해 주세요", ["지출", "수입", "이체"])
    transection_category = st.selectbox("지출 분류를 선택하세요", ["온라인쇼핑", "이체", "생활", "금융", "카페/간식", "식비", "금융수입", "교통", "카드대금", "기타수입", "Other"])
    transection_small_category = st.text_input("지출 분류의 세부 내용이 있다면 적어주세요")
    transection_content = st.text_input("지출 내용을 입력하세요")
    transection_method = st.text_input("결제 수단을 입력하세요")
    transection_bill = st.number_input("금액을 입력하세요")
    insert_transection = st.button("가계부에 추가하기")
    st.title("가계부에서 원하는 내역 삭제하기")
    del_index = st.text_input("삭제하려는 거래 내역의 index값을 입력하세요")
    delete_transection = st.button("가계부 내용 삭제하기")
    if(delete_transection):
        remove_content(del_index)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

if insert_transection == True:
    insert_result = search_index2(transection_category, transection_content, transection_date, transection_method, transection_bill, transection_small_category, transection_type)
    streamlit_js_eval(js_expressions="parent.window.location.reload()")