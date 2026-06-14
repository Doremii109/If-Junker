'''
Author: Doremi109
Github: https://github.com/Doremii109
Project Github: https://github.com/Doremii109/If-Junker
'''

import ast, random, copy, struct, operator
from collections import defaultdict
from typing import Dict, Union, Optional

# from namer import rename_ast, genName as _genName, np as _np

kw_names = []
for y in (__loader__, '', b'', 1, 1.0):
    for x in dir(y):
        if not(x.startswith('_') or x.endswith('_')):
            kw_names.append(x)

ri = random.randint
rc = random.choice

binop = [
    ast.Add(),ast.Sub(),ast.Mult(),ast.MatMult(),ast.Div(),
    ast.Mod(),ast.LShift(),ast.RShift(),ast.BitOr(),ast.BitXor(),
    ast.BitAnd(),ast.FloorDiv(),ast.Pow(),
]

cmpops = [
    ast.Eq(),ast.NotEq(),ast.Lt(),ast.LtE(),
    ast.Gt(),ast.GtE(),ast.In(),ast.NotIn(),
]

boolops = [ast.And(), ast.Or()]


allTrue = [
    '...==...',
    'not~-1',
    '[*[]]<[*[...]]'
]

allFalse = [
    'bool(*{})',
    '...==[*[]]',
    '[*[...]]<[*[]]'
]

allNone = [
    'slice(0).step',
    'type({}.get(0))()',
    '[*{}].sort()'
]

# _pref, _np = '_0x', 0
# def _genName() -> str:
#     global _np
#     return f'{_pref}{str(abs(hash(str(_np:=_np + 1))))[:9]}'
#     return f'{_pref}{(_np:=_np+1)}'

gn = set()
def _genName():
    while (n:=chr(random.randint(0x4E00,0x9FFF))) in gn: pass
    gn.add(n)
    return n

def _getParam(k, _dict):
    kws = []
    for i in range(k):
        while (n:=random.choice(_dict)) in kws:pass
        kws.append(n)
    return kws

class ImportChange(ast.NodeTransformer):
    h = f'{(impportt:=_genName())} = __import__("importlib").import_module'
    def visit_Module(self, node):
        self.generic_visit(node)
        return ast.Module(ast.parse(self.h).body + node.body, [])
    def visit_Import(self, node):
        nd = []
        for name in node.names:
            c = f'{asn if (asn:=name.asname) else name.name} = {self.impportt}("{name.name}")'
            nd.extend(ast.parse(c).body)
        return nd
    def visit_ImportFrom(self, node):
        mod = node.module
        if any(asn.name == '*' for asn in node.names): return ast.parse(f'''a=dict()
importt={self.impportt}("{mod}")
[a.update({{im: vars(importt)[im]}}) for im in dir(importt)if not im.startswith("__")]
globals().update(a)
a.clear()''')
        ni = {}
        for name in node.names: ni.update({(nn:=name.name): asn if (asn:=name.asname) else nn})
        nd = f'{','.join([ni[x]for x in ni])}, = (getattr({self.impportt}("{mod}"), x) for x in [{','.join([repr(x) for x in ni])}])'
        return ast.parse(nd).body
    def visit_AnnAssign(self, node):
        p = ast.parse
        if isinstance(tr:=node.target, ast.Name):
            _tmp = p(f'__annotations__["{tr.id}"] = {ast.unparse(node.annotation)}').body[0]
            node = p(f'{tr.id} = {ast.unparse(node.value)}').body[0]
            return [_tmp, node]
        elif isinstance(tr, ast.Attribute):
            _tmp =p(f'__annotations__["{ast.unparse(tr)}"] = {ast.unparse(node.annotation)}').body[0]
            node = p(f'{ast.unparse(tr)} = {ast.unparse(node.value)}').body[0]
            return [_tmp, node]
        return node

