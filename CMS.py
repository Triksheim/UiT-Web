from userform import UserForm
from user import User
from contentform import ContentForm
from content import Content
from CMSDB import MyDb
from commentform import CommentForm
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

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'zip'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(username):
    with MyDb() as db:
        user = User(*db.get_user((username,)))
    return user

def send_mail(id, email):
    mail = Mail(app)
    msg = Message('Aktiver din bruker', sender='tri032@uit.no', recipients=[email])
    msg.body = 'Plain text body'
    msg.html = '<b>Bekreft epostadresse </b>' + '<a href="127.0.0.1:5000/activate?id=' + id + '">Klikk her</a>'
    with app.app_context():
      mail.send(msg)

def get_content_by_type(mimetype):
    if current_user.is_active:
        try:      
            with MyDb() as db:
                result = db.get_all_content_by_type(mimetype)
                contents = [Content(*x) for x in result]
            return contents
        except:
            print("nothing")
            return ""
    else:
        try:      
            with MyDb() as db:
                result = db.get_all_open_content_by_type(mimetype)
                contents = [Content(*x) for x in result]
            return contents
        except:
            return ""

@app.route('/', methods = ["GET", "POST"])
def front():
    return render_template('base.html')


@app.route('/register', methods = ["GET", "POST"])
def register():
    form = UserForm(request.form)
    
    if request.method == "POST" and form.validate():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        firstname = form.firstname.data
        lastname = form.lastname.data
        user_uuid = str(uuid.uuid1())
        activated = 0
        user = (username, email, password, firstname, lastname, user_uuid, activated)
        try:
            with MyDb() as db:
                error = db.add_new_user(user)
                if error:
                    if 'PRIMARY' in error.msg:
                        return render_template('register.html', form = form, error = 'Brukernavn allerede i bruk')
                    elif 'email_UNIQUE' in error.msg:
                        return render_template('register.html', form = form, error = 'Epostadresse allerede i bruk')
                        
        except:
            print("failed adding user")
            return redirect(url_for('front', _external=True))

        try:
            send_mail(user_uuid, email)
            return render_template('base.html', email = email)
        except:
            print("failed sending mail")
            return redirect(url_for('front', _external=True))       
    else:   
        return render_template('register.html', form = form)


@app.route('/activate', methods = ["GET"])
def activate_user():
    id = request.args.get('id')

    if id:
        try:
            with MyDb() as db:
                db.activate_user((id,))
                return render_template('base.html', activated = True)
        except:
            return redirect(url_for('front', _external=True))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        try:
            with MyDb() as db:
                user = db.get_user((username,))
                if user:
                    user = User(*user)
                    if user.activated == 1:
                        if user.check_password(password):
                            login_user(user, remember=True)
                return redirect(url_for('front', _external=True))
        except:
            return redirect(url_for('front', _external=True))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def select_file():
    content_form = ContentForm(request.form)
    is_file_selected = request.args.get('file_selected')

    if  request.method == "GET":
        return render_template('upload.html', content = content_form)
    
    if  request.method == "POST":
        file = request.files['file']
        if allowed_file(file.filename):

            content_form.filename = secure_filename(file.filename)
            content_form.file = file
            content_form.mimetype = file.mimetype
            content_form.filedata = file.read()
            content_form.size = len(content_form.filedata)
            content_form.filedata_base64 = ""
            if 'image' in file.mimetype:
                filedata_base64 = base64.b64encode(content_form.filedata)
                content_form.filedata_base64 = filedata_base64.decode('utf-8')
            
            return render_template('upload.html', content = content_form, file = file)

        else:
            return render_template('upload.html', content = content_form, invalid_file = True)
    else:
        return render_template('upload.html', content = content_form, file = is_file_selected)
    

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
        open = content_form.open.data
        views = 0
        user = current_user.username

        content = (id, code, title, description, upload_date, tags, filename, mimetype, size, open, views, user)
        with MyDb() as db:
            db.upload_content(content)
        return redirect(url_for('content', id = id, _external=True))
    
    content_form.filename = content_form.filename.data
    content_form.filedata = content_form.filedata.data
    content_form.mimetype = content_form.mimetype.data
    content_form.size = content_form.size.data  
    content_form.filedata_base64 = content_form.filedata_base64.data
    return render_template('upload.html', content = content_form, file = True)


@app.route('/content', methods=['GET', 'POST'])
def content():
    id = request.args.get('id')
    comment_form = CommentForm()
    if  current_user.is_active and id:
        try:
            with MyDb() as db:
                db.add_view((id,))
                content = Content(*db.get_content(id))
            with MyDb() as db:
                result = db.get_comments_by_contentID(id)
                comments = [Comment(*x) for x in result]
            return render_template('content.html', content = content, comment_form = comment_form, comments = comments)
        except:
            return redirect(url_for('front', _external=True))
    elif id:
        try:
            with MyDb() as db:
                db.add_view((id,))
                content = Content(*db.get_open_content(id))
            with MyDb() as db:
                result = db.get_comments_by_contentID(id)
                comments = [Comment(*x) for x in result]
            return render_template('content.html', content = content, comments = comments)
        except:
            return redirect(url_for('front', _external=True))

    if current_user.is_active:
        try:      
            with MyDb() as db:
                result = db.get_all_content()
                contents = [Content(*x) for x in result]
            return render_template('content.html', id = id, contents = contents)
        except:
            return redirect(url_for('front', _external=True))
    else:
        try:      
            with MyDb() as db:
                result = db.get_all_open_content()
                contents = [Content(*x) for x in result]
            return render_template('content.html', id = id, contents = contents)
        except:
            return redirect(url_for('front', _external=True))


@app.route('/download/<id>', methods=['GET', 'POST'])
def download_content(id):
    if current_user.is_active and id:
        try:
            with MyDb() as db:
                content = Content(*db.get_content(id))
        except:
            return redirect(url_for('front', _external=True))

    elif id:
        try:
            with MyDb() as db:
                content = Content(*db.get_open_content(id))
        except:
            return redirect(url_for('front', _external=True))

    try:
        response = make_response(content.code)
        response.headers.set('Content-Type', content.mimetype)  
        response.headers.set('Content-Disposition', 'inline', filename = content.filename)
        return response
    except:
        return redirect(url_for('front', _external=True))
    

@app.route('/comment', methods=['POST'])
def add_comment():
    comment_form = CommentForm(request.form)
    if comment_form.validate():
        text = comment_form.text.data
        time = datetime.now()
        user = current_user.username
        contentID = comment_form.contentID.data
        comment = (text, time, user, contentID)
        try:
            with MyDb() as db:
                db.add_new_comment(comment)
        except:
            print("failed adding comment")
        return redirect(url_for('content', id=contentID, _external=True))
    print("failed comment validate")
    return redirect(url_for('front', _external=True))

@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('front', _external=True))


@app.route('/pictures', methods=['GET', 'POST'])
def pictures():
    mimetype = (('image%'),)
    contents = get_content_by_type(mimetype)
    return render_template('content.html', contents = contents)


@app.route('/videos', methods=['GET', 'POST'])
def videos():
    mimetype = (('video%'),)
    contents = get_content_by_type(mimetype)
    return render_template('content.html', contents = contents)

@app.route('/documents', methods=['GET', 'POST'])
def documents():
    mimetype = (('application%'),)
    contents = get_content_by_type(mimetype)
    return render_template('content.html', contents = contents)

@app.route('/search', methods=['GET', 'POST'])
def search():
    return redirect(url_for('front', _external=True))


if __name__ == "__main__":
    app.run(debug=True)