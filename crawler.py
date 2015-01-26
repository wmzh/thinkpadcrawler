# -*- coding: utf-8 -*-
# #!/usr/bin/python
# @author: Wayne M Zhang<wayne.m.zhang@gmail.com>

# series:model:model number

import os.path
import urllib.request

from bs4 import BeautifulSoup
from pyh import *

site = 'http://www.thinkworldshop.com.cn'
url_series_helix = "http://www.thinkworldshop.com.cn/product/index/type/4/series_id/144/series_small_id/146.html"
series_list = []


def download_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def save_to_file(name, contents):
    f = open(name, "w", encoding='utf8')
    f.write(contents)
    f.close()


def get_bs_object(url, name, force):
    name += ".html"
    if os.path.exists(name) and (not force):
        file = open(name, encoding='utf8')
        bso = BeautifulSoup(file)
        file.close()
    else:
        html = download_html(url)
        bso = BeautifulSoup(html)
        save_to_file(name, bso.prettify())
    return bso


def get_model_parameter(model_number, force):
    name = model_number["id"]
    url = site + model_number["href"]
    bso = get_bs_object(url, name, force)
    div = bso.find("div", class_="content cc")
    for tr in div.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            model_number[tds[0].text.strip()] = tds[1].text.strip()


def generate_model_table_html(model):
    title = "All " + model["name"] + " Models"
    page = PyH(title)
    page.addCSS('colors.css')
    mytab = page << table()
    mytab << caption(title)
    mytab << colgroup(col())

    keyset = set()
    for m in model["model_numbers"]:
        keyset |= set(m.keys())

    keyset.remove('id')
    keyset.remove('href')

    cls = ['class_1', 'class_2', 'class_3', 'class_4', 'class_5',
           'class_6', 'class_7', 'class_8', 'class_9', 'class_10']

    mytr = mytab << tr()                                      # first row of the table
    mytr << td('Model Number', cl='td_key_model')        # model number as the first row
    for m in model["model_numbers"]:
        mytr << td(m['id'], cl='td_model')

    for key in keyset:
        mytr = mytab << tr()                                  # new table row for each key
        mytr << td(key, cl='td_key')                         # model number as the first td
        val_list = []
        for m in model["model_numbers"]:
            value = m.get(key, "N/A")
            if value == "N/A":
                mytr << td("N/A", cl='class_grey')
            elif value in val_list:
                mytr << td(' ', cl=cls[val_list.index(value)])
            else:
                mytr << td(value, cl=cls[len(val_list)])
                val_list.append(value)

    page.printOut(file=model["name"] + "_models.html")


# X240: 20AL001GCD,...
def get_model_number(model, force):
    model["model_numbers"] = []
    name = model["name"]
    url = site + model["href"]
    bso = get_bs_object(url, name, force)
    # find all tag dd with class attribute equals "tp " or "tp last"
    # <dd class="tp ">
    # <dd class="tp last">
    dds = bso.find_all('dd', class_=["tp", "last"])
    for dd in dds:
        div = dd.find('div')  # the only div tag, including the model number of thinkpad
        a = dd.find('a')
        model_number = {"id": div.string.strip().strip('()'), "href": a["href"]}
        model["model_numbers"].append(model_number)
        print("\t\t", model_number["id"])
        get_model_parameter(model_number, force)

    #if model['name'] == 'X240' or model['name'] == 'X240s':
    generate_model_table_html(model)


# Helix series: Helix, X1 Helix
# X series: X240, X240s,...
def get_main_model(sort, force):
    sort["models"] = []
    name = sort["name"]
    url = site + sort["href"]
    bso = get_bs_object(url, name, force)
    ul = bso.find("ul", id="p_sort")
    for a in ul.find_all("a"):
        model = {}
        model["name"] = a.text.strip()
        model["href"] = "/product/product_list/series_id/" + a["href"].split('/')[-1]
        sort["models"].append(model)
        print("\t", model["name"])
        get_model_number(model, force)


# Helix, X, X1, S, T, W, L, E, Tablet
def get_series(force=True):
    bso = get_bs_object(url_series_helix, "index", force)
    ul = bso.find("ul", id="p_tabs")
    for a in ul.find_all("a"):
        sort = {"name": a.contents[0].strip(), "href": a["href"]}
        series_list.append(sort)
        print("----------------------------------------------------------")
        print(sort["name"])
        get_main_model(sort, force)


if __name__ == '__main__':
    get_series(force=False)
