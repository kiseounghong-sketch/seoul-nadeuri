"""로컬 미리 보기 서버. /teacher/ 주소를 Firebase Hosting처럼 index.html로 돌려 준다.

  python3 tools/serve.py [포트]     →  http://localhost:8765/  (학생 앱),  http://localhost:8765/teacher/  (선생님 앱)
"""
import functools, http.server, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean = path.split('?', 1)[0].split('#', 1)[0]
        if clean == '/teacher' or clean.startswith('/teacher/'):
            path = '/index.html'
        return super().translate_path(path)


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
http.server.ThreadingHTTPServer(('', port), functools.partial(Handler, directory=ROOT)).serve_forever()
