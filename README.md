<img src="docs/_static/logo_wide_rev.svg"><br>

-----------------------------------------------------

# *WATex*: machine learning research in water exploration

### *Life is much better with potable water*

 [![Documentation Status](https://readthedocs.org/projects/watex/badge/?version=latest)](https://watex.readthedocs.io/en/latest/?badge=latest)
 ![GitHub](https://img.shields.io/github/license/WEgeophysics/watex?color=blue&label=Licence&logo=Github&logoColor=blue&style=flat-square)
 ![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/WEgeophysics/watex?logo=appveyor)
 ![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/WEgeophysics/watex/ci.yaml?label=CI%20-%20Build%20&logo=github&logoColor=g)
[![Coverage Status](https://coveralls.io/repos/github/WEgeophysics/watex/badge.svg?branch=master)](https://coveralls.io/github/WEgeophysics/watex?branch=master)
 ![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/WEgeophysics/watex?color=blue&include_prereleases&logo=python)
 [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7553789.svg)](https://doi.org/10.5281/zenodo.7553789)
 ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/watex?color=orange&logo=pypi)
 [![PyPI version](https://badge.fury.io/py/watex.svg)](https://badge.fury.io/py/watex)

##  Overview

**_WATex_** is a Python-based library mainly focused on the groundwater exploration (GWE). It brings novel approaches 
    for reducing numerous losses during the hydro-geophysical exploration projects. It encompasses 
    the Direct-current (DC) resistivity ( Electrical profiling (ERP) & vertical electrical sounding (VES)), 
    short-periods electromagnetic (EM), geology and hydrogeology methods. From methodologies based on Machine Learning,  
    it allows to: 
   - auto-detect the right position to locate the drilling operations to minimize the rate of unsuccessful drillings 
     and unsustainable boreholes;
   - reduce the cost of permeability coefficient (k) data collection during the hydro-geophysical engineering projects,
   - predict the water content in the well such as the groundwater flow rate, the level of water inrush, ...
   - recover the EM loss signals in area with huge interferences noises ...
   - etc.

## Documentation 

Visit the [library website](https://watex.readthedocs.io/en/latest/) for more resources. You can also quick browse the software [API reference](https://watex.readthedocs.io/en/latest/api_references.html)
and flip through the [examples page](https://watex.readthedocs.io/en/latest/glr_examples/index.html) to see some of expected results. Furthermore, the 
[step-by-step guide](https://watex.readthedocs.io/en/latest/glr_examples/applications/index.html#applications-step-by-step-guide) is elaborated for real-world 
engineering problems such as computing DC parameters and predicting the k-parameter... 

## Licence 

**_WATex_** is under [3-Clause BSD](https://opensource.org/licenses/BSD-3-Clause) License.

## System requirement

* Python 3.9+

## Installation 

[_WATex_](https://pypi.org/project/watex/0.1.7/) can be installed from ( [PyPI](https://pypi.org/) platform distribution as: 
```bash 
pip install watex
```
Furthermore, to get the latest development of the code, it is recommended to install it from source using: 

```bash
git clone https://github.com/WEgeophysics/watex.git 
```
The installation from [conda-forge](https://conda-forge.org/) ) distribution is coming soon.

For step-by-step guide about the installation and how to manage the 
dependencies, visit our [installation guide](https://watex.readthedocs.io/en/latest/installation.html) page.

## Some demos 

1. Drilling location auto-detection

For this example, we randomly generate 50 stations of synthetic ERP resistivity data with ``minimum`` and ``maximum ``
resistivity values equal to  ``1e1`` and ``1e4`` ohm.m  respectively as:

```python 
import watex as wx 
data = wx.make_erp (n_stations=50, max_rho=1e4, min_rho=10., as_frame =True, seed =42 ) 
``` 
* Naive auto-detection (NAD)

The NAD automatically proposes a suitable location with NO restrictions (constraints) observed in the survey site
during the GWE. We may understand by ``suitable``, a location expecting to give a flow rate greater 
than 1m3/hr at least. 

```python
robj=wx.ResistivityProfiling (auto=True ).fit(data ) 
robj.sves_ 
Out[1]: 'S025'

```
The suitable drilling location is proposed at station ``S25`` (stored in the attribute ``sves_``). 

* Auto-detection with constraints (ADC)

The constraints refer to the restrictions observed in the survey area during the DWSC. This is common
in real-world exploration. For instance, a station close to a heritage site should be discarded 
since no drilling operations are authorized at that place. When many restrictions 
are enumerated in the survey site, they must be listed in a dictionary with a reason and passed to the parameter 
``constraints`` so these stations should be ignored during the automatic detection. Here is an example of constraints
application to our example.

```python 
restrictions = {
    'S10': 'Household waste site, avoid contamination',
    'S27': 'Municipality site, no authorization to make a drill',
    'S29': 'Heritage site, drilling prohibited',
    'S42': 'Anthropic polluted place, avoid contamination within a few years',
    'S46': 'Marsh zone, borehole will dry up during the dry season'
 }
robj=wx.ResistivityProfiling (constraints= restrictions, auto=True ).fit(data ) 
robj.sves_
Out[2]: 'S033'
```
Notice, the station ``S25`` is no longer considered as the `suitable` location and henceforth, propose ``S33`` as the
priority for drilling operations. However, if the station is close to a restricted area, a warning should raise to 
inform the user to avoid taking a risk to perform a drilling location at that location.

Note that before the drilling operations commence, make sure to carry out the DC-sounding (VES) at that point. **_WATex_** computes 
another parameter called `ohmic-area` `` (ohmS)`` to detect the effectiveness of the existing fracture zone at that point. See more in 
the software [documentation](https://watex.readthedocs.io/en/latest/).
  
2. Predict permeability coefficient ``k`` from logging dataset using MXS approach
 
MXS stands for mixture learning strategy. It uses upstream unsupervised learning for 
``k`` -aquifer similarity label prediction and the supervising learning for 
final ``k``-value prediction. For our toy example, we use two boreholes data 
stored in the software and merge them to compose a unique dataset. In addition, we dropped the 
``remark`` observation which is subjective data not useful for ``k`` prediction as:

```python
h= wx.fetch_data("hlogs", key='*', drop_observations =True ) # returns log data object.
h.feature_names
Out[3]: Index(['hole_id', 'depth_top', 'depth_bottom', 'strata_name', 'rock_name',
           'layer_thickness', 'resistivity', 'gamma_gamma', 'natural_gamma', 'sp',
           'short_distance_gamma', 'well_diameter'],
          dtype='object')
hdata = h.frame 
```
``k`` is collected as continue values (m/darcies) and should be categorized for the 
naive group of aquifer prediction (NGA) first. The latter is used to predict 
upstream the  MXS target ``ymxs``.  Here, we used the default categorization 
provided by the software and we expect in the area ``2`` minimum groups of 
the aquifer. The code is given as: 
```python 
mxs = wx.MXS (kname ='k', n_groups =2).fit(hdata) 
ymxs=mxs.predictNGA().makeyMXS(categorize_k=True, default_func=True)
mxs.yNGA_ [62:74]
Out[4]: array([1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2])
ymxs[62:74]
Out[5]: array([ 0,  0,  0,  0, 12, 12, 12, 12, 12, 12, 12, 12])
```
To understand the transformation from NGA to MXS target (``ymxs``), please, have a look 
of the following [paper](http://dx.doi.org/10.2139/ssrn.4326365).
Once the MXS target is predicted, we call the ``make_naive_pipe`` function, to 
impute, scale, and transform the predictor ``X`` at once into a compressed sparse 
matrix ready for final prediction using the [support vector machines](https://ieeexplore.ieee.org/document/708428) and 
[random forest](https://www.ibm.com/topics/random-forest)as examples. Here we go: 
``` python 
X= hdata [h.feature_names]
Xtransf = wx.make_naive_pipe (X, transform=True) 
Xtransf 
Out[6]: 
<218x46 sparse matrix of type '<class 'numpy.float64'>'
	with 2616 stored elements in Compressed Sparse Row format> 
Xtrain, Xtest, ytrain, ytest = wx.sklearn.train_test_split (Xtransf, ymxs ) 
ypred_k_svc= wx.sklearn.SVC().fit(Xtrain, ytrain).predict(Xtest)
ypred_k_rf = wx.sklearn.RandomForestClassifier ().fit(Xtrain, ytrain).predict(Xtest)
```
We can now check the ``k`` prediction scores using ``accuracy_score`` function as: 
```python 
wx.sklearn.accuracy_score (ytest, ypred_k_svc)
Out[7]: 0.9272727272727272
wx.sklearn.accuracy_score (ytest, ypred_k_rf)
Out[8]: 0.9636363636363636
```
As we can see, the results of ``k`` prediction are quite satisfactory for our 
toy example using only two boreholes data. Note that things can become more 
complex and interesting when using many boreholes data. For more in 
depth, visit our [examples page](https://watex.readthedocs.io/en/latest/glr_examples/index.html). 

3. EM tensors recovering and analyses

Flip through the following link for more examples about [EM tensor restoring](https://watex.readthedocs.io/en/latest/glr_examples/applications/plot_tensor_restoring.html#sphx-glr-glr-examples-applications-plot-tensor-restoring-py), 
visualize the [confidence interval](https://watex.readthedocs.io/en/latest/glr_examples/utils/plot_confidence_in_data.html#sphx-glr-glr-examples-utils-plot-confidence-in-data-py) in resistivity data, 
the [sknewness](https://watex.readthedocs.io/en/latest/glr_examples/methods/plot_phase_tensors.html#sphx-glr-glr-examples-methods-plot-phase-tensors-py) analysis plots  and else...

## Citations

If the [software](https://doi.org/10.5281/zenodo.7553789) seemed useful to you in any published work, I will much appreciate to cite the paper below:

> *Kouadio, Kouao Laurent and Liu, Jianxin and Liu, Rong, watex: Machine learning research in water exploration. Available at SSRN:  http://dx.doi.org/10.2139/ssrn.4348617*

In most situations where **_WATex_** is cited, a citation to [scikit-learn](https://scikit-learn.org/stable/about.html#citing-scikit-learn) would also be appropriate.

See also some [case history](https://watex.readthedocs.io/en/latest/citing.html) papers using **_WATex_**. 

## Contributions 

1. Department of Geophysics, School of Geosciences & Info-physics, [Central South University](https://en.csu.edu.cn/), China.
2. Hunan Key Laboratory of Nonferrous Resources and Geological Hazards Exploration Changsha, Hunan, China
3. Laboratoire de Geologie Ressources Minerales et Energetiques, UFR des Sciences de la Terre et des Ressources Minières, [Université Félix Houphouët-Boigny]( https://www.univ-fhb.edu.ci/index.php/ufr-strm/), Cote d'Ivoire.

Developer: [_L. Kouadio_](https://wegeophysics.github.io/) <<etanoyau@gmail.com>>



