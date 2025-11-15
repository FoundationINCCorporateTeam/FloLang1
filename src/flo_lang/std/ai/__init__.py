"""std/ai - AI model integration module."""

from flo_lang.std.ai.client import (
    configure,
    generate,
    stream,
    register_adapter,
)

__all__ = [
    'configure',
    'generate',
    'stream',
    'register_adapter',
]
