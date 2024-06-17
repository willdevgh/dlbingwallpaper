from pathlib import PurePath
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_email(host, port, sender, auth_password, receivers, subject, wallpapers):
    """用于将墙纸作为邮件附件发送至指定邮箱

    Args:
        host (str): _description_
        port (int): _description_
        sender (str): _description_
        auth_password (str): _description_
        receivers (list[str]): _description_
        subject (str): _description_
        wallpapers (list[str]): _description_
    """

    # 构建MIMEMultipart对象代表邮件本身，可以往里面添加文本、图片、附件等
    mm = MIMEMultipart('related')
    # 设置发送者,注意严格遵守格式,里面邮箱为发件人邮箱
    mm["From"] = sender
    # 设置接受者,注意严格遵守格式,里面邮箱为接受者邮箱
    mm["To"] = ','.join(receivers)
    # 设置邮件头部内容
    mm["Subject"] = Header(subject, 'utf-8')
    # 添加附件
    for image in wallpapers:
        with open(image, 'rb') as f:
            image_info = MIMEImage(f.read())
            image_info.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', PurePath(image).name))
            mm.attach(image_info)
    # 邮件正文
    mm.attach(MIMEText('<p style="color:red">此邮件无需回复</p>', "html", "utf-8"))
    # 创建SMTP对象
    smtp = smtplib.SMTP(host)
    # 设置发件人邮箱的域名和端口
    smtp.connect(host, port)
    # 可以打印出和SMTP服务器交互的所有信息
    smtp.set_debuglevel(1)
    smtp.starttls()
    # 登录邮箱，参数1：邮箱地址，参数2：邮箱授权码
    smtp.login(sender, auth_password)
    # 发送邮件，参数1：发件人邮箱地址，参数2：收件人邮箱地址，参数3：把邮件内容格式改为str
    smtp.sendmail(sender, receivers, mm.as_string())
    # 关闭SMTP对象
    smtp.quit()
