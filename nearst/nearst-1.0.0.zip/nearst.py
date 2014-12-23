def print_lol(the_list): #the_list 是個變數，隨你取名；當你執行lol(movies) 就會進行以下動作。' 
        for each_item in the_list:
                if isinstance (each_item,list):
                        print_lol(each_item)
                else:
                        print each_item
