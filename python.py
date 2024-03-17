import pandas as pd
from pandas import *
from underthesea import pos_tag #tách từ
from normalization import *
import re
import urllib
import json
import os
from flask import Flask
from flask import request
from flask import make_response
import math 
import re
import random
import csv
import datetime
import redis

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "underthesea":
        return()
    result = req.get("result")
    Input = result.get("resolvedQuery")

    def score(q, d):
        ret = 0
        for t in q:
            ret += (tf(t, d) * idf(t))
        return ret

    def keys_solve(string):
        string = string.lower()
        string = string.replace(",", " ").replace(".", " ").replace(";", " ").replace("“", " ").replace(":", " ").replace("”", " ").replace('"', " ").replace("'", " ").replace("!", " ").replace("?", "").replace("[", " ").replace("]", " ").replace("'"," ")
        keys_before = pos_tag(string)    
        keys_filled=list()
        keys_after=dict()
        e = 0
        while (e < len(keys_before)): 
            keys_remove = keys_before[e]
            if keys_remove[1] not in ("E","L","Np","C"): 
                keys_filled.append(keys_remove[0])
            e += 1 
        keys_after["Input"] = keys_filled  
        keys_after = list(keys_after["Input"])
        long = len(keys_after)
        return keys_after
        

    def tf(word,d):
        return d.count(word) /len(d)

    def idf(word):
        count_in_document = 0 
        for d in D:
            if word in d:
                count_in_document +=1
        return 0 if count_in_document == 0 else math.log(len(D)/float(count_in_document))

    def score(q, d):
        ret = 0
        for t in q:
            ret += (tf(t, d) * idf(t))
        return ret
     
##############################################################
    welcomex = ["Chào bạn !",
           "Chào bạn, mình là Dubo, rất vui được trò chuyện với bạn !", 
           "Dubo xin chào bạn ! Rất vui được gặp bạn. ", 
           "Xin chào !"]
##############################################################    
    #Xử lý xin chào..
    last_checking = False
    welcomeback = " "
    welcome = Input.split(" ")
    prepare_welcome = "xin chào hello hi alo hello"
    welcome_data = prepare_welcome.split(" ")
    for index in welcome:
        for index2 in welcome_data:
            if index == index2 or "xin chào" in Input or "Xin chào" in Input:
                welcomeback = random.choice(welcomex)  
                last_checking = True
                break
 
    #a) - Input 
    question_keys = keys_solve(Input)
    query = question_keys
    
    #b) - Word
    #Mapping 
    df = pd.read_csv("./data/QA.txt", names=["row"], encoding="utf8", sep = "$") #sep="."
    mt_df = df.as_matrix()
    mapmap = DataFrame(columns=["Câu hỏi","Câu hỏi bổ sung","Tổng hợp","Câu trả lời"])

    ans = []
    i = row_num = 0
    while (i<len(mt_df)):
        string = str(mt_df[i])
        if "?" in string:
            row_num +=1
            string = string.replace("[","").replace("]","").replace("'","").replace("\\t"," ")
            mapmap.loc[row_num,"Câu hỏi"] = string
            ans = []
            y = i +1
            while (y <len(mt_df)):
                string2 = str(mt_df[y])
                if "?" not in string2:
                    ans.append(string2)
                else:
                    break
                y +=1
            ans = "\n\n".join(ans)
            ans = ans.replace("[","").replace("]","").replace("'","").replace("\\t"," ")
            mapmap.loc[row_num,"Câu trả lời"] = ans
        i+=1
        
    #BỔ SUNG Q PHẨY VÀO BẢNG
    with open("./data/40.csv", encoding='utf-8') as csvfile:
        content = csv.reader(csvfile)
        for column in content:
            mina = len(column)

    colnames = list()
    ten = "qphay"
    i = 1
    while (i<=mina):
        name = ten+str(i)
        colnames.append(name) #Lấy ra tên cột, cột 1 là qphay1
        #print(colnames)
        i+=1

    with open("./data/40.csv", encoding='utf-8') as csvfile:
        content = csv.reader(csvfile)
        for column in content:
            mina = len(column)    
    data = pandas.read_csv('./data/40.csv', names=colnames)
    data.sort_index()
    i=0
    dfs = qphay = list()
    while (i<mina):
        name = ten+str(i+1)
        dfs= data.loc[1:,name]
        qphay= dfs.tolist()
        mapmap.loc[i+1,"Câu hỏi bổ sung"] = qphay
        i+=1    
        
    tonghop = []    
    y = 0
    while (y<len(mapmap)):
        cauhoi = mapmap.loc[y+1,"Câu hỏi"]
        tonghop = mapmap.loc[y+1,"Câu hỏi bổ sung"]
        tonghop.append(cauhoi)
        mapmap.loc[y+1,"Tổng hợp"] = tonghop
        y+=1
