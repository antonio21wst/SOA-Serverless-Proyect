import xml.etree.ElementTree as ET

def parse_soap_request(xml_data):
    try:
        root = ET.fromstring(xml_data)
        body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        request_data = {}
        for child in body:
            for item in child:
                request_data[item.tag] = item.text
        return {
            "engine": request_data.get("engine"),
            "operation": request_data.get("operation"),
            "dbname": request_data.get("dbname"),
            "payload": request_data.get("payload")  # JSON string
        }
    except Exception as e:
        raise ValueError(f"Error al parsear XML SOAP: {str(e)}")

def build_soap_response(response_dict):
    envelope = ET.Element("soap:Envelope", {
        "xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/"
    })
    body = ET.SubElement(envelope, "soap:Body")
    response = ET.SubElement(body, "Response")

    for key, value in response_dict.items():
        elem = ET.SubElement(response, key)
        elem.text = str(value)

    return ET.tostring(envelope, encoding="utf-8", method="xml")
