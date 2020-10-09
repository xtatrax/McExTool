
import json
import os

#独自ライブラリ
from tlib import xorshift

class Additional_Rule():
    
    def __init__(self,file):
        self.rand = xorshift.xorshift()
        self.filename=file
        self.load()

        # 現在の縛りリスト関係
        self.tmpDir = os.path.dirname(__file__)
        os.makedirs(self.tmpDir, exist_ok=True)
        self.nowRuleFile = self.tmpDir + "/rule_now.json"
        self.ruleNow = []
        
    def load(self):
        with open(self.filename, encoding='utf-8') as f:
            self.rules = json.load(f)
        self.rule_list = self.rules["rule"]
        self.rule_len = len(self.rule_list)
        self.penalty_list = self.rules["penalty"]["personal"]
        self.penalty_len = len(self.penalty_list["Contents"])

    def reload(self):
        self.load()

    def _addNowRule(self,content):
        self.ruleNow.append(content)
        #ファイル読み込み

    def getNowRule(self):
        return self.ruleNow

    def getRandRule(self):
        num = int(self.rand.uniform(32,0,self.rule_len))
        rule = self.rule_list[num]
        content = rule["Contents"] 
        if rule["type"] != "single":
            ex = self.rules[rule["type"]]
            ex_len = len(ex)
            num = int(self.rand.uniform(32,0,ex_len))
            content += "( " + ex[num] + " )"
        if rule.get("min") and rule.get("max"):
            num = int(self.rand.uniform(32,rule["min"],rule["max"]))
            content += " +"+ str(num)
        self._addNowRule(content)
        return content
    
    def getRandPenalty(self):
        num = int(self.rand.uniform(32,0,self.rule_len))
        name = self.penalty_list["name"]
        content = self.penalty_list["Contents"][num]
        msg = name + " : " + content
        return msg
