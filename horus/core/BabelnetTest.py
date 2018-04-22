from search_engines import query_babelnet

if __name__ == '__main__':
    #args[0], args[1], args[2], args[3]
    #HorusDemo().annotate_text('diego')
    metaquery, result_txts, result_imgs = query_babelnet('Dog', key='c624b573-6ed3-4039-88df-c8ca82ad980d')
    if len(result_txts) > 0:
        print "\nDescription:\n"
        keys = ['id', 'name', 'displayUrl', 'snippet']
        for key in keys:
            print '%s:\t%s' %(key, result_txts[0][key])
    if len(result_imgs) > 0:
        print "\nImage:\n"
        keys = ['contentUrl', 'thumbnailUrl', 'name', 'encodingFormat', 'width', 'height']
        for key in keys:
            print '%s:\t%s' %(key, result_imgs[0][key])