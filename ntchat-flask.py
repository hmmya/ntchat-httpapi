# -*- coding: utf-8 -*-
from flask import Flask,request
from functools import wraps
from mgr import ClientManager
from down import get_local_path
from exception import MediaNotExistsError, ClientNotExists
import ntchat
import json,threading

def response_json(status=500, data=None, msg=""):
    return {
        "status": status,
        "data": {} if data is None else data,
        "msg": msg
    }


class catch_exception:
    def __call__(self, f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            try:
                return await f(*args, **kwargs)
            except ntchat.WeChatNotLoginError:
                return response_json(msg="wechat instance not login")
            except ntchat.WeChatBindError:
                return response_json(msg="wechat bind error")
            except ntchat.WeChatVersionNotMatchError:
                return response_json(msg="wechat version not match, install require wechat version")
            except MediaNotExistsError:
                return response_json(msg="file_path or url error")
            except ClientNotExists as e:
                return response_json(msg="client not exists, guid: %s" % e.guid)
            except Exception as e:
                return response_json(msg=str(e))

        return wrapper


client_mgr = ClientManager()
app = Flask(__name__)

# 设置默认上报地址
client_mgr.callback_url = "http://127.0.0.1:8005/callback"
@app.route('/callback', methods=['get','post'])
def on_callback():
    data = request.stream.read()
    data = json.loads(data.decode('utf-8'))
    #print(data)


    return ''

#创建实例
@app.route("/client/create",methods=["GET","POST"])
@catch_exception()
async def client_create():
    guid = client_mgr.create_client()

    return response_json(200, {"guid": guid})

#打开微信
@app.route("/client/open", methods=["GET","POST"])
@catch_exception()
async def client_open():
    datax = request.get_json()
    client = client_mgr.get_client(datax["guid"])
    ret = client.open(datax["smart"],datax["show_login_qrcode"])

    if datax["show_login_qrcode"] :
        client.qrcode_event = threading.Event()
        client.qrcode_event.wait(timeout=10)

    return response_json(200 if ret else 500, {"guid": datax["guid"],'qrcode': client.qrcode})

#获取实例列表
@app.route("/client/get_guid_dict", methods=["GET","POST"])
async def get_guid_dict():
    ret = client_mgr.get_guid_dict()
    data =  list(ret.keys())
    return response_json(200 if ret else 500,data,"已创建实例")

#删除实例
@app.route("/client/remove_client", methods=["GET","POST"])
@catch_exception()
async def remove_client():
    datax = request.get_json()
    ret = client_mgr.remove_client(datax["guid"])
    data =  list(ret.keys())
    return response_json(200,data)

#设置接收通知地址
@app.route("/global/set_callback_url",  methods=["GET","POST"])
@catch_exception()
async def client_set_callback_url():
    datax = request.get_json()
    client_mgr.callback_url = datax["callback_url"]
    return response_json(200)

#获取登录信息
@app.route("/user/get_login_info", methods=["GET","POST"])
@catch_exception()
async def user_get_login_info():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).get_login_info()
    return response_json(200, data)

#获取自己的信息
@app.route("/user/get_profile", methods=["GET","POST"])
@catch_exception()
async def user_get_profile():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).get_self_info()
    return response_json(200, data)

#获取联系人列表
@app.route("/contact/get_contacts",methods=["GET","POST"])
@catch_exception()
async def get_contacts():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).get_contacts()
    return response_json(200, data)


#获取指定联系人详细信息
@app.route("/contact/get_contact_detail",methods=["GET","POST"])
@catch_exception()
async def get_contact_detail():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).get_contact_detail(datax["wxid"])
    return response_json(200, data)

#获取关注公众号列表
@app.route("/publics/get_publics",methods=["GET","POST"])
@catch_exception()
async def get_publics():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).get_publics()
    return response_json(200, data)


#获取群列表
@app.route("/room/get_rooms",methods=["GET","POST"])
@catch_exception()
async def get_rooms():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).get_rooms()
    return response_json(200, data)

#获取群成员列表
@app.route("/room/get_room_members", methods=["GET","POST"])
@catch_exception()
async def get_room_members():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).get_room_members(datax["room_wxid"])
    return response_json(200, data)

#创建群
@app.route("/room/create_room", methods=["GET","POST"])
@catch_exception()
async def create_room():
    datax = request.get_json()
    ret = client_mgr.get_client(datax["guid"]).create_room(datax["member_list"])
    return response_json(200 if ret else 500)

#添加好友入群
@app.route("/room/add_room_member", methods=["GET","POST"])
@catch_exception()
async def add_room_member():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).add_room_member(datax["room_wxid"],datax["member_list"])
    return response_json(200, data)

#邀请好友入群
@app.route("/room/invite_room_member", methods=["GET","POST"])
@catch_exception()
async def invite_room_member():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).invite_room_member(datax["room_wxid"], datax["member_list"])
    return response_json(200, data)

#删除群成员
@app.route("/room/del_room_member", methods=["GET","POST"])
@catch_exception()
async def del_room_member():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).del_room_member(datax["room_wxid"], datax["member_list"])
    return response_json(200, data)

