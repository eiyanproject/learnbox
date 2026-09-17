class AppError(Exception):
    pass


class ConfigError(AppError):
    pass


class NetworkError(AppError):
    def __init__(self, message, retryable):
        super().__init__(message)
        self.retryable = retryable


def load_port(raw):
    try:
        port = int(raw["port"])
    except (KeyError, ValueError) as e:
        raise ConfigError("port missing or not a number") from e
    if not 1 <= port <= 65535:
        raise ConfigError(f"port out of range: {port}") from None
    return port


def with_row_note(func, rows):
    for i, row in enumerate(rows):
        try:
            func(row)
        except Exception as e:
            e.add_note(f"row {i}")
            raise


def validate_all(records):
    errors = []
    for record in records:
        if "id" not in record:
            errors.append(KeyError("id"))
        if record.get("qty", 0) < 0:
            errors.append(ValueError(f"negative qty: {record['qty']}"))
    if errors:
        raise ExceptionGroup("validation failed", errors)
    return True


def count_by_kind(records):
    counts = {"key": 0, "value": 0}
    try:
        validate_all(records)
    except* KeyError as eg:
        counts["key"] = len(eg.exceptions)
    except* ValueError as eg:
        counts["value"] = len(eg.exceptions)
    return counts
