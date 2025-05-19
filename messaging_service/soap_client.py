from zeep import Client

# URL del WSDL generado por tu servicio SOAP
wsdl_url = 'http://localhost:8000/?wsdl'

client = Client(wsdl=wsdl_url)

# Crear un diccionario que simule el Payload esperado
payload = {
    'id': 2,
    'name': 'Juan SOAP',
    'email': 'juan@soap.com'
}

# Llamar la operación SOAP que definiste, por ejemplo 'perform_operation'
# El primer argumento es la operación (como 'update_user'), segundo es el payload
response = client.service.perform_operation('update_user', payload)

print("Respuesta del servicio SOAP:")
print(response)
