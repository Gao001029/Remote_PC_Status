from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_apscheduler import APScheduler
from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import os
from utils.server_status_checker import update_server_statuses  # 确保这个函数在 utils/server_status_checker.py 中定义

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "UTC"

app = Flask(__name__, static_folder='../../frontend/static', static_url_path='/static')
app.config.from_object(Config())
CORS(app, resources={r"/*": {"origins": "*"}})

DATABASE_URI = 'mysql+pymysql://root:root@localhost/appointment_db'
engine = create_engine(DATABASE_URI, pool_pre_ping=True, pool_size=10, max_overflow=20)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db_session():
    return Session()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

servers = [
    # 添加其他服务器
]
server_statuses = {}

def fetch_server_status():
    global server_statuses
    server_statuses = update_server_statuses(servers)  # 确保这个函数的实现符合你的需求
    print("Updated server statuses")

scheduler.add_job(id='Fetch Server Status', func=fetch_server_status, trigger='interval', seconds=15)

@app.route('/api/status')
def status():
    return jsonify(server_statuses)

@app.route('/appointments', methods=['GET'])
def get_appointments():
    session = get_db_session()
    server_id = request.args.get('server_id')
    try:
        # 检查查询条件，去掉 start_time 的过滤，确保不遗漏数据
        result = session.execute(
            text("SELECT * FROM appointments WHERE server_id = :server_id AND end_time>=NOW() ORDER BY start_time"),
            {'server_id': server_id}
        ).fetchall()

        appointments = [{"id": row[0], "start_time": row[2], "end_time": row[3], "name": row[4], "server_id": row[1]} for row in result]
        
        # 调试输出，检查查询结果
        # print(f"查询结果: {appointments}")

        return jsonify(appointments)
    except exc.SQLAlchemyError as e:
        print(f"查询数据库失败: {e}")
        return jsonify({"error": "查询数据库失败"}), 500
    finally:
        session.close()


@app.route('/appointments', methods=['POST'])
def create_appointment():
    session = get_db_session()
    data = request.json
    start_time = datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M')
    name = data['name']
    server_id = data['server_id']

    if start_time >= end_time:
        return jsonify({"error": "预约开始时间不能晚于预约结束时间"}), 400

    # 检查预约时间段是否与现有预约冲突
    try:
        conflict_result = session.execute(
            text("SELECT * FROM appointments WHERE server_id = :server_id AND NOT (end_time <= :start_time OR start_time >= :end_time)"),
            {'start_time': start_time, 'end_time': end_time, 'server_id': server_id}
        ).fetchall()

        if conflict_result:
            return jsonify({"error": "预约时间冲突，请选择其他时间段"}), 409

        session.execute(
            text("INSERT INTO appointments (server_id, start_time, end_time, name) VALUES (:server_id, :start_time, :end_time, :name)"),
            {'server_id': server_id, 'start_time': start_time, 'end_time': end_time, 'name': name}
        )
        session.commit()
        return jsonify({"success": True})
    except exc.SQLAlchemyError as e:
        print(f"插入数据库失败: {e}")
        session.rollback()
        return jsonify({"error": "插入数据库失败"}), 500
    finally:
        session.close()

@app.route('/appointments/<int:id>', methods=['DELETE'])
def cancel_appointment(id):
    session = get_db_session()
    try:
        session.execute(
            text("DELETE FROM appointments WHERE id = :id"),
            {'id': id}
        )
        session.commit()
        return jsonify({"success": True})
    except exc.SQLAlchemyError as e:
        print(f"取消预约失败: {e}")
        session.rollback()
        return jsonify({"error": "取消预约失败"}), 500
    finally:
        session.close()

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/book.html')
def serve_booking():
    return send_from_directory(app.static_folder, 'book.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
