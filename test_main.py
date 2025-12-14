import json
import tempfile
from pathlib import Path
from main import parse_config

def test_numbers_and_strings():
    config = '''
    42;
    "hello";
    '''
    result = parse_config(config)
    assert result == [42, "hello"]

def test_arrays():
    config = '''
    array(1, "a", 3);
    '''
    result = parse_config(config)
    assert result == [[1, "a", 3]]

def test_nested_structures():
    config = '''
    array(
        ([ A: "x", B: 10 ]),
        "top"
    );
    '''
    result = parse_config(config)
    expected = [[{"A": "x", "B": 10}, "top"]]
    assert result == expected

def test_constants_and_expressions():
    config = '''
    (def SIZE 10);
    (def LABEL "Player");
    {+ SIZE 5};
    {len LABEL};
    {chr 65};
    '''
    result = parse_config(config)
    assert result == [15, 6, "A"]

def test_dict():
    config = '''
    ([
        NAME: "Server",
        PORT: 8080,
        TAGS: array("http", "api")
    ]);
    '''
    result = parse_config(config)
    expected = [{"NAME": "Server", "PORT": 8080, "TAGS": ["http", "api"]}]
    assert result == expected

def test_complex():
    config = '''
    (def X 3);
    (def Y 4);
    ([
        AREA: {* X Y},
        MSG: {chr {+ 65 X}}
    ]);
    '''
    result = parse_config(config)
    expected = [{"AREA": 12, "MSG": "D"}]
    assert result == expected

if __name__ == "__main__":
    test_numbers_and_strings()
    test_arrays()
    test_nested_structures()
    test_constants_and_expressions()
    test_dict()
    test_complex()
    print("All tests passed!")
