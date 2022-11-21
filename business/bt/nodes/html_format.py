def persona(p):
    st = '<div class=\"persona\">'
    st += "<p class=\"persona-name\">"+p["Name"]+"</p>"
    st += " ".join(["<p class=\"persona-prop\">"+_k+": "+_v+"</p>" for _k,_v in p.items() if _k != "Name"])
    st+= "</div>"
    return st