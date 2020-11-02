from itertools import count
from models import *


class BBTree:
    identity = count()

    incumbent = float('inf')
    best_sol = {}
    s = {}
    n = 0

    tree_dict = {}
    best_tree = None
    nodes = -1

    def __init__(self, m, z, s, B, v, parent=None, newvar_dict=None):
        self.model = m
        self.solution = z
        self.status = m.status

        self.s = s
        self.B = B
        self.v = v

        self.parent = parent
        self.left_branch = None
        self.right_branch = None

        self.id_ = next(BBTree.identity)
        self.newvar_dict = newvar_dict
        self.add_tree_to_dict()

    def add_tree_to_dict(self):
        BBTree.tree_dict[self.id_] = self

    def add_left_son(self, m1, z1, s1, v, newvar_dict):
        self.left_branch = BBTree(m1, z1, s1, self.B, v, self, newvar_dict)
        return self.left_branch

    def add_right_son(self, m2, z2, s2, v):
        self.right_branch = BBTree(m2, z2, s2, self.B, v, self)
        return self.right_branch

    def objVal(self):
        return self.model.objVal

    def branch(self):

        i, j = get_ij(self.s, self.solution)

        print(f'\nStarting to branch left son from {self.id_}.')
        m1, z1, s1, v1, x = divide_left(self.s, self.B, self.v, i, j)
        newvar_dict = {x: {i, j}}
        left_son = self.add_left_son(m1, z1, s1, v1, newvar_dict)
        print(f'Branched {left_son.id_} from {self.id_}.\n')

        print(f'\nStarting to branch right son from {self.id_}.')
        m2, z2, s2, v2 = divide_right(self.s, self.B, self.v, i, j)
        right_son = self.add_right_son(m2, z2, s2, v2)
        print(f'Branched {right_son.id_} from {self.id_}.\n')

        return left_son, right_son

    def branch_and_price(self, bfs):
        if bfs:
            queue = deque()
        else:
            queue = []

        queue.append(self)
        while queue:
            if bfs:
                tree = queue.popleft()
            else:
                tree = queue.pop()

            BBTree.nodes += 1

            print(f'ID: [{tree.id_}]')
            if tree.parent is not None:
                print(f'Parent[{tree.parent.id_}]')

            if tree.model.status == 3 or tree.model.status == 4:
                print('Cutting because of infeasibility.\n')
                continue

            elif tree.objVal() >= BBTree.incumbent - 1:
                print('Cutting because of incumbent.\n')
                continue

            else:
                print(f'objVal: [{tree.objVal()}]')

            try:
                left, right = tree.branch()

                # queue.append(left)
                # queue.append(right)

                queue.append(right)
                queue.append(left)

            except ValueError:
                obj = tree.objVal()
                print(f'Solution found. objVal = [{obj}]')
                soldict = {u: v.X for u, v in tree.solution.items() if v.X}
                print({u: tree.s[u] for u, v in tree.solution.items() if v.X})

                if obj < BBTree.incumbent:
                    BBTree.incumbent = obj
                    BBTree.best_sol = tree.solution
                    BBTree.s = tree.s
                    BBTree.best_tree = tree

            finally:
                print()

    def recover_pairs(self):
        tree = self
        recovering_dict = {}
        while tree.parent is not None:
            if tree.newvar_dict is not None:
                recovering_dict.update(tree.newvar_dict)
            tree = tree.parent

        return recovering_dict
