import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "index.html"
QUIZ_FILE = ROOT / "quiz.html"

QUIZ_BANKS = {
    "html": {
        "title": "HTML Level",
        "variants": [
            [
                {"prompt": "Which element creates a hyperlink?", "options": ["<a>", "<link>", "<url>", "<href>"], "answer": "<a>"},
                {"prompt": "Which attribute gives the image path?", "options": ["src", "alt", "title", "href"], "answer": "src"},
                {"prompt": "Which tag is used for the largest heading?", "options": ["<h1>", "<h6>", "<head>", "<title>"], "answer": "<h1>"},
            ],
            [
                {"prompt": "Which tag starts a paragraph in HTML?", "options": ["<p>", "<div>", "<span>", "<br>"], "answer": "<p>"},
                {"prompt": "Which element is used for an unordered list?", "options": ["<ol>", "<ul>", "<li>", "<table>"], "answer": "<ul>"},
                {"prompt": "Which tag creates a line break?", "options": ["<br>", "<hr>", "<lb>", "<p>"], "answer": "<br>"},
            ],
            [
                {"prompt": "Which tag defines a hyperlink?", "options": ["<link>", "<a>", "<img>", "<href>"], "answer": "<a>"},
                {"prompt": "Which attribute adds alternate text to an image?", "options": ["src", "alt", "id", "class"], "answer": "alt"},
                {"prompt": "Which tag can group a block of content?", "options": ["<div>", "<span>", "<strong>", "<em>"], "answer": "<div>"},
            ],
        ],
    },
    "css": {
        "title": "CSS Level",
        "variants": [
            [
                {"prompt": "Which property changes text color?", "options": ["color", "font-size", "background", "margin"], "answer": "color"},
                {"prompt": "Which property adds space inside an element?", "options": ["padding", "margin", "border", "outline"], "answer": "padding"},
                {"prompt": "Which display value makes elements flexibly arrange?", "options": ["flex", "block", "inline", "none"], "answer": "flex"},
            ],
            [
                {"prompt": "Which property changes the background color?", "options": ["background-color", "color", "font-family", "text-align"], "answer": "background-color"},
                {"prompt": "Which property controls text size?", "options": ["font-size", "width", "padding", "border"], "answer": "font-size"},
                {"prompt": "Which property creates space outside an element?", "options": ["margin", "padding", "border", "display"], "answer": "margin"},
            ],
            [
                {"prompt": "Which property controls the order of flex items?", "options": ["order", "display", "justify-content", "flex-direction"], "answer": "order"},
                {"prompt": "Which property centers text horizontally?", "options": ["text-align", "vertical-align", "align-items", "justify-items"], "answer": "text-align"},
                {"prompt": "Which property changes the thickness of a border?", "options": ["border-width", "background-color", "color", "margin"], "answer": "border-width"},
            ],
        ],
    },
    "python": {
        "title": "Python Level",
        "variants": [
            [
                {"prompt": "Which keyword starts a function in Python?", "options": ["def", "function", "class", "loop"], "answer": "def"},
                {"prompt": "How do you create a list in Python?", "options": ["[1, 2, 3]", "{1, 2, 3}", "(1, 2, 3)", "<1, 2, 3>"], "answer": "[1, 2, 3]"},
                {"prompt": "Which symbol starts a comment in Python?", "options": ["#", "//", "/*", "<!--"], "answer": "#"},
            ],
            [
                {"prompt": "Which function prints output?", "options": ["print()", "input()", "len()", "range()"], "answer": "print()"},
                {"prompt": "Which data type stores true/false values?", "options": ["bool", "str", "int", "list"], "answer": "bool"},
                {"prompt": "Which statement checks a condition?", "options": ["if", "for", "while", "def"], "answer": "if"},
            ],
            [
                {"prompt": "Which loop repeats a fixed number of times?", "options": ["for", "if", "while", "return"], "answer": "for"},
                {"prompt": "How do you read user input?", "options": ["input()", "print()", "len()", "type()"], "answer": "input()"},
                {"prompt": "Which keyword defines a class?", "options": ["class", "def", "return", "import"], "answer": "class"},
            ],
        ],
    },
}


def build_assignments(count: int, level: str):
    level_data = QUIZ_BANKS.get(level.lower(), QUIZ_BANKS["html"])
    variants = level_data["variants"]
    assignments = []
    for index in range(1, count + 1):
        variant = variants[(index - 1) % len(variants)]
        assignments.append(
            {
                "student": f"Student {index}",
                "quiz": f"Quiz {index}",
                "level": level.lower(),
                "level_title": level_data["title"],
                "questions": variant,
            }
        )
    return assignments


class QuizHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/assignments":
            params = parse_qs(parsed_path.query)
            count_value = params.get("count", ["3"])[0]
            level_value = params.get("level", ["html"])[0].lower()
            try:
                count = max(1, min(10, int(count_value)))
            except ValueError:
                count = 3

            payload = json.dumps({"level": level_value, "assignments": build_assignments(count, level_value)}).encode("utf-8")
            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if parsed_path.path in {"/", "/index.html"}:
            content = INDEX_FILE.read_bytes()
            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed_path.path.endswith('.html'):
            file_path = ROOT / Path(parsed_path.path.lstrip('/'))
            if file_path.exists() and file_path.is_file():
                content = file_path.read_bytes()
                self.send_response(200)
                self.send_cors_headers()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        self.send_error(404)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path != "/assignments":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        params = parse_qs(body)
        count_value = params.get("count", ["3"])[0]
        level_value = params.get("level", ["html"])[0].lower()
        try:
            count = max(1, min(10, int(count_value)))
        except ValueError:
            count = 3

        payload = json.dumps({"level": level_value, "assignments": build_assignments(count, level_value)}).encode("utf-8")
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def main():
    host = "127.0.0.1"
    port = 8000
    server = ThreadingHTTPServer((host, port), QuizHandler)
    print(f"Serving quiz app at http://{host}:{port}")
    print("Open http://127.0.0.1:8000/ in your browser")
    server.serve_forever()


if __name__ == "__main__":
    main()
