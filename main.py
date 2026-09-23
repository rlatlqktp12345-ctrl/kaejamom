import os
import json
import datetime
import requests


AUTH_KEY = os.environ.get("6PKhgzMkSiSyoYMzJJokTA")

# 부산 항만 관측소 지점번호 (북항: 대청동 159, 신항: 가덕도 255)
STATIONS = {
    "북항": "159",
    "신항": "255"
}

def get_current_kst_time():
    """현재 한국 시간 기준 최근 정시 시간 구하기 (예: 202609240000)"""
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    # 정시 단위 데이터 조회를 위해 분은 00분으로 설정
    return now.strftime("%Y%m%d%H00")

def fetch_weather_data(stn_id):
    url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php"
    tm = get_current_kst_time()
    
    params = {
        'tm': tm,
        'stn': stn_id,
        'help': '0',        # 도움말 제외 (순수 데이터만 파싱)
        'authKey': AUTH_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        text_data = response.text
        
        # API허브는 텍스트(CSV 형태)로 결과를 반환하므로 줄바꿈 기준으로 파싱
        lines = text_data.strip().split('\n')
        for line in lines:
            # 주석(#)이나 안내 문구가 아닌 실제 데이터 행 찾기
            if not line.startswith('#') and line.strip():
                parts = line.split(',')
                if len(parts) > 10:
                    # 주요 변수 매핑 (출력결과 명세서 기준)
                    return {
                        "관측시각": parts[0].strip(),
                        "기온_C": float(parts[11].strip()) if parts[11].strip() else None,
                        "습도_%": float(parts[13].strip()) if parts[13].strip() else None,
                        "풍향_deg": float(parts[2].strip()) if parts[2].strip() else None,
                        "풍속_ms": float(parts[3].strip()) if parts[3].strip() else None,
                        "강수량_mm": float(parts[15].strip()) if parts[15].strip() else None
                    }
        return {"error": "유효한 데이터 행을 찾지 못했습니다.", "raw": text_data}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    result = {}
    for name, stn in STATIONS.items():
        result[name] = fetch_weather_data(stn)
        
    # data 폴더에 결과 저장
    os.makedirs("data", exist_ok=True)
    with open("data/weather.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    print("부산 신항·북항 날씨 데이터 수집 완료:", result)
