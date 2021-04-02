import zeep
import sys
import requests
import html
import logging
import datetime
import inspect
import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

#logging.getLogger('zeep').setLevel(logging.ERROR)
logging.getLogger('zeep').setLevel(logging.DEBUG)


#Due to ewus test server configuration request fails  
# when openssl is SET to SECLEVEL=2 The error is: [SSL: DH_KEY_TOO_SMALL] dh key too small (_ssl.c:1108)
# Therefore this app dockerized with python:3 default image fails (debian moved defaults to SECLEVEL=2)
# Therefore I've disabled Diffie-Hellmans key exchange
#
# Resources 
#  https://stackoverflow.com/a/61627673
#  https://weakdh.org/
#  code from https://stackoverflow.com/a/41041028
#
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass


wsdl = 'https://ewus.nfz.gov.pl/ws-broker-server-ewus-auth-test/services/Auth?wsdl'
ewusLogin='LEKARZ1'
ewusPassword='qwerty!@#'
ewusDomain = '15'

testowyPesel = '00060958187'

def main():
    try:
        client = zeep.Client(wsdl=wsdl)

        result = login(client)

        #print(result['header'])
        sessionId = result['header']['session']['id']
        tokenId = result['header']['token']['id']
        #print(sessionId, tokenId)

        #getCheckCwuMessage(testowyPesel)
        checkPesel(result['header'])


        logoutResult = logout(client, result['header'])

        ok()
        #print(logoutResult)
    except zeep.exceptions.Fault as e:
        critical(e)
        print(e.message)
    except requests.exceptions.HTTPError as e:
        critical(e)
    except Exception as e:
        print(e.__class__, e)
        unknown(e)


def login(client):
    factory = client.type_factory('http://xml.kamsoft.pl/ws/kaas/login_types')
    domianParamValue = factory.paramValue(stringValue=ewusDomain)
    domainLoginParam = factory.loginParam(name='domain', value=domianParamValue)

    loginParamValue = factory.paramValue(stringValue=ewusLogin)
    loginLoginParam = factory.loginParam(name='login', value=loginParamValue)

    loginParams = factory.loginParams(item=[domainLoginParam, loginLoginParam])

    result = client.service.login(credentials=loginParams, password=ewusPassword)
    return result

def getCheckCwuMessage(pesel):
    msg = f'''<ewus:status_cwu_pyt xmlns:ewus=\"https://ewus.nfz.gov.pl/ws/broker/ewus/status_cwu/v3\">
                  <ewus:numer_pesel>{pesel}</ewus:numer_pesel>
                  <ewus:system_swiad nazwa=\"ewus_check\" wersja=\"0.0.0\"/>
               </ewus:status_cwu_pyt>'''
    #print(msg.format(pesel))
    return msg


def checkPesel(soapheaders):
    wsdl = 'https://ewus.nfz.gov.pl/ws-broker-server-ewus-auth-test/services/ServiceBroker?wsdl'
    client = zeep.Client(wsdl=wsdl)
    #client._soapheaders =[soapheaders]
    factory = client.type_factory('http://xml.kamsoft.pl/ws/common') 

    service_location = factory.ServiceLocation()
    service_location.namespace = 'http://nfz.gov.pl/ws/broker/cwu'
    service_location.localname = 'checkCWU'
    service_location.version = '5.0'

    factory = client.type_factory('http://xml.kamsoft.pl/ws/broker') 

    params = factory.ArrayOfParam
    payload = factory.Payload
    payload.textload = getCheckCwuMessage('12345678901')

    req = """
        <![CDATA[<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:com="http://xml.kamsoft.pl/ws/common" xmlns:brok="http://xml.kamsoft.pl/ws/broker">
    <soapenv:Header>
        <com:session id="86E91D37D4C559ABE0677F7ADA1CE77F" xmlns:ns1="http://xml.kamsoft.pl/ws/common"/>
        <com:authToken id="BSmV7uJGISTPK4MdHYIcoW" xmlns:ns1="http://xml.kamsoft.pl/ws/common"/>
    </soapenv:Header>
    <soapenv:Body>
        <brok:executeService>
            <com:location>
                <com:namespace>http://nfz.gov.pl/ws/broker/cwu</com:namespace>
                <com:localname>checkCWU</com:localname>
                <com:version>5.0</com:version>
            </com:location>
            <brok:date>2008-09-12T09:37:36.406+01:00</brok:date>    
            <brok:payload>   
            <brok:textload>
                <status_cwu_pyt>
                    <numer_pesel>49091480757</numer_pesel>
                    <system_swiad nazwa="eWUS" wersja="5.0"></system_swiad>
                </status_cwu_pyt>
            </brok:textload>
            </brok:payload>    
        </brok:executeService>
    </soapenv:Body>
    </soapenv:Envelope>
    """
    client.service.executeService(id=req)
    #client.service.executeService(service_location, '2020-04-02T11:17:00', params, payload] )
    
    return True
    #return client.service.logout('',_soapheaders=[soapheaders])

def logout(client, soapheaders):
    return client.service.logout('',_soapheaders=[soapheaders])

def ok():
    print('OK: Zalogowano i wylogowano poprawnie')
    sys.exit(0)

def warning(e):
    print('WARNING: ', html.unescape(e.__str__()))
    sys.exit(1)

def critical(e):
    print('CRITICAL: ',  html.unescape(e.__str__()))
    sys.exit(2)

def unknown(e):
    print('UNKNOWN: ',  html.unescape(e.__str__()))
    sys.exit(3)



main()