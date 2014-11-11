import ast
import astunparse

def go(line, func):
    a = ast.parse(line)
    for b in a.body:
        v = b.value
        if isinstance(v, ast.Call):
            if hasattr(v, 'func'):
                f = v.func
                attr = 'id' if isinstance(f, ast.Name) else 'attr'
                if getattr(f, attr) == func:
                    for pa in v.args:
                        yield astunparse.unparse(pa).strip()

if __name__ == '__main__':
    a = 'my.x.f(t.qwe, g[t]) #ggg'
    b = 'f(t.qwe, g()) #ggg'
    print list(go(b, 'f'))
    print list(go(a, 'f'))
