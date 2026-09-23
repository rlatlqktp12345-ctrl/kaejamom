import os
import json
import datetime
import requests

AUTH_KEY = os.environ.get("KMA_AUTH_KEY")

# 부산 지역 대표 관측소 번호 (북항: 부산(159), 신항 인근: 가덕도 등)
STATIONS = {
    "북항": "159",
    "신항": "255"
}

def get_target_time():
    # 현재 시간 기준 가장 최근 정각 시간 계산
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    # 1시간 전 데이터를 조회해야 기상청 서버에 데이터가 안정적으로 쌓여 있습니다.
    target = now - datetime.timedelta(hours=1)
    return target.strftime("%Y%m%d%H00")

def fetch_weather_data(stn_id):
    url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm2.php"
    tm = get_target_time()
    
    params = {
        'tm': tm,
        'stn': stn_id,
        'help': '0',
        'authKey': AUTH_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        text_data = response.text
        
        if "ERROR" in text_data or "Unauthorized" in text_data:
            return {"error": "API 인증 또는 요청 오류", "raw": text_data}
            
        lines = text_data.strip().split('\n')
        for line in lines:
            if not line.startswith('#') and line.strip():
                parts = [p.strip() for p in line.split() if p.strip()]
                if len(parts) >= 16:
                    return {
                        "관측시각": parts[0],
                        "기온_C": float(parts[11]) if parts[11] != "-9" else None,
                        "습도_%": float(parts[13]) if parts[13] != "-9" else None,
                        "풍향_deg": float(parts[2]) if parts[2] != "-9" else None,
                        "풍속_ms": float(parts[3]) if parts[3] != "-9" else None,
                        "강수량_mm": float(parts[15]) if parts[15] != "-9" else None
                    }
        return {"error": "데이터 행을 찾지 못했습니다.", "raw": text_data[:200]}
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
