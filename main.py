import zeep
import sys
import requests
import html
import logging

logging.getLogger('zeep').setLevel(logging.ERROR)

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

        getCheckCWU(testowyPesel)

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


def getCheckCWU(pesel):
    msg = f'''<ewus:status_cwu_pyt xmlns:ewus=\"https://ewus.nfz.gov.pl/ws/broker/ewus/status_cwu/v3\">
                  <ewus:numer_pesel>{pesel}</ewus:numer_pesel>
                  <ewus:system_swiad nazwa=\"ewus_check\" wersja=\"0.0.0\"/>
               </ewus:status_cwu_pyt>'''
    print(msg.format(pesel))

main()