class FStr(ast.NodeTransformer):
    def form_val(self, node: ast.FormattedValue):
        _cv = {97: 'ascii', 114: 'repr', 115: 'str', -1: 'str'}
        cv = _cv[node.conversion]
        if (frmt_sp:=node.format_spec):
            return f'format({cv}({ast.unparse(node.value)}), "{ast.unparse(frmt_sp)}")'
        return f'{cv}({ast.unparse(node.value)})'
    def visit_JoinedStr(self, node):
        self.generic_visit(node)
        js_l = []
        for _node in node.values:
            if isinstance(_node, ast.FormattedValue):
                js_l.append(self.form_val(_node))
            elif isinstance(_node, ast.Constant):
                js_l.append(repr(_node.value))
        return ast.parse(f'str().join([{','.join(js_l)}])').body[0].value


def fixAst(AST):
    return ast.parse(ast.unparse(AST))

class FFunc(ast.NodeTransformer):
    def visit_AugAssign(self, node):
        if isinstance(tr:=node.target, ast.Attribute) and isinstance(vl:=tr.value, ast.Call):
            _tmp = f'{(tmp_n:=_genName())} = {ast.unparse(vl)}'
            node.target.value = ast.Name(tmp_n, ast.Load())
            return [ast.parse(_tmp).body[0], node]
        return node

class Assign_(ast.NodeTransformer):

    def parseTuple(self, node, elt_i, val_name):
        _ft = ''
        if isinstance(node, ast.Tuple):
            for index, _node in enumerate(node.elts):
                aaa = self.parseTuple(_node, elt_i, val_name)
                _ft += aaa[:-1]+f'[{index}];'
        else: _ft += f'{ast.unparse(node)} = {val_name}[{elt_i}];'
        return _ft

    def visit_Assign(self, node):
        if isinstance(tr:=node.targets[0], ast.Tuple):
            _ft = f'{(val_name:=_genName())} = list({ast.unparse(node.value)});'
            for index, elt in enumerate(tr.elts):
                _ft += self.parseTuple(elt, index, val_name)
            node = ast.parse(_ft).body
        return node
    
    def visit_AugAssign(self, node) -> ast.AugAssign:
        target = ast.unparse(node.target)
        op = node.op
        value = node.value
        _nd = ast.Assign(targets=[ast.Name(id=target, ctx=ast.Store())], value=ast.BinOp(left=ast.Name(id=target, ctx=ast.Load()), op=op, right=value), lineno=node.lineno)
        return _nd

def stmt_to_expr(stmt):
    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
        t = stmt.targets[0]
        if isinstance(t, ast.Name):
            return ast.NamedExpr(target=ast.Name(id=t.id, ctx=ast.Store()), value=stmt.value)
        elif isinstance(t, ast.Subscript):
            return ast.Call(func=ast.Attribute(value=t.value, attr='__setitem__', ctx=ast.Load()), args=[t.slice, stmt.value], keywords=[])
        elif isinstance(t, ast.Attribute):
            return ast.Call(func=ast.Name(id='setattr', ctx=ast.Load()), args=[t.value, ast.Constant(value=t.attr), stmt.value], keywords=[])
    elif isinstance(stmt, ast.AugAssign):
        if isinstance(stmt.target, ast.Name):
            return ast.NamedExpr(target=ast.Name(id=stmt.target.id, ctx=ast.Store()), value=ast.BinOp(left=ast.Name(id=stmt.target.id, ctx=ast.Load()), op=stmt.op, right=stmt.value))
        elif isinstance(stmt.target, ast.Subscript):
            val = ast.BinOp(left=ast.Subscript(value=stmt.target.value, slice=stmt.target.slice, ctx=ast.Load()), op=stmt.op, right=stmt.value)
            return ast.Call(func=ast.Attribute(value=stmt.target.value, attr='__setitem__', ctx=ast.Load()), args=[stmt.target.slice, val], keywords=[])
    elif isinstance(stmt, ast.Expr):
        return ast.parse(f'({_genName()} := {ast.unparse(stmt.value)})').body[0].value
    return None

