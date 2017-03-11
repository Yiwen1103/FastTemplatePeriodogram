from __future__ import print_function

import os
import sys
from time import time
from math import *
import numpy as np
from scipy.optimize import curve_fit

try:
    # Python 2.x only
    import cPickle as pickle
except ImportError:
    import pickle

from . import fast_template_periodogram as ftp
from .template import Template



class FastTemplateModeler(object):
	def __init__(self, templates=None, oversampling=5, nyquist_factor=5):
        pass

    def add_templates(self, templates):
        if isinstance(templates, list):
            self.
        elif isinstance(templates, )
        pass

    def fit(self, t, y, yerr):


    def precompute_sums(self):
        self.omegas, self.summations, \
        self.YY, self.w, self.ybar = \
            ftp.compute_summations(self.t, self.y, self.yerr, self._max_nharmonics,
                                oversampling=self.oversampling, nyquist_factor=self.nyquist_factor)



class FastTemplateModelerMultiband(FastTemplateModeler):
	def __init__(self, **kwargs):

	def fit(self, t, y, yerr, filts):

	def compute_sums(self):
		pass

	def periodogram(self):
		pass

	def best_model(self, freq=None):
		if freq is None:
			freq = self.best_freq

    def 
		

class FastTemplateModeler(object):

    """
    Base class for template modelers

    Parameters
    ----------

    verbose: boolean (default: False), optional
       	print timing information and progress
    ofac: float, optional (default: 10)
        oversampling factor -- higher values of ofac decrease
        the frequency spacing (by increasing the size of the FFT)
    hfac: float, optional (default: 3)
        high-frequency factor -- higher values of hfac increase
        the maximum frequency of the periodogram at the
        expense of larger frequency spacing.
    nharmonics: None or int, optional (default: None)
        Number of harmonics to keep if a constant number of harmonics
        is desired

    """
    def __init__(self, **kwargs):
        
    def _get_template_by_id(self, template_id):
        assert(template_id in self.templates)
        return self.templates[template_id]

    def _template_ids(self):
        return self.templates.keys()

    def get_new_template_id(self):
        i = 0
        while i in self.templates:
            i += 1
        return i

    def add_template(self, template, template_id=None):
        if template_id is None:
            if template.template_id is None:
                ID = self.get_new_template_id()
                self.templates[ID] = template
            else:
                self.templates[template.template_id] = template
        else:
            self.templates[template_id] = template
        return self

    def add_templates(self, templates, template_ids=None):

        if isinstance(templates, dict):
            for ID, template in templates.items():
                self.add_template(template, template_id=ID)

        elif isinstance(templates, list):
            if template_ids is None:
                for template in templates:
                    self.add_template(template)
            else:
                for ID, template in zip(template_ids, templates):
                    self.add_template(template, template_id=ID)
        elif not hasattr(templates, '__iter__'):
            self.add_template(templates, template_id=template_ids)
        else:
            raise Exception("did not recognize type of 'templates' passed to add_templates")

        return self

    def remove_templates(self, template_ids):
        for ID in template_ids:
            assert ID in self.templates
            del self.templates[ID]
        return self

    def set_params(self, **new_params):
        self.params.update(new_params)
        return self

    def fit(self, x, y, err):
        """
        Parameters
        ----------
        x: np.ndarray, list
            independent variable (time)
        y: np.ndarray, list
            array of observations
        err: np.ndarray
            array of observation uncertainties
        """
        self.x = x
        self.y = y
        self.err = err

        # Set all old values to none
        self.summations = None
        self.freqs_ = None
        self.best_template_id = None
        self.best_template = None
        self.best_model_params = None
        self.periodogram_ = None
        self.model_params_ = None
        self.periodogram_all_templates_ = None
        return self

    def compute_sums(self):

        self.omegas, self.summations, \
        self.YY, self.w, self.ybar = \
            ftp.compute_summations(self.x, self.y, self.err, self.max_harm,
                                ofac=self.params['ofac'], hfac=self.params['hfac'])

        return self



    def periodogram(self, **kwargs):
        self.params.update(kwargs)

        #if self.summations is None:
        #    self.compute_sums()
        loud = False if not 'loud' in self.params else self.params['loud']

        all_ftps = []
        for template_id, template in self.templates.items():
            args = (self.x, self.y, self.err, template.cn, template.sn)
            kwargs = dict(ofac       = self.params['ofac'],
                          hfac       = self.params['hfac'],
                          ptensors   = template.ptensors,
                          pvectors   = template.pvectors,
                          omegas     = self.omegas,
                          summations = self.summations,
                          YY         = self.YY,
                          ybar       = self.ybar,
                          w          = self.w,
                          loud       = loud,
                          return_best_fit_pars=True)
            all_ftps.append((template_id, ftp.fast_template_periodogram(*args, **kwargs)))

        template_ids, all_ftps_ = zip(*all_ftps)
        freqs, ftps, modelpars  = zip(*all_ftps_)
        freqs = freqs[0]

        self.periodogram_ = np.array([ max([ f[i] for f in ftps ]) for i in range(len(freqs)) ])
        self.freqs_ = freqs
        self.periodogram_all_templates_ = zip(template_ids, ftps)
        self.model_params_ = zip(template_ids, modelpars)

        # Periodogram is the maximum periodogram value at each frequency
        return self.freqs_, self.periodogram_

    def get_best_model(self, **kwargs):

        ibest = np.argmax(self.periodogram_)
        tbest = np.argmax([ f[ibest] for t, f in self.periodogram_all_templates_ ])

        self.best_freq = self.freqs_[ibest]
        self.best_template_id, self.best_model_params = self.model_params_[tbest]

        self.best_model_params = self.best_model_params[ibest]
        self.best_template = self.templates[self.best_template_id]

        return self.best_template, self.best_model_params
