from pydoc import describe
from CMSDB import MyDb
from forms import UserForm, ContentForm, CommentForm, SearchForm, LoginForm
from user import User
from content import Content
from comment import Comment

from flask import Flask, redirect, render_template, request, url_for, make_response
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_login import login_required
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import date, datetime
import secrets
import base64
import uuid

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtpserver.uit.no'
app.config['MAIL_PORT'] = 587
app.config['MAX_CONTENT_LENGTH'] = 16777215 * 2
app.secret_key = secrets.token_urlsafe(16)

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)

ALLOWED_EXTENSIONS = {'txt', 'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'zip', 'py'}

# Checks if filename got valid extension.
# Copy from dte-2509-webapp-v22\file_upload\fileUpload_db.py
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Loads user before every request to check login status.
@login_manager.user_loader
def load_user(username):
    with MyDb() as db:
        user = User(*db.get_user(username))
    return user

# Sends email with activation code
def send_mail(id, email):
    mail = Mail(app)
    msg = Message('Aktiver din bruker', sender='tri032@uit.no', recipients=[email])
    msg.body = 'Plain text body'
    msg.html = '<b>Bekreft epostadresse </b>' + '<a href="127.0.0.1:5000/activate?id=' + id + '">Klikk her</a>'
    with app.app_context():
      mail.send(msg)

# Increments view count for contentID
def increment_views(id):
    try:
        with MyDb() as db:
            db.add_view(id) 
    except:
        return

# Returns content from db by ContentID.
def get_content_by_id(id):
    if current_user.is_active:
        restriction = 'members'
    else:
        restriction = 'open'
    try:
        with MyDb() as db:
            content = Content(*db.get_content(id,restriction))
        return content
    except:
        return 
        
# Returns all contents from db by mimetype. 
def get_content_by_type(mimetype):
    if current_user.is_active:
        restriction = 'members'
    else:
        restriction = 'open'
    try:
        if 'application%' in mimetype or 'text%' in mimetype:
            with MyDb() as db:
                result = db.get_all_content_by_type_docs(mimetype, restriction)
                contents = [Content(*x) for x in result]
        else:
            with MyDb() as db:
                result = db.get_all_content_by_type(mimetype, restriction)
                contents = [Content(*x) for x in result]
        return contents
    except:
        return ""
   
# Returns all contents from db by mimetype ordered by a column.
def get_content_by_type_ordered(mimetype, column):
    if current_user.is_active:
        restriction = 'members'
    else:
        restriction = 'open'
    try:     
        if 'application%' in mimetype or 'text%' in mimetype:
            with MyDb() as db:
                    if column == 'date':
                        result = db.get_all_content_by_type_docs(mimetype, restriction)
                    elif column == 'views':
                        result = db.get_all_content_by_type_order_views_docs(mimetype, restriction)
                    contents = [Content(*x) for x in result]
        else:
            with MyDb() as db:
                if column == 'date':
                    result = db.get_all_content_by_type(mimetype, restriction)
                elif column == 'views':
                    result = db.get_all_content_by_type_order_views(mimetype, restriction)
                contents = [Content(*x) for x in result]
        return contents
    except:
        return ""

# Returns all contents from db.
def get_all_content():
    if current_user.is_active:
        restriction = 'members'
    else:
        restriction = 'open'
    try:      
        with MyDb() as db:
            result = db.get_all_content(restriction)
            contents = [Content(*x) for x in result]
        return contents
    except:
        return ""   
   
# Returns all contents ordered by a column.
def get_all_content_ordered(column):
    if current_user.is_active:
        restriction = 'members'
    else:
        restriction = 'open'
    try:      
        with MyDb() as db:
            if column == 'date':
                result = db.get_all_content(restriction)
            elif column == 'views':
                result = db.get_all_content_order_views(restriction)
            contents = [Content(*x) for x in result]
        return contents
    except:
        return ""   
    
# Returns all comments for given contentID
def get_comments_by_contentID(id):
    try:
        with MyDb() as db:
            result = db.get_comments_by_contentID(id)
            comments = [Comment(*x) for x in result]
            return comments
    except:
        return ""

# Returns comment by id
def get_comment_by_id(id):
    try:
        with MyDb() as db:
            comment = Comment(*db.get_comment_by_id(id))
            return comment
    except:
        return ""

# Frontpage
@app.route('/', methods = ["GET", "POST"])
def front():
    return render_template('base.html', login_form = LoginForm(), search_form = SearchForm())

# Register a new user
@app.route('/register', methods = ["GET", "POST"])
def register():
    form = UserForm(request.form)
    
    if request.method == "POST" and form.validate():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data) #hashes password with sha-256
        firstname = form.firstname.data
        lastname = form.lastname.data
        user_uuid = str(uuid.uuid1())   #generates a unique id 
        activated = 0
        user = (username, email, password, firstname, lastname, user_uuid, activated)
        try:
            with MyDb() as db:
                error = db.add_new_user(user)
                if error:
                    if 'PRIMARY' in error.msg:
                        return render_template('register.html', login_form = LoginForm(), search_form = SearchForm(), form = form, error = 'Brukernavn allerede i bruk')
                    elif 'email_UNIQUE' in error.msg:
                        return render_template('register.html', login_form = LoginForm(), search_form = SearchForm(), form = form, error = 'Epostadresse allerede i bruk')          
        except:
            print("failed adding user")
            return redirect(url_for('front', _external=True))

        # Sends activation email after user is successfully added to db
        try:
            send_mail(user_uuid, email)
            return render_template('base.html', login_form = LoginForm(), search_form = SearchForm(), email = email)
        except:
            print("failed sending mail")
            return redirect(url_for('front', _external=True))       
    else:   
        return render_template('register.html', login_form = LoginForm(), search_form = SearchForm(), form = form)

