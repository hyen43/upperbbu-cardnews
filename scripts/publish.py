# 캐러셀 게시. 사용법:
#   python3 scripts/publish.py weeks/2026-10-22            # 컨테이너만 만들고 게시 안 함 (기본)
#   python3 scripts/publish.py weeks/2026-10-22 --publish  # 실제 게시
# 이미지는 GitHub raw URL로 인스타가 가져가므로, out/*.jpg가 main에 push돼 있어야 함
import glob, json, os, sys, time, urllib.parse, urllib.request

G = 'https://graph.instagram.com/v23.0'
RAW = 'https://raw.githubusercontent.com/hyen43/upperbbu-cardnews/main'
T = os.environ['IG_ACCESS_TOKEN']


def call(method, path, **q):
    q['access_token'] = T
    data = urllib.parse.urlencode(q).encode()
    url = f'{G}/{path}'
    req = urllib.request.Request(url, data=data) if method == 'POST' else urllib.request.Request(f'{url}?{data.decode()}')
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        sys.exit(f'{path} 실패: {e.read().decode()}')


def wait_ready(cid):
    for _ in range(30):
        s = call('GET', cid, fields='status_code')['status_code']
        if s == 'FINISHED':
            return
        if s in ('ERROR', 'EXPIRED'):
            sys.exit(f'컨테이너 {cid} 상태 {s}')
        time.sleep(5)
    sys.exit(f'컨테이너 {cid} 준비 시간 초과')


week = sys.argv[1].rstrip('/')
images = sorted(glob.glob(f'{week}/out/[0-9][0-9].jpg'))
if not 2 <= len(images) <= 10:
    sys.exit(f'이미지 {len(images)}장: 캐러셀은 2~10장')
caption = open(f'{week}/caption.md', encoding='utf-8').read().strip()

children = []
for img in images:
    url = f'{RAW}/{img}'
    with urllib.request.urlopen(url, timeout=30) as r:  # 공개 URL 확인
        assert r.status == 200, url
    cid = call('POST', 'me/media', image_url=url, is_carousel_item='true')['id']
    wait_ready(cid)
    children.append(cid)
    print('item', os.path.basename(img), cid)

carousel = call('POST', 'me/media', media_type='CAROUSEL', children=','.join(children), caption=caption)['id']
wait_ready(carousel)
print('carousel ready', carousel)

if '--publish' in sys.argv:
    media = call('POST', 'me/media_publish', creation_id=carousel)['id']
    print('published', call('GET', media, fields='permalink')['permalink'])
else:
    print('게시 안 함 (--publish 없이 실행). 컨테이너는 24시간 뒤 자동 만료')
