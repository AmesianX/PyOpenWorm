from os.path import exists, abspath, join as pth_join, dirname
import json
import logging


L = logging.getLogger(__name__)


# XXX: How should we handle arguments that apply to many different commands,
# but which don't belong to a sub-command??


class POW(object):
    """
    Attributes set on this object parameterize commands, but they are not
    to be changed by the commands
    """

    def __init__(self):
        self.store_name = 'worm.db'
        """ The file name of the database store """

        self.config_file = 'default.conf'
        """ The config file name """

        self.graph_accessor_finder = None
        """ Callable that returns a graph accessor when given a URL for the graph """

    # Imports, other than those from the standard library, are included in each
    # method separately since, eventually, each method should be independent of
    # the others to the extent that you may even choose not to install
    # dependencies for commands which are not used.  This should permit a
    # generic handler for ImportError wherein a dependency is only installed
    # when needed. This should also reduce load times for each command

    def init(self, update_existing_config=False):
        """
        Makes a new graph store.

        The configuration file will be created if it does not exist. If it
        *does* exist, the location of the database store will, by default, not
        be changed in that file

        Parameters
        ----------
        update_existing_config : bool
            If True, updates the existing config file to point to the given
            file for the store configuration
        """
        store_fname = abspath(self.store_name)
        if not exists(self.config_file):
            with open(self._default_config(), 'r') as f:
                default = json.load(f)
                with open(self.config_file, 'w') as of:
                    default['rdf.store_conf'] = store_fname
                    json.dump(default, of)
        elif update_existing_config:
            with open(self.config_file, 'r+') as f:
                conf = json.load(f)
                conf['rdf.store_conf'] = store_fname
                f.seek(0)
                json.dump(conf, f)

        self._init_store()

    def fetch_graph(self, url):
        """
        Fetch a graph
        """
        res = self._obtain_graph_accessor(url)
        if not res:
            raise UnreadableGraphException('Could not read the graph at {}'.format(url))
        return res()

    def add_graph(self, url=None, context=None, include_imports=True):
        """
        Fetch a graph and add it to the local store.

        Parameters
        ----------
        url : str
            The URL of the graph to fetch
        context : rdflib.term.URIRef
            If provided, only this context and, optionally, its imported graphs
            will be added.
        include_imports : bool
            If True, imports of the named context will be included. Has no
            effect if context is None.
        """
        graph = self.fetch_graph(url)
        dat = self._conf()

        dat['rdf.graph'].addN(graph.quads((None, None, None, context)))

    def _obtain_graph_accessor(self, url):
        if self.graph_accessor_finder is None:
            raise Exception('No graph_accessor_finder has been configured')

        return self.graph_accessor_finder(url)

    def _conf(self):
        from PyOpenWorm.data import Data
        dat = getattr(self, '_dat', None)
        if not dat:
            dat = Data.open(self.config_file)
            dat.init_database()
            self._dat = dat
        return dat

    _init_store = _conf

    def clone(self, url=None, update_existing_config=False):
        """Clone a data store

        Parameters
        ----------
        url : str
            URL of the data store to clone
        """
        # TODO: As a first cut
        # 1) should download a file at the given URL
        #
        # 2) verify that it's an RDF graph
        #
        # 3) init a git repo
        #
        # 4) rewrite the serialization as an nquads (setting the clone url as
        # the default context)
        #
        # 5) add the nquads serialization to the git repo
        #
        # 6) commit to the git repo
        #
        # 7) do a similar thing to POW::init for initializing the database
        #
        # 8) add the contents of the nquads to the new database
        #
        # 9) and, finally, print some summary stats about the newly created
        # database like how many triples, contexts, total size downloaded, etc.

    def translate(self, translator, output_key=None, *data_sources, **named_data_sources):
        """
        Do a translation with the named translator and inputs
        """

    def reconstitute(self, data_source):
        """
        Recreate a data source by executing the chain of translators that went
        into making it.
        """

    def _package_path(self):
        """
        Get the package path
        """
        from pkgutil import get_loader
        return dirname(get_loader('PyOpenWorm').get_filename())

    def _default_config(self):
        return pth_join(self._package_path(), 'default.conf')

    def commit(self):
        """
        """

    def diff(self):
        """
        """

    def merge(self):
        """
        """

    def push(self):
        """
        """

    def tag(self):
        """
        """


class POWSource(object):
    # Commands specific to sources
    def create(self, kind, key, *args, **kwargs):
        """
        Create the source and add it to the graph.

        Arguments are determined by the type of the data source

        Parameters
        ----------
        kind : rdflib.term.URIRef
            The kind of source to create
        key : str
            The key, a unique name for the source
        """

    def list(self, context=None):
        """
        List known sources
        """

    def list_kinds(self):
        """
        List kinds of sources
        """


class UnreadableGraphException(Exception):
    pass


class InvalidGraphException(Exception):
    pass
