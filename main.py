import zeep

wsdl = 'https://ewus.nfz.gov.pl/ws-broker-server-ewus-auth-test/services/Auth?wsdl'
ewusLogin='LEKARZ1'
ewusPassword='qwerty!@#'
ewusDomain = '15'

def main():
    client = zeep.Client(wsdl=wsdl)

    result = login(client)

    print(result['header'])
    sessionId = result['header']['session']['id']
    tokenId = result['header']['token']['id']
    print(sessionId, tokenId)

    logoutResult = logout(client, result['header'])

    print(logoutResult)

#print(client._get_service("Auth"))

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

main()