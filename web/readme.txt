安装需求
pip install -r requirements.txt

初始化
进入到bcd目录下，然后输入命令
python manage.py db_init

管理员账号：admin
管理员密码：admin123

运行
python manage.py runserver

自定义端口
python manage.py runserver host:port
例如：python manage.py runserver 0.0.0.0:80


如果启动失败，一般是因为选择了错误的dll文件
打开utils/nlpir.py，修改第21行的路径
windows 32位系统：'./nlpir/NLPIR32.dll'
windows 64位系统：'./nlpir/NLPIR64.dll'
linux 32位系统：'./nlpir/NLPIR32.lib'
linux 64位系统：'./nlpir/NLPIR64.lib'

网站访问
默认访问http://localhost:5000
