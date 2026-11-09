import json


def handler(event, context):
    """Process a batch of SQS messages; report the ones that failed."""
    failures = []
    for record in event.get("Records", []):
        try:
            body = json.loads(record["body"])
            if "order" not in body:
                raise ValueError("no order in the message")
        except (ValueError, TypeError):
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}
