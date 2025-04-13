import re


class StringManipulate:

    def __init__(self):
        self.notation_synonyms()

    def __call__(self, notation_string):
        """
        This method can be called to get the parsed moves from a notation string.
        - Cleans the notation string by parsing it into spaced moves.
        - Replaces common notations with their synonyms.
        - Expands Commutators and conjugates into their canonical form.
        - Returns the cleaned notation string.
        Examples:
            "R U R'U RU2 R' \\Sune" → "R U R' U R U2 R'"
            "[R U R'] [R U2 R]" → "R U R' U2 R"
            "[R, U][U2, R] " → "R U R' U2 R"
            [R: [U R', U]] → "R U R' U2 R"

        
        Args:
            notation_string (str): The notation string to parse
            
        Returns:
            string: cleaned to canonical notation
        """
        s = self.split_moves(notation_string)
        s = [self.synonyms[i] if i in self.synonyms else i for i in s]
        parsed_comm = self.parse_comm(" ".join(s))
        return parsed_comm 
    @staticmethod
    def split_moves(notation_string):
        """
        Splits a Rubik's cube notation string into individual moves.
        Works with both space-separated and compact notation.
        
        Examples:
            "R U R' U R U2 R'" → ["R", "U", "R'", "U", "R", "U2", "R'"]
            "RUR'URU2R'" → ["R", "U", "R'", "U", "R", "U2", "R'"]
            
        Args:
            notation_string (str): The notation string to split
            
        Returns:
            list: List of individual moves
        """
        # Remove any comments and extra whitespace
        clean_string = re.sub(r'//.*', '', notation_string).strip()
        
        # Define regex pattern for moves
        # Matches:
        # - Standard face moves (RUFLDB)
        # - Wide moves (lowercase or w/W suffix)
        # - Slice moves (MES)
        # - Rotation moves (xyz)
        # - With optional ' or 2 modifier
        pattern = r'([RUFLDBMESrufdbxyz][w|W]?[\'2]?)'
        
        # Find all matches
        moves = re.findall(pattern, clean_string)
    
        return moves
    

    def notation_synonyms(self):
        '''
        Returns a mapping from common notations to synonyms of the notation. 
        '''
        faces = ["U", "R", "F", "D", "L", "B"]
        modifiers = ["", "'", "2"]

        synonyms = {}
        for i in faces:
            for j in modifiers:
                synonyms[i+"W"+j] = i.lower() + j
                synonyms[i+"w"+j] = i.lower() + j
                synonyms[i+j] = i + j
                synonyms[i.lower()+j] = i.lower() + j
        rotations = ["x", "y", "z"]
        for i in rotations:
            for j in modifiers:
                synonyms[i+j] = i+j
                synonyms[i.upper()+j] = i+j
        self.synonyms = synonyms
        return synonyms

    @staticmethod
    def inverse(A):
        '''
        Inverts a sequence of turns:
        R U R' becomes R U' R'
        '''
        x = A.split(" ")
        x = [p for p in x if p != ""]
        reformatted = [l+"'" if len(l) == 1 else l if "2" in l else l[0] for l in x]
        reformatted = reformatted[::-1]
        return " ".join(reformatted)

    @staticmethod
    def parse_comm(s):
        shortcut = set([",",":","[", "]"]).intersection(set(s))
        if len(shortcut) == 0:
            return(s)
        start = 0
        count = 0
        out = []
        for i in range(len(s)):
            l = s[i]
            if l == "[":
                if count == 0:
                    out.append(s[start:i])
                    start = i+1
                count += 1
            elif l == "]":
                count -= 1
                if count == 0:
                    out.append(s[start:i])
                    start = i+1
            elif (l == "," or l == ":") and count == 0:
                a = " ".join([StringManipulate.parse_comm(x) for x in out]) + s[start: i]
                b = s[i+1:len(s)]
                a, b = StringManipulate.parse_comm(a), StringManipulate.parse_comm(b)
                if l == ",":
                    comm_out = a + b + " "+ StringManipulate.inverse(a) +" "+ StringManipulate.inverse(b)
                if l == ":":
                    comm_out = a + b + " " +StringManipulate.inverse(a)
                return comm_out
        if len(out) == 0:
            return s
        else:
            if start < len(s):
                out.append(s[start:len(s)])
            out = [StringManipulate.parse_comm(x) for x in out]
            return " ".join(out)

if __name__ == "__main__":
    # This runs tests on the commutator parser.
    wow = { 1 : "R U R' U'",
            2 : "[R U R': [R U R' U2, R2 U' R]]",
            3 : "[R, U]",
            7 : "[R: [U R', U]]",
            4 : " F [R U: R' [x, y] F]",
            5 : "[ F R: [M', U2]] [[r: U], D2]",
            6 : "[ F R: [[M', U2]: [[r:U], D2]]]"}
    #print(wow[5])
    def io_verbose(func):
        def wrapper(s):
            print("Processing substring: " + s)
            x = func(s)
            print("Output is: " + x)
            return func(s)
        return wrapper
    #parse_comm = io_verbose(parse_comm)
    #print(parse_comm(wow[5]))
    #'''
    for thingy in wow.values():
        print(thingy)
        print("becomes")
        print(StringManipulate.parse_comm(thingy) + "\n")
    str1 = "R U R' U R U2 R' RwUr' U' r x y R' U2 \\ This is a comment\nR2 U2 R' U2 R rwU'r"
    str2 = str1.replace(" ", "")
    print(StringManipulate.split_moves(str1))
    print(StringManipulate.split_moves(str2))
    #print(StringManipulate.inverse(str1))
    #'''