def has_yield_or_await(node):
    for child in ast.walk(node):
        if isinstance(child, (ast.Yield, ast.YieldFrom, ast.Await)):
            return True
    return False

class Walrus(ast.NodeTransformer):
    def wrap_expr(self, node):
        return node
    def _process_body(self, body):
        _rest = [n for n in body]
        
        _nb = []
        for stmt in _rest:
            if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.Expr)):
                if not has_yield_or_await(stmt):
                    if (expr:=stmt_to_expr(stmt)):
                        _nb.append(ast.Expr(value=self.wrap_expr(expr)))
                        continue
            _nb.append(stmt)
        return _nb
    
    def visit_Module(self, n): 
        self.generic_visit(n)
        n.body = self._process_body(n.body)
        return n
    visit_FunctionDef = visit_Module
    visit_ClassDef = visit_Module
    visit_ExceptHandler = visit_Module
    visit_With = visit_Module
    def visit_If(self, n): 
        self.generic_visit(n)
        n.body = self._process_body(n.body)
        n.orelse = self._process_body(n.orelse)
        return n
    visit_While = visit_If
    visit_For = visit_If
    def visit_Try(self, n): 
        self.generic_visit(n)
        n.body = self._process_body(n.body)
        n.handlers = [self.visit(h) for h in n.handlers]
        n.orelse = self._process_body(n.orelse)
        n.finalbody = self._process_body(n.finalbody)
        return n


# было сгенерено чатом гпт, мне было лень писать код
class OpaquePredicateGen:
    def __init__(self, env: Dict[str, int]):
        self.e, self.k = env, list(env.keys())
        self._op_map = {
            '+': operator.add, '-': operator.sub, '*': operator.mul, 
            '^': operator.xor, r'//': operator.floordiv, '|':operator.or_, 
            '%': operator.mod,
            '==': operator.eq, '!=': operator.ne, '<': operator.lt, 
            '>': operator.gt, '<=': operator.le, '>=': operator.ge
        }
    def _leaf(self, exp: bool) -> str:
        r_op = (lambda: random.choice(['+', '-', '*', '^', r'//', '|', '%']))
        k1, k2 = random.choice(self.k), random.choice(self.k)
        lv = self._op_map[mo:=r_op()](self.e[k1], self.e[k2])
        ls = f"({k1} {mo} {k2})"
        if (r:=random.random()) < 0.2:
            k3, v3 = (_k:=random.choice(self.k)), self.e[_k]
            v_ops = [o for o in ['==', '!=', '<', '>', '<=', '>='] if self._op_map[o](lv, v3)]
            inv_ops = [o for o in ['==', '!=', '<', '>', '<=', '>='] if not self._op_map[o](lv, v3)]
            return f"{ls} {random.choice(v_ops if exp else inv_ops)} {k3}"
        elif r > 0.2 and r < 0.6:
            r_i = random.randint(1000000, 1000000000)
            args = (self.e[k1], r_i)if (m:=random.randint(0,1)) else(r_i, self.e[k1])
            _args = (k1, r_i)if m else(r_i, k1)
            res = self._op_map[_op:=r_op()](*args)
            offset = random.randint(1, 1000)
            if (r1:=random.random()) < 0.3: _t = f'{random.choice(['==', '>=', '<='] if exp else ['!=', '<', '>'])} {res}' # ==
            elif r1 < 0.6: _t = f'{random.choice(['!=', '>=', '>'] if exp else ['==', '<', '<='])} {res-offset}' # >
            else: _t = f'{random.choice(['!=', '<', '<='] if exp else ['==', '>', '>='])} {res+offset}' # <
            return f'(({_args[0]} {_op} {_args[1]}) {_t})'
        else:
            lst = random.sample(self.k, k=min(random.randint(2, 6), len(self.k)))
            op = 'in' if ((lv in [self.e[x] for x in lst]) == exp) else 'not in'
            return f"{ls} {op} [{', '.join(lst)}]"

    def gen(self, exp: bool, d: int = 2) -> str:
        if d <= 0: return self._leaf(exp)
        op = random.choice(['and', 'or', 'if_exp'])
        match op:
            case 'and':
                l_exp, r_exp = (True, True) if exp else random.choice([(False, True), (True, False), (False, False)])
                return f"({self.gen(l_exp, d-1)} and {self.gen(r_exp, d-1)})"
            case 'or':
                l_exp, r_exp = (False, False) if not exp else random.choice([(True, False), (False, True), (True, True)])
                return f"({self.gen(l_exp, d-1)} or {self.gen(r_exp, d-1)})"
            case _:  # if ... else ...
                test_exp = random.choice([True, False])
                if test_exp:body_exp, orelse_exp = exp, random.choice([True, False])
                else:body_exp, orelse_exp = random.choice([True, False]), exp
                return f"({self.gen(body_exp, d-1)} if {self.gen(test_exp, d-1)} else {self.gen(orelse_exp, d-1)})"

    def genUser(self, user_cond: str, d: int = 2) -> str:
        if d <= 0:return f"({user_cond})"
        wrapped = self.genUser(user_cond, d=d-1)
        op = random.choice(['and', 'or', 'if_true', 'if_false'])
        # op = random.choice(['and', 'or'])
        match op:
            case 'and':
                junk = self.gen(exp=True, d=d-1)
                return f"({junk} and {wrapped})" if random.random() > 0.5 else f"({wrapped} and {junk})"
            case 'or':
                junk = self.gen(exp=False, d=d-1)
                return f"({junk} or {wrapped})" if random.random() > 0.5 else f"({wrapped} or {junk})"
            case 'if_true':
                test = self.gen(exp=True, d=d-1)
                orelse = self.gen(exp=random.choice([True, False]), d=d-1)
                return f"({wrapped} if {test} else {orelse})"
            case _:
                test = self.gen(exp=False, d=d-1)
                body = self.gen(exp=random.choice([True, False]), d=d-1)
                return f"({body} if {test} else {wrapped})"

