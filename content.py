class Content:

    def __init__(self,contentID, code, title, description, date, tags, filename, mimetype, size, restriction, views, user):
        self.contentID = contentID
        self.code = code
        self.title = title
        self.description = description
        self.date = date
        self.tags = tags
        self.filename = filename
        self.mimetype = mimetype
        self.size = size
        self.restriction = restriction
        self.views = views
        self.users_username = user