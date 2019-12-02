from abe_tokens import get_token
from get_symbol_table import analysis_db
from get_symbol_table import Symbol

"""

"""


class Parser:
    def __init__(self, input, metadata):
        self._token_l = get_token(input)  # get a token list
        self._cur_pos = 0  # point to the token which is under analyzing
        # self._post_pos = self._cur_pos - 1
        # self._post_pos_tok = self._token_l[self._cur_pos-3].get_value()
        # self._cur_pos_tok = self._token_l[self._cur_pos-1].get_value()  # which token is under analyzing
        self._token_l_len = len(get_token(input))  # how many tokens?
        self._sem_stack = []  # store the semantic operations
        self._final_stack = []  # store the grammar tree
        self._table_list = analysis_db(metadata)
        self._table_list_len = len(analysis_db(metadata))
        # self._attr_list = analysis_db(metadata)[1]
        # self._attr_list_len = len(analysis_db(metadata)[1])
        self._symb_tab_list = []  # store the table names and their references to the table_list
        self._symb_col_list = []  # store the column names and their references to the table_list
        self._temp = ''

    def get_cur_pos(self):
        return self._cur_pos

    def read(self):
        return self._token_l[self._cur_pos]

    def next(self):
        if self._cur_pos+1 < self._token_l_len:
            self._cur_pos += 1

    def get_final_stack(self):
        return self._final_stack

    def find_tab_ref(self):
        # _post_pos_tok = self._token_l[self._cur_pos - 3].get_value()
        _cur_pos_tok = self._token_l[self._cur_pos - 1].get_value()
        for tab in self._table_list:
            if tab.get_relation_name() == _cur_pos_tok:
                return Symbol(tab.get_relation_name(), tab)

    # find which item in table/column list is table/column in the symbol list referred to
    def find_col_ref(self):
        _post_pos_tok = self._token_l[self._cur_pos - 3].get_value()
        _cur_pos_tok = self._token_l[self._cur_pos - 1].get_value()
        c = self._token_l[self._cur_pos-2].get_value() == '.'
        if c:
            for tab in self._table_list:
                if tab.get_relation_name() == _post_pos_tok:
                    tab_attr = tab.get_attributes()
                    for attr in tab_attr:
                        if attr.get_name() == _cur_pos_tok:
                            attr_name = _post_pos_tok + '.' + _cur_pos_tok
                            return Symbol(attr_name, attr)
        if not c:
            for tab in self._table_list:
                tab_attr = tab.get_attributes()
                tab_name = tab.get_relation_name()
                for attr in tab_attr:
                    if attr.get_name() == _cur_pos_tok:
                        attr_name = tab_name + '.' + _cur_pos_tok
                        return Symbol(attr_name, attr)

    # find whether the self._cur_pos_token is in symb_tab_list/symb_col_list or not
    def compare_id(self, symbol_list):
        _post_pos_tok = self._token_l[self._cur_pos - 3].get_value()
        _cur_pos_tok = self._token_l[self._cur_pos - 1].get_value()
        temp = 0
        t = self._token_l[self._cur_pos - 2].get_value() == '.'
        if t:
            for item in symbol_list:
                if item.get_symbol_name == _post_pos_tok + '.' + _cur_pos_tok:
                    temp = 1
        if not t:
            for item in symbol_list:
                if item.get_symbol_name == _cur_pos_tok:
                    temp = 1
        if temp == 1:
            return True
        else:
            return False

    '''
    all the code below is SQL Grammar Analyzing
    '''
    def match(self, *args):
        pos = self._cur_pos
        f = True
        for arg in args:
            # while pos < len(self._token_l):
            if hasattr(arg, '__call__'):
                if not arg():
                    f = False
                    break
            else:
                t = self.read()
                if t.get_type() == 'SEMICOLON':
                    f = arg == t.get_type()
                elif t.get_type() == 'KEYWORD':
                    f = arg == t.get_value().upper()
                elif t.get_type() == 'IDENTIFIER':
                    f = arg == t.get_type()
                elif t.get_type() == 'PUNCTUATION':
                    f = arg == t.get_value()
                elif t.get_type() == 'CONSTANT':
                    f = arg == t.get_type()
                elif t.get_type() == 'WHITESPACE':
                    f = True
                if f:
                    self.next()
                else:
                    f = False
                    self._cur_pos = pos
                    break
        return f

    def preparable_stmt(self):
        f = self.match(self.select_stmt)
        if not f:
            f = self.match(self.create_stmt)

        return f

    def create_stmt(self):
        f = self.match(self.create_ddl_stmt)
        return f

    def create_ddl_stmt(self):
        f = self.match(self.create_database_stmt)
        if not f:
            f = self.match(self.create_table_stmt)
        if not f:
            f = self.match(self.create_table_as_stmt)
        if not f:
            f = self.match(self.create_index_stmt)
        # if not f:
        #     f = self.match(self.create_view_stmt)
        return f

    def create_database_stmt(self):
        f = self.match('CREATE', 'DATABASE')
        if f:
            self.match('IF', 'NOT', 'EXISTS')
        if f:
            # f = self.match('IDENTIFIER', self.opt_with, self.opt_template_clause,
            #                self.opt_encoding_clause, self.opt_lc_collate_clause,
            #                self.opt_lc_ctype_clause)
            f = self.match('IDENTIFIER')
        return f

    def create_table_stmt(self):
        # f = self.match('CREATE', self.opt_temp_create_table, 'TABLE')
        f = self.match('CREATE', 'TABLE')
        if f:
            self.match('IF', 'NOT', 'EXISTS')
        if f:
            # f = self.match('IDENTIFIER', '(', self.opt_table_elem_list, ')',
            #                self.opt_interleave, self.opt_partition_by)
            f = self.match('IDENTIFIER')
        return f

    def create_table_as_stmt(self):
        # f = self.match('CREATE', self.opt_temp_create_table, 'TABLE')
        f = self.match('CREATE', 'TABLE')
        if f:
            self.match('IF', 'NOT', 'EXISTS')
        if f:
            # f = self.match('IDENTIFIER', self.create_as_opt_col_list, 'AS', self.select_stmt)
            f = self.match('IDENTIFIER', 'AS', self.select_stmt)
        return f

    def create_index_stmt(self):
        f = self.match('CREATE', self.opt_unique)
        if f:
            f = self.match('INDEX')
            if f:
                self.match('IF', 'NOT', 'EXISTS')
            if f:
                f = self.match('IDENTIFIER', 'ON', 'IDENTIFIER')
            if not f:
                f = self.match('INVERTED', 'INDEX')
                if f:
                    self.match('IF', 'NOT', 'EXISTS')
                if f:
                    f = self.match('IDENTIFIER', 'ON', 'IDENTIFIER')
        if f:
            # f = self.match('(', self.index_params, ')', self.opt_sorting, self.opt_interleave, self.opt_patition_by)
            f = self.match('(', self.index_params, ')')
        return f

    def opt_with(self):
        self.match('WITH')
        return True

    def opt_unique(self):
        self.match('UNIQUE')
        return True

    def index_params(self):
        f = self.match(',')
        if not f:
            f = self.match(self.index_elem)
        return f

    def index_elem(self):
        f = self.match(self.a_expr, self.opt_asc_desc, self.opt_nulls_order)
        return f

    '''
    go to:
        select_no_parens
        select_with_parens
    '''
    def select_stmt(self):
        f = self.match(self.select_no_parens)
        if not f:
            f = self.match(self.select_with_parens)
        return f

    '''
    go to:
        simple_select
        sort_clause
        opt_sort_clause
        select_limit
        locking_clause
    '''
    def select_no_parens(self):
        f = self.match(self.simple_select)
        if not f:
            f = self.match(self.sort_clause)
        # if not f:
        #   f = self.match(self.opt_sort_clause, self.select_limit)
        return f

    '''
    go to use:
        select_no_parens
        select_with_parens
    '''
    def select_with_parens(self):
        f = self.match('(')
        if f:
            f = self.match(self.select_no_parens)
            if not f:
                f = self.match(self.select_with_parens)
        if f:
            f = self.match(')')
        return f

    '''
    go to:
        simple_select_clause
        set_operation

    referenced by:
        select_clause
        select_no_parens
    '''
    def simple_select(self):
        f = self.match(self.simple_select_clause)
        if not f:
            f = self.match(self.select_with_parens)
        if f:
            self.match(self.set_operation)
        return f

    '''
    go to :
        simple_select
        select_with_parens
    '''
    def select_clause(self):
        f = self.match(self.simple_select)
        if not f:
            f = self.match(self.select_with_parens)
        return f

    '''
    referenced by:
        simple_select
    '''
    def simple_select_clause(self):
        f = self.match('SELECT')
        if f:
            f = self.match(self.opt_all_clause)
        if not f:
            f = self.match('DISTINCT')
        if not f:
            f = self.match(self.distinct_on_clause)
        if f:
            f = self.match(self.target_list, self.from_clause, self.opt_where_clause,
                           self.group_clause, self.having_clause)
        return f

    '''
    go to use:
        select_clause
        all_or_distinct
    '''
    def set_operation(self):
        f = self.match('UNION')
        if not f:
            f = self.match('INTERSECT')
        if not f:
            f = self.match('EXCEPT')
        if f:
            f = self.match(self.all_or_distinct, self.select_clause)
        return f

    def all_or_distinct(self):
        f = self.match('ALL')
        if not f:
            f = self.match('DISTINCT')
        else:
            f = True
        return f

    def opt_all_clause(self):
        self.match('ALL')
        return True

    '''
    go to use: expr_list
    referenced by: simple_select_clause
    '''
    def distinct_on_clause(self):
        f = self.match('DISTINCT', 'ON', '(', self.match(self.expr_list), ')')
        return f

    '''
    go to use: sortby_list
    '''
    def sort_clause(self):
        f = self.match('ORDER', 'BY', self.sortby_list)
        return f

    '''
    go to use: sortby
    '''
    def sortby_list(self):
        f = self.match(',')
        if not f:
            f = self.match(self.sortby)
        return f

    '''
    go to use:
        a_expr
        opt_asc_desc
        opt_nulls_order
        index_name
        
    '''
    def sortby(self):
        f = self.match(self.a_expr, self.opt_asc_desc, self.opt_nulls_order)
        if not f:
            f = self.match('PRIMARY', 'KEY', 'IDENTIFIER')
            if not f:
                f = self.match('INDEX', 'IDENTIFIER', '@', self.index_name)
            if f:
                f = self.match(self.opt_asc_desc)
        return f

    def opt_nulls_order(self):
        f = self.match('NULLS')
        if f:
            f = self.match('FIRST')
            if not f:
                f = self.match('LAST')
        if not f:
            f = True
        return f

    def opt_asc_desc(self):
        f = self.match('ASC')
        if not f:
            f = self.match('DESC')
        return True

    def index_name(self):
        f = self.match('IDENTIFIER')
        return f

    '''
    go to use: a_expr
    '''
    def expr_list(self):
        f = self.match(self.a_expr)
        if not f:
            f = self.match(',')
        return f

    '''
    go to use:
        a_expr
        b_expr
        c_expr
        in_expr
        subquery_op
        sub_type
    '''
    def a_expr(self):
        f = self.match(self.c_expr)
        if not f:
            f = self.match('DEFAULT')
        if not f:
            f = self.match('+')
            if not f:
                f = self.match('-')
            if not f:
                f = self.match('~')
            if not f:
                f = self.match('NOT')
            if f:
                f = self.match(self.a_expr)
        if f:
            f = self.match('AT', 'TIME', 'ZONE', self.a_expr)
            if not f:
                f = self.match('+', self.a_expr)

                if f:
                    q = ['+']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('-', self.a_expr)

                if f:
                    q = ['-']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('*', self.a_expr)

                if f:
                    q = ['*']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('/', self.a_expr)

                if f:
                    q = ['/']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('%', self.a_expr)

                if f:
                    q = ['%']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('^', self.a_expr)

                if f:
                    q = ['^']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('#', self.a_expr)

                if f:
                    q = ['#']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('&', self.a_expr)

                if f:
                    q = ['&']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('|', self.a_expr)

                if f:
                    q = ['|']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('<', self.a_expr)

                if f:
                    q = ['<']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('>', self.a_expr)

                if f:
                    q = ['>']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('=', self.a_expr)

                if f:
                    q = ['=']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('CONCAT', self.a_expr)

                if f:
                    q = ['CONCAT']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('LSHIFT', self.a_expr)

                if f:
                    q = ['LSHIFT']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('RSHIFT', self.a_expr)

                if f:
                    q = ['RSHIFT']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('<=', self.a_expr)

                if f:
                    q = ['<=']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('>=', self.a_expr)

                if f:
                    q = ['>=']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('><', self.a_expr)

                if f:
                    q = ['><']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('AND', self.a_expr)

                if f:
                    q = ['AND']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('OR', self.a_expr)

                if f:
                    q = ['OR']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('LIKE', self.a_expr)

                if f:
                    q = ['LIKE']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('NOT', 'LIKE', self.a_expr)

                if f:
                    q = ['NOT LIKE']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('SIMILAR', 'TO', self.a_expr)

                if f:
                    q = ['SIMILAR TO']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('NOT', 'SIMILAR', 'TO', self.a_expr)

                if f:
                    q = ['NOT SIMILAR TO']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('~', self.a_expr)

                if f:
                    q = ['~']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('ISNULL')

                if f:
                    q = ['IS NULL']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'NULL')

                if f:
                    q = ['IS NULL']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'NOT', 'NULL')

                if f:
                    q = ['IS NOT NULL']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('NOTNULL')

                if f:
                    q = ['NOT NULL']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'TRUE')

                if f:
                    q = ['IS TRUE']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'NOT', 'TRUE')

                if f:
                    q = ['IS NOT TRUE']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'FALSE')

                if f:
                    q = ['IS FALSE']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'NOT', 'FALSE')

                if f:
                    q = ['IS NOT FALSE']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'UNKNOWN')

                if f:
                    q = ['IS UNKNOWN']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'NOT', 'UNKNOWN')

                if f:
                    q = ['IS NOT UNKNOWN']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'DISTINCT', 'FROM', self.a_expr)

                if f:
                    q = ['IS DISTINCT FROM']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IS', 'NOT', 'DISTINCT', 'FROM', self.a_expr)

                if f:
                    q = ['IS NOT DISTINCT  FROM']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('BETWEEN', self.b_expr(), 'AND', self.a_expr)

                if f:
                    q = ['BETWEEN']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('NOT', 'BETWEEN', self.b_expr(), 'AND', self.a_expr)

                if f:
                    q = ['NOT BETWEEN']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('IN', self.in_expr())

                if f:
                    q = ['IN']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match('NOT', 'IN', self.in_expr())

                if f:
                    q = ['NOT IN']
                    for sym in self._sem_stack:
                        q.append(sym)
                    self._final_stack.append(q)
            if not f:
                f = self.match(self.subquery_op(), self.sub_type(), self.a_expr)
            if not f:
                f = True
        return f

    '''
    go to use: b_expr
    '''
    def b_expr(self):
        f = self.match(self.c_expr)
        if not f:
            f = self.match('+')
            if not f:
                f = self.match('-')
            if not f:
                f = self.match('~')
            if f:
                f = self.match(self.b_expr)
        if f:
            f = self.match('+')
            if not f:
                f = self.match('-')
            if not f:
                f = self.match('*')
            if not f:
                f = self.match('/')
            if not f:
                f = self.match('%')
            if not f:
                f = self.match('^')
            if not f:
                f = self.match('#')
            if not f:
                f = self.match('&')
            if not f:
                f = self.match('|')
            if not f:
                f = self.match('<')
            if not f:
                f = self.match('>')
            if not f:
                f = self.match('=')
            if not f:
                f = self.match('LSHIFT')
            if not f:
                f = self.match('RSHIFT')
            if not f:
                f = self.match('LESS_EQUALS')
            if not f:
                f = self.match('GREATER_EQUALS')
            if not f:
                f = self.match('NOT_EQUALS')
            if f:
                f = self.match(self.b_expr)
            else:
                f = True
        return f

    '''
    go to use: 
        d_expr
        case_expr
        select_with_parens
    '''
    def c_expr(self):
        f = self.match(self.d_expr)
        # if f:
        #     self.match(self.array_subscripts)
        if not f:
            f = self.match(self.case_expr)
        if not f:
            f = self.match('EXISTS', self.select_with_parens)
        return f

    '''
    go to use:
        column_path_with_star
        a_expr
        func_expr
        select_with_parens
    '''
    def d_expr(self):
        f = self.match('CONSTANT')
        # if not f:
        #     f = self.match(self.interval)
        if not f:
            f = self.match('TRUE')
        if not f:
            f = self.match('FALSE')
        if not f:
            f = self.match('NULL')
        if not f:
            f = self.match(self.column_path_with_star)
        if not f:
            f = self.match('PLACEHOLDER')
        if not f:
            f = self.match('(', self.a_expr, ')')
            if f:
                if self.match('.'):
                    f = self.match('*')
                    if not f:
                        f = self.match('IDENTIFIER')
        if not f:
            f = self.match(self.func_expr)
        if not f:
            f = self.match(self.select_with_parens)
        # if not f:
        #     f = self.match(self.labeled_row)
        # if not f:
        #     f = self.match('ARRAY')
        return f

    '''
    go to use:
        case_arg
        when_clause_list
        case_default
    '''
    def case_expr(self):
        f = self.match('CASE', self.case_arg, self.when_clause_list, self.case_default)
        return f

    def func_expr(self):
        pass

    '''
    go to use: a_expr
    '''
    def case_arg(self):
        f = self.match(self.a_expr)
        return f

    '''
    go to use: a_expr
    '''
    def case_default(self):
        self.match('ELSE', self.a_expr())
        return True

    '''
    go to:
        select_with_parens
        expr_tuple1_ambiguous
    '''
    def in_expr(self):
        f = self.match(self.select_with_parens)
        if not f:
            f = self.match(self.expr_tuple1_ambiguous)
        return f

    '''
    go to use: where_clause
    '''
    def opt_where_clause(self):
        self.match(self.where_clause)
        return True

    '''
    go to use: a_expr
    '''
    def where_clause(self):
        f = self.match('WHERE', self.a_expr)

        # pop the conditions from sem_stack, and push the t to sem_stack and final_stack
        t = ['CONDITION']
        for sym in self._sem_stack:
            t.append(sym)
        self._sem_stack.clear()
        self._final_stack.append(t)

        return f

    '''
    go to use: when_clause
    '''
    def when_clause_list(self):
        f = self.match(self.when_clause)
        return f

    '''
    go to use: a_expr
    '''
    def when_clause(self):
        f = self.match('WHEN', self.a_expr, 'THEN', self.a_expr)
        return f

    '''
    go to use: expr_list
    '''
    def group_clause(self):
        self.match('GROUP', 'BY', self.expr_list)
        return True

    '''
    go to use: a_expr
    '''
    def having_clause(self):
        self.match('HAVING', self.a_expr)
        return True

    def type_list(self):
        pass

    '''
    go to use: math_op
    '''
    def subquery_op(self):
        f = self.match(self.math_op)
        if not f:
            self.match('NOT')
            f = self.match('LIKE')
            if not f:
                f = self.match('ILIKE')
        return f

    def sub_type(self):
        f = self.match('ANY')
        if not f:
            f = self.match('SOME')
        if not f:
            f = self.match('ALL')
        return f

    def target_list(self):
        f = self.match(self.target_elem)
        while f and self.match(','):
            f = self.match(self.target_elem)

        # pop the target_elem from sem_stack, and push the q back to sem_stack and final_stack
        q = ['PROJECTION']
        for sym in self._sem_stack:
            q.append(sym)
        self._sem_stack.clear()
        self._final_stack.append(q)

        return f

    def target_elem(self):
        f = self.match('*')
        if not f:
            f = self.match(self.a_expr)
            if f:
                f = self.match('AS', self.target_name)
                if not f:
                    f = self.match('IDENTIFIER')
                if not f:
                    f = True
        return f

    def target_name(self):
        pass

    '''
    go to use:
        from_list
        opt_as_of_clause
    '''
    def from_clause(self):
        self.match('FROM', self.from_list, self.opt_as_of_clause)

        for sym_tab in self._symb_tab_list:
            if sym_tab.get_reference is None:
                for tb in self._table_list:
                    if tb.get_relation_name() == sym_tab.get_symbol_name:
                        self._symb_tab_list.remove(sym_tab)
                        self._symb_tab_list.append(Symbol(tb.get_relation_name(), tb))

        for sym_col in self._symb_col_list:
            if sym_col.get_reference is None:
                for tb in self._table_list:
                    for cl in tb.get_attributes():
                        t_c_name = tb.get_relation_name() + '.' + cl.get_name
                        if t_c_name == sym_col.get_symbol_name:
                            self._symb_col_list.remove(sym_col)
                            self._symb_col_list.append(Symbol(t_c_name, cl))

        return True

    '''
    go to use: table_ref
    '''
    def from_list(self):
        f = self.match(self.table_ref)
        while f and self.match(','):
            f = self.match(self.table_ref)

        # pop the target_elem from sem_stack, and push the p back to sem_stack and final_stack
        p = ['SELECT']
        for sym in self._sem_stack:
            p.append(sym)
        self._sem_stack.clear()
        self._final_stack.append(p)

        return f

    '''
    go to use: as_of_clause
    '''
    def opt_as_of_clause(self):
        self.match(self.as_of_clause)
        return True

    '''
    go to use: a_expr
    '''
    def as_of_clause(self):
        f = self.match('AS', 'OF', 'SYSTEM', 'TIME', self.a_expr)
        return f

    '''
    go to use:
        relation_expr
        opt_index_flags
        func_table
        select_with_parens
        row_source_extension_stmt
        joined_table
        opt_alias_clause
        alias_clause
    '''
    def table_ref(self):
        f = self.match('(', self.joined_table, ')', self.alias_clause)
        if not f:
            f = self.match('IDENTIFIER')

            # push the current symb_tab_list into the stack
            _cur_pos_tok = self._token_l[self._cur_pos - 1].get_value()
            # if it has already existed before, then pop it first
            if self.compare_id(self._symb_tab_list):
                while i < len(self._symb_tab_list):
                    s_t = self._symb_tab_list[i]
                    if _cur_pos_tok == s_t.get_symbol_name():
                        self._symb_tab_list.remove(s_t)

            # then, push a new one, which is with reference
            for t in self._table_list:
                if _cur_pos_tok == t.get_relation_name():
                    tab_ref = t
            tab_name = _cur_pos_tok
            self._symb_tab_list.append(Symbol(tab_name, tab_ref))

            # push this symbol into semantic stack
            self._sem_stack.append(Symbol(tab_name, tab_ref))

            if f:
                f = self.match(self.joined_table)
                if not f:
                    f = self.match(self.opt_alias_clause)
        # if not f:
        #     self.match('LATERAL')
        #     f = self.match(self.select_with_parens)
        #     if not f:
        #         f = self.match(self.func_table)

        return f

    def relation_expr(self):
        f = self.match('IDENTIFIER')
        # self.match('*')

        # push the current symb_tab_list into the stack
        _cur_pos_tok = self._token_l[self._cur_pos - 1].get_value()
        # if it has already existed before, pop it first
        if self.compare_id(self._symb_tab_list):
            while i < len(self._symb_tab_list):
                s_t = self._symb_tab_list[i]
                if _cur_pos_tok == s_t.get_symbol_name():
                    self._symb_tab_list.remove(s_t)

        # then, push a new one, which is with reference
        for t in self._table_list:
            if _cur_pos_tok == t.get_relation_name():
                tab_ref = t
        tab_name = _cur_pos_tok
        self._symb_tab_list.append(Symbol(tab_name, tab_ref))

        # push this symbol into semantic stack
        self._sem_stack.append(Symbol(tab_name, tab_ref))

        if not f:
            f = self.match('ONLY')
            if f:
                f = self.match('IDENTIFIER')
                if not f:
                    f = self.match('(', 'IDENTIFIER', ')')
        return f

    # def table_name(self):
    #     f = self.match('IDENTIFIER')
    #     return f

    def func_table(self):
        pass

    def row_source_extension(self):
        pass

    def column_path_with_star(self):
        f = self.match('*')
        if not f:
            f = self.match('IDENTIFIER')
            # d_expr = self._cur_pos_tok
            if f:
                if self.match('.'):
                    f = self.match('*')
                    if not f:
                        f = self.match('IDENTIFIER')
                        if f:
                            _post_pos_tok = self._token_l[self._cur_pos - 3].get_value()
                            _cur_pos_tok = self._token_l[self._cur_pos - 1].get_value()
                            if not self.compare_id(self._symb_tab_list):
                                tab_name = _post_pos_tok
                                self._symb_tab_list.append(Symbol(tab_name, []))
                            if not self.compare_id(self._symb_col_list):
                                col_name = _post_pos_tok + '.' + _cur_pos_tok
                                self._symb_col_list.append(Symbol(col_name, []))
                                self._sem_stack.append(Symbol(col_name, []))
                else:
                    if not self.compare_id(self._symb_col_list):
                        # _post_pos_tok = self._token_l[self._cur_pos - 3].get_value()
                        _cur_pos_tok = self._token_l[self._cur_pos - 1].get_value()
                        col_name = _cur_pos_tok
                        self._symb_col_list.append(Symbol(col_name, []))
                        self._sem_stack.append(Symbol(col_name, []))
                    f = True

        return f

    # '''
    # go to use: prefixed_column_path
    # '''
    # def column_path(self):
    #     f = self.match('IDENTIFIER')
    #     if not f:
    #         f = self.match(self.prefixed_column_path)
    #     return f
    #
    # def prefixed_column_path(self):
    #     f = self.match('IDENTIFIER', '.', 'IDENTIFIER')
    #     if f:
    #         if self.match('.', 'IDENTIFIER'):
    #             self.match('.', 'IDENTIFIER')
    #     return f

    '''
    go to use: 
        joined_table
        table_ref
        opt_join_hint
        join_qual
    '''
    def joined_table(self):
        # f = self.match('(', self.joined_table, ')')

        # if f:
        #     q = ['+']
        #     for sym in self._sem_stack:
        #         q.append(sym)
        #     self._final_stack.append(q)

        f = self.match('CROSS', self.opt_join_hint)
        if f:
            self._temp += 'CROSS'
        if not f:
            f = self.match('NATURAL')
            if f:
                self._temp += 'NATURAL'
                self.match(self.join_type, self.opt_join_hint)
        if f:
            f = self.match('JOIN', 'IDENTIFIER')
            if f:
                self._temp += 'JOIN'
        if not f:
            self.match(self.join_type, self.opt_join_hint)

            f = self.match('JOIN', 'IDENTIFIER')
            if f:
                # push the current symb_tab_list into the stack
                _cur_pos_tok = self._token_l[self._cur_pos - 1].get_value()
                # if it has already existed before, then pop it first
                if self.compare_id(self._symb_tab_list):
                    while i < len(self._symb_tab_list):
                        s_t = self._symb_tab_list[i]
                        if _cur_pos_tok == s_t.get_symbol_name():
                            self._symb_tab_list.remove(s_t)

                # then, push a new one, which is with reference
                for t in self._table_list:
                    if _cur_pos_tok == t.get_relation_name():
                        tab_ref = t
                tab_name = _cur_pos_tok
                self._symb_tab_list.append(Symbol(tab_name, tab_ref))

                # push this symbol into semantic stack
                self._sem_stack.append(Symbol(tab_name, tab_ref))

                self._temp += 'JOIN'
                self.match(self.join_qual)

        if f:
            q = [self._temp]
            for sym in self._sem_stack:
                q.append(sym)
            self._final_stack.append(q)
        return f

    '''
    go to use: join_outer
    '''
    def join_type(self):
        f = self.match('INNER')
        if f:
            self._temp += 'INNER'
        if not f:
            f = self.match('FULL')
            if f:
                self._temp += 'FULL'
            if not f:
                f = self.match('LEFT')
                if f:
                    self._temp += 'LEFT'
            if not f:
                f = self.match('RIGHT')
                if f:
                    self._temp += 'RIGHT'
            if f:
                f = self.match(self.join_outer)
        return f

    def join_outer(self):
        if self.match('OUTER'):
            self._temp += 'OUTER'
        return True

    '''
    go to use: a_expr
    '''
    def join_qual(self):
        f = self.match('USING', '(', 'IDENTIFIER', ')')
        if not f:
            f = self.match('ON', self.a_expr)
        return f

    def opt_join_hint(self):
        f = self.match('HASH')
        if f:
            self._temp += 'HASH'
        if not f:
            f = self.match('MERGE')
            if f:
                self._temp += 'MERGE'
        if not f:
            f = self.match('LOOKUP')
            if f:
                self._temp += 'LOOKUP'
        if not f:
            f = True
        return f

    def opt_alias_clause(self):
        self.match(self.alias_clause)
        return True

    '''
    go to use: opt_column_list
    '''
    def alias_clause(self):
        self.match('AS')
        f = self.match('IDENTIFIER', self.opt_column_list)
        return True

    def math_op(self):
        f = self.match('+')
        if not f:
            f = self.match('-')
        if not f:
            f = self.match('*')
        if not f:
            f = self.match('/')
        if not f:
            f = self.match('%')
        if not f:
            f = self.match('&')
        if not f:
            f = self.match('|')
        if not f:
            f = self.match('^')
        if not f:
            f = self.match('#')
        if not f:
            f = self.match('<')
        if not f:
            f = self.match('>')
        if not f:
            f = self.match('=')
        if not f:
            f = self.match('LESS_EQUALS')
        if not f:
            f = self.match('GREATER_EQUALS')
        if not f:
            f = self.match('NOT_EQUALS')
        return f

    '''
    go to use: name_list
    '''
    def opt_column_list(self):
        self.match('(', self.name_list, ')')
        return True

    '''
    go to use: name
    '''
    def name_list(self):
        f = self.match(',')
        if not f:
            f = self.match(self.name)
        return f

    def name(self):
        f = self.match('IDENTIFIER')
        return f

    '''
    go to use: tuple1_ambiguous_values
    '''
    def expr_tuple1_ambiguous(self):
        f = self.match('(')
        if f:
            f = self.match(self.tuple1_ambiguous_values)
            if not f:
                f = True
            if f:
                f = self.match(')')
        return f

    '''
    go to use:
        a_expr
        expr_list
    '''
    def tuple1_ambiguous_values(self):
        f = self.match(self.a_expr)
        if f:
            f = self.match(',')
            if f:
                f = self.match(self.expr_list)
            else:
                f = True
        else:
            f = True
        return f


if __name__ == '__main__':
    test = 'SELECT R1.x, R2.n*5 FROM R1 JOIN R2 WHERE R1.x=R2.m;'
    # test = 'SELECT R1.x, R2.y FROM R1, R2 WHERE R1.x>200 and R2.x < 100;'

    test_token = get_token(test)
    for i in test_token:
        print('< ' + i.get_type() + ' ------ ' + i.get_value() + ' >')

    R1_value = {'x': 'INT', 'y': 'INT', 'z': 'CHAR'}
    R2_value = {'y': 'INT', 'm': 'INT', 'n': 'INT'}
    db = {'R1': R1_value, 'R2': R2_value}

    pr = Parser(test, db)
    if pr.select_stmt():
        print('yes\n')
    else:
        print('no\n')

    print('rem --', len(test_token) - pr.get_cur_pos())
    print('\n')
    l = []

    for i in pr.get_final_stack():
        print('[', end='')
        l.append(i)
        for obj in i:
            print(obj, end='')
            print(' ', end='')
        print(']')
