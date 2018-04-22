import re
import traceback
import csv

from PyOpenWorm.utils import normalize_cell_name
from PyOpenWorm.connection import Connection
from PyOpenWorm.cell import Cell
from PyOpenWorm.context import Context
from PyOpenWorm.document import Document
from PyOpenWorm.evidence import Evidence
from PyOpenWorm.neuron import Neuron
from PyOpenWorm.muscle import Muscle
from PyOpenWorm.worm import Worm
from PyOpenWorm.network import Network
from PyOpenWorm.datasource import Translation

from .csv_ds import CSVDataTranslator, CSVDataSource
from .common_data import TRANS_NS
from .data_with_evidence_ds import DataWithEvidenceDataSource


class ConnectomeCSVDataSource(CSVDataSource):
    pass


class NeuronConnectomeCSVTranslation(Translation):
    def __init__(self, **kwargs):
        super(NeuronConnectomeCSVTranslation, self).__init__(**kwargs)
        self.neurons_source = NeuronConnectomeCSVTranslation.ObjectProperty()


class NeuronConnectomeCSVTranslator(CSVDataTranslator):
    input_type = (ConnectomeCSVDataSource, DataWithEvidenceDataSource)
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.NeuronConnectomeCSVTranslator
    translation_type = NeuronConnectomeCSVTranslation

    def translate(self, data_source, neurons_source):

        print ("uploading statements about connections", neurons_source)

        # muscle cells that are generically defined in source and need to be broken
        # into pair of L and R before being added to PyOpenWorm

        # muscle cells that have different names in connectome source and cell list.
        # Their wormbase cell list names will be used in PyOpenWorm
        changed_muscles = ['ANAL', 'INTR', 'INTL', 'SPH']

        # counters for terminal printing
        neuron_connections = 0
        muscle_connections = 0
        other_connections = 0

        res = self.make_new_output(sources=(data_source, neurons_source))
        tr = res.translation.onedef()
        tr.neurons_source(neurons_source)

        try:
            w = Worm()
            n_q = neurons_source.data_context.query(Network)()
            n = next(n_q.load(), n_q)

            neuron_objs = list(set(n.neurons()))
            muscle_objs = list(w.muscles())

            # get lists of neuron and muscles names
            neurons = [neuron.name() for neuron in neuron_objs]
            muscles = [muscle.name() for muscle in muscle_objs]

            # Evidence object to assert each connection
            ctxd_Document = res.evidence_context(Document)
            doc = ctxd_Document(key="emmons2015",
                                title='Whole-animal C. elegans connectomes',
                                year=2015,
                                uri='http://abstracts.genetics-gsa.org/cgi-bin/'
                                'celegans15s/wsrch15.pl?author=emmons&sort=ptimes&'
                                'sbutton=Detail&absno=155110844&sid=668862')
            doc.author('Emmons, S.')
            doc.author('Cook, S.')
            doc.author('Jarrell, T.')
            doc.author('Wang, Y.')
            doc.author('Yakolev, M.')
            doc.author('Nguyen, K.')
            doc.author('Hall, D.')
            e = res.evidence_context(Evidence)(key="emmons2015", reference=doc)
            docctx = res.evidence_context(Context)(ident=self.translator_identifier + '/emmons2015-context')
            e.supports(docctx.rdf_object)
            with docctx(Neuron, Muscle, Cell, Connection) as ctx:
                res.data_context.add_import(ctx.context)
                with open(data_source.csv_file_name.onedef()) as csvfile:
                    edge_reader = csv.reader(csvfile)
                    next(edge_reader)  # skip header row
                    for row in edge_reader:
                        source, target, weight, syn_type = map(str.strip, row)

                        # set synapse type to something the Connection object
                        # expects, and normalize the source and target names
                        if syn_type == 'electrical':
                            syn_type = 'gapJunction'
                        elif syn_type == 'chemical':
                            syn_type = 'send'

                        source = normalize_cell_name(source).upper()
                        target = normalize_cell_name(target).upper()

                        weight = int(weight)

                        # remove BMW from Body Wall Muscle cells
                        if 'BWM' in source:
                            source = normalize_muscle(source)
                        if 'BWM' in target:
                            target = normalize_muscle(target)

                        # change certain muscle names to names in wormbase
                        if source in changed_muscles:
                            source = changed_muscle(source)
                        if target in changed_muscles:
                            target = changed_muscle(target)

                        sources = marshall(ctx, source, muscles, neurons)
                        targets = marshall(ctx, target, muscles, neurons)

                        for s in sources:
                            for t in targets:
                                conn = add_synapse(ctx, s, t, weight, syn_type)
                                n.synapse(conn)
                                kind = conn.termination()
                                if kind == 'muscle':
                                    muscle_connections += 1
                                elif kind == 'neuron':
                                    neuron_connections += 1
                                else:
                                    other_connections += 1

            print('Total neuron to neuron connections added = %i' % neuron_connections)
            print('Total neuron to muscle connections added = %i' % muscle_connections)
            print('Total other connections added = %i' % other_connections)
            print('uploaded connections')

        except Exception:
            traceback.print_exc()
        return res


def marshall(ctx, name, muscles, neurons):
    ret = []
    res = None
    res2 = None
    if name in neurons:
        res = ctx.Neuron(name)
    elif name in muscles:
        res = ctx.Muscle(name)
    elif name in TO_EXPAND_MUSCLES:
        res, res2 = expand_muscle(ctx, name)
    elif name in OTHER_CELLS:
        res = ctx.Cell(name)

    if res is not None:
        ret.append(res)
    if res2 is not None:
        ret.append(res2)

    return ret


def add_synapse(ctx, source, target, weight, syn_type):
    c = ctx.Connection(pre_cell=source, post_cell=target,
                       number=weight, syntype=syn_type)

    if isinstance(source, ctx.Neuron) and isinstance(target, ctx.Neuron):
        c.termination('neuron')
    elif isinstance(source, ctx.Neuron) and isinstance(target, ctx.Muscle):
        c.termination('muscle')
    elif isinstance(source, ctx.Muscle) and isinstance(target, ctx.Neuron):
        c.termination('muscle')

    return c


# to normalize certian body wall muscle cell names
SEARCH_STRING_MUSCLE = re.compile(r'\w+[BWM]+\w+')
REPLACE_STRING_MUSCLE = re.compile(r'[BWM]+')


def normalize_muscle(name):
    # normalize names of Body Wall Muscles
    # if there is 'BWM' in the name, remove it
    if re.match(SEARCH_STRING_MUSCLE, name):
        name = REPLACE_STRING_MUSCLE.sub('', name)
    return name


MUSCLES = {
    'ANAL': 'MU_ANAL',
    'INTR': 'MU_INT_R',
    'INTL': 'MU_INT_L',
    'SPH': 'MU_SPH'
}

TO_EXPAND_MUSCLES = ['PM1D', 'PM2D', 'PM3D', 'PM4D', 'PM5D']

#
# cells that are neither neurons or muscles. These are marked as
# 'Other Cells' in the wormbase cell list but are still part of the new
# connectome.
#
# TODO: In future work these should be uploaded seperately to
# PyOpenWorm in a new upload function and should be referred from there
# instead of this list.
OTHER_CELLS = ['MC1DL', 'MC1DR', 'MC1V', 'MC2DL', 'MC2DR', 'MC2V', 'MC3DL',
               'MC3DR', 'MC3V']


def changed_muscle(x):
    return MUSCLES[x]


def expand_muscle(ctx, name):
    return ctx(Muscle)(name + 'L'), ctx(Muscle)(name + 'R')
