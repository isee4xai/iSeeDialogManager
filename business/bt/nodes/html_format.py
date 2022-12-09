def persona(p):
    st = '<div class=\"persona\">'
    st += "<p class=\"persona-name\">"+p["Name"]+"</p>"
    st += " ".join(["<p class=\"persona-prop\">"+_k+": "+_v+"</p>" for _k,_v in p.items() if _k != "Name"])
    st+= "</div>"
    return st

def target(df):
    st = '<div class=\"target-prediction\">'
    st += df.to_html(index=False)
    st += "</div>"
    return st

def explanation(explainer_result, output_description):
    st ='<a href=\"'+explainer_result["plot_png"]+'\" target=\"_blank\"><img src=\"'+explainer_result["plot_png"]+'\"style=\" width: 600px; margin-bottom: -200px; margin-right: -50px;\"></a>'
    st +='<p><strong>Explanation Description:</strong> <br>'+output_description+'</p>'
    return st