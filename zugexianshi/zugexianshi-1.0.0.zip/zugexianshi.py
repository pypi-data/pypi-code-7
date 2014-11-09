def zugexianshi(liebiao):
    for liebiaoxian in liebiao:
        if isinstance(liebiaoxian,list):
            zugexianshi(liebiaoxian)
        else:
            print(liebiaoxian)
