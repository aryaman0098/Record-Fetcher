class protocol:
    
    query = None
    response = None
    
    def fillHeaders(self, auth, query, response):
        self.header = {"isAuthenticated" : auth,
                       "queryLength" : len(query),
                       "responseLength" : len(response)}
        self.query = query
        self.response = response

