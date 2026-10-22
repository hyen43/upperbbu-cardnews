# 게시물별 도달/저장/공유 집계. 사용법: python3 scripts/insights.py [개수]
import json, os, sys, urllib.parse, urllib.request

G = 'https://graph.instagram.com/v23.0'
T = os.environ['IG_ACCESS_TOKEN']


def get(path, **q):
    q['access_token'] = T
    return json.load(urllib.request.urlopen(f'{G}/{path}?{urllib.parse.urlencode(q)}'))


limit = int(sys.argv[1]) if len(sys.argv) > 1 else 25
media = get('me/media', fields='id,caption,media_type,timestamp,like_count,comments_count,permalink', limit=limit)['data']
for m in media:
    v = {x['name']: x['values'][0]['value'] for x in get(f"{m['id']}/insights", metric='reach,saved,shares,views')['data']}
    cap = (m.get('caption') or '').split('\n')[0][:40]
    print(f"{m['timestamp'][:10]} {m['media_type'][:5]:5} reach={v.get('reach', 0):>7} save={v.get('saved', 0):>5} share={v.get('shares', 0):>5} {cap}")
