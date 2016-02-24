
from abc import ABCMeta
import ply.yacc as yacc
from pyfranca import franca_lexer
from pyfranca import ast


class ArgumentGroup(object):

    __metaclass__ = ABCMeta

    def __init__(self, arguments=None):
        self.arguments = arguments if arguments else []


class InArgumentGroup(ArgumentGroup):
    pass


class OutArgumentGroup(ArgumentGroup):
    pass


class ErrorArgumentGroup(ArgumentGroup):
    pass


class Parser(object):
    """
    Franca IDL PLY parser.
    """

    # noinspection PyUnusedLocal,PyIncorrectDocstring
    @staticmethod
    def p_fidl_1(p):
        """
        fidl : fidl def
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyUnusedLocal,PyIncorrectDocstring
    @staticmethod
    def p_fidl_2(p):
        """
        fidl : def
        """
        p[0] = [p[1]]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_package_def(p):
        """
        def : PACKAGE namespace
        """
        p[0] = p[2]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_namespace_1(p):
        """
        namespace : ID '.' namespace
        """
        p[0] = "{}.{}".format(p[1], p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_namespace_2(p):
        """
        namespace : ID
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_namespace_3(p):
        """
        namespace : '*'
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    # TODO: Support for "import model"
    @staticmethod
    def p_import_def(p):
        """
        def : IMPORT namespace FROM FILE_NAME
        """
        p[0] = ast.Import(p[4], p[2])

    @staticmethod
    def _interface_def(members):
        res = {
            "version": None,
            "attributes": [],
            "methods": [],
            "broadcasts": [],
            "typedefs": [],
            "enumerations": [],
            "structs": [],
            "arrays": [],
            "maps": [],
        }
        if members:
            for member in members:
                if isinstance(member, ast.Version):
                    if not res["version"]:
                        res["version"] = member
                    else:
                        raise SyntaxError
                elif isinstance(member, ast.Attribute):
                    res["attributes"].append(member)
                elif isinstance(member, ast.Method):
                    res["methods"].append(member)
                elif isinstance(member, ast.Broadcast):
                    res["broadcasts"].append(member)
                elif isinstance(member, ast.Typedef):
                    res["typedefs"].append(member)
                elif isinstance(member, ast.Enumeration):
                    res["enumerations"].append(member)
                elif isinstance(member, ast.Struct):
                    res["structs"].append(member)
                elif isinstance(member, ast.Array):
                    res["arrays"].append(member)
                elif isinstance(member, ast.Map):
                    res["maps"].append(member)
                else:
                    raise SyntaxError
        return res

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_typecollection(p):
        """
        def : TYPECOLLECTION ID '{' typecollection_members '}'
        """
        members = Parser._interface_def(p[4])
        if members["attributes"]:
            raise SyntaxError
        if members["methods"]:
            raise SyntaxError
        if members["broadcasts"]:
            raise SyntaxError
        p[0] = ast.TypeCollection(name=p[2],
                                  flags=None,
                                  version=members["version"],
                                  typedefs=members["typedefs"],
                                  enumerations=members["enumerations"],
                                  structs=members["structs"],
                                  arrays=members["arrays"],
                                  maps=members["maps"])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_typecollection_members_1(p):
        """
        typecollection_members : typecollection_members typecollection_member
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_typecollection_members_2(p):
        """
        typecollection_members : typecollection_member
        """
        p[0] = [p[1]]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_typecollection_members_3(p):
        """
        typecollection_members : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_typecollection_member(p):
        """
        typecollection_member : version_def
                              | type_def
                              | enumeration_def
                              | struct_def
                              | array_def
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_version_def(p):
        """
        version_def : VERSION '{' MAJOR INTEGER MINOR INTEGER '}'
        """
        p[0] = ast.Version(p[4], p[6])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_def_1(p):
        """
        type_def : TYPEDEF ID IS ID
        """
        base_type = ast.CustomType(p[4])
        p[0] = ast.Typedef(p[2], base_type)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_def_2(p):
        """
        type_def : TYPEDEF ID IS type
        """
        p[0] = ast.Typedef(p[2], p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_interface_1(p):
        """
        def : INTERFACE ID '{' interface_members '}'
        """
        members = Parser._interface_def(p[4])
        p[0] = ast.Interface(name=p[2],
                             flags=None,
                             version=members["version"],
                             attributes=members["attributes"],
                             methods=members["methods"],
                             broadcasts=members["broadcasts"],
                             extends=None)
        p[0].typedefs = members["typedefs"],
        p[0].enumerations = members["enumerations"],
        p[0].structs = members["structs"],
        p[0].arrays = members["arrays"],
        p[0].maps = members["maps"]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_interface_2(p):
        """
        def : INTERFACE ID EXTENDS ID '{' interface_members '}'
        """
        members = Parser._interface_def(p[6])
        p[0] = ast.Interface(name=p[2],
                             flags=None,
                             version=members["version"],
                             attributes=members["attributes"],
                             methods=members["methods"],
                             broadcasts=members["broadcasts"],
                             extends=p[4])
        p[0].typedefs = members["typedefs"],
        p[0].enumerations = members["enumerations"],
        p[0].structs = members["structs"],
        p[0].arrays = members["arrays"],
        p[0].maps = members["maps"]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_interface_members_1(p):
        """
        interface_members : interface_members interface_member
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_interface_members_2(p):
        """
        interface_members : interface_member
        """
        p[0] = [p[1]]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_interface_members_3(p):
        """
        interface_members : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_interface_member(p):
        """
        interface_member : version_def
                         | attribute_def
                         | method_def
                         | broadcast_def
                         | type_def
                         | enumeration_def
                         | struct_def
                         | array_def
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_attribute_def_1(p):
        """
        attribute_def : ATTRIBUTE type ID
        """
        # TODO: Support for flags.
        p[0] = ast.Attribute(p[3], p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_attribute_def_2(p):
        """
        attribute_def : ATTRIBUTE ID ID
        """
        attr_type = ast.CustomType(p[3])
        p[0] = ast.Attribute(p[3], attr_type)

    @staticmethod
    def _method_def(arg_groups):
        in_args = None
        out_args = None
        errors = None
        if arg_groups:
            for arg_group in arg_groups:
                if isinstance(arg_group, InArgumentGroup):
                    if not in_args:
                        in_args = arg_group.arguments
                    else:
                        raise SyntaxError
                elif isinstance(arg_group, OutArgumentGroup):
                    if not out_args:
                        out_args = arg_group.arguments
                    else:
                        raise SyntaxError
                elif isinstance(arg_group, ErrorArgumentGroup):
                    if not errors:
                        errors = arg_group.arguments
                    else:
                        raise SyntaxError
                else:
                    raise SyntaxError
        return in_args, out_args, errors

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_method_def_1(p):
        """
        method_def : METHOD ID flag_defs '{' arg_group_defs '}'
        """
        in_args, out_args, errors = Parser._method_def(p[5])
        p[0] = ast.Method(p[2], flags=p[3],
                          in_args=in_args, out_args=out_args, errors=errors)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_method_def_2(p):
        """
        method_def : METHOD ID '{' arg_group_defs '}'
        """
        in_args, out_args, errors = Parser._method_def(p[4])
        p[0] = ast.Method(p[2], flags=None,
                          in_args=in_args, out_args=out_args, errors=errors)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_flag_defs_1(p):
        """
        flag_defs : flag_defs flag_def
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_flag_defs_2(p):
        """
        flag_defs : flag_def
        """
        p[0] = [p[1]]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_flag_defs_3(p):
        """
        flag_defs : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_flag_def(p):
        """
        flag_def : SELECTIVE
                 | FIREANDFORGET
                 | POLYMORPHIC
                 | NOSUBSCRIPTIONS
                 | READONLY
        """
        p[0] = p[1]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_defs_1(p):
        """
        arg_group_defs : arg_group_defs arg_group_def
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_defs_2(p):
        """
        arg_group_defs : arg_group_def
        """
        p[0] = [p[1]]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_froup_defs_3(p):
        """
        arg_group_defs : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_def_1(p):
        """
        arg_group_def : IN '{' arg_defs '}'
        """
        p[0] = InArgumentGroup(p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_def_2(p):
        """
        arg_group_def : OUT '{' arg_defs '}'
        """
        p[0] = OutArgumentGroup(p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_group_def_3(p):
        """
        arg_group_def : ERROR '{' enumerators '}'
        """
        p[0] = ErrorArgumentGroup(p[3])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_broadcast_def_1(p):
        """
        broadcast_def : BROADCAST ID flag_defs '{' arg_group_defs '}'
        """
        in_args, out_args, errors = Parser._method_def(p[5])
        if in_args or errors:
            raise SyntaxError
        p[0] = ast.Broadcast(p[2], flags=p[3], out_args=out_args)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_broadcast_def_2(p):
        """
        broadcast_def : BROADCAST ID '{' arg_group_defs '}'
        """
        in_args, out_args, errors = Parser._method_def(p[4])
        if in_args or errors:
            raise SyntaxError
        p[0] = ast.Broadcast(p[2], flags=None, out_args=out_args)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_defs_1(p):
        """
        arg_defs : arg_defs arg_def
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_defs_2(p):
        """
        arg_defs : arg_def
        """
        p[0] = [p[1]]

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_def_1(p):
        """
        arg_def : type ID
        """
        p[0] = ast.Argument(p[2], p[1])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_arg_def_2(p):
        """
        arg_def : ID ID
        """
        arg_type = ast.CustomType(p[1])
        p[0] = ast.Argument(p[2], arg_type)

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_enumeration_def_1(p):
        """
        enumeration_def : ENUMERATION ID '{' enumerators '}'
        """
        p[0] = ast.Enumeration(p[2], p[4])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_enumeration_def_2(p):
        """
        enumeration_def : ENUMERATION ID EXTENDS ID '{' enumerators '}'
        """
        p[0] = ast.Enumeration(p[2], p[6], p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumerators_1(p):
        """
        enumerators : enumerators enumerator
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumerators_2(p):
        """
        enumerators : enumerator
        """
        p[0] = [p[1]]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_enumerators_3(p):
        """
        enumerators : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumerator_1(p):
        """
        enumerator : ID
        """
        p[0] = ast.Enumerator(p[1], None)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_enumerator_2(p):
        """
        enumerator : ID '=' INTEGER
        """
        p[0] = ast.Enumerator(p[1], p[3])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_struct_def_1(p):
        """
        struct_def : STRUCT ID '{' struct_fields '}'
        """
        p[0] = ast.Struct(p[2], p[4])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_struct_def_2(p):
        """
        struct_def : STRUCT ID EXTENDS ID '{' struct_fields '}'
        """
        p[0] = ast.Struct(p[2], p[6], p[4])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_fields_1(p):
        """
        struct_fields : struct_fields struct_field
        """
        p[0] = p[1]
        p[0].append(p[2])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_fields_2(p):
        """
        struct_fields : struct_field
        """
        p[0] = [p[1]]

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_struct_fields_3(p):
        """
        struct_fields : empty
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_field_1(p):
        """
        struct_field : type ID
        """
        p[0] = ast.StructField(p[2], p[1])

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_struct_field_2(p):
        """
        struct_field : ID ID
        """
        filed_type = ast.CustomType(p[1])
        p[0] = ast.StructField(p[2], filed_type)

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_array_def_1(p):
        """
        array_def : ARRAY ID OF type
        """
        p[0] = ast.Array(p[2], p[4])

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_array_def_2(p):
        """
        array_def : ARRAY ID OF ID
        """
        element_type = ast.CustomType(p[4])
        p[0] = ast.Array(p[2], element_type)

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_1(p):
        """
        type : INT8
             | INT16
             | INT32
             | INT64
             | UINT8
             | UINT16
             | UINT32
             | UINT64
             | BOOLEAN
             | FLOAT
             | DOUBLE
             | STRING
             | BYTEBUFFER
        """
        type_class = getattr(ast, p[1])
        p[0] = type_class()

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_type_2(p):
        """
        type : INT8 '[' ']'
             | INT16 '[' ']'
             | INT32 '[' ']'
             | INT64 '[' ']'
             | UINT8 '[' ']'
             | UINT16 '[' ']'
             | UINT32 '[' ']'
             | UINT64 '[' ']'
             | BOOLEAN '[' ']'
             | FLOAT '[' ']'
             | DOUBLE '[' ']'
             | STRING '[' ']'
             | BYTEBUFFER '[' ']'
        """
        type_class = getattr(ast, p[1])
        p[0] = ast.Array(None, type_class())

    # noinspection PyUnusedLocal, PyIncorrectDocstring
    @staticmethod
    def p_empty(p):
        """
        empty :
        """
        pass

    # noinspection PyIncorrectDocstring
    @staticmethod
    def p_error(p):
        # TODO: How to handle errors?
        print("Syntax error at line {} near '{}'".format(p.lineno, p.value))

    def __init__(self, the_lexer=None, **kwargs):
        """
        Constructor.

        :param lexer: a lexer object to use.
        """
        if not the_lexer:
            the_lexer = franca_lexer.Lexer()
        self._lexer = the_lexer
        self.tokens = self._lexer.tokens
        # Disable debugging, by default.
        if "debug" not in kwargs:
            kwargs["debug"] = False
        if "write_tables" not in kwargs:
            kwargs["write_tables"] = False
        self._parser = yacc.yacc(module=self, **kwargs)

    def parse(self, data):
        """
        Parse input text

        :param data: Input text to parse.
        :return: AST representation of the input.
        """
        return self._parser.parse(data)
