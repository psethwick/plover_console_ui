from prompt_toolkit.document import Document
from prompt_toolkit.application import get_app


def output_to_buffer(buffer, text):
    o = f"{buffer.text}\n{text}"
    buffer.document = Document(text=o, cursor_position=len(o))
    get_app().invalidate()


def output_to_buffer_position(buffer, position, text):
    o = f"{buffer.text[:position]}\n{text}"
    buffer.document = Document(text=o, cursor_position=len(o))
    get_app().invalidate()
