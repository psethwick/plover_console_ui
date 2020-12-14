class PaperTapeModel():
    def __init__(self):
        self.tape = []

    def add(self, s):
        self.tape.insert(0, s)

    def get(self):
        return [(s, i) for (i, s)
                in enumerate(self.tape)]


def on_stroked(paper_tape_model, stroke):
    paper_tape_model.add(stroke.rtfcre)
