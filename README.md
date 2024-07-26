项目目录结构：
  后端（Backend）
    api
      __init__.py: 使api文件夹成为Python模块。
      server_status_api.py: 可能用于获取服务器状态的API。
    utils
      __init__.py: 使utils文件夹成为Python模块。
      server_status_checker.py: 可能用于检查服务器状态的工具。
    main.py: 主程序入口。
  前端（Frontend）
    css
      body.css: 页面主题样式设计。
      footer.css：页面底部样式设计。
      header.css：页面顶部样式设计。
    js
      script.js: JavaScript文件，用于处理前端的交互逻辑。
    index.html: 主页面，用户的访问入口。
    logo.svg:公司log，前端页面设计。

Linux部署项目：
  项目成功运行需要安装项目所需的依赖，我整理到requirement.txt了，你打开terminal后，输入：pip install -r requirements.txt，即可安装txt中列出的全部依赖
  安装后，将项目放入Linux指定路径，假设：/DATA1/pc_monitor/Remote_PC_Status
    通过vscode连接远程Linux服务器
    进入项目路径（/DATA1/pc_monitor/Remote_PC_Status）
    先启动后端
      打开一个新的Terminal进入backend路径下，或者直接右击backend
      
        在命令行输入：nohup python3 main.py > output.log 2>&1 &   
        这样就是将后端程序放置后台持续运行。
      如果想关闭
        先查询任务ps：ps aux | grep main.py
        然后根据返回的ps结束进程：ps aux | grep main.py
        再次查询就查不到了
        后台程序运行后，会在同级目录下生成一个日志，日志记录了程序的运行情况
      日志中 http://ip:端口号 再加上/api/status，即：ip:端口号/api/status，就可以查看后端生成的json数据
    
    再来启动前端
      右击frontend，打开Terminal（必须在frontend路径下哦）
      使用python内置的http服务器即可，在命令行输入：nohup python3 -m http.server 8000 > server.log 2>&1 &
      即可让前端持续后台运行。
    如果想关闭
      先查询ps aux | grep http.server
      再kill ps即可，同样也会在同级目录生成一个日志。