def genCond(
        env: Dict[str, int], 
        user_cond: Optional[str] = None, 
        expected: bool = True 
    ) -> Union[str, ast.expr]:
    gen = OpaquePredicateGen(env)
    if user_cond is not None:
        res = gen.genUser(user_cond)
    else:
        res = gen.gen(expected)
    return ast.parse(res).body[0].value

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


all_str = []

def colConsts(tr):
    tr = copy.deepcopy(tr)
    for node in ast.walk(tr):
        if isinstance(node, ast.Constant) and isinstance(v:=node.value, str):
            all_str.append(v)


# штука сгенерена чатом гпт, мне было лень что-то придумывать
class ConstsObf:
    @classmethod
    def _pack_bytes_repr(cls, b: bytes) -> str:
        packed_ints = [(k:=random.randint(0, 255))] + [byte ^ k for byte in b]
        return f'b"{"".join(f"\\x{i:02x}" for i in packed_ints)}"'

    @classmethod
    def genAssign(cls, consts: list[tuple[str, any]]) -> str:
        if not consts: return ""
        groups = defaultdict(list)
        for name, val in consts:
            groups[type(val).__name__].append((name, val))

        lhs_vars = []
        rhs_tuples = []
        for t_name, items in groups.items():
            packed_list = []

            for name, val in items:
                lhs_vars.append(name)
                match t_name:
                    case 'str':
                        packed_list.append(cls._pack_bytes_repr(val.encode('utf-8')))
                    case 'int':
                        length = (val.bit_length() + 8) // 8
                        b_data = val.to_bytes(length, 'big', signed=True)
                        packed_list.append(cls._pack_bytes_repr(b_data))
                    case 'float':
                        packed_list.append(cls._pack_bytes_repr(struct.pack('!d', val)))
                    case 'bytes':
                        packed_list.append(cls._pack_bytes_repr(val))
                    case 'bool':
                        dummy = bytes([i for i in _genName().encode()])
                        packed_list.append(cls._pack_bytes_repr(dummy))
                    case 'NoneType':
                        dummy = bytes([i for i in _genName().encode()])
                        packed_list.append(cls._pack_bytes_repr(dummy))

            arr_str = "[" + ", ".join(packed_list) + "]"
            match t_name:
                case 'str':
                    gen = f"tuple(bytes(_^__ for __,*___ in [i] for _ in ___).decode() for i in {arr_str})"
                case 'int':
                    gen = f"tuple(int.from_bytes((_^__ for __,*___ in [i] for _ in ___), 'big') for i in {arr_str})"
                case 'float':
                    gen = f"tuple(__import__('struct').unpack('!d', bytes(_^__ for __,*___ in [i] for _ in ___))[0] for i in {arr_str})"
                case 'bytes':
                    gen = f"tuple(bytes(_^__ for __,*___ in [i] for _ in ___) for i in {arr_str})"
                case 'bool':
                    gen = f"tuple((not not bytes(_^__ for __,*___ in [i] for _ in ___)) for i in {arr_str})"
                case 'NoneType':
                    gen = f"tuple(dict().get(bytes(_^__ for __,*___ in [i] for _ in ___)) for i in {arr_str})"
            
            rhs_tuples.append(gen)

        lhs_expr = ", ".join(lhs_vars)
        
        if len(lhs_vars) == 1:
            lhs_expr += ","

        rhs_expr = rhs_tuples[0]
        for t in rhs_tuples[1:]:
            rhs_expr += f".__add__({t})"

        return f"{lhs_expr} = {rhs_expr}"
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class ReplConst(ast.NodeTransformer):
    def __init__(self):
        self.global_consts: list[tuple[str, any]] = []
        self.const_cache: dict[tuple, str] = {}

    def _get_const_name(self, val) -> str:
        if (k:=(type(val), val)) in self.const_cache:
            return self.const_cache[k]
        self.const_cache[k] = (n:=_genName())
        self.global_consts.append((n, val))
        return n
    
    def visit_Constant(s, n):
        s.generic_visit(n)
        if isinstance(val:=n.value, (int, float, str, bool, type(None), bytes)):
            return ast.Name(id=s._get_const_name(val), ctx=ast.Load())
        return n
    
    def visit_match_case(self, node):
        if node.guard: node.guard = self.visit(node.guard)
        node.body = [self.visit(stmt) for stmt in node.body]
        return node

