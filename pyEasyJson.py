# -*- coding: utf-8 -*-


#
#任何人都拥有平等的获取知识的权利
#CppEasyJson 是开放源代码的软件，任何人都可以下载、使用、修改和重新发布，不必担心任何版权问题
#请在重新发布的时候保留以上信息
#
import string

 
NODE_OBJECT=1
NODE_ARRAY=2
VALUE_NUM_INT=1
VALUE_NUM_FLOAT=2
VALUE_STRING=3
VALUE_BOOL=4
VALUE_ARRAY=5
VALUE_OBJECT=6
VALUE_NULL=7


JsonLeftBrace = '{';
JsonRightBrace = '}';
JsonLeftBracket = '[';
JsonRightBracket = ']';
JsonEscapeCharacter = '\\';
JsonColon = ':';
JsonDoubleQuote = '"';
JsonComma = ',';
JsonNodeRefrence = '.';
JsonStar = '*';
JsonHash = '#';
JsonSlash = '/';

#
#一个结构良好的JSON字符串或JSON文件可以解析为一个树形结构
#{}对象和[]数组可以认为是树上的一个节点
#"":"" 名称键值对可以认为是节点上的一个叶子
#JSON解析过程实际上就是构建这棵树的过程
#*/

class JsonNode:
    def __init__(self):
        self.nodetype = 0
        self.values=list()
    def ToString(self):
        temp=""
        if (self.nodetype == NODE_OBJECT):
            temp =temp+ "{"
        else:
            temp =temp+ "["
        if(len(self.values)>0):
            for iv in self.values:            
                temp =temp+ iv.ToString()
                temp =temp+ ","
            temp = temp[0:len(temp)-1]
        if (self.nodetype == NODE_OBJECT):
            temp =temp+ "}"
        else:
            temp =temp+ "]";
        return temp;
    values=list()
    nodetype=0
 
class JsonValue:
    valuetype=0
    name=""
    vstr=''
    node=JsonNode()
    def __init__(self):
        self.name =""
        self.vstr=""
        self.valuetype=0
        self.node=JsonNode()
    
    def ToString(self):
        temp=""
        if(self.valuetype == VALUE_STRING):
            if (self.name!=""):
                temp += "\""
                temp += self.name
                temp += "\""
                temp += ":"
            temp += "\""
            temp += self.vstr
            temp += "\""
        elif(self.valuetype == VALUE_OBJECT):
            if(self.name!=""):
                temp += "\""
                temp += self.name
                temp += "\""
                temp += ":"
            temp += self.node.ToString()
        elif(self.valuetype == VALUE_ARRAY):
            if (self.name!=""):
                temp += "\""
                temp += self.name
                temp += "\""
                temp += ":"
            temp += self.node.ToString()
        else:
            if (self.name!=""):
                temp += "\""
                temp += self.name
                temp += "\""
                temp += ":"
            temp += self.vstr
        return temp;


