from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType
from pyecharts.faker import Faker
import time
import pandas as pd

# 创建Flask实例
app = Flask(__name__, static_url_path='/')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/flask_demo'  # 这里替换为自己的用户名和密码
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# 创建用户信息类, 映射到数据库中的user表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


# 初始化数据库
with app.app_context():
    # 调用 Flask-SQLAlchemy 的方法，根据定义的模型类（如 User）在数据库中创建对应的表。如果表已经存在，则不会重复创建。
    db.create_all()


# 配置“/”访问路由
@app.route('/')
def hello_world():
    return render_template('register-2.html')

# 配置注册路由
@app.route("/add_user", methods=['POST'])
def register():
    username = request.form.get("registerUsername")
    email = request.form.get("registerEmail")
    password = request.form.get("registerPassword")
    print(username, email, password)
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return render_template("login-2.html")

@app.route('/login', methods=['POST'])
def submit():
    email = request.form.get('loginEmail')
    password = request.form.get('loginPassword')
    user = User.query.filter_by(email=email).first()
    if user is not None and user.password == password:
        return render_template('index.html')
    else:
        return render_template('login-2.html', login_fail_info="用户名或密码错误, 请重新输入!")

@app.route('/sign_in')
def sign_in():
    return render_template('login-2.html')

def bar_base():
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(Faker.choose())
            .add_yaxis("商家A", Faker.values())
            .add_yaxis("商家B", Faker.values())
        # .set_global_opts(title_opts=opts.TitleOpts(title="主标题", subtitle="副标题"))
    )
    return bar
@app.route("/barChart")
def get_bar_chart():
    c = bar_base()
    return c.dump_options_with_quotes()

def bar_2():
    data = pd.read_excel('static/data/商家A和商家B的各类商品的销售数据.xlsx',
                         index_col='商家')
    init_opts = opts.InitOpts(width='800px', height='400px')
    print(data)
    time.sleep(5)
    bar = (
        Bar(init_opts)
            .add_xaxis(data.columns.tolist())
            .add_yaxis('商家A', data.loc['商家A'].tolist())
            .add_yaxis('商家B', data.loc['商家B'].tolist())
            .set_global_opts(title_opts=opts.TitleOpts(title='指定标记点的柱形图'))
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_='max', name='最大值'),
                    opts.MarkPointItem(type_='min', name='最小值'),
                ]
            )
        )
    )
    return bar
@app.route("/barChart2")
def get_bar_chart2():
    c = bar_2()
    return c.dump_options_with_quotes()

if __name__ == '__main__':
    app.run(debug=True)