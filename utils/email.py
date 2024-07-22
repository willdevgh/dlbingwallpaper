#! python 3
# --*-- encoding: UTF-8 --*--

from typing import Sequence
from pathlib import PurePath
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import logging

logger = logging.getLogger(__name__)


def send_email(
    host: str,
    port: int,
    sender: str,
    auth_password: str,
    receivers: Sequence[str],
    subject: str,
    wallpaper: str,
    copyright: str,
) -> None:
    """用于将墙纸作为邮件附件发送至指定邮箱

    Args:
        host (str): 发送邮件的服务器
        port (int): 端口号
        sender (str): 发送方邮箱
        auth_password (str): 授权密码
        receivers (list[str]): 接收方邮箱列表
        subject (str): 邮件主题
        wallpapers (list[str]): 附件墙纸图片列表
    """
    logger.debug(f"send email to: {receivers}")
    # 构建MIMEMultipart对象代表邮件本身，可以往里面添加文本、图片、附件等
    mm = MIMEMultipart('related')
    # 设置发送者,注意严格遵守格式,里面邮箱为发件人邮箱
    mm["From"] = sender
    # 设置接受者,注意严格遵守格式,里面邮箱为接受者邮箱
    mm["To"] = ','.join(receivers)
    # 设置邮件头部内容
    mm["Subject"] = Header(subject, 'utf-8')
    # 添加附件
    with open(wallpaper, 'rb') as f:
        image_data = f.read()
        image_show = MIMEImage(image_data)
        image_show.add_header('Content-ID', '<image>')
        image_attachment = MIMEImage(image_data)
        image_attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename=('utf-8', '', PurePath(wallpaper).name),
        )
        mm.attach(image_attachment)
    # 邮件正文
    mm.attach(image_show)
    mm.attach(
        MIMEText(
            f'<p><img src="cid:image"></p><p style="color:black">{copyright}</p><p style="color:red">此邮件无需回复</p>',
            "html",
            "utf-8",
        )
    )
    # 创建SMTP对象
    smtp = smtplib.SMTP(host)
    # 设置发件人邮箱的域名和端口
    smtp.connect(host, port)
    # 可以打印出和SMTP服务器交互的所有信息
    # smtp.set_debuglevel(1)
    smtp.starttls()
    # 登录邮箱，参数1：邮箱地址，参数2：邮箱授权码
    smtp.login(sender, auth_password)
    # 发送邮件，参数1：发件人邮箱地址，参数2：收件人邮箱地址，参数3：把邮件内容格式改为str
    smtp.sendmail(sender, receivers, mm.as_string())
    # 关闭SMTP对象
    smtp.quit()
