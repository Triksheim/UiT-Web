import mysql.connector


class MyDb:

    def __init__(self) -> None:
        dbconfig = {'host': '127.0.0.1',
                    'user': 'user',
                    'password': 'test',
                    'database': 'myDb', }
        self.configuration = dbconfig

    def __enter__(self) -> 'cursor':
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor(prepared=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def query(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    

    def add_new_user(self, user):
        try:
            statement = """ INSERT INTO users (username, email, password, firstname, lastname, uuid, activated)
                            VALUES (%s, %s, %s, %s, %s, %s, %s) 
                        """
            self.cursor.execute(statement, user)
        except mysql.connector.Error as error:
            print(error)
            return error

    def get_user(self, username):
        try:
            statement = """ SELECT * 
                            FROM users 
                            WHERE username=(%s)
                        """
            self.cursor.execute(statement, username)
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
                print(err)
    
    def activate_user(self, id):
        try:
            statement = """ UPDATE users 
                            SET activated = 1
                            WHERE uuid = %s
                        """
            self.cursor.execute(statement, id)
        except mysql.connector.Error as error:
                print(error)
                return error


   

    def upload_content(self, content):
        try:
            statement = """ INSERT INTO content (contentID, code, title, description, date, tags, filename, mimetype, size, open, views, users_username)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s) 
                        """
            self.cursor.execute(statement, content)
        except mysql.connector.Error as error:
                print(error)
                return error

    def edit_content(self, edit):
        try:
            statement = """ UPDATE content
                            SET title=%s, description=%s, tags=%s, open=%s
                            WHERE contentID = %s
                        """
            self.cursor.execute(statement, edit)
        except mysql.connector.Error as error:
                print(error)
                return error


    def get_content(self, id):
        try:
            self.cursor.execute("SELECT * FROM content WHERE contentID=(%s)", (id,))
            result = self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(error)
        return result

    def get_open_content(self, id):
        try:
            self.cursor.execute("SELECT * FROM content WHERE contentID=(%s) AND open=(%s)", (id,1))
            result = self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(error)
        return result

    def get_all_content(self):
        try:
            self.cursor.execute("SELECT * FROM content")
            result = self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(error)
        return result

    def get_all_open_content(self):
        try:
            self.cursor.execute("SELECT * FROM content WHERE open=(%s)", (1,))
            result = self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(error)
        return result

    def get_all_content_by_type(self, type):
        try:
            self.cursor.execute("SELECT * FROM content WHERE mimetype like (%s)", (type))
            result = self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(error)
        return result

    def get_all_open_content_by_type(self, type):
        try:
            self.cursor.execute("SELECT * FROM content WHERE mimetype like (%s) and open=1", (type))
            result = self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(error)
        return result


    def add_view(self, id):
        try:
            statement1 = """SELECT views
                            FROM content
                            WHERE contentID=%s
                        """
            self.cursor.execute(statement1, id)

            views = self.cursor.fetchone()
            updated_views = (views[0]+1, id[0])

            statement2 = """UPDATE content
                            SET views=%s
                            WHERE contentID=%s 
                        """
            self.cursor.execute(statement2, updated_views)    
        except mysql.connector.Error as error:
                print(error)

    def add_new_comment(self, comment):
        try:
            statement = """ INSERT INTO comments (commentID, text, time, users_username, content_contentID)
                            VALUES (%s, %s, %s, %s, %s) 
                        """
            self.cursor.execute(statement, comment)
        except mysql.connector.Error as error:
            print(error)
            return error

    def delete_comment(self, id):
        try:
            statement = """ DELETE FROM comments
                            WHERE commentID = (%s)
                        """
            self.cursor.execute(statement, id)
        except mysql.connector.Error as error:
            print(error)
            return error

    def get_comments_by_contentID(self, id):
        try:
            self.cursor.execute("SELECT * FROM comments WHERE content_contentID=(%s) ORDER BY time DESC", (id,))
            result = self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(error)
        return result

    def get_comment_by_id(self, id):
        try:
            self.cursor.execute("SELECT * FROM comments WHERE commentID=(%s)", (id,))
            result = self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(error)
        return result