from pyjob.misc import typecast


class TestTypecast(object):
    def test_int(self):
        output = typecast("1")
        assert isinstance(output, int)
        assert output == 1

    def test_float(self):
        output = typecast("1.0")
        assert isinstance(output, float)
        assert output == 1

    def test_char(self):
        output = typecast("a")
        assert isinstance(output, str)
        assert output == "a"

    def test_str(self):
        output = typecast("abc")
        assert isinstance(output, str)
        assert output == "abc"

    def test_none(self):
        output = typecast("None")
        assert output is None

    def test_bool(self):
        output = typecast("True")
        assert isinstance(output, bool)
        assert output is True

    def test_list(self):
        output = typecast(["1", "True", "3.0", "t", "test"])
        assert isinstance(output, list)
        assert output == [1, True, 3.0, "t", "test"]

    def test_dict(self):
        output = typecast(
            {"int": "1", "bool": "False", "float": "3.0", "char": "t", "str": "test"}
        )
        assert isinstance(output, dict)
        assert output == {
            "int": 1,
            "bool": False,
            "float": 3.0,
            "char": "t",
            "str": "test",
        }

    def test_nested(self):
        output = typecast(
            {
                "int": ["1", "2", 3],
                "bool": "False",
                "mixed": ["3.0", "foo"],
                "char": "t",
                "str": "test",
            }
        )
        assert isinstance(output, dict)
        assert output == {
            "int": [1, 2, 3],
            "bool": False,
            "mixed": [3.0, "foo"],
            "char": "t",
            "str": "test",
        }
