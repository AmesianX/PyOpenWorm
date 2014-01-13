# -*- coding: utf-8 -*-

import unittest

import PyOpenWorm


class PyOpenWormTest(unittest.TestCase):
    """Test for PyOpenWorm."""

    def test_network(self):
        self.assertTrue(isinstance(PyOpenWorm.Network(),PyOpenWorm.Network))
        
    def test_network_aneuron(self):
    	self.assertTrue(isinstance(PyOpenWorm.Network().aneuron('AVAL'),PyOpenWorm.Neuron))
    	
    def test_neuron_type(self):
    	self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').type(),'Interneuron')
    	self.assertEquals(PyOpenWorm.Network().aneuron('DD5').type(),'Motor')
    	self.assertEquals(PyOpenWorm.Network().aneuron('PHAL').type(),'Sensory')
    	
    def test_neuron_name(self):
    	self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').name(),'AVAL')
    	self.assertEquals(PyOpenWorm.Network().aneuron('AVAR').name(),'AVAR')
    	
    def test_neuron_GJ_degree(self):
    	self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').GJ_degree(),60)
    	
    def test_neuron_Syn_degree(self):
    	self.assertEquals(PyOpenWorm.Network().aneuron('AVAL').Syn_degree(),74)
        
#    def test_bneuron(self):
#        self.assertTrue(1)

        