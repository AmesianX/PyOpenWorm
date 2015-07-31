from __future__ import print_function
import PyOpenWorm as P
from PyOpenWorm.dataObject import DataObject
from PyOpenWorm.relationship import Relationship
from PyOpenWorm.neuron import Neuron

__all__ = ['Connection']


class SynapseType:
    Chemical = 'send'
    GapJunction = 'gapJunction'


class Termination:
    Neuron = 'neuron'
    Muscle = 'muscle'


class Connection(Relationship):

    """Connection between Cells

    Parameters
    ----------
    pre_cell : string, Muscle or Neuron, optional
        The pre-synaptic cell
    post_cell : string, Muscle or Neuron, optional
        The post-synaptic cell
    number : int, optional
        The weight of the connection
    syntype : {'gapJunction', 'send'}, optional
        The kind of synaptic connection. 'gapJunction' indicates
        a gap junction and 'send' a chemical synapse
    synclass : string, optional
        The kind of Neurotransmitter (if any) sent between `pre_cell` and `post_cell`

    Attributes
    ----------
    termination : {'neuron', 'muscle'}
        Where the connection terminates. Inferred from type of post_cell
    """

    def __init__(self,
                 pre_cell=None,
                 post_cell=None,
                 number=None,
                 syntype=None,
                 synclass=None,
                 termination=None,
                 **kwargs):
        Relationship.__init__(self, **kwargs)

        Connection.ObjectProperty('post_cell', owner=self, value_type=Cell)
        Connection.ObjectProperty('pre_cell', owner=self, value_type=Cell)

        Connection.DatatypeProperty('number', owner=self)
        Connection.DatatypeProperty('synclass', owner=self)
        Connection.DatatypeProperty('syntype', owner=self)
        Connection.DatatypeProperty('termination', owner=self)

        if isinstance(pre_cell, P.Cell):
            self.pre_cell(pre_cell)
        elif pre_cell is not None:
            # TODO: don't assume that the pre_cell is a neuron
            self.pre_cell(P.Neuron(name=pre_cell, conf=self.conf))

        if (isinstance(post_cell, P.Cell)):
            self.post_cell(post_cell)
        elif post_cell is not None:
            # TODO: don't assume that the post_cell is a neuron
            self.post_cell(P.Neuron(name=post_cell, conf=self.conf))

        if isinstance(termination, basestring):
            termination = termination.lower()
            if termination in ('neuron', Termination.Neuron):
                self.termination(Termination.Neuron)
            elif termination in ('muscle', Termination.Muscle):
                self.termination(Termination.Muscle)

        if isinstance(number, int):
            self.number(int(number))
        elif number is not None:
            raise Exception(
                "Connection number must be an int, given %s" %
                number)

        if isinstance(syntype, basestring):
            syntype = syntype.lower()
            if syntype in ('send', SynapseType.Chemical):
                self.syntype(SynapseType.Chemical)
            elif syntype in ('gapjunction', SynapseType.GapJunction):
                self.syntype(SynapseType.GapJunction)

        if isinstance(synclass, basestring):
            self.synclass(synclass)

    def identifier(self, *args, **kwargs):
        ident = DataObject.identifier(self, *args, **kwargs)
        if ident is not None:
            return ident

        if self.pre_cell.hasValue()\
            and self.post_cell.hasValue()\
            and self.syntype.hasValue():

            data = []

            data.append(self.pre_cell.defined_values)
            data.append(self.post_cell.defined_values)
            data.append(self.syntype.defined_values)

            data.append(self.synclass.defined_values)
            data.append(self.number.defined_values)

            return self.make_identifier(data)

        return None
