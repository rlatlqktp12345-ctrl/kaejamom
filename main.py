import os
import json
import datetime
import requests

AUTH_KEY = os.environ.get("KMA_AUTH_KEY")

# 부산 항만 관측소 (북항: 대청동 159, 신항 인근: 가덕도 등)
STATIONS = {
    "북항": "159",
    "신항": "255"
}

def get_current_kst_time():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    return now.strftime("%Y%m%d%H00")

def fetch_weather_data(stn_id):
    # API허브에서 안정적으로 데이터를 받아오는 종관기상관측(ASOS) 시간자료 URL
    url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php"
    tm = get_current_kst_time()
    
    params = {
        'tm': tm,
        'stn': stn_id,
        'help': '0',
        'authKey': AUTH_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        text_data = response.text
        
        # 데이터가 정상이 아닐 경우 예외 처리
        if "ERROR" in text_data or "Unauthorized" in text_data:
            return {"error": "API 인증 또는 요청 오류", "raw": text_data}
            
        lines = text_data.strip().split('\n')
        for line in lines:
            if not line.startswith('#') and line.strip():
                parts = [p.strip() for p in line.split(',')]
                if len(parts) > 15:
                    return {
                        "관측시각": parts[0],
                        "기온_C": float(parts[11]) if parts[11] else None,
                        "습도_%": float(parts[13]) if parts[13] else None,
                        "풍향_deg": float(parts[2]) if parts[2] else None,
                        "풍속_ms": float(parts[3]) if parts[3] else None,
                        "강수량_mm": float(parts[15]) if parts[15] else None
                    }
        return {"error": "데이터 행을 찾지 못했습니다.", "raw": text_data}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    result = {}
    for name, stn in STATIONS.items():
        result[name] = fetch_weather_data(stn)
        
    os.makedirs("data", exist_ok=True)
    with open("data/weather.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    print("수집 결과:", result)
