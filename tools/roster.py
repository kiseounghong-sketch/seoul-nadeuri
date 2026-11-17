"""조·방 명단 잠금 도구. 명단과 코드는 저장소에 넣지 않는다(공개 저장소).

  꺼내기: python3 tools/roster.py open  <학생코드>            > /tmp/roster.json
  넣기:   python3 tools/roster.py close /tmp/roster.json <학생코드> <선생님코드>

roster.json 모양: {"teams": {"1": [["이름", ...], ...], "2": [...]}, "rooms": [{"room": "503", "names": ["이름", ...]}]}
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
    student = {'teams': roster['teams'], 'rooms': roster.get('rooms', [])}
    teacher = dict(student, scode=scode)
    for name, obj, code in (('TEAMS_SEALED', student, scode), ('TEACH_SEALED', teacher, tcode)):
        html, n = re.subn(PAT[name], lambda m: 'const %s = %s;' % (name, seal(obj, code)), html, count=1)
        assert n == 1, name
    open(HTML, 'w', encoding='utf-8').write(html)
    print('index.html 의 잠금 블록 두 개를 새로 만들었습니다.')
