from bottle import abort, route, run, template, request
import disambiguation


@route('/link')
def link():
    if request.params.get('ne') is not None:
        ne = request.params.get('ne')
        link, p, mainLabel = disambiguation.linkEntity(ne)
        result = dict()
        result['ne'] = ne
        if link is not None:
            result['link'] = link[1:-1]
            result['p'] = p
            result['name'] = mainLabel
        return result
    else:
        abort(400, "No fitting argument (\"ne=...\") given.")

run(host='localhost', port=5000)
