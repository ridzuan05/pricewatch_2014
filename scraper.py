import scraperwiki
import time
import json
import random
import lxml.html
import requests

base_url = 'http://www.1pengguna.com/11pengguna/'

def get_options(page, cssid):
    select_options = page.cssselect(cssid)
    options = []
    for count, option in enumerate(select_options):
        if count == 0:
            continue
        options.append([option.values()[0], option.text_content()])
    return options

def get_kawasan(kod_negeri):
    params = "neg=" + kod_negeri
    url = base_url + 'index.php?pg=mysearch/ajax_kawasan&hd=0&' + params
    #print "\t", url
    resp = requests.get(url)
    page = lxml.html.fromstring(resp.content)
    kawasan_options = get_options(page, '#KodKawasan > option')
    kawasan = []
    for option in kawasan_options:
        kawasan.append([option[0], option[1]])
    return kawasan

html = requests.get(base_url).content
page = lxml.html.fromstring(html)

select_options = get_options(page, '#negeri > option')
for count, option in enumerate(select_options):
    kod_negeri = option[0]
    nama_negeri = option[1]
    kawasan = get_kawasan(kod_negeri)
    
    for kaw in kawasan:
        area_list = {
            'kod_negeri': kod_negeri,
            'nama_negeri': nama_negeri,
            'kod_kawasan': kaw[0],
            'nama_kawasan': kaw[1],
        }

html = requests.get(base_url).content
#html = open('result.html').read()
page = lxml.html.fromstring(html)

select_options = get_options(page, '#KodBrg > option')
for count, option in enumerate(select_options):
    kod_barang = option[0]
    nama_barang = option[1]

    if kod_barang.isdigit() == True:
        item_list = {
            'kod_barang': kod_barang,
            'nama_barang': nama_barang,
        }

headers = {
    'Referer': base_url,
}

# random_seconds = [1, 5, 10, 12, 11, 15]
# for item in item_list[4:]:
for item in item_list:
    for area in area_list:
        data = {
            'KodBrg': item['kod_barang'],
            'negeri': area['kod_negeri'],
            'KodKawasan': area['kod_kawasan'],
        }
        
        url = base_url + 'index.php?pg=mysearch/result_search#content'

        try:
            resp = requests.post(url, data, headers=headers)
        except Exception as e:
            print e
            continue

        html = resp.content
        page = lxml.html.fromstring(html)
        table = page.cssselect('#content table')[0]
        product = {}
        product['kod_barang'] = item['kod_barang']
        product['kod_negeri'] = area['kod_negeri']
        product['kod_kawasan'] = area['kod_kawasan']
        for count, tr in enumerate(table.getchildren()):
            if count == 0:
                product['tarikh'] = tr.getchildren()[0].text.split(':')[-1].strip()
                continue
            if count == 1:
                product['nama'] = tr.getchildren()[0].text.split(':')[-1].strip()
                continue
            if count == 2:
                continue
            
            try:
                cat_img = tr.getchildren()[1].cssselect('img')[0].items()[0][1]
                cat = cat_img.split('/')[-1]
                premise = tr.getchildren()[2].text
                price = tr.getchildren()[4].text
                product['kategori'] = cat
                product['premis'] = premise
                product['harga'] = price
            except Exception as e:
                print e
                continue

            scraperwiki.sqlite.save(unique_keys=['kod_barang', 'kod_negeri', 'kod_kawasan', 'premis', 'tarikh'], data=product)
            print product
            # second = random.choice(random_seconds)
            # print 'Sleep %ds' % second
            # time.sleep(second)
