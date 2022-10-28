import datetime
import json
import logging


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        return json.dump(
            {
                'args': record.args,
                'file': record.filename,
                'func': record.funcName,
                'line': record.lineno,
                'message': record.getMessage(),
                'datetime': datetime.datetime.utcnow(),
            },
            ensure_ascii=False
        )


log = logging.getLogger()
log.setLevel("INFO")
std_handler = logging.StreamHandler()
std_handler.setFormatter(JSONFormatter())
file_handler = logging.FileHandler(filename="aesn.log", mode="a")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(JSONFormatter())
log.addHandler(std_handler)
log.addHandler(file_handler)