class Finder(ast.NodeVisitor):
    def __init__(self, target_node):
        self.target = target_node
        self.scopes = [[]]
        self.result = []
        self.found = False

    def visit(self, node):
        if self.found: return
        if node is self.target:
            self.found = True
            self.result = list(self.scopes[-1])
            return
        super().visit(node)

    def _enter_scope(self, node):
        self.scopes.append([])
        self.generic_visit(node)
        if not self.found:
            self.scopes.pop()

    visit_FunctionDef = _enter_scope
    visit_AsyncFunctionDef = _enter_scope
    visit_Lambda = _enter_scope
    visit_ClassDef = _enter_scope
    visit_ListComp = _enter_scope
    visit_DictComp = _enter_scope
    visit_SetComp = _enter_scope
    visit_GeneratorExp = _enter_scope

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            if node.id not in self.scopes[-1]:
                self.scopes[-1].append(node.id)

def _getVars(tree, target_node):
    f = Finder(target_node)
    f.visit(tree)
    return f.result

dummy_str = ['__doc__', '__dict__', '__loader__', '__main__', '__add__', '__str__', '__init__', '__builtins__', '__file__', '__cached__']

def rConst(_type):
    match _type:
        case 0: # type: str
            t = rc(dummy_str + all_str)
        case 1: # type: bytes
            t = random.randbytes(ri(1, 5))
        case 2: # type: int
            t = ri(10000000, 900000000)
        case 3: # type: float
            t = random.random()
    return t

