"""The checks the Pub/Sub service applies to a publish request.

The real producer leaves them to the service; the in-process test broker applies them, so a
publish the service would reject is rejected in tests too, with the same exception type.
"""

import re
from typing import Any

from google.api_core.exceptions import InvalidArgument

__all__ = ("validate_publish_request",)

MAX_MESSAGES_PER_REQUEST = 1000
MAX_REQUEST_BYTES = 10 * 1000 * 1000
MAX_MESSAGE_BYTES = 10 * 1000 * 1000
MAX_ATTRIBUTES = 100
MAX_ATTRIBUTE_KEY_BYTES = 256
MAX_ATTRIBUTE_VALUE_BYTES = 1024
MAX_ORDERING_KEY_BYTES = 1024

# A resource id: a letter, then 2..254 of letters, digits and `-_.~+%`, not starting with goog.
_RESOURCE_ID = re.compile(r"[A-Za-z][A-Za-z0-9\-_.~+%]{2,254}")


def validate_resource_id(kind: str, path: str) -> None:
    """Reject a topic or subscription id the service does not accept as a name."""
    name = path.rsplit("/", 1)[-1]
    if not _RESOURCE_ID.fullmatch(name) or name.lower().startswith("goog"):
        msg = (
            f"Invalid {kind} id {name!r}: 3 to 255 characters, starting with a letter, of "
            "letters, digits and -_.~+%, and not starting with 'goog'"
        )
        raise InvalidArgument(msg)


def validate_message(message: Any) -> None:
    """Reject one raw ``PubsubMessage`` the service would refuse."""
    attributes = message.attributes
    if not message.data and not attributes:
        msg = "A message needs data or at least one attribute"
        raise InvalidArgument(msg)
    if len(attributes) > MAX_ATTRIBUTES:
        msg = f"A message has at most {MAX_ATTRIBUTES} attributes, got {len(attributes)}"
        raise InvalidArgument(msg)
    size = len(message.data)
    for key, value in attributes.items():
        key_bytes = len(key.encode())
        value_bytes = len(value.encode())
        if not 1 <= key_bytes <= MAX_ATTRIBUTE_KEY_BYTES:
            msg = f"An attribute key is 1 to {MAX_ATTRIBUTE_KEY_BYTES} bytes: {key!r}"
            raise InvalidArgument(msg)
        if key.startswith("goog"):
            msg = f"Attribute keys starting with 'goog' are reserved: {key!r}"
            raise InvalidArgument(msg)
        if value_bytes > MAX_ATTRIBUTE_VALUE_BYTES:
            msg = f"An attribute value is at most {MAX_ATTRIBUTE_VALUE_BYTES} bytes: {key!r}"
            raise InvalidArgument(msg)
        size += key_bytes + value_bytes
    if len(message.ordering_key.encode()) > MAX_ORDERING_KEY_BYTES:
        msg = f"An ordering key is at most {MAX_ORDERING_KEY_BYTES} bytes"
        raise InvalidArgument(msg)
    if size > MAX_MESSAGE_BYTES:
        msg = f"A message is at most {MAX_MESSAGE_BYTES} bytes, got {size}"
        raise InvalidArgument(msg)


def validate_publish_request(request: Any) -> None:
    """Reject a raw ``PublishRequest`` the service would refuse."""
    validate_resource_id("topic", request.topic)
    messages = request.messages
    if not messages:
        msg = "A publish request needs at least one message"
        raise InvalidArgument(msg)
    if len(messages) > MAX_MESSAGES_PER_REQUEST:
        msg = (
            f"A publish request takes at most {MAX_MESSAGES_PER_REQUEST} messages, "
            f"got {len(messages)}"
        )
        raise InvalidArgument(msg)
    for message in messages:
        validate_message(message)
    if request.ByteSize() > MAX_REQUEST_BYTES:
        msg = f"A publish request is at most {MAX_REQUEST_BYTES} bytes"
        raise InvalidArgument(msg)
