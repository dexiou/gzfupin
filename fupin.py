import config, os
import random, string
from flask import Flask, request, url_for, send_from_directory, render_template, session, redirect
from werkzeug.utils import secure_filename
import xlrd, xlwt, pymysql,time
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email



# 配置文件类型
ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])

app = Flask(__name__)
# 加载配置文件
app.config.from_object(config)
db = SQLAlchemy(app)
update_sql = 'update t_user, t_gz ' + \
             'set t_user.pkhsx = t_gz.pkhsx, t_user.tpzt = t_gz.tpzt ' + \
             'where t_user.sfzh = t_gz.pkhsfzh and ' + \
             't_user.token = "{0}"'

EXCEL_COLUMN_NAME = ['序号','身份证号','姓名','贫困户属性','脱贫状态']

class User(db.Model):
    # 定义表名
    __tablename__ = 't_user'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True)
    sfzh = db.Column(db.String(18), unique=False)
    xm = db.Column(db.String(20), unique=False)
    pkhsx = db.Column(db.String(20), unique=False)
    tpzt = db.Column(db.String(20), unique=False)
    token = db.Column(db.String(8), unique=False)

    def __init__(self, sfzh, xm, token):
        self.sfzh = sfzh
        self.xm = xm
        self.token = token

    #repr()方法显示一个可读字符串，虽然不是完全必要，不过用于调试和测试还是很不错的。
    @property
    def __repr__(self):
        return '<User {}> '.format(self.sfzh)



# 输出到客户端的字符串
error_html = '''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
    <meta charset="UTF-8">
    <title>出错信息</title>
    <link rel="stylesheet" type="text/css" href="/static/semantic.min.css" />
    <script type="text/javascript" src="/static/jquery-3.2.1.min.js" ></script>
    <script type="text/javascript" src="/static/semantic.min.js" ></script>
    </head>
    <body>
    <div class="ui negative message">
    <i class="close icon"></i>
     <div class="header">
    {title}
    </div>
    <p>{error}</p></div>
    </body>
    </html>
    '''

# 判断上传的文件类型
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 返回token，用于设置session
@app.route('/token')
def gen_token():
    return ''.join(random.sample(string.ascii_letters + string.digits, 8))

# 比较token值
def compare_tokens(t1, t2):
    return t1 == t2


# 列表写入xls文化，讲究的是
def list_to_excel(user_list):
    workbook = xlwt.Workbook()
    user_sheet = workbook.add_sheet('核查结果', cell_overwrite_ok=True)
    bold_style = xlwt.easyxf('font: bold 1')

    for index, data in enumerate(EXCEL_COLUMN_NAME):
        user_sheet.write(0, index, data, bold_style)

    for i, user_info in enumerate(user_list):
        user_sheet.write(i + 1, 0, i + 1)
        for j in range(len(user_info)-1):
            user_sheet.write(i + 1, j + 1, user_info[j + 1])

    now = time.strftime('%Y%m%d', time.localtime(time.time()))
    filename = now + '_' + session['token'] + '.xls'
    file_full_name = os.path.join(app.config['DOWNLOAD_FOLDER'],filename)
    workbook.save(file_full_name)

    return True, filename


# 读写excel文件
def excel_to_list(xls_filename):
    data = xlrd.open_workbook(xls_filename)
    table = data.sheets()[0]
    rows = table.nrows
    if rows < 1:
        return False, error_html.format(title='表内长度不够', error='请检查一下上传的表是否包括身份证号（第一列）和姓名（第二列）字段')

    token = session['token']
    i = 0
    while i < rows:
        sfzh = table.cell(i,0).value
        xm  = table.cell(i,1).value
        db.session.add(User(sfzh, xm, token))
        i += 1

    db.session.commit()

    db.session.execute(update_sql.format(token))
    users = db.session.execute(User.query.filter_by(token=token))
    return list_to_excel(users)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename)


# 响应根路由,get访问自动导向到首页，只接受post访问
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        token = request.form.get('token','')
        # token校验不一致，会返回错误，通过/token给客户端调用留下处理措施
        if not compare_tokens(token, session['token']):
            return error_html.format(title='操作校验失败', error='未包含必要的token字段')

        # 如果文件符合要求
        if file and allowed_file(file.filename):
            filename = token + secure_filename(file.filename)
            file_abs_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_abs_name)
            # 处理excel文件
            ok, info = excel_to_list(file_abs_name)
            if ok :
                #重新生成token
                token = gen_token()
                return render_template('index.html', file_url=info, token=token)
            else:
                return info
        else:
            return error_html.format(title='文件格式不对', error='仅支持[xls,xlsx]格式的excel文件。')
    return redirect(url_for('index'))


@app.route('/')
def index():
    token = gen_token()
    session['token'] = token
    # return send_from_directory('static','index.html')
    return render_template('index.html', file_url=None, token=token)



if __name__ == '__main__':

    db.create_all()


    app.run()
