import logging
import urllib2
import urllib
import requests
import json
from StringIO import StringIO
import gzip

#TODO: to implement
def query_wikipedia(query):
    raise Exception('not implemented')

#TODO: to implement
def query_flickr(query):
    raise Exception('not implemented')

def query_microsoft_graph(query, top=10):
    try:
        url = 'https://concept.research.microsoft.com/api/Concept/ScoreByProb?instance={}&topK={}'.format(query, top)
        #urllib2.urlopen(url).read()
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception ('error when querying microsoft graph! status code = ' + r.status_code)
        return r.json()

    except Exception as e:
        raise e

def query_bing(query, key, top, market='en-us', safe='Moderate', source='Web', version='v5'):
    if version == 'v2':
        return __bing_api2(query, key, top, market, source)
    elif version =='v5':
        return __bing_api5(query, key, top, market, safe)
    else:
        raise Exception('bing api version not implemented')
		
def query_babelnet(word, key, srcLang='EN'):

    url='https://babelnet.io/v5/getVersion?key=%s' % (key)
    result = __request_babelnet_url(url)
    if result is None:
        return word, None, None
    elif result['version'] == 'V4_0':
        return __babelnet_api4(word, key, srcLang)
    else:
        raise Exception('babelnet api version not implemented')
 

def __bing_api5(query, key, top, market, safe):
    # https://msdn.microsoft.com/en-us/library/dn760794(v=bsynd.50).aspx
    try:
        txts = None
        imgs = None
        url = 'https://api.cognitive.microsoft.com/bing/v5.0/search'
        # query string parameters
        if top != 0:
            payload = {'q': query, 'mkt': market, 'count': top, 'offset': 0, 'safesearch': safe}
        else:
            payload = {'q': query, 'mkt': market, 'offset': 0, 'safesearch': safe}
        # custom headers
        headers = {'Ocp-Apim-Subscription-Key': key}
        # make GET request
        r = requests.get(url, params=payload, headers=headers)
        # get JSON response
        try:
            if r.status_code != 200:
                raise Exception (':: problem when querying Bing! Status code = ' + r.status_code)
            txts = r.json().get('webPages', {}).get('value', {})
            imgs = r.json().get('images', {}).get('value', {})

        except Exception as e:
            logging.error(':: error on retrieving search results: ', e)

        return query, txts, imgs
    except Exception as e:
        print (':: an error has occurred: ', e)
        return query, None

def __bing_api2(query, key, top, market, source):

    try:
        format = 'json'
        keyBing = key  # get Bing key from: https://datamarket.azure.com/account/keys
        credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[
                                    :-1]  # the "-1" is to remove the trailing "\n" which encode adds
        query = '%27' + urllib.quote(query) + '%27'
        market = '%27' + urllib.quote(market) + '%27'
        offset = 0

        url = 'https://api.datamarket.azure.com/Bing/Search/' + source + \
              '?Query=%s&Market=%s&$top=%d&$skip=%d&$format=json' % (query, market, int(top), offset)

        request = urllib2.Request(url)
        request.add_header('Authorization', credentialBing)
        requestOpener = urllib2.build_opener()
        response = requestOpener.open(request)

        results = json.load(response)

        if response.code != 200:
            return query, None
        else:
            return query, results

    except Exception as e:
        print (':: an error has occurred: ', e)
        return query, None




'''
def bing_api(query, api, source_type="Web", top=10, format='json', market='en-US'):
    """Returns the decoded json response content
    :param query: query for search
    :param source_type: type for seacrh result
    :param top: number of search result
    :param format: format of search result
    :param market: market of search result
    """
    try:
        # set search url
        query = '%27' + urllib.quote(query) + '%27'
        market2 = '%27' + urllib.quote(market) + '%27'
        # web result only base url
        base_url = 'https://api.datamarket.azure.com/Bing/Search/' + source_type
        url = base_url + '?Query=' + query + '&Market=' + market2 + '&$top=' + str(top) + '&$format=' + format

        # create credential for authentication
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/42.0.2311.135 Safari/537.36"

        urllib3.disable_warnings()
        http = urllib3.PoolManager(num_pools=10)
        headers = urllib3.util.make_headers(user_agent=user_agent, basic_auth='{}:{}'.format(api, api))
        resp = http.request('GET',
                            url=url,
                            headers=headers)
        jsonobject = json.loads(resp.data.decode('utf-8'))

        if resp.status != 200:
            return query, None
        else:
            return query, jsonobject

    except Exception as e:
        logging.error(':: an error has occurred: ', e)
        raise
'''

def __request_babelnet_url(url):
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    requestOpener = urllib2.build_opener()
    response = requestOpener.open(request)

    if response.code != 200:
        return None

    if response.info().get('Content-Encoding') ==  'gzip':
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj = buf)
        results = json.loads(f.read())
        return results

    return None

def __babelnet_api4(word, key, srcLang):

    #try:
        url = 'https://babelnet.io/v5/getSynsetIds?'+ \
              'lemma=%s&searchLang=%s&key=%s' % (word, srcLang, key)

        results = __request_babelnet_url(url)
        if results is None:
            return word, None, None

        resulttxts = []
        resultimgs = []
        for result in results:
            suburl = 'https://babelnet.io/v5/getSynset?' + \
                'id=%s&key=%s' % (result['id'], key)

            subresult = __request_babelnet_url(suburl)
            if subresult is None:
                continue
            resulttxt = {}
            resulttxt['id'] = result['id']
            resulttxt['name'] = subresult['mainSense']
            resulttxt['displayUrl'] = 'live.babelnet.org/synset?word=%s&lang=%s' % (result['id'], srcLang)#''    #nothing found which could equals the meaning in bing.
            glosses = subresult['glosses']
            if len(glosses) > 0:
                resulttxt['snippet'] = glosses[0]['gloss']
            else:	
                resulttxt['snippet'] = ''

            resulttxts.append(resulttxt)
            resultimg ={}
            images = subresult['images']
            if len(images) > 0:
                resultimg['contentUrl'] = images[0]['url']
                resultimg['thumbnailUrl'] = images[0]['thumbUrl']
                resultimg['name'] = images[0]['name']
            else:
                resultimg['contentUrl'] = ''
                resultimg['thumbnailUrl'] = ''
                resultimg['name'] = ''
				
            resultimg['encodingFormat'] = ''        #no information given 
            resultimg['width'] = ''     #no information given
            resultimg['height'] = ''    #no information given
			
            resultimgs.append(resultimg)
        return word, resulttxts, resultimgs

    #except Exception as e:
    #    print (':: an error has occurred: ', e)
    #    return word, None, None

def main():
    out = query_microsoft_graph('microsoft', 10)

if __name__ == "__main__":
    main()
