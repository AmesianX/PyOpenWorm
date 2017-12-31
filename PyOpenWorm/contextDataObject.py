from PyOpenWorm.dataObject import DataObject


class ContextDataObject(DataObject):
    """ Represents a context """
    class_context = 'http://openworm.org/schema'


__yarom_mapped_classes__ = (ContextDataObject,)