# Activates user account when id == user uuid
@app.route('/activate', methods = ["GET"])
def activate_user():
    id = request.args.get('id')
    if id:
        try:
            with MyDb() as db:
                db.activate_user((id,))
                return render_template('base.html', login_form = LoginForm(), search_form = SearchForm(), activated = True)
        except:
            return redirect(url_for('front', _external=True))
    return redirect(url_for('front', _external=True))

# Login when user pw hash matches db hash and user is activated
@app.route('/login', methods=["POST"])
def login():
    login_form = LoginForm(request.form)
    if login_form.validate():
        username = request.form['username']
        password = request.form['password']
        try:
            with MyDb() as db:
                user = db.get_user(username)
                if user:
                    user = User(*user)
                    if user.activated == 1:
                        if user.check_password(password):
                            login_user(user, remember=True)
                return redirect(url_for('front', _external=True))
        except:
            return redirect(url_for('front', _external=True))
    return redirect(url_for('front', _external=True))

# Logout user and return to frontpage
@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('front', _external=True))

# Add file and information for content upload
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def select_file():
    content_form = ContentForm(request.form)
    is_file_selected = request.args.get('file_selected')

    if  request.method == "GET":
        return render_template('upload.html', login_form = LoginForm(), search_form = SearchForm(), content = content_form)
    
    if  request.method == "POST":
        file = request.files['file']
        if allowed_file(file.filename):
            content_form.filename = secure_filename(file.filename)
            content_form.file = file
            content_form.mimetype = file.mimetype
            content_form.filedata = file.read()
            content_form.size = len(content_form.filedata)
            content_form.filedata_base64 = None
            if 'image' in file.mimetype:
                filedata_base64 = base64.b64encode(content_form.filedata)
                content_form.filedata_base64 = filedata_base64.decode('utf-8')
            return render_template('upload.html', login_form = LoginForm(), search_form = SearchForm(), content = content_form, file = True)
        else:
            return render_template('upload.html', login_form = LoginForm(), search_form = SearchForm(), content = content_form, invalid_file = True)
    else:
        return render_template('upload.html', login_form = LoginForm(), search_form = SearchForm(), content = content_form, file = is_file_selected)
    
# Adds content to db if form is validated
@app.route('/uploading', methods=['GET', 'POST'])
@login_required
def upload_file():
    content_form = ContentForm(request.form)

    if request.method == "POST" and content_form.validate():
        id = str(uuid.uuid1())
        code = eval(content_form.filedata.data)
        title = content_form.title.data
        description = content_form.description.data
        upload_date = date.today()
        tags = content_form.tags.data
        filename = content_form.filename.data
        mimetype = content_form.mimetype.data
        size = len(code)
        restriction = content_form.restriction.data
        views = 0
        user = current_user.username

        content = (id, code, title, description, upload_date, tags, filename, mimetype, size, restriction, views, user)
        with MyDb() as db:
            db.upload_content(content)
        return redirect(url_for('content', login_form = LoginForm(), search_form = SearchForm(), id = id, _external=True))
    
    content_form.filename = content_form.filename.data
    content_form.filedata = content_form.filedata.data
    content_form.mimetype = content_form.mimetype.data
    content_form.size = content_form.size.data  
    content_form.filedata_base64 = content_form.filedata_base64.data
    return render_template('upload.html', content = content_form, file = True)

# Edit content details
@app.route('/edit', methods=['POST'])
@login_required
def edit_content():
    content_form = ContentForm(request.form)
    content_form.owner = content_form.owner.data
    if current_user.username == content_form.owner or current_user.username == 'admin':
        content_form.filename = content_form.filename.data
        content_form.mimetype = content_form.mimetype.data
        content_form.size = content_form.size.data
        content_form.contentID = content_form.contentID.data
        return render_template('edit.html', search_form = SearchForm(), content = content_form)
    return redirect(url_for('front', _external=True))

# Update content details in db if form is validated
@app.route('/edit_update', methods=['POST'])
@login_required
def edit_update():
    content_form = ContentForm(request.form)
    if current_user.username == content_form.owner.data or current_user.username == 'admin':
        if content_form.validate():
            title = content_form.title.data
            description = content_form.description.data
            tags = content_form.tags.data
            restriction = content_form.restriction.data
            contentID = content_form.contentID.data
            content_edit = (title, description, tags, restriction, contentID)
            with MyDb() as db:
                db.edit_content(content_edit)
                return redirect(url_for('content', id=contentID, _external=True))
        else:
            content_form.filename = content_form.filename.data
            content_form.mimetype = content_form.mimetype.data
            content_form.size = content_form.size.data 
            contentID = content_form.contentID.data 
            content_form.owner = content_form.owner.data
            return render_template('edit.html', search_form = SearchForm(), content = content_form)
    return redirect(url_for('front', _external=True))

