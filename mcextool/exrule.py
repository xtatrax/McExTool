
import json

from tlib import xorshift

class Additional_Rule():
    
    def __init__(self,file):
        self.rand = xorshift.xorshift()
        self.filename=file
        self.load()

    def load(self):
        with open(self.filename, encoding='utf-8') as f:
            self.rules = json.load(f)
        self.rule_list = self.rules["rule"]
        self.rule_len = len(self.rule_list)

    def reload(self):
        self.load()

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
        return content
    