import config, os
import random, string
from flask import Flask, request, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email


# 配置文件类型
ALLOWED_EXTENSIONS = set(['xls', 'xlsx', 'png', 'jpg'])

app = Flask(__name__)

# 加载配置文件
app.config.from_object(config)

# 输出到客户端的字符串
html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>图片上传</h1>
    <form method=post enctype=multipart/form-data action="/">
         <input type=file name=file>
         <input type=submit value=上传>
    </form>
    '''

# 判断上传的文件类型
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 返回token，用于设置session
@app.route('/token')
def gen_token():
    return ''.join(random.sample(string.ascii_letters + string.digits, 8))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


# 响应根路由
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        print(file)
        print(file.filename.rsplit('.', 1))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = url_for('uploaded_file', filename=filename)
            print(file_url)
            return html + '<br><img src=' + file_url + '>'
    return html


@app.route('/')
def index():
    # return send_from_directory('static','index.html')
    return render_template('index.html', file_url=None)



if __name__ == '__main__':
    app.run()
