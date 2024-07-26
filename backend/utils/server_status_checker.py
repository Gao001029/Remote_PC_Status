# 引入两个库
# paramiko用于远程执行命令、上传、下载文件，项目中用于建立SSH连接到指定的服务器
import paramiko
# threading用于多线程编程，多线程可以并行处理多个任务，有提升程序执行效率
import threading
import re

def parse_fsutil_output(output): 
    """处理Disk的格式返回百分数"""
    lines = output.strip().split('\n')    
    # Extract numbers from the output
    total_free_bytes = int(re.findall(r'\d+', lines[0].replace(',', ''))[0])
    total_bytes = int(re.findall(r'\d+', lines[1].replace(',', ''))[0])    
    used_bytes = total_bytes - total_free_bytes
    used_percentage = round((used_bytes / total_bytes) * 100)
    used_percentage = f"{used_percentage}%"
    return used_percentage

def ssh_command(ssh, command):
    """执行单个SSH命令并返回输出"""
    stdin, stdout, stderr = ssh.exec_command(command)
    if stdout:
        return stdout.read().decode()
    else:
        return None
# def get_status_linux(users_info):
#     """处理linux得到的users_info格式问题并返回"""
#     users = []
#     lines = users_info.strip().split('\n')
#     for line in lines:
#         parts = line.split()
#         if len(parts) >= 5:
#             user = parts[0]
#             source = parts[4] if len(parts) > 4 else 'Local'
#             login_type = 'Local' if 'tmux' in source else 'Remote'
#             # if (user,login_type) not in users:
#                 # users.append((user, login_type))  
#             users.append((user, login_type))      
#     status = 'Available\n' if not users else ''
#     for user, login_type in users:
#         status += f'Occupied by {user} {login_type} connection\n'
#     return status
     
def get_status_windows(users_info_all):
    """处理windows得到的users_info格式问题并返回"""
    users = [] # 存储所有在线用户
    lines = users_info_all.strip().split('\n')[1:] # 分行存储
    for line in lines:
        parts = line.split()
        if len(parts) >= 5:
            user, login_type = parts[0], 'Remote' if 'rdp-tcp' in parts[1] else 'Local'
        users.append((user, login_type))
    users_info = '' # 命名一个字符串，存储状态         
    if users:   # 形成状态字符串
        for u in users:
            users_info = users_info + 'Occupied '  + ' by '+ u[0] + ' ' + u[1] + ' connection\n'
    else:
        users_info = 'Available\n'
    return users_info
def get_logged_in_users(host, port, username, password, result_dict):
    # 创建一个SSHClient类的实例，这个实例属于Paramiko模块
    ssh = paramiko.SSHClient()
    # 设置缺失主机密钥策略，AutoAddPolicy()表示自动接收未知的主机密钥。
    # 就是不需要点yes，可以输入ip、name、psw正确后，直接登录
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port=port, username=username, password=password)
        # 根据用户名的最后一个字符判断使用的命令        
        if host[-1] == 'w':
            users_info_all = ssh_command(ssh,'query user')
            users_info = get_status_windows(users_info_all)
            status = 'Available'

            # disk_data = ssh_command(ssh,f'fsutil volume diskfree C:') # 获取windows下命令输出
            # disk_usage = parse_fsutil_output(disk_data) # 将输出格式化，截取百分数

            # disk_data_d = ssh_command(ssh,f'fsutil volume diskfree D:') # 获取windows下命令输出
            # disk_usage_d = parse_fsutil_output(disk_data_d) # 将输出格式化，截取百分数

            # # 判断是否有E盘
            # drive_info = ssh_command(ssh,f'fsutil fsinfo drives')
            # if 'E:' in drive_info:
            #     disk_data_e = ssh_command(ssh,f'fsutil volume diskfree E:') # 获取windows下命令输出
            #     disk_usage_e = parse_fsutil_output(disk_data_e) # 将输出格式化，截取百分数
            # else:
            #     disk_usage_e =None            
            result_dict[host] = {
                'status':status.strip(), # 去除字符串开头和结尾的空白字符
                'users_info':users_info.strip()
                # 'disk':disk_usage,
                # 'disk_d':disk_usage_d,
                # 'dick_e':disk_usage_e
            }
        elif host[-1] == 'u':
            docker_id = ssh_command(ssh,"docker ps --format '{{.ID}}'") # 获取Docker信息
            docker_image = ssh_command(ssh,"docker ps --format '{{.Image}}'") # 获取Docker信息
            docker_status = ssh_command(ssh,"docker ps --format '{{.Status}}'") # 获取Docker信息
            # status = get_status_linux(users_info)  
            status = 'Available'
            # 获取CPU使用率
            cpu_usage = ssh_command(ssh, "top -bn1 | grep \"Cpu(s)\" | sed \"s/.*, *\\([0-9.]*\\)%* id.*/\\1/\" | awk '{print 100 - $1}'")
            # 获取RAM使用率
            ram_usage = ssh_command(ssh, "free | grep Mem | awk '{print int($3/$2 * 100.0)}'")
            # 获取磁盘使用率
            root = ssh_command(ssh, "df -h | awk '$6 == \"/\" {print $5}'")
            data1 = ssh_command(ssh, "df -h | awk '$6 == \"/DATA1\" {print $5}'")
            data2 = ssh_command(ssh, "df -h | awk '$6 == \"/DATA2\" {print $5}'")
            data3 = ssh_command(ssh, "df -h | awk '$6 == \"/DATA3\" {print $5}'")
            data4 = ssh_command(ssh, "df -h | awk '$6 == \"/DATA4\" {print $5}'")
            if data4 == "":
                data4 = "None"
            result_dict[host] = {
                'status':status, # 去除字符串开头和结尾的空白字符
                'docker_id':docker_id.strip(),
                'docker_image':docker_image.strip(),
                'docker_status':docker_status.strip(),
                'cpu':cpu_usage.strip() + '%',
                'ram':ram_usage.strip() + '%',
                'root':root.strip(),
                'data1':data1.strip(),
                'data2':data2.strip(),
                'data3':data3.strip(),
                'data4':data4.strip()
            }
    except Exception as e:
        print(f"An error occurred while connecting to {host}: {e}")
        result_dict[host] = {
                'status':'Unavailable'
            }
    finally:
        ssh.close()
        # 存储结果到字典，使得每个服务器的状态都能通过其主机地址（host）作为键来获取
 
def update_server_statuses(servers):
    # 创建字典，用于get_logged_in_users传参，保存host对应的status
    server_statuses = {} 
    threads = []

    for server in servers:
        # 创建新的线程对象
        thread = threading.Thread(target=get_logged_in_users, args=(server['host'], server['port'], server['username'], server['password'], server_statuses))
        threads.append(thread)
        thread.start() # 启动线程

    # 确保所有启动的线程都已完成其任务，之后主线程才继续执行，因为你不能线程没运行完，就直接return server_statuses
    # 目的是防止子线程未结束，主线程结束
    for thread in threads:
        thread.join()

    return server_statuses
