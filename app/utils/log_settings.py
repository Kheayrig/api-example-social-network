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
