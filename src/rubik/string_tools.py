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
        commentless = self.remove_comments(notation_string)
        split = self.split_moves(commentless)
        replaced = [self.synonyms[i] if i in self.synonyms else i for i in split]
        parsed_comm = self.parse_comm(" ".join(replaced))
        result = re.sub(r"\s+", ' ', parsed_comm).strip()
        return result
    
    @staticmethod
    def remove_comments(notation_string):
        lines = notation_string.split("\n")
        cleaned_lines = []
        for line in lines:
            # Remove comments (both styles)
            comment_start_slash = line.find('\\')
            comment_start_double = line.find('//')
            
            if comment_start_slash >= 0:
                line = line[:comment_start_slash]
            if comment_start_double >= 0:
                line = line[:comment_start_double]
                
            if line.strip():  # Only keep non-empty lines
                cleaned_lines.append(line)
        # Join cleaned lines back together
        return " ".join(cleaned_lines)
    
    @staticmethod
    def clean_string(notation_string):
        """
        Cleans a Rubik's cube notation string by removing comments and extra whitespace.
        
        Args:
            notation_string (str): The notation string to clean
            
        Returns:
            str: Cleaned notation string
        """
        commentless = StringManipulate.remove_comments(notation_string)
        as_list = StringManipulate.split_moves(commentless)
        clean_string = " ".join(as_list)
        
        return clean_string
    
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
        
        # Define regex pattern for moves, commutator notation, and brackets
        # Matches:
        # - Standard face moves (RUFLDB)
        # - Wide moves (lowercase or w/W suffix)
        # - Slice moves (MES)
        # - Rotation moves (xyz)
        # - With optional ' or 2 modifier
        # - [ , : ]
        pattern = r'([RUFLDBMESrufdbxyz][w|W]?[\'2]?|\[|\]|,|:)'
        
        # Find all matches
        moves = re.findall(pattern, notation_string)
        
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
                synonyms[i.lower()+"W"+j] = i.lower() + j
                synonyms[i.lower()+"w"+j] = i.lower() + j
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
        reformatted = [chunk+"'" if len(chunk) == 1 else chunk if "2" in chunk else chunk[0] for chunk in x]
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
            6 : "[ F R: [[M', U2]: [[r: U], D2]]]"}
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
    # print(StringManipulate.split_moves(str1))
    # print(StringManipulate.split_moves(str2))
    manipulator = StringManipulate()
    weird_case = "[R U R', D] \\ Shitty situation \n [D2: [R U R', D]] \\ URF->LBD->BRD"
    print(StringManipulate.split_moves(weird_case))
    #print(StringManipulate.inverse(str1))
    joined = " ".join(StringManipulate.split_moves(weird_case))
    print(joined)
    print(manipulator(weird_case))
    print(manipulator("[Rw: [U, R']] // This is a test"))
    print(manipulator("[R,U]"))
    print("Done")
    #'''