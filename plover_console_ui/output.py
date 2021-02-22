from prompt_toolkit.document import Document
from prompt_toolkit.application import get_app


def set_buffer_text(buffer, text):
    trimmed = text[-5000:]
    buffer.document = Document(trimmed, cursor_position=len(trimmed))
    get_app().invalidate()


def output_to_buffer(buffer, text):
    o = f"{buffer.text}\n{text}"
    set_buffer_text(buffer, o)


def output_to_buffer_position(buffer, position, text):
    o = f"{buffer.text[:position]}\n{text}"
    set_buffer_text(buffer, o)
