import markdown
from django.http import HttpResponse, HttpResponseNotFound ##HttpResponseBadRequest, HttpResponseRedirect

VERSION="2.0.1 (#10+)" ##Rename and data entry can be processed remotely (with web interface)"
VERSION="2.1.3 (#45+) alpha"
VERSION="2.1.3 alpha" ## 2024-05-08 (bzr:revno #50+)

HTML_="""<html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/> 
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
      <meta name="keywords" content=""/>
      <title>Salicicola PhotoDB: Data Entry</title>
      <!--<link rel="stylesheet" type="text/css" href="/static/CSS/main.css"/>-->
      <style type="text/css">
      body {
        background-color:#F0FFF0;
        padding:1ex;
        color: #8B0000;
        max-width:1500px;
      }
      h2 {
        margin-bottom:0;
        padding-bottom:0;
      }
      h2 + p {
        margin-top:0;
      }
      h2 + ul {
        margin-top:0;
      }
      h2 + ol {
        margin-top:0; /* FIXME */
      }
      a {
        color:red;
      }
      img {
        width:600px;
        float:right;
      }
    </style>
    </head>
    <body>
    """
def show_readme(request):
    html = HTML_
    txt = open("README.md").read()
    html += markdown.markdown(txt)
    html += """<hr align="left" width="33%"/>"""
    html += "Version: <i>%s</i>" % VERSION
    html += "</body></html>"
    return HttpResponse(html)

def docker_readme(request):
    try:
        html = HTML_
        txt = open("data/static/documents/README_DOCKER_DESKTOP.md").read()
        html += markdown.markdown(txt)
        html += """<hr align="left" width="33%"/>"""
        txt = open("data/static/documents/README_DOCKER.md").read()
        html += markdown.markdown(txt)
        html += """<hr align="left" width="33%"/>"""
        try:
           txt = open("data/static/documents/README_DOCKER_COMPOSE.md").read()
           if txt and len(txt) > 30:
               html += markdown.markdown(txt)
               html += """<hr align="left" width="33%"/>"""
        except:
            print ("docker compose readme is not available")
        html += "Version: <i>%s</i>" % VERSION
        html += "</body></html>"
        return HttpResponse(html)
    except:
        return HttpResponseNotFound("Something wrong: resource not found")
