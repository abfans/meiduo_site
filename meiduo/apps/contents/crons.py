import os
from django.conf import settings

from django.shortcuts import render
from .models import ContentCategory,Content
from utils.category import category_list

def generate_static_index_html():
    categories = category_list()
    contents ={}
    content_categories = ContentCategory.objects.all()
    for cons in content_categories:
        contents[cons.key] = cons.content_set.filter(status =True).order_by('sequence')

    renders = render(None,"index.html",context={"categories":categories,"contents":contents})
    html_con = renders.content.decode()
    html_path = os.path.join(settings.GENERATE_STATIC_HTML,"index.html")
    with open(html_path,"w") as f:
        f.write(html_con)