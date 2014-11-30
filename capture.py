from netlib.odict import ODictCaseless
from libmproxy.protocol.http import HTTPResponse
import cgi
import re
from gzip import GzipFile
import StringIO
import time

XML_OK_RESPONSE = '''<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>iPhone6,2</key><array><string>powerDiagnostics</string></array></dict></plist>'''


def request(context, flow):
    print 'Requesting -> %s' % flow.request.path  


def saveContent(flow, prefix):
    print "Saving data with prefix -> ", prefix
    decodedData = StringIO.StringIO()
    decodedData.write(flow.request.get_decoded_content())

    contentType = flow.request.headers['Content-Type'][0]
    multipart_boundary_re = re.compile('^multipart/form-data; boundary=(.*)$')
    matches = multipart_boundary_re.match(contentType) 

    decodedData.seek(0)

    query = cgi.parse_multipart( decodedData, {"boundary" : matches.group(1)})

    with open("%s-%s.tar.gz" % (prefix, time.strftime("%Y%m%d-%H%M%S")), "w") as logs:
        logs.write(query['log_archive'][0])

def set_response(flow, content):
    print 'Response from server -> ', flow.response
    flow.response.code = 200
    flow.response.msg = "OK"
    flow.response.headers = ODictCaseless([["Content-Type","text/xml"]])
    flow.response.content = content
    print "Setting new response -> ", flow.response
    print "Body -> ", content


def response(context, flow):
    path = flow.request.path

    if path == '/ios/TestConfiguration/1.2':
        set_response(flow, XML_OK_RESPONSE)  
    elif path == '/MR3Server/ValidateTicket?ticket_number=123456':    
        set_response(flow, XML_OK_RESPONSE)
    elif path == '/MR3Server/MR3Post':
        saveContent(flow, 'general')
        set_response(flow, XML_OK_RESPONSE)
    elif path == '/ios/log/extendedUpload':
        saveContent(flow, 'power')
        set_response(flow, XML_OK_RESPONSE)
