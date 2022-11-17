#正雨 @ 1695960757
import os
import sys
import os.path
import shutil

def  del_file(path):
      if not os.listdir(path):
            pass
      else:
            for i in os.listdir(path):
                  path_file = os.path.join(path,i)  #取文件绝对路径
                  if os.path.isfile(path_file):
                        os.remove(path_file)
                  else:
                        del_file(path_file)
                        shutil.rmtree(path_file)

def get_exec_dir():
    return os.path.dirname(sys.argv[0])


def get_download_dir():
    user_dir = os.path.join(get_exec_dir(), 'download')
    user_dir = os.path.abspath(user_dir)
    if not os.path.isdir(user_dir):
        os.makedirs(user_dir)
    del_file(user_dir)
    return user_dir