# Displays a single content when id is given. Else shows all contents.
@app.route('/content', methods=['GET', 'POST'])
def content():
    id = request.args.get('id')
    delete_commentID = request.args.get('delete_commentID')
    if id:
        try:
            increment_views(id)
            content = get_content_by_id(id)
            comments = get_comments_by_contentID(id)
            if content:
                return render_template('content.html', login_form = LoginForm(), search_form = SearchForm(), content = content,
                    comments = comments, comment_form = CommentForm(), delete_commentID = delete_commentID, content_form = ContentForm())
            else:
                print("no content")
                return redirect(url_for('front', _external=True))
        except:
            print("failed loading content")
            return render_template('content.html', login_form = LoginForm(), search_form = SearchForm(), content = content,
                    comments = comments, comment_form = CommentForm(), delete_commentID = delete_commentID)
    else:
        try:
            order = request.form
            if order:
                column = order['column']
                contents = get_all_content_ordered(column)
            else:
                contents = get_all_content()
            return render_template('content.html', login_form = LoginForm(), search_form = SearchForm(), contents = contents)
        except:
            return redirect(url_for('front', _external=True))

# Downloads content by id to display in browser using make_response.
@app.route('/download/<id>', methods=['GET', 'POST'])
def download_content(id):
    if id:
        content = get_content_by_id(id)
        try:
            response = make_response(content.code)
            response.headers.set('Content-Type', content.mimetype)  
            response.headers.set('Content-Disposition', 'inline', filename = content.filename)
            return response
        except:
            return redirect(url_for('front', _external=True))
    return redirect(url_for('front', _external=True))
    
# Adds comment linked to contentID to db when form is validated
@app.route('/comment', methods=['POST'])
def add_comment():
    comment_form = CommentForm(request.form)
    if comment_form.validate():
        commentID = str(uuid.uuid1())
        text = comment_form.text.data
        time = datetime.now()
        user = current_user.username
        contentID = comment_form.contentID.data
        comment = (commentID,text, time, user, contentID)
        try:
            with MyDb() as db:
                db.add_new_comment(comment)
        except:
            print("failed adding comment")
        return redirect(url_for('content', id=contentID, _external=True))
    print("failed comment validate")
    return redirect(url_for('front', _external=True))

# Deletes a comment by id
@app.route('/delete_comment', methods=['GET','POST'])
@login_required
def delete_comment():
    id = request.args.get('id')
    contentID = request.args.get('contentID')
    if id:
        try:
            comment = get_comment_by_id(id)
            if current_user.username == 'admin' or current_user.username == comment.users_username:
                with MyDb() as db:
                    db.delete_comment(id)
                    return redirect(url_for('content', id=contentID, _external=True))
        except:
            return redirect(url_for('front', _external=True))
    return redirect(url_for('front', _external=True))

# Displays only images
@app.route('/pictures', methods=['GET', 'POST'])
def pictures():
    mimetype = 'image%'
    order = request.form
    if order:
        column = order['column']
        contents = get_content_by_type_ordered(mimetype, column)
    else:
        contents = get_content_by_type(mimetype)
    return render_template('content.html', login_form = LoginForm(), search_form = SearchForm(), contents = contents)

# Displays only videos
@app.route('/videos', methods=['GET', 'POST'])
def videos():
    mimetype = 'video%'
    order = request.form
    if order:
        column = order['column']
        contents = get_content_by_type_ordered(mimetype, column)
    else:
        contents = get_content_by_type(mimetype)
    return render_template('content.html', login_form = LoginForm(), search_form = SearchForm(), contents = contents)

# Displays only docs/text/applications
@app.route('/documents', methods=['GET', 'POST'])
def documents():
    mimetype = ('application%', 'text%')
    order = request.form
    if order:
        column = order['column']
        contents = get_content_by_type_ordered(mimetype, column)
    else:
        contents = get_content_by_type(mimetype)
    return render_template('content.html', login_form = LoginForm(), search_form = SearchForm(), contents = contents)

# Search for content by text. Returns content with part of 'text' in title or tags. Or exact match for username
@app.route('/search', methods=['POST'])
def search():
    search_form = SearchForm(request.form)
    if search_form:
        try:
            text = search_form.search_text.data.lower()
            all_contents = get_all_content()
            found_content = []
            for content in all_contents:
                if text in content.tags.lower() or text in content.title.lower() or  text == content.users_username.lower():
                    found_content.append(content)
            return render_template('content.html', login_form = LoginForm(), search_form = search_form, contents = found_content)
        except:
            return redirect(url_for('front', _external=True))
    return redirect(url_for('front', _external=True))


if __name__ == "__main__":
    app.run(debug=True)