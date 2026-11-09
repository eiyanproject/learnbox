import json


def handler(event, context):
    """Process a batch of SQS messages; report the ones that failed."""
    failures = []
    # For each record in event["Records"]: parse record["body"] as JSON;
    # if that fails, or there is no "order" key, it is a failure -
    # record its record["messageId"].
    return {"batchItemFailures": failures}
