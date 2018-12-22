from parser_class import Parser

MY_PARSER = Parser()
file_name = input('File name : ')
MY_PARSER.parse(in_file_dir=file_name)