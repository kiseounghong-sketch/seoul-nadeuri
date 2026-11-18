"""조·방 명단 잠금 도구. 명단과 코드는 저장소에 넣지 않는다(공개 저장소).

  꺼내기: python3 tools/roster.py open  <학생코드>            > /tmp/roster.json
  넣기:   python3 tools/roster.py close /tmp/roster.json <학생코드> <선생님코드>

roster.json 모양: {"teams": {"1": [["이름", ...], ...], "2": [...]}, "rooms": [{"room": "503", "names": ["이름", ...]}],
                "nums": {"1": {"1": "이름", ...}, "2": {...}}, "wk": "..."}
  - nums: 학년 → 번호 → 이름. 학생은 학번(학년+번호)으로 로그인한다. 불참 학생은 teams와 nums에서 뺀다.
  - lunch: 학년 → 이름 → 확정된 점심 메뉴 id(LUNCH.menu의 id). 있으면 학생은 고르지 않고 확정 메뉴를 본다.
  - wk: 활동지 암호 열쇠 재료. 없으면 새로 만든다. 한 번 정해지면 바꾸지 않는다(바꾸면 서버에 올라간 내용을 못 읽는다).
필요한 것: pip install cryptography
"""
import base64, json, os, re, sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

HTML = os.path.join(os.path.dirname(__file__), '..', 'public', 'index.html')
PAT = {'TEAMS_SEALED': r'const TEAMS_SEALED = (\{.*?\});', 'TEACH_SEALED': r'const TEACH_SEALED = (\{.*?\});'}


def key(code, salt, it):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(code.encode())


def seal(obj, code):
    data = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()
    salt, iv, it = os.urandom(16), os.urandom(12), 300000
    b = lambda x: base64.b64encode(x).decode()
    return json.dumps({'it': it, 'salt': b(salt), 'iv': b(iv), 'ct': b(AESGCM(key(code, salt, it)).encrypt(iv, data, None))})


def unseal(box, code):
    d = base64.b64decode
    return json.loads(AESGCM(key(code, d(box['salt']), box['it'])).decrypt(d(box['iv']), d(box['ct']), None))


html = open(HTML, encoding='utf-8').read()
if sys.argv[1] == 'open':
    box = json.loads(re.search(PAT['TEAMS_SEALED'], html).group(1))
    print(json.dumps(unseal(box, sys.argv[2]), ensure_ascii=False, indent=1))
elif sys.argv[1] == 'close':
    roster = json.load(open(sys.argv[2], encoding='utf-8'))
    scode, tcode = sys.argv[3], sys.argv[4]
    if not roster.get('wk'):
        roster['wk'] = base64.b64encode(os.urandom(24)).decode()
    student = {'teams': roster['teams'], 'rooms': roster.get('rooms', []), 'nums': roster.get('nums', {}), 'lunch': roster.get('lunch', {}), 'wk': roster['wk']}
    teacher = dict(student, scode=scode)
    for name, obj, code in (('TEAMS_SEALED', student, scode), ('TEACH_SEALED', teacher, tcode)):
        html, n = re.subn(PAT[name], lambda m: 'const %s = %s;' % (name, seal(obj, code)), html, count=1)
        assert n == 1, name
    open(HTML, 'w', encoding='utf-8').write(html)
    print('index.html 의 잠금 블록 두 개를 새로 만들었습니다.')
