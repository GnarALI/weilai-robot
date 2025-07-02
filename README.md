# weilai-robot
# 微信机器人+未来云启，写一个机器人脚本目前只是一个雏形，慢慢迭代吧！
## wxauto+SQLite 实现微信自动化

## 记不住git 命令
## git add .
## git commit -m "11"
## git push origin master
## git add .
## pip freeze > requirements.txt
## pip install -r requirements.txt
##  git rm --cached dao/weilai.db
## python -m venv venv
## .\venv\Scripts\Activate.ps1
## pip install -r requirements.txt  # 如果有依赖文件
## deactivate

weilai_robot/
│
├── accommon/                      # 固定常亮
│   └── constant.py
│
├── dao/                         # 数据库访问模块（DAO层）
│   ├── __init__.py                
│   ├── db.py                    # 数据库连接
│   ├── user_dao.py              # 用户信息操作
│   └── weilai.db                # db生成的数据库
│
├── service/                      # 方法目录（操作方法）
│   ├── weilai/
│   │   ├── check_token.py        #检查用户是否过期
│   │   ├── get_task.py           #根据数据库取得任务数量并且整合数据
│   │   ├── login.py              #未来登录脚本
│   │   ├── scheduler.py          #线程调度器,设置最大线程数
│   │   └── task.py               #未来任务脚本
│   └── wx/                       #微信监控操作目录
│       ├── opration.py           #监控用户信息做出对应操作
│       └── wechat.py             #微信监控
│
├── utils/                        #工具类（如日志、网络请求封装、加解密）
│   ├── log/                      #不同任务对应的请求
│   ├── request.py                #请求
│   └── logger.py                 #日志
│
│
├── main.py                       # 启动入口
├── requirements.txt              # 所需依赖列表
└── README.md                     # 项目说明文档