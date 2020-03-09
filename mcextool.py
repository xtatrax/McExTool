# -*- coding: utf-8 -*-

############################################################
# file : mcextool.py （旧 autobackup.py
# 制作 ： tatra 2020年2月7日
# 
# 自動バックアップスクリプト
#
# 対象バージョン : python 3.x 
# 外部モジュール :
#   python-dateutil , schedule , watchdog , six
#
# メモ :
#   コードをきれいにしたい
#   マインクラフトログ監視
#
#[13:30:54] [Server thread/INFO]: <xtatrax> testtext てすとてきすとー
############################################################

import argparse
import datetime
import glob
import os
import os.path
import tarfile
import time
import dateutil.tz
import schedule
import subprocess
import sys
import threading
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


version = '2.1.2'
pyname = os.path.basename(__file__)

# python 3.x 確認
if sys.version_info.major == 3:
    print("start backup (version '"+version+"')")
else:
    print('python 3.xで実行してください')
    exit()

# 引数定義
parser = argparse.ArgumentParser(description='定期バックアップスクリプト',add_help = True)
parser.add_argument('--version', action='version', version='%(prog)s ' + version) # version
parser.add_argument('-s', '--srcdir',required=True, help='バックアップ対象のディレクトリ') # 絶対
parser.add_argument('-d', '--dstdir',required=True, help='バックアップ保存のディレクトリ') # 絶対
parser.add_argument('-t', '--time', required=True, help='バックアップ間隔(現状分指定)') 
parser.add_argument('-n', '--name', help='[オプション]バックアップ保存名') 
parser.add_argument('-m', '--mcscname', default=None, help='[オプション]マインクラフトを動ごかしてるSCREEN名') 
parser.add_argument('-c', '--mcexcommand', help='[オプション]マインクラフト log ファイルへのパス。：チャットからの入力に対応します。-m --mcscname オプションが指定されている必要があります。') 
parser.add_argument('--savenum', help='[オプション]バックアップ保持数') 
parser.add_argument('--numdebug', help='[デバッグ]引数回バックアップ実行') 
args = parser.parse_args()

def mc_ex_command_arg_type(string):
    if args.mcscname == None:
        msg = "-c --mcexcommand は -m --mcscname オプションが指定されている必要があります。"
        print(msg)
        parser.print_help()
    exit(1)

# 出力ラッパー
is_debug_print=False
is_debug_mc_print=False

mc_msg_header="[§bfrom "+pyname+" Ver"+version+"§r]"
def debug_print(msg: str):
    print("[DEBUG]"+msg)

def mcmsg4screen_common(msg: str):
    subprocess.call("screen -p 0 -S "+args.mcscname+" -X eval 'stuff \"say " + msg + "\"\015'", shell=True)
    
def mcmsg4screen_debug(msg: str):
    if is_debug_mc_print:
        mcmsg4screen(mc_msg_header+"[§eDEBUG§r] : " + msg)

def mcmsg4screen(msg: str):
    if args.mcscname != None:
        mcmsg4screen_common(mc_msg_header+" : " + msg)

# 古いバックアップ削除
def listup(name):
    if args.savenum == None:
        return
    filelist_old = glob.glob(os.path.join(args.dstdir,name+'*'))
    filelist=sorted(filelist_old, key = str.lower)
    if is_debug_print:
        debug_print("*****filelist_old*****")
        for file in filelist_old:
            debug_print(" : "+file)
        debug_print("*****filelist*****")
        for file in filelist:
            debug_print(" : "+file)
        debug_print("*****end*****")
    while len(filelist) > int(args.savenum):
        filename = filelist.pop(0) 
        os.remove(filename)
        msg = 'delete the ' + filename
        msg_mc='delete the '+os.path.basename(filename)
        print(msg)
        if is_debug_mc_print:
            mcmsg4screen_debug(msg)
        else:
            mcmsg4screen(msg_mc)

is_backup_lock=False
# バックアップ生成
def backup():
    if args.mcscname != None:
        mcmsg4screen('30秒後バックアップを開始します。')
        time.sleep(24)
        mcmsg4screen('カウントダウンを開始')
        time.sleep(1)
        for t in range(5, -1, -1):
            mcmsg4screen(str(t))
            time.sleep(1)
        mcmsg4screen('backupを開始、ワールドを保存')
        subprocess.call("screen -p 0 -S "+args.mcscname+" -X eval 'stuff \"save-all\"\015'", shell=True)
        time.sleep(10)

    name = args.name
    if name == None:
        name = os.path.basename(args.srcdir)

    d = datetime.datetime.now(dateutil.tz.tzlocal())
    os.makedirs(args.dstdir, exist_ok=True)
    tar_name = os.path.join( args.dstdir, name + d.strftime('_%Y-%m-%d_%H-%M-%S-%f_%z') + '.tar.gz')
    archive = tarfile.open(tar_name, mode='w:gz')
    archive.add(args.srcdir)
    archive.close()
    msg = 'backup the ' + tar_name
    msg_mc='backup the '+os.path.basename(tar_name)
    print(msg)
    if is_debug_mc_print:
        mcmsg4screen_debug(msg)
    else:
        mcmsg4screen(msg_mc)
    listup(name)

# 自動バックアップジョブ
job_running=True
def autobackup_job():
    def job():
        global is_backup_lock
        is_backup_lock=True
        backup()
        is_backup_lock=False
    schedule.every(int(args.time)).minutes.do(job)
    global job_running 
    while job_running:
        schedule.run_pending()
        time.sleep(1)