def Reform(n, vals):
    return ast.fix_missing_locations(Val(vals).visit(copy.deepcopy(n)))

class Val(ast.NodeTransformer):
    def __init__(self, vals):
        self.vals = vals
    def generic_visit(self, n):
        n = super().generic_visit(n)
        vals = self.vals

        if hasattr(n, 'args'):
            if (nar:=n.args) and vals:
                n.args[ri(0, len(nar) - 1)] = ast.Name(rc(vals), ast.Load())
            elif vals:
                if (_ll:=len(vals)) > 3: _t = [ast.Name(i, ast.Load()) for i in _getParam(ri(1, 3), vals)]
                else: _t = [ast.Name(i, ast.Load()) for i in _getParam(ri(1, _ll), vals)]
                n.args = _t
            else: 
                # _t = [ast.Constant(rConst(ri(0, 3))) for i in range(ri(1, 3))]
                _t = [ast.Name(i, ast.Load()) for i in _getParam(ri(1, 3), list(vars(__builtins__).keys()))]
                n.args = _t
        
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)) and isinstance(n.value, ast.Name):
            n.value = ast.Name(rc(vals), ast.Load()) if vals else ast.Constant(rConst(ri(0, 3)))

        if hasattr(n, 'keywords'):
            _l = len(kws:=n.keywords)
            f_kws = _getParam(_l, kw_names)
            for i, node in enumerate(kws):
                node.arg = f_kws[i]

        if isinstance(n, ast.Compare):
            n.ops[0] = cmpops[ri(0, 7)]
        if isinstance(n, (ast.BinOp, ast.AugAssign)):
            n.op = binop[ri(0, 12)]
        if isinstance(n, ast.BoolOp):
            n.op = boolops[ri(0, 1)]
        if isinstance(n, (ast.List, ast.Tuple, ast.Set)):
            is_store = hasattr(n, 'ctx') and isinstance(n.ctx, ast.Store)
            if vals:
                if (_ll:=len(vals)) > 3: _t = [ast.Name(i, ast.Store() if is_store else ast.Load()) for i in _getParam(ri(1, 3), vals)]
                else: _t = [ast.Name(i, ast.Store() if is_store else ast.Load()) for i in _getParam(ri(1, _ll), vals)]
            elif is_store: _t = [ast.Name(_genName(), ast.Store()) for i in range(ri(1, 3))]
            else: _t = [ast.Constant(rConst(ri(0, 3))) for i in range(ri(1, 3))]
            n.elts.extend(_t)
        if isinstance(n, ast.Global):
            if vals:
                if (_ll:=len(vals)) > 3: _t = _getParam(ri(1, 3), vals)
                else: _t = _getParam(ri(1, _ll), vals)
            else: _t = _getParam(ri(1, 3), dummy_str)
            n.names = _t
        if isinstance(n, ast.Return):
            if vals: _t = rc(vals)
            else: _t = rc(dummy_str)
            if isinstance(v:=n.value, ast.Name):
                n.value.id = _t
            elif isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name):
                n.value.value.id = _t
        if isinstance(n, ast.Dict):
            for i in range(ri(1, 3)):
                n.keys.append(ast.Name(rc(vals), ast.Load()) if vals else ast.Constant(rConst(ri(0, 3))))
                n.values.append(ast.Name(rc(vals), ast.Load()) if vals else ast.Constant(rConst(ri(0, 3))))

        if isinstance(n, ast.Constant):
            t = n.value
            if isinstance(v:=n.value, str):
                t = rConst(0)
            elif isinstance(v, (bool, type(None), type(Ellipsis))):
                t = rConst(ri(0, 3))
            elif isinstance(v, bytes):
                t = rConst(1)
            elif isinstance(v, int):
                t = rConst(2)
            elif isinstance(v, float):
                t = rConst(3)
            n.value = t

        if isinstance(n, (ast.Continue, ast.Break, ast.Pass)):
            a = ['print', 'input', 'abs', 'int', 'str', 'isinstance', 'hasattr', 'getattr', 'setattr', 'list', 'dict', 'float', 'bytes', 'type', 'range', 'enumerate', 'bool']
            # n = ast.parse(f'{rc(vals)} = {rc(a)}({_getParam(ri(1, 3), vals)})').body[0]
            if vals:
                n = ast.parse(f'({rc(vals)} := {rc(a)}({rc(vals)}))').body[0]
            else: 
                n = ast.parse(f'{rc(a)}{rConst(ri(0, 3))}').body[0]
        return n

