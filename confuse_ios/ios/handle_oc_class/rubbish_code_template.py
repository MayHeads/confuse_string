import random

random_texts = [
    '''double R_LOCAL_IVAR_1 = %s;\n
       while (R_LOCAL_IVAR_1 >= %s) { break; }''' % (random.uniform(1, 1000), random.uniform(1, 1000)),

    '''double R_LOCAL_IVAR_1 = %s;\n
       while (R_LOCAL_IVAR_1 < %s) { break; }''' % (random.uniform(1, 1000), random.uniform(1, 1000)),

    '''float R_LOCAL_IVAR_1 = %s;\n
       while (R_LOCAL_IVAR_1 >= %s) { break; }''' % (random.uniform(1, 1000), random.uniform(1, 1000)),

    '''float R_LOCAL_IVAR_1 = %s;\n
       while (R_LOCAL_IVAR_1 < %s) { break; }''' % (random.uniform(1, 1000), random.uniform(1, 1000)),

    '''int R_LOCAL_IVAR_1 = %s;\n
       while (R_LOCAL_IVAR_1 >= %s) { break; }''' % (random.uniform(1, 1000), random.uniform(1, 1000)),

    '''int R_LOCAL_IVAR_1 = %s;\n
       while (R_LOCAL_IVAR_1 < %s) { break; }''' % (random.uniform(1, 1000), random.uniform(1, 1000)),

]