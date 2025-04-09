class StringManipulate:
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
            7 : "[R: U]",
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
    #'''