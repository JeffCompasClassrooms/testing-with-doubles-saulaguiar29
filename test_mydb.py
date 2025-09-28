import pytest
from unittest.mock import mock_open, MagicMock
from mydb import MyDB

def describe_MyDB():
    def describe_init():      
        def file_name_atrributeset(mocker):
            # Stub os.path.isfile to return True (file exists)
            mock_isfile = mocker.patch('os.path.isfile', return_value=True)
        
            db = MyDB("test.db")
            #filename is set correctly
            assert db.fname == "test.db"
            mock_isfile.assert_called_once_with("test.db")
        
        def check_file_existence(mocker):    
            mock_isfile = mocker.patch('os.path.isfile', return_value=True)
            MyDB("database.db")
            mock_isfile.assert_called_once_with("database.db")
        
    def describe_loadStrings():
        def open_file_binary(mocker):
            # Stub file operations
            mock_file_open = mocker.patch('builtins.open', mock_open())
            mock_pickle_load = mocker.patch('pickle.load', return_value=['test'])
            
            # Create instance and call loadStrings
            db = MyDB.__new__(MyDB)  # Create without calling __init__
            db.fname = "test.db"
            db.loadStrings()
            
            #  opened in binary read mode
            mock_file_open.assert_called_once_with("test.db", 'rb')
        
        
        def loaded_data_frompickle(mocker):
            expected_data = ['string1', 'string2', 'string3']
            
            # Stub file operations
            mocker.patch('builtins.open', mock_open())
            mock_pickle_load = mocker.patch('pickle.load', return_value=expected_data)
         
            db = MyDB.__new__(MyDB)
            db.fname = "test.db"
            result = db.loadStrings()
        
            assert result == expected_data
        
    
    def describe_saveStrings():       
        def empty_list_saved_correctly(mocker):
            mock_file_open = mocker.patch('builtins.open', mock_open())
            mock_pickle_dump = mocker.patch('pickle.dump')
            
            # Create instance and call saveStrings with empty list
            db = MyDB.__new__(MyDB)
            db.fname = "test.db"
            db.saveStrings([])
            
            mock_pickle_dump.assert_called_once_with([], mock_file_open.return_value)
        
        def handles_file_context_manager(mocker):
            mock_file_handle = MagicMock()
            mock_file_open = mocker.patch('builtins.open', return_value=mock_file_handle)
            mock_pickle_dump = mocker.patch('pickle.dump')

            db = MyDB.__new__(MyDB)
            db.fname = "test.db"
            db.saveStrings(['data'])
            

            mock_file_handle.__enter__.assert_called_once()
            mock_file_handle.__exit__.assert_called_once()
    
    def describe_saveString():
        def calls_load_string(mocker):
            mock_load_strings = mocker.patch.object(MyDB, 'loadStrings', return_value=['existing'])
            mock_save_strings = mocker.patch.object(MyDB, 'saveStrings')
     
            db = MyDB.__new__(MyDB)
            db.fname = "test.db"
            db.saveString('new')
            
            mock_load_strings.assert_called_once()
        
        def appends_string_to_existing(mocker):
            existing_data = ['string1', 'string2']
            new_string = 'string3'
            expected_data = ['string1', 'string2', 'string3']
            
            mock_load_strings = mocker.patch.object(MyDB, 'loadStrings', return_value=existing_data)
            mock_save_strings = mocker.patch.object(MyDB, 'saveStrings')
            
            db = MyDB.__new__(MyDB)
            db.fname = "test.db"
            db.saveString(new_string)
            
            mock_save_strings.assert_called_once_with(expected_data)

        