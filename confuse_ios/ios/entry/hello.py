from guizero import App,Box,Text,ButtonGroup,CheckBox,PushButton
from tkinter import filedialog

ADD_P_PREFIX = ''
PROJECT_DICTIONARY = ''


class OptionItem:
    title:str
    tag:int
    selected:bool


    def __init__(self,title:str,tag:int,selected:bool):
        self.title = title
        self.tag = tag
        self.selected = selected


option_items = [
    OptionItem('添加类/文件名前缀',1,False),
    OptionItem('图片资源压缩/md5修改',2,False),
    OptionItem('插入垃圾代码',3,False),
    OptionItem('插入垃圾属性',4,False),
    OptionItem('修改类名',5,False),
]

def start_confuse():
    print("开始混淆")
    pass


class OptionItemsbox(Box):

    checkboxes = []

    

    def add_prefix(self):
        
        name = app.question("添加前缀", "混淆后项目的类/文件名前缀是?",initial_value="")
        if name is not None and len(name) != 0:
            print(name)
            ADD_P_PREFIX = f'{name}_'
        # else:
        #     app.info("提示", "请添加类/文件名前缀")

    def select_action(self,value,index):
        
        #遍历出对应item 并改值
        for item in option_items:
            if item.tag == value:
                item.selected = not item.selected
                
        
        checkbox = self.checkboxes[index]
        

        
        if value == 1:
            
            if checkbox.value == True:
                self.add_prefix()

        else:
            if value == 2:
                print('图片资源压缩/md5修改')
            elif value == 3:
                print('插入垃圾代码')
            elif value == 4:
                print('插入垃圾属性')
            elif value == 5:
                print('修改类名')
        
    #加载混淆配置
    def load_config(value):
        print('待开发')
    
    #加载混淆项目
    def load_project(value):
        directory_path = filedialog.askdirectory()
        if directory_path:
            print("Selected directory: ", directory_path)
            PROJECT_DICTIONARY = directory_path

    def start_obfuscate(value):
        start_confuse()


    def __init__(self,master,width,height,layout):
        super().__init__(master,width=width,height=height,layout=layout)
        
        top_margin_box = Box(self,width='fill',height=20,grid=[0,0])
        title_text = Text(self,text="混淆选项",width='fill',grid=[0,1],size=20,align='left',color='green')

        margin_box = Box(self,width='fill',height=10,grid=[0,2])

        items_box = Box(self,width='fill',grid=[0,3],layout='grid',align='left')

        
     

        index = 0
        
        for item in option_items:
            checkbox = CheckBox(items_box, text=item.title,grid=[0,index],align='left',args=[item.tag,index],command=self.select_action)
            checkbox.text_size = 15
            
            self.checkboxes.append(checkbox)
            index += 1

        margin_box = Box(self,width='fill',height=10,grid=[0,4])

        button_box = Box(self,width='fill',grid=[0,5],height=40,align='left',layout='grid')
        

        button = PushButton(button_box,text="加载混淆配置",align='left',grid=[0,0],command=self.load_config)
        button = PushButton(button_box,text="加载混淆项目",align='left',grid=[1,0],command=self.load_project)
        button = PushButton(button_box,text="开始混淆",align='left',grid=[0,1],command=self.start_obfuscate)



class LogBox(Box):
    def __init__(self,master,width,height,align):
        super().__init__(master,width=width,height=height,align=align)

if __name__ == '__main__':

    app_width = 800
    app_height = 800

    def on_resize():
        log_box.width = app.width-option_item_box.width
        log_box.height = app.height

        option_item_box.height = app.height


    def select_option_item():
        print(checkbox.value)

        
    #app
    app = App(title="Hello world",height=app_width,width=app_height,bg = "white")
    app.when_resized = on_resize
    
    #选择
    option_item_box = Box(app,width=400,height=app.height,align='left')
    option_item_box.bg = 'white'

    option_items_box = OptionItemsbox(option_item_box,width=option_item_box.width - 30,height=option_item_box.height,layout='grid')

    #日志
    log_box = LogBox(app,width=app.width-option_item_box.width,height=app.height,align='right')
    log_box.bg = 'black'



    app.display()


