# flask是一个使用python编写的轻量级Web应用框架。
# 本项目中Flask 用于设置 Web 服务器，管理 URL 路由，
# 并处理 HTTP 请求和响应。通过定义路由和视图函数，
# Flask 可以监听来自前端（如浏览器）的请求，并返回所请求的数据或页面。

# 从flask中导入两个重要组件：Flask、jsonify
# 通过实例化Flask类，可以创建一个应用实例，允许定义路由、处理请求
# jsonify用于将数据结构转换成JSON格式响应

from flask import Flask, jsonify
# 导入Flask的一个扩展：Flask-CORS
# 他用于处理跨资源共享（CORS）问题
# 通过使用Flask-CORS，确保前端应用能够安全地从Flask后端获取数据，无论他们部署在何处。
from flask_cors import CORS
# 导入Flask的另一个扩展：APScheduler。
# 他用于在应用中安排和管理周期性任务，定时执行任务
from flask_apscheduler import APScheduler
# 将位于utils文件内的server_status_checker函数导入
from utils.server_status_checker import update_server_statuses


# 定义一个名为Config的类
class Config:
    # 启动APScheduler的Web API，允许通过HTTP请求监控和管理调度器中的任务
    # 这样就可以监控任务：通过API查询任务是否在运行、下一次运行时间
    # 管理任务：动态地添加、修改或删除调度任务
    SCHEDULER_API_ENABLED = True
    # 设置调度器的时区为UTC，UTC是一个参考国际参考时间，更多用于跨时区的服务器
    # 使得服务器物理位置无论在哪，任务调度时间都一致
    SCHEDULER_TIMEZONE = "UTC"  # Ensure you set the correct timezone for your needs

# 创建一个Flask应用的实例
app = Flask(__name__)
# 加载配置，config就是加载Config启动的配置到app.config字典中，之后就可以通过app.config['CONFIG_NAME']访问这些配置
app.config.from_object(Config())

# 在Flask应用中启用跨资源共享（CORS）：允许API接受来自不同源的请求
# 项目中使用 CORS(app) 是为了确保前端应用可以无障碍地调用后端 API
CORS(app)

# 定义服务器列表
servers = [
    {'host': 'hostname', 'port': 22, 'username': 'usn', 'password': 'psw'},
    # 添加其他服务器
]

# 全局字典来存储服务器状态
server_statuses = {}
# 创建一个APScheduler的调度器实例
scheduler = APScheduler()
# 将APScheduler与Flask应用进行集成，这样就可以访问app.config读取配置，包括上面定义的启动API以及定义时区
scheduler.init_app(app)
# 启动调度器
scheduler.start()

# 获得服务器状态函数
def fetch_server_status():
    # 函数内想修改外部定义的变量，需要global一下
    global server_statuses
    # 赋值服务器状态
    server_statuses = update_server_statuses(servers)
    # 状态更新后，打印到Terminal
    print("Updated server statuses")

# 设置定时任务，每30秒更新一次服务器状态
# id为任务指定的唯一标识符
# trigger='interval'触发方式为间隔触发
scheduler.add_job(id='Fetch Server Status', func=fetch_server_status, trigger='interval', seconds=15)
# 定义一个路由，将一个URL路径映射到一个视图函数（status）
# 当HTTP请求这个特定路由时，关联的视图函数（status）将被调用来处理请求并返回相应
# 定当script.js中请求 http://10.214.153.34:5000/api/status 时，应该调用哪个函数（status）。
#简单点说，这个路由紧随的函数，就是关联的函数，里面的参数，就规定了前端需要访问的路由地址（ip+这里定义的地址）
@app.route('/api/status') 
def status():
    # 直接返回最近一次更新的服务器状态，并转成JSON的格式返回
    # jsonify是Flask提供的一个辅助函数，用于将Python字典或者列表转换为JSON格式
    return jsonify(server_statuses)

if __name__ == '__main__':
    # app.run（）是Flask内置开发服务器的启动命令
    # debug=true,开启调试模式：在调试模式下，Flask 会在应用中显示详细的错误页面，并在代码更改时自动重载应用。
    # port=5000：设置服务器监听的端口号
    # host='0.0.0.0':接受所有公共 IP 地址的访问，这使得服务器可以从任何设备上通过网络访问。
    app.run(debug=True, port=5000,host='0.0.0.0')
