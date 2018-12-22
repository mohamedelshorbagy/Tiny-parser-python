from token_ds import Token

class Scanner(object):
    """
    Defines the scanner class implementation follows the doubly nested switch-case approach

    ### Attributes
    - res_words : an array of all the reserver words for the language
    - sp_symbols : an array of all the reserved symbols for the language
    - _tokens_file : a string of the overall value+type to be shown @ the text file [can be omitted]
    - tokens : array of Token objects
    - state : a variable indicating the current state. Negative value for this
    variable indicates an error; Note : 1 is the input state, 0 is the end state
    - stream_pos : a variable indicating the index at the input stream character
    - current_token_val : FSM internal variable to track the 
    - look_up_symbols : used to lookup for the symbols of the language
    - look_up_numbers : used to look up for a valid number

    ### Args
    - res_words : An array of all the reserved words that the scanner should consider.
    By default it will assume `["if", "then", "else", "end",
    "repeat", "until", "read", "write"]`
    - sp_symbols : An array of all the special symbols supported by the language.
    By default it will assume `["+", "-", "*", "/", "=", "<", "(", ")", ";", ":", "="]`
    as the only special symbols

    """

    def __init__(self, res_words=None, sp_symbols=None):
        """
        out_file_dir : assumes a def. value for the dir
        """
        # Initially set the default values if not given at constructor
        if res_words is None:
            self.res_words = ["if", "then", "else", "end", "repeat", "until", "read", "write"]
        if sp_symbols is None:
            self.sp_symbols = ["+", "-", "*", "/", "=", "<", "(", ")", ";"]
        # initiallize the empty tokens array
        self._tokens_file = []
        self.tokens = []
        #Set the initial state to the input state and the initial stream_pos
        self.state = 1
        self.stream_pos = 0

        self.look_up_symbols = "abcdefghijklmnopqrstuvwxyz"
        self.look_up_numbers = "1234567890"

        self.current_token_val = ""
        self.current_token_type = ""

    def scan(self, in_file_dir="tiny_sample_code.txt", out_file_dir="scanner_output.txt", write_opt=True):
        """
        Collects the tokens of in_file_dir and saves the result at out_file_dir

        ## Args
        - in_file_dir : input tiny code file
        - out_file_dir : text output location
        
        ## Returns
        0 : in case the scanner failed
        1 : in case the scanner successfully scanned the tiny without errors
        """
        # read input text
        in_file = open(in_file_dir)
        # initially we start at the 1st line
        current_line = 1
        for line in in_file.readlines():
            line = line + " "
            end = len(line[:-1])-1
            while self.stream_pos <= end:
                self.get_token(line[self.stream_pos])
            self.stream_pos = 0
            if self.state < 0:
                break
            current_line += 1
        in_file.close()
        if self.state < 0:
            print ("ERROR IN YOUR CODE AT LINE : ", current_line)
            return 0
        # store the results
        if write_opt:
            out_file = open(out_file_dir, 'w')
            for i in self._tokens_file:
                out_file.write(i+"\n")
            out_file.close()
            print ("Scanner executed successfully")
        return 1

    def get_token(self, next_in):
        """
        Reads and may consume the current input from the input stream
        """
        if self.state == 1:
            # ignore white spaces
            if next_in == "{":
                self.state = 2
            elif next_in in self.look_up_numbers:
                self.state = 3
                self.current_token_val = next_in
                self.current_token_type = ": number"
            elif next_in in self.look_up_symbols:
                self.state = 4
                self.current_token_val = next_in
                self.current_token_type = ": identifier"
            elif next_in == ":":
                self.state = 5
                self.current_token_type = ": assignment"
            elif next_in in self.sp_symbols:
                self.current_token_val = next_in
                self.current_token_type = ": special symbol"
                self.state = 6
            elif next_in != " " and next_in != "\n":
                #error
                self.state = -1
        elif self.state == 2:
            #comment state
            if next_in == "}":
                self.state = 1
                self.current_token_val = ""
        elif self.state == 3:
            # input number state
            if next_in in self.look_up_numbers:
                self.current_token_val += next_in
            else:
                self.state = 6
                #dont consume the current input
                self.stream_pos -= 1
        elif self.state == 4:
            #letter state
            if next_in in self.look_up_symbols:
                self.current_token_val += next_in
            else:
                self.state = 6
                if self.current_token_val in self.res_words:
                    self.current_token_type = ": reserved word"
                # dont consume next output
                self.stream_pos -= 1
        elif self.state == 5:
            if next_in == "=":
                self.current_token_val = ":="
                self.state = 6
        elif self.state == 6:
            self._tokens_file.append(self.current_token_val + self.current_token_type)
            self.tokens.append(Token(self.current_token_val, self.current_token_type[2:]))
            self.stream_pos -= 1
            self.state = 1
        self.stream_pos += 1
        