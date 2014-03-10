import models

def get_config(platform):
    config = None
    if(platform == 'mobile'):
        config = models.mobile_config.objects.order_by('-id')[0]
    elif(platform == 'pc'):
        config = models.pc_config.objects.order_by('-id')[0]  
    return config
