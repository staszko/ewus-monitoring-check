import zeep

wsdl = 'https://ewus.nfz.gov.pl/ws-broker-server-ewus-auth-test/services/Auth?wsdl'
client = zeep.Client(wsdl=wsdl)

#print(client._get_service("Auth"))
factory = client.type_factory('ns3')
domianParamValue = factory.paramValue(stringValue='15')
domainLoginParam = factory.loginParam(name='domain', value=domianParamValue)


loginParamValue = factory.paramValue(stringValue='LEKARZ1')
loginLoginParam = factory.loginParam(name='login', value=loginParamValue)

loginParams = factory.loginParams(item=[domainLoginParam, loginLoginParam])

print(loginParams)

