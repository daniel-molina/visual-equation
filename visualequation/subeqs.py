# visualequation is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# visualequation is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Module to manage subequations, the basic building block.

Subequation format:

Symbols: [str|Op0]
Blocks:  [OpN, par1, par2, ..., parN] where parX can be a symbol or a block.

Example: [PJUXT, ["2"], ["x"], [FRAC, ["c"], ["d"]]]

.. note::
    Current implementation: A non-usubeq is necessarily a GOP-block and its
    parameter cannot be a GOP-block.

.. note::
    Policy:

        *   Idxs can return a Idx or mutate itself.
        *   Subeqs can return a reference to part of itself or return a Idx.
        *   Whenever a Idx is returned, it must be not a reference to
            another Idx.
"""

from typing import List, Tuple, Union, Iterable, Optional

from visualequation.idx import Idx, NOIDX
from visualequation import ops

SUBEQ_CONTAINER_TYPE_ERROR_MSG = "Allowed iterables to provide Subeq " \
                                 "elements are lists and tuples"
SubeqContainerTypeError = TypeError(SUBEQ_CONTAINER_TYPE_ERROR_MSG)
SUBEQ_ELEM_TYPE_ERROR_MSG = "Elements allowed to build a Subeq must be " \
                            "lists, tuples, strings and/or Ops"
SubeqElemTypeError = TypeError(SUBEQ_ELEM_TYPE_ERROR_MSG)
SUBEQ_APPEND_TYPE_ERROR_MSG = "Elements allowed to be appended to a Subeq " \
                              "are Subeqs, strings and Ops"
SubeqAppendTypeError = TypeError(SUBEQ_APPEND_TYPE_ERROR_MSG)
SUBEQ_EXTEND_TYPE_ERROR_MSG = "Elements allowed to extend a Subeq are " \
                              "Subeqs and Ops with n_args != 0"
SubeqExtendTypeError = TypeError(SUBEQ_EXTEND_TYPE_ERROR_MSG)
SUBEQ_INSERT_TYPE_ERROR_MSG = "Elements allowed to be inserted in a Subeq " \
                              "are Subeqs and Ops with n_args != 0"
SubeqInsertTypeError = TypeError(SUBEQ_INSERT_TYPE_ERROR_MSG)
SUBEQ_VALUE_ERROR_MSG = "Strings and 0-args ops must always be the single " \
                        "element of a list or tuple."
SubeqValueError = ValueError(SUBEQ_VALUE_ERROR_MSG)
SUBEQ_ORDINARY_INDEXING_ERROR_MSG = "Accessing Subeq elements with a key ([" \
                                    "]) requires key being an integer or slice"
SubeqOrdinaryIndexingError = TypeError(SUBEQ_ORDINARY_INDEXING_ERROR_MSG)
NOT_SUBEQ_ERROR_MSG = "Pointed element is not a Subeq"
NotSubeqError = TypeError(NOT_SUBEQ_ERROR_MSG)
NON_EXISTENT_SUBEQ_ERROR_MSG = "Requested subeq does not exist"
NonExistentSubeqError = IndexError(NON_EXISTENT_SUBEQ_ERROR_MSG)
EMPTY_SUBEQ_ERROR_MSG = "Pointed subeq is empty"
EmptySubeqError = ValueError(EMPTY_SUBEQ_ERROR_MSG)


class Subeq(list):
    """A class to manage subequations.

    .. note::
        To simplify slicing and concatenation, Subeqs are allowed to have
        Ops with n_args != 0 in random positions or just one subeq ([["d"]]).

    Some methods will provide only correct results for every input if self is
    a whole equation and not a strict subeq.

    Implementation note:

        *   It will be supposed that a referred subequation is correctly built.
        *   It will not be supposed (in most of cases) that the user call the
            methods knowing that what is being asked is legitimate.
    """
    @classmethod
    def check_noncontainer_value(cls, value, container_len):
        if not isinstance(value, str) and not isinstance(value, ops.Op):
            raise SubeqElemTypeError
        if container_len > 1 \
                and (isinstance(value, str) or not value.n_args):
            raise SubeqValueError

    def __init__(self, *args):
        # Better allow [] to be a Subeq even if that is not a valid subeq than
        # reject it or transform it into [VOID].
        # This way, we keep compatibility with list slicing, etc.
        # Equivalently, do not force a correct structure or geometry of
        # elements here, better use the debug module for that task.
        if len(args) == 1 and args[0] is None:
            list.__init__(self, [ops.PVOID])
        elif len(args) == 1 and not (isinstance(args[0], (list, tuple))):
            # Subeqs are derived from lists, so they pass the check
            raise SubeqContainerTypeError
        else:
            # Let list.__init__ manage any len( args) > 1 issue
            list.__init__(self, *args)

        for pos, e in enumerate(self):
            if isinstance(e, Subeq):
                # Trust in any Subeq previously built
                pass
            elif isinstance(e, (list, tuple)):
                self[pos] = Subeq(e)
            else:
                self.check_noncontainer_value(e, len(self))

    def __add__(self, other: List):
        return Subeq(list.__add__(self, other))

    def __getitem__(self, key: Union[slice, int]):
        if isinstance(key, slice):
            return Subeq(list.__getitem__(self, key))
        elif isinstance(key, int):
            return list.__getitem__(self, key)
        else:
            raise SubeqOrdinaryIndexingError

    def __setitem__(self, key: Union[slice, int],
                    value: Union[List, Tuple, str, ops.Op]):
        if isinstance(key, int):
            # Incorrect subeqs formed by this method should be equivalent to
            # those allowed by __init__.
            if not isinstance(value, (str, ops.Op, list, tuple)):
                raise SubeqElemTypeError
            if len(self) > 1 \
                    and (isinstance(value, str)
                         or (isinstance(value, ops.Op) and not value.n_args)):
                raise SubeqValueError
        elif isinstance(key, slice):
            if not isinstance(value, (list, tuple)):
                raise SubeqContainerTypeError
        else:
            raise SubeqOrdinaryIndexingError

        if isinstance(value, (str, ops.Op)):
            list.__setitem__(self, key, value)
        else:
            list.__setitem__(self, key, Subeq(value))

    def __str__(self):
        if len(self) == 0:
            return "[]"
        s_str = "[" + str(self[0])
        for e in self[1:]:
            s_str += ", " + str(e)
        return s_str + "]"

    @classmethod
    def _repr_aux(cls, elem):
        if not isinstance(elem, Subeq):
            return repr(elem)
        elif not len(elem):
            return "[]"
        else:
            s_str = "[" + cls._repr_aux(elem[0])
            for e in elem[1:]:
                s_str += ", " + cls._repr_aux(e)
            return s_str + "]"

    def __repr__(self):
        if len(self) == 0:
            return "Subeq()"
        return "Subeq(" + self._repr_aux(self) + ")"

    def append(self, value: Union['Subeq', str, ops.Op]):
        if not isinstance(value, (Subeq, ops.Op, str)):
            raise SubeqAppendTypeError
        if len(self) and ((isinstance(value, ops.Op) and not value.n_args)
                          or isinstance(value, str)):
            # Allowing a str/(0-arg Op) to be appended to empty Subeqs is
            # crucial to copy.deepcopy
            raise SubeqValueError
        list.append(self, value)

    def extend(self, collect: Iterable[Union['Subeq', ops.Op]]):
        # Because extend is used to support insertion of several elements
        # there are no reasons to allow its use to an append use of single
        # strings and 0-args ops in empty Subeqs.
        if not (isinstance(collect, (list, tuple))):
            # Subeqs are derived from lists, so they pass the check
            raise SubeqContainerTypeError
        for s in collect:
            if not (isinstance(s, Subeq) or
                    (isinstance(s, ops.Op) and s.n_args)):
                raise SubeqExtendTypeError
        list.extend(self, collect)

    def insert(self, pos: int, value: Union['Subeq', ops.Op]):
        # Not supporting insertion of strings or 0-args Ops in empty subeqs.
        if not (isinstance(value, Subeq) or
                (isinstance(value, ops.Op) and value.n_args)):
            raise SubeqInsertTypeError
        list.insert(self, pos, value)

    @classmethod
    def subeq2latex(cls, s):
        """Return latex code of a valid subeq."""
        if len(s) == 1:
            return s[0] if isinstance(s[0], str) else s[0].latex_code
        elif s[0].n_args == -1:
            return " ".join(map(cls.subeq2latex, s[1:]))
        else:
            return s[0].latex_code.format(*map(cls.subeq2latex, s[1:]))

    def latex(self):
        return self.subeq2latex(self)

    def __call__(self, *args):
        """Get a reference to eq element given its index or specifying the
        indices as separated arguments.

        If you modify the return value, subeq is modified.
        """
        # Transforming into Idx has the advantage of checking for some errors
        # automatically
        s = self
        # Using an Idx has the advantage of checking for most of errors
        # automatically
        for pos in Idx(*args):
            s = s[pos]
        return s

    def supeq(self, idx):
        """Return the supeq of subeq pointed by idx or -2."""
        index = Idx(idx)
        if not index:
            return -2
        sup = self(index[:-1])
        if not isinstance(sup[index[-1]], Subeq):
            raise NotSubeqError
        return sup

    def is_pvoid(self, idx=None):
        return self(idx) == [ops.PVOID]

    def is_tvoid(self, idx=None):
        return self(idx) == [ops.TVOID]

    def is_void(self, idx=None):
        return self(idx) in ([ops.PVOID], [ops.TVOID])

    def isb(self, idx=None):
        s = self(idx)
        return isinstance(s, Subeq) and len(s) > 1

    def isusubeq(self, idx=None):
        """Return if a subeq element is an usubeq, including lops."""
        s = self(idx)
        return isinstance(s, Subeq) and s[0] != ops.GOP

    def is_perm_jb(self, idx=None):
        s = self(idx)
        return isinstance(s, Subeq) and s[0] == ops.PJUXT

    def is_temp_jb(self, idx=None):
        s = self(idx)
        return isinstance(s, Subeq) and s[0] == ops.TJUXT

    def is_jb(self, idx=None):
        s = self(idx)
        return isinstance(s, Subeq) and s[0] in (ops.PJUXT, ops.TJUXT)

    def is_juxted(self, idx):
        index = Idx(idx)
        # Do not assume that pointed elem is a subeq
        if not index:
            return False
        sup = self(index[:-1])
        return isinstance(sup[index[-1]], Subeq) and sup.is_jb()

    def is_gopb(self, idx=None):
        s = self(idx)
        return isinstance(s, Subeq) and s[0] == ops.GOP

    def is_goppar(self, idx):
        index = Idx(idx)
        # Do not assume that pointed elem is a subeq
        if not index:
            return False
        sup = self(index[:-1])
        return isinstance(sup[index[-1]], Subeq) and sup[0] == ops.GOP

    def outlop(self, idx, retidx=False):
        """Get the lop of parameter pointed by idx.

        self must be a whole equation to have reliable results for every *idx*.

        If the whole subeq is pointed, -2 is returned.
        """
        index = Idx(idx)
        if not isinstance(self(index), Subeq):
            raise NotSubeqError
        if not index:
            return -2
        index.outlop(set=True)
        # This index is different!! (Do not reuse previous self(index))
        return index if retidx else self(index)

    def inlop(self, idx=None, retidx=False):
        """Get lop of subeq S of self pointed by idx or -3 if S is a symbol."""
        index = Idx(idx)
        s = self(index)
        if not isinstance(s, Subeq):
            raise NotSubeqError
        if not s:
            raise EmptySubeqError
        if len(s) == 1:
            return -3
        return index + [0] if retidx else s[0]

    def nthpar(self, idx=None, n=-1, retidx=False):
        """Return the n-th parameter of an op given the index of its op-block.

        If you want the last parameter, pass n == -1.

        If *idx* points to a symbol, -3 is returned.
        If the operator does not have enough args, -1 is returned.
        """
        block = self(idx)
        if not isinstance(block, Subeq):
            raise NotSubeqError
        last_ord = len(block) - 1
        if not last_ord:
            return -3
        if n == -1:
            n = last_ord
        if n > last_ord:
            return -1
        if n < 1:
            raise NonExistentSubeqError

        return Idx(idx) + [n] if retidx else block[n]

    def relpar(self, idx, n=1, retidx=False):
        """Get the nth co-parameter to the left/right, depending on the sign of
         n.

        Return -1 if requested parameter does not exist or -2 if idx is [].

        Since this method is intended to be used with relative position, it
        can be useful to call this method without actually knowing the passed
        value of *idx and/or *n*. => No error is raised if requested parameter
        does not exist in any direction.
        """
        index = Idx(idx)
        if not index:
            return -2
        # Do not suppose that pointed elem is a subeq
        sup = self(index[:-1])
        if not isinstance(sup[index[-1]], Subeq):
            raise NotSubeqError
        ord = index[-1] + n
        if 0 < ord < len(sup):
            return index[:-1] + [ord] if retidx else sup[ord]
        return -1

    def prevpar(self, idx, retidx=False):
        """Return prev co-parameter.

        If idx is [], return -2.
        Elif idx points to first param or lop, return -1.
        """
        return self.relpar(idx, -1, retidx)

    def nextpar(self, idx, retidx=False):
        """Return parameter to the right.

        If idx is [], return -2.
        Elif it is a last param or lop, return -1.
        """
        return self.relpar(idx, 1, retidx)

    def urepr(self, idx=None, retidx=False):
        """Return the urepr of a subeq.

        A more general approach based on "VE's ops are faithful" was previously
        coded and can be recovered from the DVCS.

        It assumes that no GOP-block can be GOP-par and only GOPs are
        non-user ops.
        """
        index = Idx(idx)
        s = self(index)
        if not isinstance(s, Subeq):
            raise NotSubeqError
        if s.is_gopb():
            return index + [1] if retidx else s[1]
        return index if retidx else s

    def biggest_supeq_with_urepr(self, idx=None, retidx=False):
        """Get biggest subeq which has pointed usubeq as urepr.

        self is recommended to be an equation (see note below).

        If pointed subeq is a non-usubeq, -1 is returned.

        A more general approach based on "VE's ops are faithful" was previously
        coded and can be recovered from the DVCS.

        .. note::
            If idx is [] and self is a usubeq, result is only guaranteed to be
            valid if self is the whole equation.
        """
        index = Idx(idx)
        # It is supposed that self is a valid (sub)eq
        if not index:
            if self.is_gopb():
                return -1
            return index if retidx else self

        # Do not suppose pointed elem is a subeq
        sup = self(index[:-1])
        parord = index[-1]
        if not isinstance(sup[parord], Subeq):
            raise NotSubeqError
        if sup.is_gopb():
            return index[:-1] if retidx else sup
        if sup[parord].is_gopb():
            return -1
        return index if retidx else sup[parord]

    def ulevel(self, idx):
        """Return the nesting ulevel of pointed usubeq.

        If *idx* does not point to a usubeq, minus the ulevel of its urepr is
        returned.
        """
        s = self
        ulev = 0
        for pos in idx:
            if not s.is_gopb():
                ulev += 1
            s = s[pos]
        if s.is_gopb():
            return -ulev
        return ulev

    def selectivity(self, idx):
        """Give information on selectivity of a subequation.

        self must be an equation.

        Return  2 if subequation is SELECTABLE and is not a GOP-par.
        Return  1 if subequation is SELECTABLE and is a GOP-par.
        Return  0 if subequation is a GOP-block which par is selectable.
        Return -1 if subequation is a GOP-par strict subeq.

        .. note::
            A subequation is selectable if, and only if, return value is
            positive.

        .. note::
            To know that return value is -1 is not enough to know if subeq is a
            usubeq. Since this function informs about selectivity, it is not
            considered important to inform about the user property itself.
        """
        s = self
        gopb_reached = False
        for parord in idx:
            if gopb_reached:
                return -1
            if s.is_gopb():
                gopb_reached = True
            s = s[parord]

        if gopb_reached:
            return 1
        if s.is_gopb():
            return 0
        return 2

    def mate(self, idx, right: bool, ulevel_diff=0, retidx=False):
        """Return the mate to the left and a ulevel difference.

        self must be an equation.

        If it is a last mate and right is True or it is a first mate and right
        is, False, -1 is returned.

        Parameter *ulevel_diff* indicate the ulevel of the mates as an offset:
        Supposing that subeq pointed by *idx* is a N-ulevel peer and the
        intention is to find its M-ulevel mate to the right or left for M > N,
        *ulevel_diff* must be M - N.

        .. note::
            If first call to this function is done with *ulevel_diff* equal to
            0, then a next call using the correspondent second output value is
            a valid call to look for mates of usubeq pointed in the former
            call.

        .. note::
            The algorithm described in HACKING.md.
        """
        sidx = idx[:]
        uld = ulevel_diff

        # Find common usupeq
        while True:
            pord = sidx.parord()
            if pord == -2:
                return -1, None
            sidx = sidx[:-1]
            s = self(sidx)
            uld += 0 if s.is_gopb() else 1
            if (right and pord != len(s) - 1) or (not right and pord != 1):
                break

        # Find mate
        pord += 1 if right else -1
        while True:
            uld -= 0 if self(sidx).is_gopb() else 1
            sidx = self.nthpar(sidx, pord, True)
            lop_s = self.inlop(sidx)
            if not uld or lop_s == -3 or lop_s == ops.GOP:
                return self.urepr(sidx, retidx), uld
            # -1 is a flag value accepted by nthpar
            pord = 1 if right else -1

    def boundary_mate(self, ulevel: int, last=False, retidx=False):
        """Return the first or last *N*-ulevel mate of eq.

        self must be an equation.
        """
        s = self
        bmate_idx = NOIDX
        ul = -1
        while True:
            if len(s) == 1:
                return bmate_idx if retidx else s
            if s.is_gopb():
                return bmate_idx + [1] if retidx else s[1]
            ul += 1
            if ul == ulevel:
                return bmate_idx if retidx else s
            bmate_idx.append(len(s) - 1 if last else 1)
            s = s[bmate_idx[-1]]

    def boundary_symbol(self, idx=None, last=False, strict=True, retidx=False):
        """Return the first or last symbol of a subeq.

        self must be an equation if *strict* is False.

        If *strict* is False and the boundary symbol is not selectable, it will
        return the GOP-par with biggest usupeq nesting level.

        If *strict* is False, and pointed subeq has not a selectable urepr, -1
        is returned.
        """
        new_idx = NOIDX[:] if idx is None else idx[:]
        s = self(new_idx)
        flag = self.selectivity(new_idx)
        if not strict:
            if flag == -1:
                return -1
            if flag == 1:
                return new_idx if retidx else s

        # From this point we know that s is not a subeq of a GOP-par
        while True:
            if len(s) == 1:
                return new_idx if retidx else s
            if not strict and s.is_gopb():
                return new_idx + [1] if retidx else s[1]
            new_idx.append(len(s) - 1 if last else 1)
            s = s[new_idx[-1]]
