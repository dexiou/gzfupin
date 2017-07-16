# 配置DEBUG模式，测试阶段热部署
DEBUG = True
# 配置上传目录，可能变更到应用目录下
UPLOAD_FOLDER = '/tmp/uploads'
# 配置上传目录，可能变更到应用目录下
DOWNLOAD_FOLDER = '/tmp/downloads'
# 最大文件体积
MAX_CONTENT_LENGTH = 2 * 1024 * 1024
# 预防跨站伪造
SECRET_KEY = 'P4S5W0RD'
# 数据库连接字符串
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Hello123@127.0.0.1:3306/jzfp'
# 数据自动提交
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
