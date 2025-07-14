import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_order(message_body: Dict[str, Any]) -> None:
    """
    Business logic to process a single order message.
    Raises an exception to simulate failure when montant == -1.
    """
    order_id = message_body.get("id")
    amount = message_body.get("montant")

    logger.info(f"Processing order: {order_id} | Amount: {amount}")

    if amount == -1:
        raise ValueError("Invalid order: amount cannot be -1")

    # Simulate order processing
    logger.info(f"Order {order_id} processed successfully.")


def lambda_handler(
    event: Dict[str, Any], context: Any
) -> Dict[str, List[Dict[str, str]]]:
    """
    Lambda handler to process a batch of SQS messages.
    Uses partial batch failure response to handle individual message failures.
    """
    failed: List[Dict[str, str]] = []
    records = event.get("Records", [])

    logger.info(f"Received {len(records)} messages from SQS.")

    for record in records:
        message_id = record["messageId"]
        try:
            body = json.loads(record["body"])
            logger.info(f"Message ID: {message_id} | Body: {body}")
            process_order(body)
        except Exception as e:
            logger.error(f"Failed to process message {message_id}: {e}")
            failed.append({"itemIdentifier": message_id})

    if failed:
        logger.warning(
            f"{len(failed)} message(s) failed and will be retried or sent to DLQ."
        )

    return {"batchItemFailures": failed}
