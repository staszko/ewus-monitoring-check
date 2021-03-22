import zeep

wsdl = 'https://ewus.nfz.gov.pl/ws-broker-server-ewus-auth-test/services/Auth?wsdl'
ewusLogin='LEKARZ1'
ewusPassword='qwerty!@#'
ewusDomain = '15'


client = zeep.Client(wsdl=wsdl)

#print(client._get_service("Auth"))
factory = client.type_factory('ns3')
domianParamValue = factory.paramValue(stringValue=ewusDomain)
domainLoginParam = factory.loginParam(name='domain', value=domianParamValue)


loginParamValue = factory.paramValue(stringValue=ewusLogin)
loginLoginParam = factory.loginParam(name='login', value=loginParamValue)

loginParams = factory.loginParams(item=[domainLoginParam, loginLoginParam])

result = client.service.login(credentials=loginParams, password=ewusPassword)

print(result['header'])
sessionId = result['header']['session']['id']
tokenId = result['header']['token']['id']
print(sessionId, tokenId)

logoutResult = client.service.logout('',_soapheaders=[result['header']])

print(logoutResult)