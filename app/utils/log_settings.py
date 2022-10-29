import datetime
import json
import logging


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        logs = []
        with open('aesn.json', 'r') as f:
            data = f.read()
            if len(data) > 0:
                logs = json.loads(data)
            logs.append(
                {
                    'args': record.args,
                    'file': record.filename,
                    'func': record.funcName,
                    'line': record.lineno,
                    'message': record.getMessage(),
                    'datetime': str(datetime.datetime.utcnow()),
                }
            )
        return json.dumps(logs, ensure_ascii=False)


log = logging.getLogger()
log.setLevel("INFO")
std_handler = logging.StreamHandler()
std_handler.setFormatter(JSONFormatter())
file_handler = logging.FileHandler(filename="aesn.json", mode="w")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(JSONFormatter())
log.addHandler(std_handler)
log.addHandler(file_handler)
