'''
client
======

Convenience functions for working with the Onshape API
'''

from onshape import Onshape

import mimetypes
import random
import string
import os


class Client():
    '''
    Defines methods for testing the Onshape API. Comes with several methods:

    - Create a document
    - Delete a document
    - Get a list of documents

    Attributes:
        - stack (str, default='https://cad.onshape.com'): Base URL
        - logging (bool, default=True): Turn logging on or off
    '''

    def __init__(self, stack='https://cad.onshape.com', logging=True):
        '''
        Instantiates a new Onshape client.

        Args:
            - stack (str, default='https://cad.onshape.com'): Base URL
            - logging (bool, default=True): Turn logging on or off
        '''

        self._stack = stack
        self._api = Onshape(stack=stack, logging=logging)

    def new_document(self, name='Test Document', owner_type=0, public=False):
        '''
        Create a new document.

        Args:
            - name (str, default='Test Document'): The doc name
            - owner_type (int, default=0): 0 for user, 1 for company, 2 for team
            - public (bool, default=False): Whether or not to make doc public

        Returns:
            - requests.Response: Onshape response data
        '''

        payload = {
            'name': name,
            'ownerType': owner_type,
            'isPublic': public
        }

        return self._api.request('post', '/api/documents', body=payload)

    def rename_document(self, did, name):
        '''
        Renames the specified document.

        Args:
            - did (str): Document ID
            - name (str): New document name

        Returns:
            - requests.Response: Onshape response data
        '''

        payload = {
            'name': name
        }

        return self._api.request('post', '/api/documents/' + did, body=payload)

    def delete_document(self, did):
        '''
        Delete the specified document.

        Args:
            - did (str): Document ID

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('delete', '/api/documents/' + did)

    def get_document(self, did):
        '''
        Get details for a specified document.

        Args:
            - did (str): Document ID

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/documents/' + did)

    def list_documents(self):
        '''
        Get list of documents for current user.

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/documents')

    def create_assembly(self, did, wid, name='My Assembly'):
        '''
        Creates a new assembly element in the specified document / workspace.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - name (str, default='My Assembly')

        Returns:
            - requests.Response: Onshape response data
        '''

        payload = {
            'name': name
        }

        return self._api.request('post', '/api/assemblies/d/' + did + '/w/' + wid, body=payload)

    def get_features(self, did, wid, eid, timeout=None):
        '''
        Gets the feature list for specified document / workspace / part studio.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID
            - timeout (float): Timeout passed to requests.request().

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request(
            'get', '/api/partstudios/d/' + did + '/w/' + wid + '/e/' + eid + '/features',
            timeout=timeout)

    def sketch_information(self, did, wid, eid, payload=None):
        '''
        Get information for sketches in a part studio.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/partstudios/d/' + did + '/w/' + wid + '/e/' + eid + '/sketches', body=payload)

    def get_thumbnail_with_size(self, did, wid, sz):
        '''
        Gets the thumbnail image for specified document / workspace with size sz.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - sz (int): Dimension of square image

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/thumbnails/d/' + did + '/w/' + wid +  ('/s/%ix%i' % (sz, sz)), headers={'Accept': 'application/vnd.onshape.v1+octet-stream', 'Content-Type': 'application/json'})

    def get_tess_sketch_entities(self, did, wid, eid, sid):
        '''
        Gets the tessellations of the sketch entities in a sketch.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID
            - sid (str): Sketch feature ID

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/partstudios/d/' + did + '/w/' + wid + '/e/' + eid + '/sketches/' + sid + '/tessellatedentities')

    def add_feature(self, did, wid, eid, payload):
        '''
        Add feature for specified document / workspace / part studio.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''
        return self._api.request('post', '/api/partstudios/d/' + did + '/w/' + wid + '/e/' + eid + '/features', body=payload)

    def delete_feature(self, did, wid, eid, fid):
        '''
        Delete feature for specified document / workspace / part studio / feature.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID
            - fid (str): Feature ID

        Returns:
            - requests.Response: Onshape response data
        '''
        return self._api.request('delete', '/api/partstudios/d/' + did + '/w/' + wid + '/e/' + eid + '/features/featureid/' + fid)

    def get_partstudio_tessellatededges(self, did, wid, eid):
        '''
        Gets the tessellation of the edges of all parts in a part studio.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/partstudios/d/' + did + '/w/' + wid + '/e/' + eid + '/tessellatededges')

    def upload_blob(self, did, wid, filepath='./blob.json'):
        '''
        Uploads a file to a new blob element in the specified doc.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - filepath (str, default='./blob.json'): Blob element location

        Returns:
            - requests.Response: Onshape response data
        '''

        chars = string.ascii_letters + string.digits
        boundary_key = ''.join(random.choice(chars) for i in range(8))

        mimetype = mimetypes.guess_type(filepath)[0]
        encoded_filename = os.path.basename(filepath)
        file_content_length = str(os.path.getsize(filepath))
        blob = open(filepath)

        req_headers = {
            'Content-Type': 'multipart/form-data; boundary="%s"' % boundary_key
        }

        # build request body
        payload = '--' + boundary_key + \
            '\r\nContent-Disposition: form-data; name="encodedFilename"\r\n\r\n' + \
            encoded_filename + '\r\n'
        payload += '--' + boundary_key + \
            '\r\nContent-Disposition: form-data; name="fileContentLength"\r\n\r\n' + \
            file_content_length + '\r\n'
        payload += '--' + boundary_key + \
            '\r\nContent-Disposition: form-data; name="file"; filename="' + \
            encoded_filename + '"\r\n'
        payload += 'Content-Type: ' + mimetype + '\r\n\r\n'
        payload += blob.read()
        payload += '\r\n--' + boundary_key + '--'

        return self._api.request('post', '/api/blobelements/d/' + did + '/w/' + wid, headers=req_headers, body=payload)

    def part_studio_stl(self, did, wid, eid):
        '''
        Exports STL export from a part studio

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''

        req_headers = {
            'Accept': 'application/vnd.onshape.v1+octet-stream'
        }
        return self._api.request('get', '/api/partstudios/d/' + did + '/w/' + wid + '/e/' + eid + '/stl', headers=req_headers)

    def get_drawing_translation_formats(self, did, wid, eid):
        '''
        Get drawing translation formats.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''
        return self._api.request('get', '/api/drawings/d/' + did + '/w/' + wid + '/e/' + eid + '/translationformats')
    
    def get_drawing_translation(self, did, wid, eid, payload):
        '''
        Get a drawing translation.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''
        return self._api.request('post', '/api/drawings/d/' + did + '/w/' + wid + '/e/' + eid + '/translations', body=payload)

    def get_translation_status(self, id):
        '''
        Get the status of a translation.

        Args:
            - id (str): Translation ID

        Returns:
            - requests.Response: Onshape response data
        '''
        return self._api.request('get', '/api/translations/' + id)
    
    def download_external_data(self, did, fid):
        '''
        Download external data

        Args:
            - did (str): Document ID
            - fid (str): External data ID

        Returns:
            - requests.Response: Onshape response data
        '''

        req_headers = {
            'Accept': 'application/vnd.onshape.v1+octet-stream'
        }
        return self._api.request('get', '/api/documents/d/' + did + '/externaldata/' + fid, headers=req_headers)

    def list_elements(self, did, wid, element_type=None):
        '''
        List the elements in a workspace.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - element_type (str): Return results of this element type

        Returns:
            - requests.Response: Onshape response data
        '''
        if element_type:            
            query = {
                'elementType': element_type
            }
        else:
            query = None
        return self._api.request('get', '/api/documents/d/' + did + '/w/' + wid + '/elements', query=query)

    def get_documents(self, limit=20, filter=4, offset=0, sort_order='desc'):
        '''
        List documents.

        Args:
            - filter (int): Filter ID, which can be 0: my docs, 1: created, 2: shared, 3: trash, 4: public, 5: recent, 6: by owner, 7: by company, or 9: by team
            - offset (int): Where to begin listing documents
            - sort_order (str): Sort order to list can be desc: descending, or asc: ascending

        Returns:
            - requests.Response: Onshape response data
        '''
        query = {
            'limit': limit,
            'filter': filter,
            'offset': offset,
            'sortOrder': sort_order
        }
        return self._api.request('get', '/api/documents/', query=query)
