# 1.项目介绍
&emsp;&emsp;本项目为BIT calendar平台后端，使用python以及flask框架编写。
# 2.目录结构
&emsp;&emsp;项目根路径下包括了所有源代码，以及需要的其余文件。
包括app.py、config.py、db.py等。save文件夹中包含了项目运行过程中保存的文件，子文件夹
ics文件夹下为保存的用户课程ics文件，json文件夹下为保存的用户课程json文件，
schedule文件夹下为保存的用户日程文件。
# 3.项目运行
## 3.1 config
&emsp;&emsp;项目运行首先需要更改config.py中的参数，包括数据库url、项目路径、
文件保存路径等。
## 3.2 app
&emsp;&emsp;当进行本地测试时，在app.py的main方法中，需要设置debug=True；
当进行实际部署时，在app.py的main方法中，需要设置debug=False。