# コマンド一覧クラス
class command_list():
    class com:
        def __init__(self, command_name,command_action,command_help):
            self.Name   = command_name
            self.Action = command_action
            self.Help   = command_help

    def __init__(self, ):
        self.cmmands={}

    def add_command(self, command_name,command_action,command_help):
        self.cmmands[command_name]=command_list.com(command_name,command_action,command_help)

    def get_command(self,command_name):
        if command_name in self.cmmands :
            return self.cmmands[command_name]
        else:
            return None

    def help(self,command_name=None):
        retlist=[]
        if command_name != command_name :
            retlist.append(self.cmmands[command_name].Help)
        else :
            for k in self.cmmands:
                retlist.append(self.cmmands[k].Help)
        return retlist


cmdList = command_list()

def command_init():
    def backup_func(mc_print_on=False):
        backup()
        return 0
    cmdList.add_command("backup",backup_func,
        "backup          : backupを強制実行します。"
    )
    def stop_func(mc_print_on=False):
        return 1
    cmdList.add_command("stop",stop_func,
        "stop            : プロセスを終了します。"
    )
    def stop_and_backup_func(mc_print_on=False):
        backup()
        return 1
    cmdList.add_command("stop_and_backup",stop_and_backup_func,
        "stop_and_backup : backupを強制実行した後にプロセスを終了します。"
    )
    def debug_info_func(mc_print_on=False):
        global is_debug_print
        is_debug_print = not is_debug_print
        if is_debug_print:
            print("デバッグ情報表示はONです")
        else:
            print("デバッグ情報表示はOFFです")
        return 0
    cmdList.add_command("debug_info",debug_info_func,
        "debug_info      : デバッグ表示をON/OFFにします。"
    )
    def debug_mc_info_func(mc_print_on=False):
        if args.mcscname != None:
            global is_debug_mc_print
            is_debug_mc_print = not is_debug_mc_print
            if is_debug_mc_print:
                print("マインクラフトでのデバッグ情報表示はONです。")
            else:
                print("マインクラフトでのデバッグ情報表示はOFFです。")
        else:
            print("-m/--mcscname 情報が提供されている場合のみ有効です。")
        return 0
    cmdList.add_command("debug_mc_info",debug_mc_info_func,
        "debug_mc_info   : マイクラ内デバッグ表示をON/OFFにします。"
    )
    def command_help_func(mc_print_on=False):
        help_list = cmdList.help()
        for l in help_list:
            if mc_print_on :
                mcmsg4screen(l)
            print(l)
        return 0
    cmdList.add_command("help",command_help_func,
        "help             : このヘルプを表示します"
    )
    
class FileChangeHandler(PatternMatchingEventHandler):

    def __init__(self, patterns):
        super(FileChangeHandler, self).__init__(patterns=patterns)
        self.mc_cmmand_header="$mc_ex_tool:"

    def check_mc_ex_command(self,filepath):
        global is_backup_lock
        if is_backup_lock:
            return 
        
        with open(filepath,"r") as f:
            lines = f.readlines()
            lastLine= lines[-1]
            
            hd_pos = lastLine.find(self.mc_cmmand_header)
            if hd_pos > -1:
                cmd_txt = lastLine[hd_pos+len(self.mc_cmmand_header)-1 : -1] 
                fspcmd = cmd_txt.lstrip()
                fspcmdrsp = cmd_txt.rstrip()
                fspcmdrsp
                cmd = cmdList.get_command(fspcmdrsp)
                if cmd != None:
                    cmd.Action(True)
                else:
                    cmdList.get_command("help").Action(True)

    # ファイル作成時のイベント
    def on_created(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        debug_print('%s created' % filename)

    # ファイル変更時のイベント
    def on_modified(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        debug_print('%s changed' % filename)

    # ファイル削除時のイベント
    def on_deleted(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        debug_print('%s deleted' % filename)

    # ファイル移動時のイベント
    def on_moved(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        debug_print('%s moved' % filename)

def stdin_command_job(auto_thread,mc_command_thread):
    global job_running 
    ret = 0 
    while job_running:
        cmd = cmdList.get_command(input())
        if cmd != None:
            ret = cmd.Action()
        else:
            cmdList.get_command("help").Action(False)
        if ret == 1:
            job_running=False
            auto_thread.join()
            mc_command_thread.join()
            break

def mc_command_job():
    if args.mcexcommand != None:
        # ファイル監視の開始
        dfname=os.path.split(args.mcexcommand)
        basedir= dfname[0]
        filemame= dfname[1]
        event_handler = FileChangeHandler([filemame])
        observer = Observer()
        observer.schedule(event_handler, basedir, recursive=True)
        observer.start()
        debug_print("basedir  : "+basedir)
        debug_print("filemame : "+filemame)
        debug_print("でmc_command_jobを開始")
        # 処理が終了しないようスリープを挟んで無限ループ
        global job_running 
        try:
            while job_running:
                time.sleep(1)
        except Exception as e:
            print("ログ監視ジョブで例外が発生しました args:", e.args)
 
        observer.stop()
        observer.join()

 
if __name__=='__main__':
    if args.numdebug != None:
        print("test")
        for i in range(int(args.numdebug)):
            backup()
            time.sleep(1)
        exit()
    command_init()
    auto_thread=threading.Thread(target=autobackup_job,name="autobackup_job")
    auto_thread.start()
    mc_command_thread=threading.Thread(target=mc_command_job,name="mc_command_job")
    mc_command_thread.start()
    stdin_command_job(auto_thread,mc_command_thread)