class JsonLex:
    json=""
    currenttoken=""
    prevtoken=""
    currentpos = 0
    def __init__(self):
        self.json=""
        self.currenttoken=""
        self.prevtoken=""
        return
        
    def ParseString(self,jsonstring):
        root = JsonNode()
        self.json = jsonstring
        self.currentpos = 0
        while (self.currentpos<len(self.json)):
            if (self.json[self.currentpos] == JsonLeftBrace):
                self.currentpos=self.currentpos+1
                root = self.BulidJsonNode(None, NODE_OBJECT)
                break
            elif(self.json[self.currentpos] == JsonLeftBracket):
                self.currentpos=self.currentpos+1
                root = self.BulidJsonNode(None, NODE_ARRAY)
                break		
            self.currentpos=self.currentpos+1
        return root
      
    
    def BuildJsonValue(self,parentnode):
        value = JsonValue()
        haskey=0
        JsonDoubleQuoteMeet = 0
        value=JsonValue()
        token = self.currenttoken
        while (self.currentpos!=len(self.json)):
            if(self.TokenIsComment(token)):
                self.GoCommentEnd(token)
                token =self.GetNextToken(0)
            elif (token == "{"):
                value.node = self.BulidJsonNode(parentnode, NODE_OBJECT)
                value.valuetype = VALUE_OBJECT
                value.node.nodetype = NODE_OBJECT
                return value
            elif (token == "["):
                value.node = self.BulidJsonNode(parentnode, NODE_ARRAY)
                value.node.nodetype = NODE_ARRAY
                value.valuetype = VALUE_ARRAY
                return value
            elif (token == "}"):
                #返回，交给上层处理
                self.currentpos=self.currentpos-1
                break
            elif (token == "]"):
                #返回，交给上层处理
                self.currentpos=self.currentpos-1
                break
            elif (token == "\""):
                JsonDoubleQuoteMeet=JsonDoubleQuoteMeet+1
                if (value.name==""):
                    value.valuetype = VALUE_STRING
                if(JsonDoubleQuoteMeet%2==0):
                    token = self.GetNextToken(0)
                else:
                    token = self.GetNextToken(1)
            elif(token == ":"):
                if (JsonDoubleQuoteMeet == 2):
                    if (value.name==""):
                        haskey = 0
                    else:
                        haskey = 1
                elif(JsonDoubleQuoteMeet==3):
                    haskey = 1
                else:
                    haskey = 0
                value.valuetype = VALUE_NULL
                token =self.GetNextToken(0)
                if (self.currentpos==len(self.json)):
                    self.currentpos=self.currentpos-1
            elif (token == ","):
                break
            else:
                if (value.name==""):
                    value.name = token
                elif (value.vstr==""):
                    value.vstr=token
                    self.AssignStringToJsonValue(value, token)
                    if (self.json[self.currentpos]== '"'):
                        self.currentpos=self.currentpos+1
                    break
                token =self.GetNextToken(0)
        if (haskey==0):
            value.vstr=value.name
            self.AssignStringToJsonValue(value, value.name)
            value.name = ""
        return value
                    
    def BulidJsonNode(self,parentnode,nodetype):
        node = JsonNode()
        node.nodetype = nodetype
        token =self.GetNextToken(0)
        while(self.currentpos!=len(self.json)):
            if(self.TokenIsComment(token)):
                self.GoCommentEnd(token)
                token=self.GetNextToken(0)
            elif (token=='"'):
                node.values.append(self.BuildJsonValue(node))
                token=self.GetNextToken(0)
            elif (token=="}"):
                if(nodetype==NODE_ARRAY):
                    token=self.GetNextToken(0)
                else:
                    break
            elif (token=="{"):
                node.values.append(self.BuildJsonValue(node))
                token=self.GetNextToken(0)
            elif (token=="["):
                node.values.append(self.BuildJsonValue(node))
                token=self.GetNextToken(0)
            elif (token=="]"):
                break
            elif (token==":"):
                token=self.GetNextToken(0)
            elif(token==","):
                token=self.GetNextToken(0)
            else:
                node.values.append(self.BuildJsonValue(node))
                token=self.GetNextToken(0)
        return node
        
    def GoCommentEnd(self,commentstyle):
        if(commentstyle=="//"):
            while(self.currentpos!=len(self.json)):
                if(self.json[self.currentpos]=='\n'):
                    self.currentpos=self.currentpos+1
                    break
                elif(self.json[self.currentpos]=='\r' and self.json[self.currentpos+1]=='\n'):
                    self.currentpos=self.currentpos+2
                    break
                self.currentpos=self.currentpos+1
        elif(commentstyle=="/*"):
            while(self.currentpos!=len(self.json)):
                if(self.json[self.currentpos]=="*" and self.json[self.currentpos+1]=='/'):
                    self.currentpos=self.currentpos+2
                    break
                self.currentpos=self.currentpos+1     
        return 

    def TokenIsComment(self,token):
        bret = 0
        if(token=="//" or token=="/*" or token=="*/"):
            bret = 1
        return bret
        
    def GetNextToken(self,tonextJsonDoubleQuote):
        token =""       
        self.prevtoken = self.currenttoken
        if(tonextJsonDoubleQuote==1):
            if(self.json[self.currentpos]==JsonDoubleQuote):
                self.currentpos=self.currentpos+1
            while(self.currentpos<len(self.json)):
                if(self.json[self.currentpos]==JsonEscapeCharacter):
                    if(self.currentpos+1!=len(self.json)):
                        if(self.json[self.currentpos]==JsonDoubleQuote):
                            token+=JsonDoubleQuote
                            self.currentpos=self.currentpos+2
                        else:
                            token +=self.json[self.currentpos]
                            self.currentpos=self.currentpos+1
                else:
                    if(self.json[self.currentpos]==JsonDoubleQuote):
                        break
                    else:
                        token+=self.json[self.currentpos]
                        self.currentpos=self.currentpos+1
            self.currenttoken=token
            return token
        else:
            while(self.currentpos!=len(self.json)):
                temp = self.json[self.currentpos]
                if(temp==JsonDoubleQuote or temp == JsonRightBrace or temp==JsonLeftBrace or temp==JsonLeftBracket or temp==JsonRightBracket or temp==JsonColon or temp == JsonComma):
                    if(token==""):
                        token=temp
                        self.currentpos=self.currentpos+1
                        break
                    else:
                        break
                elif(temp==JsonSlash):
                    if(self.currentpos+1!=len(self.json) and self.json[self.currentpos+1]==JsonSlash):
                        token="//"
                        self.currentpos=self.currentpos+2
                        break
                    elif(self.currentpos+1!=len(self.json) and self.json[self.currentpos+1]==JsonStar):
                        token="/*"
                        self.currentpos=self.currentpos+2
                        break
                    else:
                        token=token+self.json[self.currentpos]
                elif(temp==JsonEscapeCharacter):
                    if(token!=""):
                        if(self.json[self.currentpos+1]==JsonDoubleQuote):
                            token=token+JsonDoubleQuote
                            self.currentpos=self.currentpos+1
                        elif(self.json[self.currentpos+1]=='b'):
                            token=token+'\b'
                            self.currentpos=self.currentpos+1
                        elif(self.json[self.currentpos+1]=='f'):
                            token=token+'\f'
                            self.currentpos=self.currentpos+1
                        elif(self.json[self.currentpos+1]=='t'):
                            token=token+'\t'
                            self.currentpos=self.currentpos+1
                        elif(self.json[self.currentpos+1]=='n'):
                            token=token+'\n'
                            self.currentpos=self.currentpos+1
                        elif(self.json[self.currentpos+1]=='r'):
                            token=token+'\r'
                            self.currentpos=self.currentpos+1
                        elif(self.json[self.currentpos+1]=='\\'):
                            token=token+'\\'
                            self.currentpos=self.currentpos+1
                        elif(self.json[self.currentpos+1]=='/'):
                            token=token+'/'
                            self.currentpos=self.currentpos+1
                        elif(self.json[self.currentpos+1]=='u'):
                            token=token+temp
                            self.currentpos=self.currentpos+1
                        else:
                            token=token+temp
                elif(temp==' ' or temp=='\t' or temp=='\n' or temp=='\r'):
                    token=token
                else:
                    token=token+temp
                self.currentpos=self.currentpos+1
        self.currenttoken=token   
        return token
        
    def AssignStringToJsonValue(self,value,text):
        value.vstr=text
        if(value.valuetype==VALUE_STRING):
            value.vstr = text
        else:
            if(text=="null"):
                value.valuetype = VALUE_NULL
            elif(text=="true"):
                value.valuetype=VALUE_BOOL
            elif(text=="false"):
                value.valuetype=VALUE_BOOL
            elif(text.find(JsonNodeRefrence)>=0):
                value.valuetype = VALUE_NUM_FLOAT
            else:
                value.valuetype = VALUE_NUM_INT
        return 0
    
        

 

