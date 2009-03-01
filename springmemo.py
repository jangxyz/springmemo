import sprintnote_client
import notegui

class SpringMemo:
  def __init__(self):

    self.client = springnote_client.SpringnoteClient()
    self.notegui = notegui.NoteTaskBar(self)


