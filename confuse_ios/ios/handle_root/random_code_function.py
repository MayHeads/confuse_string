import os
import sys
import random
sys.path.append("./")
from ios.log import random_strs

def getMethodNamne():
  return random_strs.camel_case_fun_name()

def getVarriable():
  return random_strs.get_one_or_two_nonu_words()[0]

def keys():
   total = []
   for x in range(20):
      total.append(f"name{x}")
   return total


def templatelists():
   return [
    """
    func name10() {
        let name2 = "name1name2name3"
        var name3 = ""
        
        for name4 in name2 {
            let name5 = String(Character(UnicodeScalar(Int.random(in: 97...122))!))
            name3.append(name4)
            name3.append(name5)
        }
        
        if name3.count > 3 {
            let name6 = name3.index(name3.startIndex, offsetBy: 3)
            let name7 = String(name3[name6...])
        } else {
            let name8 = name3
        }
    }
    """,
    """
    func name15() {
        var name1 = "name2name3name4"
        var name2 = 0
        let name3 = 200
        for name4 in 0...name3  {
            name2 += name4
        }
    }
    """
   ]


def c_generate_code_random_method():
#     template = """
#     func methodName() {
#         var name = "xxx"
#         var count = 0
#         let all = 200
#         for index in 0...all  {
#             count += index
#         }
#         print(count)
#     }
# """
#     r_method = getMethodNamne()
#     template = template.replace("methodName", r_method)
#     replaces = ["name", "xxx", "count", "all", "index"]
#     for x in replaces:
#       template = template.replace(x, getVarriable())
#     print(template)
#     return template
    
    

    x = random.choice(templatelists())
    y = keys()
    for item in y:
        x = x.replace(item, getVarriable())
    return x
       




if __name__=='__main__':

    y = c_generate_code_random_method()



