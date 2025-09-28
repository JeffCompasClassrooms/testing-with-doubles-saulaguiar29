#curl -X GET http://localhost:8080/squirrels
#curl -X POST http://localhost:8080/squirrels -d "name=Chippy&size=small"
#curl -X POST http://localhost:8080/squirrels -d "name=Josh&"   # bad request
#python squirrel_server.py
#brew install sqlite


import io
import json
import pytest
from squirrel_server import SquirrelServerHandler
from squirrel_db import SquirrelDB

class FakeRequest:
    def __init__(self, mock_wfile, method, path, body=None):
        self._mock_wfile = mock_wfile
        self._method = method
        self._path = path
        self._body = body

    def sendall(self, x):
        return

    def makefile(self, *args, **kwargs):
        if args[0] == 'rb':
            if self._body:
                headers = f'Content-Length: {len(self._body)}\r\n'
                body = self._body
            else:
                headers = ''
                body = ''
            request = bytes(f'{self._method} {self._path} HTTP/1.0\r\n{headers}\r\n{body}', 'utf-8')
            return io.BytesIO(request)
        elif args[0] == 'wb':
            return self._mock_wfile

# Fixtures
@pytest.fixture
def dummy_client():
    return ('127.0.0.1', 80)

@pytest.fixture
def dummy_server():
    return None

@pytest.fixture(autouse=True)
def patch_handler_properties(mocker):
    mocker.patch.object(SquirrelServerHandler, 'wbufsize', 1)
    mocker.patch.object(SquirrelServerHandler, 'end_headers')

@pytest.fixture
def mock_response_methods(mocker):
    mock_send_response = mocker.patch.object(SquirrelServerHandler, 'send_response')
    mock_send_header = mocker.patch.object(SquirrelServerHandler, 'send_header')
    mock_end_headers = mocker.patch.object(SquirrelServerHandler, 'end_headers')
    return mock_send_response, mock_send_header, mock_end_headers

def describe_SquirrelServerHandler():
    """Test suite for SquirrelServerHandler using test doubles."""
    
    def describe_handleSquirrelsIndex():
        def calls_getsquirrels_on_database(mocker, dummy_client, dummy_server):
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrels = mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=[])
            fake_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_get_squirrels.assert_called_once()
        
        def send_200_status_and_json_content_type(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrels = mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=[])
            fake_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_send_response.assert_called_once_with(200)
            mock_send_header.assert_called_once_with("Content-Type", "application/json")
        
        def write_json_response_body(mocker, dummy_client, dummy_server):
            expected_squirrels = [{'id': 1, 'name': 'Test', 'size': 'small'}]
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrels = mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=expected_squirrels)
            fake_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels')
            
            handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            expected_json = bytes(json.dumps(expected_squirrels), "utf-8")
            handler.wfile.write.assert_called_once_with(expected_json)
    
    def describe_handleSquirrelsRetrieve(): 
        def getSquirrel_with_correct_id(mocker, dummy_client, dummy_server):
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1})
            fake_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels/123')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_get_squirrel.assert_called_once_with('123')
        
        def send_200_when_squirrel_found(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1, 'name': 'Test'})
            fake_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels/1')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_send_response.assert_called_once_with(200)
        
        def handle404_when_squirrel_not_found(mocker, dummy_client, dummy_server):
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value=None)
            mock_handle404 = mocker.patch.object(SquirrelServerHandler, 'handle404')
            fake_request = FakeRequest(mocker.Mock(), 'GET', '/squirrels/999')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_handle404.assert_called_once()
    
    def describe_handleSquirrelsCreate():        
        def call_createSquirrel_with_parsed_data(mocker, dummy_client, dummy_server):
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_create_squirrel = mocker.patch.object(SquirrelDB, 'createSquirrel')
            mock_get_request_data = mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={'name': 'Chippy', 'size': 'medium'})
            fake_request = FakeRequest(mocker.Mock(), 'POST', '/squirrels', 'name=Chippy&size=medium')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_create_squirrel.assert_called_once_with('Chippy', 'medium')
        
        def send_201_status_code(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_create_squirrel = mocker.patch.object(SquirrelDB, 'createSquirrel')
            mock_get_request_data = mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={'name': 'Test', 'size': 'small'})
            fake_request = FakeRequest(mocker.Mock(), 'POST', '/squirrels', 'name=Test&size=small')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_send_response.assert_called_once_with(201)
    
    def describe_handleSquirrelsUpdate():
        def updateSquirrel_with_correct_parameters(mocker, dummy_client, dummy_server):
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel')
            mock_get_request_data = mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={'name': 'NewName', 'size': 'tiny'})
            fake_request = FakeRequest(mocker.Mock(), 'PUT', '/squirrels/42', 'name=NewName&size=tiny')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_update_squirrel.assert_called_once_with('42', 'NewName', 'tiny')
        
        def send_204_status_when_update_successful(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1})
            mock_update_squirrel = mocker.patch.object(SquirrelDB, 'updateSquirrel')
            mock_get_request_data = mocker.patch.object(SquirrelServerHandler, 'getRequestData', return_value={'name': 'Updated', 'size': 'large'})
            fake_request = FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', 'name=Updated&size=large')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_send_response.assert_called_once_with(204)
        
        def handle404_when_squirrel_not_found(mocker, dummy_client, dummy_server):
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value=None)
            mock_handle404 = mocker.patch.object(SquirrelServerHandler, 'handle404')
            fake_request = FakeRequest(mocker.Mock(), 'PUT', '/squirrels/999', 'name=Updated&size=large')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_handle404.assert_called_once()
    
    def describe_handleSquirrelsDelete():
        def deleteSquirrel_with_correct_id(mocker, dummy_client, dummy_server):
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1})
            mock_delete_squirrel = mocker.patch.object(SquirrelDB, 'deleteSquirrel')
            fake_request = FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/15')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_delete_squirrel.assert_called_once_with('15')
        
        def send_204_status_when_delete_successful(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value={'id': 1})
            mock_delete_squirrel = mocker.patch.object(SquirrelDB, 'deleteSquirrel')
            fake_request = FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/1')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_send_response.assert_called_once_with(204)
        
        def handle404_when_squirrel_not_found(mocker, dummy_client, dummy_server):
            mock_db_init = mocker.patch.object(SquirrelDB, '__init__', return_value=None)
            mock_get_squirrel = mocker.patch.object(SquirrelDB, 'getSquirrel', return_value=None)
            mock_handle404 = mocker.patch.object(SquirrelServerHandler, 'handle404')
            fake_request = FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/999')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_handle404.assert_called_once()
    
    def describe_handle404():
        def send_404_status_and_text_content_type(mocker, dummy_client, dummy_server, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            fake_request = FakeRequest(mocker.Mock(), 'GET', '/nonexistent')
            
            SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            mock_send_response.assert_called_with(404)
            mock_send_header.assert_called_with("Content-Type", "text/plain")
        
        def write_404_message_to_response_body(mocker, dummy_client, dummy_server):
            fake_request = FakeRequest(mocker.Mock(), 'GET', '/nonexistent')
            
            handler = SquirrelServerHandler(fake_request, dummy_client, dummy_server)
            
            expected_message = bytes("404 Not Found", "utf-8")
            handler.wfile.write.assert_called_with(expected_message)