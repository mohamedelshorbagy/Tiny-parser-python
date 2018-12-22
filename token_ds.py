class Token(object):
    """
    Implementation of the Scanner tokens

    ### Attributes
    - literal : the literal value of the token, this might contain the identifier name or numeber
    value or whatever
    the reserved word
    - base_type : a string used for indicating wheather this token is a number, identifier
    or some reserved word

    ### Args
    - literal : the literal value of the token
    - base_type : the type  [used for further processing @ the parser]
    """
    def __init__(self, literal, base_type=''):
        """
        constructor
        """
        self.literal = literal
        self.base_type = base_type

    def is_number(self):
        """
        returns true if this token is a number, be it a float or an integer
        """
        return self.base_type == 0

    def is_id(self):
        """
        returns true if this token is for an identifier
        """
        return self.base_type == 1