def consts_obf(tree: ast.Module) -> ast.Module:
    tree = (tr:=ReplConst()).visit(tree)
    if not (obf_expr:=ConstsObf.genAssign(tr.global_consts)): return tree
    tree.body = ast.parse(obf_expr).body + tree.body
    ast.fix_missing_locations(tree)
    return tree

class IfTransformer(ast.NodeTransformer):
    def __init__(self, sn):
        self.sn = sn
    def visit_Expr(self, node):
        vals = _getVars(self.sn, node)
        _type = ri(0, 1)
        if _type: return ast.If(ast.Constant(1), [node], [ast.If(ast.Constant(0), [Reform(node, vals)], [])])
        else: return ast.If(ast.Constant(0), [Reform(node, vals)], [ast.If(ast.Constant(1), [node], [])])
    visit_Assign = visit_Expr
    visit_Import = visit_Expr
    visit_ImportFrom = visit_Expr
    visit_AugAssign = visit_Expr
    visit_AnnAssign = visit_Expr
    visit_Return = visit_Expr
    visit_Global = visit_Expr
    visit_Pass = visit_Expr
    visit_Break = visit_Expr
    visit_Continue = visit_Expr

class _test(ast.NodeTransformer):
    def __init__(self, sn):
        self.sn = sn
    def visit_NamedExpr(self, node):
        vals = _getVars(self.sn, node)
        _type = ri(0, 1)
        if _type: return ast.IfExp(ast.Constant(1), node, Reform(node, vals))
        else: return ast.IfExp(ast.Constant(0), Reform(node, vals), node)

class hardIf(ast.NodeTransformer):
    def __init__(s):
        # s._vars = {_genName(): hash(str(_np*2)) for i in range(ri(20, 35))}
        s._vars = {_genName(): hash(str(len(gn)*2)) for i in range(ri(20, 35))}
        
    def visit_If(s, node: ast.If):
        s.generic_visit(node)
        auf = ast.unparse
        if auf(node.test) == '1': node.test = genCond(s._vars, None, True)
        elif auf(node.test) == '0': node.test = genCond(s._vars, None, False)
        else: node.test = genCond(s._vars, auf(node.test))
        return node
    visit_IfExp = visit_If
    
    def visit_Constant(self, node):
        if node.value is False:
            node = ast.parse('True^True').body[0].value
        return node

def main(inp: str, out: str):
    c = open(inp, 'r', encoding='utf8', errors='ignore').read()
    colConsts(src_n:=ast.parse(c))
    tr = FStr().visit(src_n)
    tr = ImportChange().visit(tr)

    tr = FFunc().visit(tr)
    tr = Assign_().visit(tr)
    tr = fixAst(tr)
    tr = Walrus().visit(tr)

    # tr = rename_ast(tr, __builtins__)
    tr = IfTransformer(tr).visit(tr)
    tr = _test(tr).visit(tr)
    tr = (hI:=hardIf()).visit(tr)
    ast.fix_missing_locations(tr)

    _n = [x for x in hI._vars]
    _v = [repr(hI._vars[x]) for x in hI._vars]
    _t = f'{','.join(_n)}={','.join(_v)}\n'
    asd = ast.unparse(consts_obf(ast.parse(_t+ast.unparse(tr))))

    open(out, 'w', encoding='utf8').write(asd)

if __name__ == '__main__':
    main('tester.py', 'obf.py')