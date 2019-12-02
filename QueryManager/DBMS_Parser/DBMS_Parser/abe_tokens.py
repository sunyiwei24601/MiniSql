keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'AND', 'OR', 'NOT', 'CREATE', 'IN', 'DISTINCT', 'ALL']
punctuation = ['.', ',', '+', '-', '*', '/', '>', '<', '=', '>=', '<=', '><' '(', ')', '_', '\n', '\t', '*']


class _Tokens:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value


def is_keyword(string, pointer):
    token_keyword_value = ''
    start_pos = pointer
    cur_pos = start_pos

    while cur_pos < len(string):
        if string[cur_pos].isalpha():
            token_keyword_value += string[cur_pos]
            cur_pos += 1
            if string[cur_pos] == ' ' and cur_pos < len(string):
                break
            elif string[cur_pos].isalpha():
                token_keyword_value += string[cur_pos]
                cur_pos += 1
            else:
                break
        else:
            break

    up_tok_key = token_keyword_value.upper()
    if up_tok_key in keywords:
        new_pointer = cur_pos
        result = 1
        token_keyword = _Tokens('KEYWORD', token_keyword_value)
        return token_keyword, new_pointer, result
    else:
        new_pointer2 = cur_pos
        result = 0
        token_keyword = _Tokens('KEYWORD', token_keyword_value)
        return token_keyword, new_pointer2, result


def is_punctuation(string, pointer):
    token_punc_value = ''
    temp_punc = punctuation[:]
    temp_punc.remove('\n')
    temp_punc.remove('\t')

    if string[pointer] in temp_punc:
        token_punc_value += string[pointer]
        result = 1
        new_pointer = pointer + 1
        if string[new_pointer] in temp_punc and pointer < len(string):
            token_punc_value += string[new_pointer]
            new_pointer += 1
        token_punc = _Tokens('PUNCTUATION', token_punc_value)
        return token_punc, new_pointer, result
    else:
        result = 0
        new_pointer2 = pointer + 1
        token_punc = _Tokens('PUNCTUATION', token_punc_value)
        return token_punc, new_pointer2, result


def is_constant(string, pointer):
    token_constant_value = ''
    start_pos = pointer
    cur_pos = start_pos
    dot_exam = 0
    temp_punc = punctuation[:]
    temp_punc.remove('.')
    result = 0

    while cur_pos < len(string):
        if string[cur_pos].isdigit():
            token_constant_value += string[cur_pos]
            cur_pos += 1
            if string[cur_pos] == '.' and dot_exam == 0 and cur_pos < len(string):
                token_constant_value += string[cur_pos]
                cur_pos += 1
                dot_exam += 1
            else:
                pass
            result += 1
        elif string[cur_pos] in temp_punc or string[cur_pos] == ' ':
            break
        else:
            break

    new_pointer = cur_pos
    token_constant = _Tokens('CONSTANT', token_constant_value)
    return token_constant, new_pointer, result


def is_identifier(string, pointer):
    token_identifier_value = ''
    start_pos = pointer
    cur_pos = start_pos
    temp_punc = punctuation[:]
    temp_punc.remove('_')
    result = 0

    while cur_pos < len(string):
        if string[cur_pos].isalpha():
            token_identifier_value += string[cur_pos]
            cur_pos += 1
            result += 1
            if cur_pos < len(string):
                if string[cur_pos].isdigit() or string[cur_pos] == '_' or string[cur_pos] == '#':
                    token_identifier_value += string[cur_pos]
                    cur_pos += 1
                    result += 1
        elif string[cur_pos] in temp_punc:
            break
        else:
            break

    new_pointer = cur_pos
    token_identifier = _Tokens('IDENTIFIER', token_identifier_value)
    return token_identifier, new_pointer, result


def is_whitespace(string, pointer):
    token_whitespace_value = ''

    if string[pointer] == ' ':
        token_whitespace_value += string[pointer]
        result = 1
        new_pointer = pointer + 1
        token_whitespace = _Tokens('WHITESPACE', token_whitespace_value)
        return token_whitespace, new_pointer, result

    else:
        result = 0
        new_pointer = pointer + 1
        token_whitespace = _Tokens('WHITESPACE', token_whitespace_value)
        return token_whitespace, new_pointer, result


def is_semicolon(string, pointer):
    token_semicolon_value = ''

    if string[pointer] == ';':
        token_semicolon_value += string[pointer]
        result = 1
        token_semicolon = _Tokens('SEMICOLON', token_semicolon_value)
        return token_semicolon, result
    else:
        result = 0
        token_semicolon = _Tokens('SEMICOLON', token_semicolon_value)
        return token_semicolon, result


def get_token(string):
    pointer = 0
    token_list = []
    while pointer < len(string):
        tok_key, pointer_key, is_keyword_result = is_keyword(string, pointer)
        if is_keyword_result != 0:
            token_list.append(tok_key)
            pointer = pointer_key

        tok_const, pointer_const, is_constant_result = is_constant(string, pointer)
        if is_constant_result != 0:
            token_list.append(tok_const)
            pointer = pointer_const

        tok_punc, pointer_punc, is_punctuation_result = is_punctuation(string, pointer)
        if is_punctuation_result != 0:
            token_list.append(tok_punc)
            pointer = pointer_punc

        tok_identi, pointer_identi, is_identifier_result = is_identifier(string, pointer)
        if is_identifier_result != 0:
            token_list.append(tok_identi)
            pointer = pointer_identi

        tok_whsp, pointer_whsp, is_whitespace_result = is_whitespace(string, pointer)
        if is_whitespace_result != 0:
            # token_list.append(tok_whsp)
            pointer = pointer_whsp

        tok_semicolon, is_semicolon_result = is_semicolon(string, pointer)
        if is_semicolon_result != 0:
            token_list.append(tok_semicolon)
            break
    return token_list
