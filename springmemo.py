import springnote_client
import notegui


class SpringMemo:
    def __init__(self):
        self.consumer_token = ""
        self.consumer_token_secret = ""

        self.client = sprintnote_client.SpringnoteClient()
        self.notegui = NoteTaskBar(self)




def run():
    print "adsfdsfs"
    

if __name__=="__main__":
    run()
