def get_treemap(users):
    
    network1 = ""
    network2 = ""
    networks1 = {}
    networks2 = {}
    treemap = []
    
    for user in users:
        network1 = ".".join(user.address.split(".")[:2])
        network2 = ".".join(user.address.split(".")[:3])
        if network1 in networks1:
            if network2 in networks2:
                treemap[networks1[network1]]["children"][networks2[network2]]["children"].append(user.treemap_layout())
            else:
                treemap[networks1[network1]]["children"].append({
                                                                 "name":network2,
                                                                 "children":[user.treemap_layout()]
                                                                 })
                networks2[network2] = len(treemap[networks1[network1]]["children"])-1
        else:
            treemap.append({ 
                            "name" : network1,
                            "children":[{
                                        "name":network2,
                                        "children":[user.treemap_layout()]
                                        }]
                            })
            networks1[network1] = len(treemap)-1
            
    return treemap