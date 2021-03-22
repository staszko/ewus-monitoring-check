import zeep
import sys
import requests
import html
import logging

logging.getLogger('zeep').setLevel(logging.ERROR)

wsdl = 'https://ewus.nfz.gov.pl/ws-broker-server-ewus-auth-test/services/Auth?wsdl'
ewusLogin='LEKARZ1'
ewusPassword='qwerty!@#'
ewusDomain = '15'

def main():
    try:
        client = zeep.Client(wsdl=wsdl)

        result = login(client)

        #print(result['header'])
        sessionId = result['header']['session']['id']
        tokenId = result['header']['token']['id']
        #print(sessionId, tokenId)

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

main()