
# import objc
# from rubicon.objc import ObjCClass
# # from pygments.lexers import LEXERS
# # from pygments.token import Token



# import ctypes
# from ctypes import c_void_p, c_char_p, c_bool
# from objc import runtime

# def is_ios_system_class(class_name):
#     NSObject = ObjCClass('NSObject')
#     try:
#         cls = ObjCClass(class_name)
#     except:
#         return False
#     return issubclass(cls, NSObject)

# if __name__ == '__main__':
#     class_name = 'Array'
#     is_system_class = is_swift_system_class(class_name)
#     print(f"Is {class_name} a system class? {is_system_class}")

import click

@click.command()
@click.option('-name',default='World',help='The name of the person to greet.',type=str)
@click.option('-count',default=1,help='The number of times to greet.',type=int)
def hello(name,count):
    for i in range(count):
        click.echo(f'Hello {name}!')




if __name__ == '__main__':
    hello()