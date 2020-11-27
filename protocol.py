#Creating protocol for communication between server and client
class protocol:

    query = None
    response = None
    header = None
    
    def createMsgProtocol(self, auth, query, response):
        self.header = {"isAuthenticated" : auth,
                       "queryLength" : len(query),
                       "responseLength" : len(response)}
        self.query = query
        self.response = response

