# 장기 토큰 만료일 확인 + 연장. 연장된 토큰은 출력만 하므로 환경 설정에 직접 바꿔 넣어야 반영됨
import json, os, time, urllib.parse, urllib.request

T = os.environ['IG_ACCESS_TOKEN']
q = urllib.parse.urlencode({'grant_type': 'ig_refresh_token', 'access_token': T})
r = json.load(urllib.request.urlopen(f'https://graph.instagram.com/refresh_access_token?{q}', timeout=30))
days = r['expires_in'] // 86400
print(f'토큰 유효기간: {days}일 남음 (연장 후 기준)')
