import zeep

wsdl = 'https://ewus.nfz.gov.pl/ws-broker-server-ewus-auth-test/services/Auth?wsdl'
client = zeep.Client(wsdl=wsdl)

print(client._get_service("Auth"))