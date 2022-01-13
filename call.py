"""

Command line utility for querying the Onshape API for dwg drawings

"""

import argparse
import json
import time
import urllib.parse
from pathlib import Path

from client import Client


def _parse_resp(resp):
    """Parse the response of a retrieval call.
    """
    parsed_resp = json.loads(resp.content.decode('utf8').replace("'", '"'))
    return parsed_resp


def _save_or_print_resp(resp_dict, output_path=None, indent=4):
    """Saves or prints the given response dict.
    """
    if output_path:
        with open(output_path, 'w') as fh:
            json.dump(resp_dict, fh, indent=indent)
    else:
        print(json.dumps(resp_dict, indent=indent))


def _create_client(logging):
    """Creates a `Client` with the given bool value for `logging`.
    """
    client = Client(stack='https://cad.onshape.com',
                    logging=logging)
    return client


def _parse_url(url):  
    """Extracts doc, workspace, element ids from url.
    """
    ids = urllib.parse.urlparse(url).path.split('/')
    did = ids[2]
    wid = ids[4]
    if len(ids) >= 7:
        eid = ids[6]
    else:
        eid = None
    return did, wid, eid


def wait_for_translation(client, id):
    """Wait for a translation to finish"""
    while True:
        res = client.get_translation_status(id)
        res_data = res.json()
        state = res_data['requestState']
        if state == 'ACTIVE':
            time.sleep(2)
            continue
        else:
            return res_data


def export_drawing_translation(client, did, wid, eid, output_dir, formats=['DWG', 'PNG']):
    """Get a drawing translation in a given format"""
    for format in formats:
        output_file = output_dir / f'd{did}_w{wid}_e{eid}.{format.lower()}'
        if output_file.exists():
            print(f'Skipping: {output_file}')
            continue
        # response = client.get_drawing_translation_formats(did, wid, eid)
        # print(response.json())

        # Request the drawing 
        request_body = {
            'formatName': format,
            'destinationName': output_file.name,
            'notifyUser': False,
            'storeInDocument': False,
            'linkDocumentWorkspaceId': None
        }
        res = client.get_drawing_translation(did, wid, eid, payload=request_body)
        res_data = res.json()
        if res_data['requestState'] == 'FAILED':
            raise Exception(f'Translation request failed: {res_data["failureReason"]}')

        # Wait for the file to be ready to download
        res_data = wait_for_translation(client, res_data['id'])
        if res_data['requestState'] == 'FAILED':
            raise Exception(f'Translation request failed: {res_data["failureReason"]}')

        # Write the file to disk
        # TODO: Check if res_data['resultExternalDataIds'] is ever greater than 1
        ex_data_id = res_data['resultExternalDataIds'][0]
        res = client.download_external_data(did, ex_data_id)
        with open(output_file, 'wb') as f:
            f.write(res.content)
        assert output_file.exists()
        print(f'Drawing exported: {output_file}')
        time.sleep(1)


def list_drawings_from_document(client, did, wid):
    """List the drawings in a given workspace"""
    # Restrict to the application type for drawings
    res = client.list_elements(did, wid, element_type='APPLICATION')
    res_data = res.json()
    drawings = []
    for element in res_data:
        if element['dataType'] == "onshape-app/drawing":
            drawings.append(element)
    return drawings


def list_documents(client, offset, list_doc_limit):
    """List public documents"""
    res = client.get_documents(limit=list_doc_limit, offset=offset)
    res_data = res.json()
    return res_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='data', type=str, help='Output directory to save data')
    parser.add_argument('--limit', default='1000', type=int, help='Limit the number of documents to search')
    parser.add_argument('--offset', default='0', type=int, help='Offset the documents to search')
    parser.add_argument('--enable_logging', help='Whether to log API messages', action='store_true')        
    args = parser.parse_args()

    output_dir = Path(args.output)
    if not output_dir.exists():
        output_dir.mkdir()
    client = _create_client(args.enable_logging)

    drawing_count = 0
    list_doc_limit = 20
    loop_count = int(args.limit / list_doc_limit)
    for i in range(loop_count):
        offset = args.offset + i * list_doc_limit
        documents_data = list_documents(client, offset, list_doc_limit)
        documents = documents_data['items']
        for document in documents:
            did = document['id']
            wid = document['defaultWorkspace']['id']
            drawings = list_drawings_from_document(client, did, wid)
            if len(drawings) == 0:
                print('--------------No drawings found--------------')
            for drawing in drawings:
                eid = drawing['id']
                export_drawing_translation(client, did, wid, eid, output_dir)
                drawing_count += 1
    print()
    print('--------------')
    print(f'Drawing count: {drawing_count} from {args.limit} documents')

if __name__ == '__main__':
    main()