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
                treemap[networks1[network1]]["values"][networks2[network2]]["values"].append(user.treemap_layout())
            else:
                treemap[networks1[network1]]["values"].append({
                                                                 "key":network2,
                                                                 "values":[user.treemap_layout()]
                                                                 })
                networks2[network2] = len(treemap[networks1[network1]]["values"])-1
        else:
            treemap.append({
                            "key" : network1,
                            "values":[{
                                        "key":network2,
                                        "values":[user.treemap_layout()]
                                        }]
                            })
            networks1[network1] = len(treemap)-1

    return treemap
