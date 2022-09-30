# -*- coding: utf-8 -*-
import ntchat
import requests
import threading
from typing import Dict, Union
from ntchat.utils.singleton import Singleton
from utils import generate_guid
from exception import ClientNotExists


class ClientWeChat(ntchat.WeChat):
    guid: str = ""
    qrcode_event: threading.Event = None
    qrcode: str = ""


class ClientManager(metaclass=Singleton):
    __client_map: Dict[str, ntchat.WeChat] = {}
    callback_url: str = ""

    def new_guid(self):
        """
        生成新的guid
        """
        while True:
            guid = generate_guid("wechat")
            if guid not in self.__client_map:
                return guid
    # 创建实例
    def create_client(self):
        guid = self.new_guid()
        wechat = ClientWeChat()
        wechat.guid = guid
        self.__client_map[guid] = wechat

        # 注册回调
        wechat.on(ntchat.MT_ALL, self.__on_callback)
        wechat.on(ntchat.MT_RECV_WECHAT_QUIT_MSG, self.__on_quit_callback)
        return guid
    # 返回实例
    def get_client(self, guid: str) -> Union[None, ntchat.WeChat]:
        client = self.__client_map.get(guid, None)
        if client is None:
            raise ClientNotExists(guid)
        return client
    # 删除实例
    def remove_client(self, guid):
        if guid in self.__client_map:
            del self.__client_map[guid]
        return self.__client_map


    def __on_callback(self, wechat: ClientWeChat, message: dict):

        # 通知二维码显示
        msg_type = message['type']
        if msg_type == ntchat.MT_RECV_LOGIN_QRCODE_MSG and wechat.qrcode_event:
            wechat.qrcode = message["data"]["code"]
            wechat.qrcode_event.set()

        if not self.callback_url:
            return

        client_message = {
            "guid": wechat.guid,
            "message": message
        }
        requests.post(self.callback_url, json=client_message)

    def __on_quit_callback(self, wechat):
        self.__on_callback(wechat, {"type": ntchat.MT_RECV_WECHAT_QUIT_MSG, "data": {}})

    # 返回实例字典
    def get_guid_dict(self):
        return self.__client_map