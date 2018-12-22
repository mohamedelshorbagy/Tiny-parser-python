from scanner_class import Scanner
from syntaxtree_draw import SyntaxTree

class Parser(object):
    """
    Defines the parser class implementation follows the recursive descent approach
    The flow is as the following
    1. Invoke the parser scan()
    2. Get the parser array of tokens
    3. Using recursive descent navigate token by token
    4. Form the syntax tree, export it to an output file

    ### Attributes
    - scanner : the scanner object
    - graph : graphviz object, used to form the syntax tree
    - next_token : an int that points to the next token from the scanner token array
    PyGraphviz must be installed
    - num_tokens : the total number of tokens to be consumed
    - log : the text output [ONLY FOR THE ASSIGNMENT]
    - num_nodes : the number of nodes in the syntax tree
    - parent_node : the name of the last node to attach at the same level
    - draw_horizontal : bool used to determine if statements are at the same scope or not
    - draw_id : used to ensure an ID will not be drawn in the specific cases for read, assign
    it is set to false everytime we are drawing a block that is part of other block
    e.g. the 'then' @ the 'if block'
    - last_factor : the last factor node id in the graph
    """

    def __init__(self):
        self.scanner = Scanner()
        self.graph = None
        self.next_token = 0
        self.num_tokens = 0
        self.log = ""
        self.num_nodes = 0
        self.parent_node = None
        self.draw_horizontal = True
        self.draw_id = False
        self.last_factor = None
        self.draw_id_block = True

    def parse(self, in_file_dir="tiny_sample_code.txt", out_file_dir="parser_output.txt",
             out_image_dir="syntax_tree_output.png"):
        """
        Implements the parse functionality. Attempts to 
        1. scan the input file
        2. check everything is ok from the scanner side
        3. form the syntax tree and the parser output file

        Note : Everything is considered at the same [or a relative] directory to the code
        this includes inputs and outputs
        ### Arguments
        - in_file_dir : input tiny code file in a .txt format
        - out_file_dir : the parser text output
        - out_image_dir : the image output for the syntax tree
        """
        s = self.scanner.scan(in_file_dir, write_opt=False)
        if s == 0:
            return
        self.num_tokens = len(self.scanner.tokens)
        self.graph = SyntaxTree(out_image_dir)

        # Attempts to check if the progam is a sequence of statements
        s = self.is_stmt_seq()
        if s:
            self.log += "Program found\n"
        print("Parser executed successfully")
        out_file = open(out_file_dir, 'w')
        out_file.write(self.log+"\n")
        out_file.close()
        self.graph.show()

    def match(self, val):
        """
        Attempts to check if the current token value
        is identical to val, if yes the next token will be incremented
        """
        if self.is_done():
            return False
        if self.scanner.tokens[self.next_token].literal == val:
            self.next_token += 1
            return True
        return False

    def is_done(self):
        """
        Indicate the parsing consumed all the tokens from the scanner
        """
        return self.num_tokens == self.next_token

    def is_stmt_seq(self):
        """
        Check if the current token represents a statement sequence by calling other
        checking helper functions
        The top checking function
        """
        # check if the current token represents a statement
        s = self.is_statement()

        # now check the optional semicolon
        while self.match(';'):
            s = self.is_statement()
        self.log += "Statement_Sequence Found\n"
        return s

    def is_statement(self):
        """
        Check if the current token represents a statement
        """
        s = self.is_if() or self.is_repeat() or self.is_assig() or self.is_read()\
            or self.is_write()
        if not s:
            raise ValueError('Error, malformed statement')
        self.log += "Statement Found\n"
        return s

    def is_if(self):
        """
        Attempts to check if the current token represents an if statement
        """
        s = self.match('if')
        if not s:
            return False
        ## now we are sure an if exisits
        self.parent_node = self.graph.create_node('I', "If", inline_with=self.parent_node)
        self.draw_horizontal = False
        rec = self.parent_node
        if_node = self.parent_node 
        s = self.is_expr()
        if not s:
            return False
        # throw an error
        s = self.match('then')
        if not s:
            raise ValueError('Missing "then" after an if statement')
        self.parent_node = if_node
        self.draw_horizontal = False
        s = self.is_stmt_seq()
        if not s:
            return False
        # else is optional
        if self.match('else'):
            self.parent_node = if_node
            self.draw_horizontal = False
            s = self.is_stmt_seq()
            if not s:
                return False
        s = self.match('end')
        if not s:
            raise ValueError('Missing "end" after an if statement')
        # now we are sure an if exists, return the parent node to the if block
        self.parent_node = rec
        self.draw_horizontal = True
        self.log += "IF_statement found\n"
        return True

    def is_repeat(self):
        """
        Check if the current token is for a repeat statement
        """
        s = self.match('repeat')
        if not s:
            return False
        # now a repeat exists, draw its block and keep a reference to the current parent
        self.parent_node = self.graph.create_node('R', "Repeat", inline_with=self.parent_node)
        repeat_node = self.parent_node
        self.draw_horizontal = False
        # check if statement sequence after the repeat
        s = self.is_stmt_seq()
        if not s:
            return False
        s = self.match('until')
        if not s:
            raise ValueError('Missing "until" after a repeat statement')
        # when creating the rec, connect it to the repeat block
        self.parent_node = repeat_node
        self.draw_horizontal = False
        s = self.is_expr()
        if not s:
            raise ValueError('Missing "expression" after until statement')
        # return the parent node again
        self.draw_horizontal = True
        self.log += "Repeat_statement found\n"
        return True

    def is_assig(self):
        """
        Check if the current token is for an assignment statement
        """
        self.draw_id = False
        self.draw_id_block = False
        s = self.is_identifier()
        self.draw_id_block = True
        #current_draw_h = self.draw_horizontal
        if not s:
            return False
        s = self.match(':=')
        if not s:
            return False
        block_name = "Assign\n("+self.scanner.tokens[self.next_token-2].literal+")"
        if self.draw_horizontal:
            self.parent_node = self.graph.create_node('A', block_name, inline_with=self.parent_node)
        else:
            # 1- create it
            # 2- connect it to the upper parent
            # 3- declare it as the new parent
            _p = self.graph.create_node('A', block_name)
            self.graph.connect_node(self.parent_node, _p)
            self.parent_node = _p
        self.draw_horizontal = False
        self.draw_id = False
        self.last_factor = None
        s = self.is_expr()
        if not s:
            raise ValueError('Missing "expression" after assignment statement')
        if self.last_factor is not None:
            self.graph.connect_node(self.parent_node, self.last_factor)
        self.draw_horizontal = True#current_draw_h
        self.log += "Assignment_Statement found\n"
        self.draw_id = True
        self.draw_id_block = True
        return True 

    def is_read(self):
        """
        Check if the current token is for a read statement
        """
        s = self.match('read')
        if not s:
            return False
        #self.draw_id = False
        self.draw_id_block = False
        s = self.is_identifier()
        #self.draw_id = True
        if not s:
            raise ValueError('Missing "identifier" after read statement')
        ## Now read followed by an identifier is detected, draw it attached to the current parent
        ## and set it as the new parent node
        block_name = "Read\n("+self.scanner.tokens[self.next_token-1].literal+")"
        self.parent_node = self.graph.create_node('R', block_name, inline_with=self.parent_node)
        self.log += "Read_Statement found\n"
        self.draw_id_block = True
        return True

    def is_write(self):
        """
        Check if the current token is for a write statement
        """
        s = self.match("write")
        if not s:
            return False
        # get the current parent, needed in case is_expr() wanted to draw
        #rec = self.parent_node
        #current_draw_h = self.draw_horizontal
        if self.draw_horizontal:
            self.parent_node = self.graph.create_node('W', "Write", inline_with=self.parent_node)
        else:
            _p = self.graph.create_node('A', "Write")
            self.graph.connect_node(self.parent_node, _p)
            self.parent_node = _p
        self.draw_horizontal = False
        s = self.is_expr(True)
        if not s:
            raise ValueError('Missing "expression" after write statement')
        #self.parent_node = rec
        self.draw_horizontal = True#current_draw_h
        self.log += "Write_Statement found\n"
        self.draw_id = True
        self.draw_id_block = True        
        return True

    def is_expr(self, draw_id=False):
        """
        Check if the current token represents an expression
        """
        self.draw_id = draw_id
        self.last_factor = None
        s = self.is_simple_expr()
        # since this is not a statement, no node can exist near it
        rec = self.parent_node
        current_draw_h = self.draw_horizontal
        if not s:
            return False
        if self.match('<') or self.match('='):
            #lhs = self.last_factor
            self.draw_id_block = True
            self.log += "Comparison_Operator found\n"
            block_name = "OP\n("+self.scanner.tokens[self.next_token-1].literal+")"
            if self.draw_horizontal:
                self.parent_node = self.graph.create_node('O', block_name, inline_with=self.parent_node, shape='circle')
            else:
                _p = self.graph.create_node('O', block_name, shape='circle')
                self.graph.connect_node(self.parent_node, _p)
                self.parent_node = _p
            if self.last_factor is not None:
                self.graph.connect_node(self.parent_node, self.last_factor)
            self.draw_horizontal = False
            self.draw_id = True
            s = self.is_simple_expr()
            if not s:
                return False
        self.draw_horizontal = current_draw_h
        self.parent_node = rec
        self.log += "Expression found\n"
        return True

    def is_simple_expr(self):
        """
        Check if the current token is in a simple expression
        """
        self.last_factor = None
        s = self.is_term()
        rec = self.parent_node
        current_draw_h = self.draw_horizontal
        if not s:
            return False
        while self.match('+') or self.match('-'):
            self.draw_id_block = True
            self.log += "Add_Operator found\n"
            block_name = "OP\n("+self.scanner.tokens[self.next_token-1].literal+")"
            if self.draw_horizontal:
                self.parent_node = self.graph.create_node('O', block_name, inline_with=self.parent_node, shape='circle')
            else:
                _p = self.graph.create_node('O', block_name, shape='circle')
                self.graph.connect_node(self.parent_node, _p)
                self.parent_node = _p
            if self.last_factor is not None:
                self.graph.connect_node(self.parent_node, self.last_factor)
            self.draw_horizontal = False
            #self.draw_id = True
            self.last_factor = None
            s = self.is_term()
            if self.last_factor is not None:
                self.graph.connect_node(self.parent_node, self.last_factor)
                self.last_factor = None
            if not s:
                return False
            self.last_factor = None
        self.draw_horizontal = current_draw_h
        self.parent_node = rec
        self.log += "Simple_Expression found\n"
        return True

    def is_term(self):
        """
        Check if the current token is a term
        """
        self.last_factor = None
        s = self.is_factor()
        rec = self.parent_node
        current_draw_h = self.draw_horizontal
        if not s:
            return False
        while self.match('*') or self.match('/'):
            self.draw_id_block = True
            self.log += "Mul_Operator found\n"
            block_name = "OP\n("+self.scanner.tokens[self.next_token-1].literal+")"
            if self.draw_horizontal:
                self.parent_node = self.graph.create_node('O', block_name, inline_with=self.parent_node, shape='circle')
            else:
                _p = self.graph.create_node('O', block_name, shape='circle')
                self.graph.connect_node(self.parent_node, _p)
                self.parent_node = _p
            if self.last_factor is not None:
                self.graph.connect_node(self.parent_node, self.last_factor)
            self.draw_horizontal = False
            self.last_factor = None
            s = self.is_factor()
            if self.last_factor is not None:
                self.graph.connect_node(self.parent_node, self.last_factor)
                self.last_factor = None            
            if not s:
                return False
        self.parent_node = rec
        self.log += "Term found\n"
        return True

    def is_factor(self):
        """
        Check if the current token is a factor
        """
        s = self.match('(') and self.is_expr() and self.match(')')
        s = s or self.is_number()
        s = s or self.is_identifier()
        if s:
            self.log += "Factor found\n"
        return s 

    def is_number(self):
        """
        Check if the current token value is for a number
        """
        if self.scanner.tokens[self.next_token].base_type == 'number':
            s = self.graph.create_node('C', "const\n("+self.scanner.tokens[self.next_token].literal+")", shape='circle')
            if self.draw_id:
                self.graph.connect_node(self.parent_node, s)
            self.last_factor = s
            self.next_token += 1
            return True
        return False

    def is_identifier(self):
        """
        Check if the current token value is for an identifier
        """
        s = None
        if self.scanner.tokens[self.next_token].base_type == 'identifier':
            if self.draw_id_block:
                s = self.graph.create_node('C', "Id\n("+self.scanner.tokens[self.next_token].literal+")", shape='circle')            
            if self.draw_id and self.draw_id_block:
                self.graph.connect_node(self.parent_node, s)
            self.last_factor = s
            self.next_token += 1
            return True
        return False