#添加群成员为好友
@app.route("/room/add_room_friend", methods=["GET","POST"])
@catch_exception()
async def add_room_friend():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).add_room_friend(datax["room_wxid"],
                                                             datax["wxid"],
                                                             datax["verify"])
    return response_json(200, data)

#修改群名
@app.route("/room/modify_name", methods=["GET","POST"])
@catch_exception()
async def modify_name():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).modify_room_name(datax["room_wxid"],datax["name"])
    return response_json(200, data)

#修改群公告
@app.route("/room/modify_room_notice", methods=["GET","POST"])
@catch_exception()
async def modify_room_notice():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).modify_room_notice(datax["room_wxid"],datax["notice"])
    return response_json(200, data)


#退出群
@app.route("/room/quit_room", methods=["GET","POST"])
@catch_exception()
async def quit_room():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).quit_room(datax["room_wxid"])
    return response_json(200, data)

#发送文本消息
@app.route("/msg/send_text",methods=["GET","POST"])
@catch_exception()
async def msg_send_text():
    datax = request.get_json()
    print(datax)
    ret = client_mgr.get_client(datax["guid"]).send_text(datax["to_wxid"], datax["content"])
    return response_json(200 if ret else 500)

#发送群@消息
@app.route("/msg/send_room_at", methods=["GET","POST"])
@catch_exception()
async def send_room_at():
    datax = request.get_json()
    ret = client_mgr.get_client(datax["guid"]).send_room_at_msg(datax["to_wxid"],
                                                             datax["content"],
                                                             datax["at_list"])
    return response_json(200 if ret else 500)

#发送名片
@app.route("/msg/send_card", methods=["GET","POST"])
@catch_exception()
async def send_card():
    datax = request.get_json()
    ret = client_mgr.get_client(datax["guid"]).send_card(datax["to_wxid"],
                                                      datax["card_wxid"])
    return response_json(200 if ret else 500)

#发送链接卡片消息
@app.route("/msg/send_link_card", methods=["GET","POST"])
@catch_exception()
async def send_link_card():
    datax = request.get_json()
    ret = client_mgr.get_client(datax["guid"]).send_link_card(datax["to_wxid"],
                                                           datax["title"],
                                                           datax["desc"],
                                                           datax["url"],
                                                           datax["image_url"])
    return response_json(200 if ret else 500)

#发送图片
@app.route("/msg/send_image", methods=["GET","POST"])
@catch_exception()
async def send_image():
    datax = request.get_json()
    file_path = get_local_path(datax)
    if file_path is None:
        raise MediaNotExistsError()
    ret = client_mgr.get_client(datax["guid"]).send_image(datax["to_wxid"], file_path)
    return response_json(200 if ret else 500)

#发送文件
@app.route("/msg/send_file",methods=["GET","POST"])
@catch_exception()
async def send_file():
    datax = request.get_json()
    file_path = get_local_path(datax)
    if file_path is None:
        raise MediaNotExistsError()
    ret = client_mgr.get_client(datax["guid"]).send_file(datax["to_wxid"], file_path)
    return response_json(200 if ret else 500)

#发送视频
@app.route("/msg/send_video", methods=["GET","POST"])
@catch_exception()
async def send_video():
    datax = request.get_json()
    file_path = get_local_path(datax)
    if file_path is None:
        raise MediaNotExistsError()
    ret = client_mgr.get_client(datax["guid"]).send_video(datax["to_wxid"], file_path)
    return response_json(200 if ret else 500)

#发送GIF
@app.route("/msg/send_gif",methods=["GET","POST"])
@catch_exception()
async def send_gif():
    datax = request.get_json()
    file_path = get_local_path(datax)
    if file_path is None:
        raise MediaNotExistsError()
    ret = client_mgr.get_client(datax["guid"]).send_gif(datax["to_wxid"], file_path)
    return response_json(200 if ret else 500)

#同意加好友请求
@app.route("/msg/accept_friend_request",methods=["GET","POST"])
@catch_exception()
async def accept_friend_request():
    datax = request.get_json()
    ret = client_mgr.get_client(datax["guid"]).accept_friend_request(datax["encryptusername"], datax["ticket"],datax["scene"])
    return response_json(200 if ret else 500)

#发送XML原始消息
@app.route("/msg/send_xml",methods=["GET","POST"])
@catch_exception()
async def send_xml():
    datax = request.get_json()
    ret = client_mgr.get_client(datax["guid"]).send_xml(datax["to_wxid"],datax["xml"])
    return response_json(200 if ret else 500)

#发送拍一拍
@app.route("/msg/send_pat", methods=["GET","POST"])
@catch_exception()
async def send_pat():
    datax = request.get_json()
    data = client_mgr.get_client(datax["guid"]).send_pat(datax["room_wxid"], datax["patted_wxid"])
    return response_json(200, data)


if __name__ == '__main__':
    app.debug = False # 设置调试模式，生产模式的时候要关掉debug
    app.run(host='0.0.0.0',port=8005)