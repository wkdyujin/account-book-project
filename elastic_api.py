from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A
client = Elasticsearch('http://localhost:9200')

INDEX = 'bank_salad_02'

def set_range(month):
    start_date = f"2023-{month:02d}-01"
    end_date = f"2023-{month:02d}-31"
    return start_date,end_date

# 월 별 데이터 조회
def search_index(month):
    start_date, end_date = set_range(month)
    s = Search(index=INDEX).using(client).query("match_all")
    s = s.filter('range', 날짜={'gte': start_date, 'lte': end_date})
    s = s.extra(size=500)
    response = s.execute()
    return response

# 데이터 제거
def remove_content(content_id):
    client.delete(index=INDEX, id=content_id)
    print("제거되었습니다.")

# 총 소비, 총 지출 내역 조회
def get_total_price(month):
    start_date, end_date = set_range(month)
    s = Search(index=INDEX).using(client).query("match_all")
    s = s.filter('range', 날짜={'gte': start_date, 'lte': end_date})
    s.aggs.bucket('positive_amounts', 'range', field='금액', ranges=[{"from": 0.01}]).metric('sum_positive', 'sum', field='금액')6
    s.aggs.bucket('negative_amounts', 'range', field='금액', ranges=[{"to": 0}]).metric('sum_negative', 'sum', field='금액')
    response = s.execute()

    total_positive = response.aggregations.positive_amounts.buckets[0].sum_positive.value
    total_negative = response.aggregations.negative_amounts.buckets[0].sum_negative.value

    return total_positive, total_negative

# 데이터 삽입
def search_index2(transection_category, transection_content, transection_date, transection_method, transection_bill, transection_small_category, transection_type):
    doc = {
    '대분류': transection_category,
    '내용': transection_content,
    '날짜': transection_date,
    '결제수단': transection_method,
    '금액' : transection_bill,
    '소분류' : transection_small_category,
    '타입' : transection_type
}
    resp = client.index(index=INDEX, body=doc)
    print(resp['result'])