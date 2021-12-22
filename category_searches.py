import json

def highest_usd_pledged_search():##FIX ME
    fileInstance = open('ks-projects-201801.json',encoding = "utf-8-sig")
    #fileInstance = open(r'parser\Files\output\2018ksprojects.json',encoding = "utf-8-sig")
    data = json.load(fileInstance) 

    projs = [data[0]]
    largestNumber = float(0)

    for proj in data:
        if proj['usd pledged'] != "": # makes sure that any empty usd pledged is ignored
            if float(proj['usd pledged']) > largestNumber:
                projs[0] = proj
                largestNumber = float(proj['usd pledged'])

    fileInstance.close()
    return projs  #(at this point the return data is loaded with every entry of the desired state)