class PyEasyJson: 
    jsoncontent=""
    jsonlex=JsonLex()
    jsonroot=JsonNode()
    def __init(self):
        self.jsonroot= None
    def ParseString(self,jsonstring):
        self.jsonroot = self.jsonlex.ParseString(jsonstring)
        return 1
    def ParseFile(self,jsonfile):
        return 0
        

	#//路径方式
	#//节点名称.子节点名称.数组节点名称[数组元素下表].值名称
    def GetValue(self,nodepath):
        index=-1
        keyname=""
        value=""
        node=self.FindNodeInternal(nodepath,self.jsonroot,index,keyname)
        if(node!=None):
            valuecount = len(node.values)
            pos1 = keyname.find(JsonLeftBracket)
            pos2 = keyname.find(JsonRightBracket)
            if(pos1>=0 and pos2 == len(keyname)-1):
                valueindex=string.atoi(keyname[pos1+1:pos2-pos1-1])
                if(valueindex>=0 and valueindex<valuecount):
                    jsvalue=node.values[valueindex]
            else:
                i=0
                while(i<valuecount):
                    if(node.values[index].name==keyname):
                        jsvalue = node.values[i]
                        break
                    i=i+1
        value = jsvalue.vstr
        return  value
        
    def SetValue(self,nodepath,value):
        return 0
    def SetNullValue(self,nodepath):
        return 0
    def DelValue(self,nodepath):
        return 0

	#//按节点逐层访问方式
    def AppendValue(self,node,name,value):
        return 0
    def AppendNullValue(self,node,name):
        return 0
    def AppendObjectValue(self,node,name,obj):
        return 0
    def AppendArrayValue(self,node,name,objarray):
        return 0
    def GetJsonValue(self,node,nameorindex):
        value = JsonValue()
        return value
    def DelJsonValue(self,node,nameofindex):
        return 0
    def CreateJsonNode(self,nodetype):
        node = JsonNode()
        node.nodetype=nodetype
        return node
    def GetRoot(self):
        return self.jsonroot
    def SetRoot(self,node):
        self.jsonroot = node
    def ToString(self):
        jsoncontent=""
        jsoncontent=self.jsonroot.ToString()
        return jsoncontent
    def SaveToFile(self,jsonfile):
        return 0
    def WellFormat(self):
        return 0
    def FindNodeInternal(self,path,parentnode,index,keyname):
        if(parentnode==None):
            return None
        if(path==""):
            return None
        sub = path
        pos = path.find(JsonNodeRefrence)
        if(pos>=0):
            path=path[0:pos]
            inode = self.FindNodeInternal(path,parentnode,index,keyname)
            sub = sub[pos+1:len(sub)-pos-1]
            node = self.FindNodeInternal(sub,inode,index,keyname)
        else:
            pos1=sub.find(JsonLeftBracket)
            pos2=sub.find(JsonRightBracket)
            if(pos1>=0 and pos2==len(sub)-1):
                if(pos1!=0):
                    path=path[0:pos1]
                    inode = self.FindNodeInternal(path,parentnode,index,keyname)
                else:
                    inode = parentnode
                keyname=sub
                index=string.atoi(sub[pos1+1:pos2-pos1])
                if(index>=0 and index<len(inode.values)):
                    inode2=inode.values[index]
                else:
                    inode2=None
                return inode2
            else:
                keyname = path
                if(parentnode.nodetype==NODE_OBJECT):
                    count = len(parentnode.values)
                    i=0
                    while(i<count):
                        if(parentnode.values[i].name==path):
                            if(parentnode.values[i].node!=None):
                                node = parentnode.values[i].node
                            else:
                                node = parentnode
                            break
                elif(parentnode.nodetype==NODE_ARRAY):
                    if(index>=0 and index<len(parentnode.values)):
                        if(parentnode.values[index].node!=None):
                            return parentnode.values[index].node
                        else:
                            return parentnode
        return node





 
 
if __name__=="__main__":
    v =JsonValue()
    v.name ="abc"
    v.vstr = "1234"
    v.valuetype =VALUE_NUM_INT    
    print(v.ToString())
    
    ejson =PyEasyJson()
    ejson.ParseString("{\"abcd\":1234,\"efgh\":[999,666]}")
    print(ejson.ToString())
    
    ejson.ParseString("{/*this is test comment*/\"firstName\":\"Bret\\b\\t\\\"t\\u9001\"}")
    print(ejson.ToString())
 
    ejson.ParseString("//thiis commentline \
{\"firstName\":\"Brett\",/*this is test comment*/\"lastName\" : \"McLaughlin\",\"email\" : \"aaaa\" }")
    print(ejson.ToString())
    
    ejson2=PyEasyJson()
    ejson2.ParseString("{\"abc\":{\"x\": true,\"y\": false},\"key\":[1,2,true,false,4,4.90241,{},22013,14],\"xxx\":{\"y\":{ },\"z\":{ },\"abc\":{},\"def\":null},\"qwr\": [48559,{},\"abc\",true]}")
    print(ejson2.ToString())
    
    




