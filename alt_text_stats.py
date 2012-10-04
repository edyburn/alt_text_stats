import requests
import html5lib
import re
import csv

URL_FILE = "urls.csv"
OUTPUT_AGGREGATE_FILE = "aggregate.txt"
OUTPUT_DETAIL_FILE = "detail.txt"

def parse_url_file(path):
    fh = open(path, 'r')
    reader = csv.reader(fh)
    urls = []
    for i, row in zip(range(200), reader):
        urls.append('http://' + row[1])
    fh.close()
    return urls

def check_page(url):
    print "Checking: %s" % url
    r = requests.get(url)
    h = html5lib.parse(r.text, treebuilder='dom')
    results = []
    for img in h.getElementsByTagName('img'):
        print "processing image"
        results.append(check_img(img, url))
    return results
   
def check_img(img, page_url=None):
    i = {
        'src': img.getAttribute('src'),
        'has_alt': img.hasAttribute('alt'),
        'has_title': img.hasAttribute('title'),
        'has_longdesc': img.hasAttribute('longdesc'),
        'alt_blank': False,
        'alt_filename_equal': False,
        'alt_title_equal': False,
        'longdesc_blank': False,
        'longdesc_anchor': False,
        'longdesc_not_url': False,
        'longdesc_invalid': False,
        'longdesc_src_equal': False,
        'longdesc_page_equal': False,
        'longdesc_domain_root': False,
        'longdesc_parent_link_equal': False,
        'alt_content': '~N/A~',
        'title_content': '~N/A~',
        'longdesc_content': '~N/A~'
    }
    
    if i['has_alt']:
        i['alt_content'] = img.getAttribute('alt').encode('ascii', 'backslashreplace')
        if i['alt_content'] == '':
            i['alt_blank'] = True
        if '/' in i['src'] and i['alt_content'] == i['src'].rsplit('/', 1)[1]:
            i['alt_filename_equal'] = True
    if i['has_title']:
        i['title_content'] = img.getAttribute('title').encode('ascii', 'backslashreplace')
    if i['has_alt'] and i['has_title']:
        if i['alt_content'] == i['title_content']:
            i['alt_title_equal'] = True
    if i['has_longdesc']:
        i['longdesc_content'] = img.getAttribute('longdesc').encode('ascii', 'backslashreplace')
        if i['longdesc_content'] == '':
            i['longdesc_blank'] = True
        if i['longdesc_content'].startswith('//'):
            # fix relative protocol urls
            i['longdesc_content'] = 'http:' + i['longdesc_content']
        if i['longdesc_content'].startswith('#'):
            i['longdesc_anchor'] = True
        else:
            try:
                longdesc_r = requests.get(i['longdesc_content'])
                if longdesc_r.status_code != requests.codes.ok:
                    i['longdesc_invalid'] = True
            except requests.exceptions.MissingSchema:
                i['longdesc_not_url'] = True
        if i['longdesc_content'] == i['src']:
            i['longdesc_src_equal'] = True
        if i['longdesc_content'] == page_url:
            i['longdesc_page_equal'] = True
        if re.match('.+://[^/]+/?$', i['longdesc_content']):
            i['longdesc_domain_root'] = True
        current_node = img.parentNode
        keep_checking = True
        parent_link = None
        while keep_checking:
            if current_node.tagName == 'body':
                break
            elif current_node.tagName == 'a':
                if current_node.hasAttribute('href'):
                    parent_link = current_node.getAttribute('href')
                    break
            current_node = current_node.parentNode
        if i['longdesc_content'] == parent_link:
            i['longdesc_parent_link_equal'] = True

    return i

def aggregate_results(url, results):
    fields_to_aggregate = ['has_alt', 'has_title', 'has_longdesc', 'alt_blank',
                           'alt_filename_equal', 'alt_title_equal', 'longdesc_blank',
                           'longdesc_anchor', 'longdesc_not_url', 'longdesc_invalid',
                           'longdesc_src_equal', 'longdesc_page_equal',
                           'longdesc_domain_root', 'longdesc_parent_link_equal']
    aggregate_results = [url, len(results)]
    for field in fields_to_aggregate:
        aggregate_results.append(reduce(lambda x, y: x+1 if y[field] else x,
                                          results, 0))
    return aggregate_results

def write_results(urls, all_results):
    # dump summary and detailed results to a file
    a_fh = open(OUTPUT_AGGREGATE_FILE, 'w')
    a_w = csv.writer(a_fh, dialect='excel-tab')
    d_fh = open(OUTPUT_DETAIL_FILE, 'w')
    d_w = csv.writer(d_fh, dialect='excel-tab')

    #headings
    a_headings = ['url', 'total_images', 'has_alt', 'has_title', 'has_longdesc',
                  'alt_blank', 'alt_filename_equal', 'alt_title_equal',
                  'longdesc_blank','longdesc_anchor', 'longdesc_not_url',
                  'longdesc_invalid','longdesc_src_equal',
                  'longdesc_page_equal','longdesc_domain_root',
                  'longdesc_parent_link_equal']
    a_w.writerow(a_headings)
    d_headings = ['src', 'has_alt', 'has_title', 'has_longdesc',
                  'alt_blank', 'alt_filename_equal', 'alt_title_equal',
                  'longdesc_blank','longdesc_anchor', 'longdesc_not_url',
                  'longdesc_invalid','longdesc_src_equal',
                  'longdesc_page_equal','longdesc_domain_root',
                  'longdesc_parent_link_equal', 'alt_content', 'title_content',
                  'longdesc_content']

    # write data
    for url, results in zip(urls, all_results):
        a_w.writerow(aggregate_results(url, results))
        d_w.writerow([url])
        d_w.writerow(d_headings)
        for result in results:
            result_row = []
            for col in d_headings:
                result_row.append(result[col])
            d_w.writerow(result_row)

    a_fh.close()
    d_fh.close()

def generate_stats():
    # parse url list
    urls = parse_url_file(URL_FILE)
    # check urls
    all_results = []
    for url in urls:
        try:
            all_results.append(check_page(url))
        except:
            print "Skipping %s" % url
    # save results
    write_results(urls, all_results)

if __name__ == "main":
    pass