###################################################
    falseans = ["Mình chưa hiểu lắm, bạn có thể hỏi rõ hơn được không ?",
           "Mình nhận được tin nhắn của bạn rồi :) nhưng mình vẫn chưa hình dung ra, bạn hỏi kĩ hơn chút nha ?", 
           "Câu này khó hiểu quá, bạn nói thêm được không ? ", 
           "Mình không chắc là mình hiểu thắc mắc của bạn, hỏi lại kĩ hơn giúp mình nhé ?",
           "Xin lỗi.. cách diễn đạt của bạn hơi khó hiểu với mình, thử lại giúp mình nha ",
           "Thật sự là mình vẫn chưa nắm được ý của bạn, bạn hỏi chi tiết hơn giúp mình nha ? ",
           "Mình khá bất ngờ với tin nhắn này... mình chưa hiểu lắm, bạn diễn đạt cụ thể hơn thử xem ?",
           "Câu hỏi của bạn có vẻ lạ lạ, bạn thử diễn đạt kĩ hơn giúp mình nhé ? "]
    none = random.choice(falseans)   
###################################################    
    recommend_data = ["Bạn có thắc mắc gì mình cứ nói với mình, mình sẽ giải đáp cho bạn nha. ",
           "Không biết mấy câu mình gợi ý có đúng ý bạn không, cứ thoải mái hỏi mình nha, mình sẽ hỗ trợ hết sức.", 
           "Bạn muốn hỏi gì cứ nói với mình nha, mình sẽ giúp bạn giải đáp thắc mắc.", 
           "Mình có thể giúp bạn giải đáp thắc mắc của bạn không ? Gõ câu hỏi của bạn ra nhé :D"]
###################################################

    D = [] 
    xxx = []
    i = 0
    while (i < len(mapmap)):
        takeout = mapmap.loc[i+1, "Tổng hợp" ] 
        k = 0
        while (k < len(takeout)):
            z = takeout[k]
            #print("Z nè: ",z)
            if type(z) is str :
                m = keys_solve(z)
                if m != 0 :
                    D.append(m)
                xxx.append(z)
            k +=1
        i+=1            
    
    scores ={}
    i=0
    for d in D:
        sc= score(query,d)
        scores[i]=sc 
        i+=1
    top_docs= sorted(scores, key=scores.get, reverse=True)[:1]
    i = 0
    for i in top_docs:
        if scores[i] > 1.3:
            x = 0
            while (x<len(mapmap)):
                if xxx[i] in mapmap.loc[x+1,"Tổng hợp"]:
                    answerfinal = mapmap.loc[x+1,"Câu trả lời"]
                x+=1
            answer = answerfinal
            break
        elif scores[i] >=0.8:
            D = []
            i = 1
            while (i < len(mapmap)+1):
                string = mapmap.loc[i, "Câu hỏi"] 
                if type(string) is str :
                    string = keys_solve(string)
                    if string != 0 :
                        D.append(string)
                i+=1
            scores2 ={}
            i = 0
            for d in D:
                sc= score(query,d)
                scores2[i]=sc
                i+=1  
            top_docs2= sorted(scores2, key=scores2.get, reverse=True)[:2]
            chec = 0
            recommend_sentence = ("Có phải bạn muốn hỏi : \n\n")
            recommends = [ ]
            for chec in top_docs2:
                recommends.append(mapmap.loc[chec+1,"Câu hỏi"])
                recommends.append("&")
                chec +=1
            recommends = str(recommends)
            recommend_asking = random.choice(recommend_data)      
            recommends = recommends.replace("["," ").replace("]"," ").replace("'"," ").replace("&","\n").replace(",","\n")
            answer = recommend_sentence + recommends + recommend_asking
        else :
            out = {}
            now = datetime.datetime.now()
            current = str(now.day)+"/"+str(now.month)+"/"+str(now.year)+"|"+str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            out[current] = str(Input)
            with open('./json/storage.json',encoding='utf-8') as f:
                data = json.load(f)
            data.update(out)
            with open('./json/storage.json','w',encoding='utf-8') as f:
                json.dump(data, f,indent=2, ensure_ascii=False)
            answer = none
            break 
    
###
    if len(Input) < 9 and last_checking == True:
        speech = welcomeback
    else:
        speech = welcomeback +" \n" + answer
###
         
    print(speech)
    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        #"contextOut": [],
        "source": "Tach_tu"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 88))

    print ("Starting app on port %d" %(port))

    app.run(debug=True, port=port, host='0.0.0.0')
