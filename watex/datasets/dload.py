# -*- coding: utf-8 -*-
#   Licence:BSD 3-Clause, Author: LKouadio 

"""
load different data as a function 
=================================

Inspired from the machine learning popular dataset loading 

Created on Thu Oct 13 16:26:47 2022
@author: Daniel
"""

from warnings import warn 
from importlib import resources 
import pandas as pd 
from .._docstring import erp_doc , ves_doc 
from ._io import csv_data_loader, _to_dataframe , DMODULE 
from ..utils.coreutils import vesSelector, erpSelector 
from ..utils.mlutils import split_train_test_by_id , existfeatures
from ..utils.funcutils import to_numeric_dtypes , smart_format
from ..utils.box import Boxspace

__all__= [ "load_bagoue" , "load_gbalo", "load_iris", "load_semien",
          "load_tankesse",  "load_boundiali", "load_hlogs"]

def load_tankesse (
        *, as_frame =True, tag=None,data_names=None, **kws 
   ):
    data_file ="tankesse.csv"
    with resources.path (DMODULE , data_file) as p : 
        data_file = p 
    df =  erpSelector(f = data_file )
    return df if as_frame else Boxspace(
            data = df.values , 
            resistivity = df.resistivity,  
            station= df.station, 
            northing = df.northing,
            easting = df.easting, 
            longitude= df.longitude, 
            latitude = df.latitude
            ) 

load_tankesse.__doc__= erp_doc.__doc__.format(
    survey_name = 'TANKESSE',  shape = (100, 4), max_depth = 100. ,
    AB_distance=100., MN_distance = 10., profiling_number=99)

def load_boundiali (
        *, as_frame =True, index_rhoa =0, tag=None,data_names=None, **kws 
  ):
   
    data_file ="boundiali_ves.csv"
    with resources.path (DMODULE , data_file) as p : 
        data_file = p 
    df =  vesSelector(f = data_file  ,index_rhoa = index_rhoa)
    return df if as_frame else Boxspace(
            data = df.values, 
            resistivity = df.resistivity,  
            AB= df.AB, 
            MN = df.MN,
            feature_names= list(df.columns)
            ) 

load_boundiali.__doc__ = ves_doc.__doc__.format(
    survey_name = 'BOUNDIALI',  shape = (33, 6), max_depth = 110. ,
    c_start= 1., c_stop =110. , p_start=.4 , p_stop=10., 
    sounding_number= 4
    )

def load_semien (
        *, as_frame =True , index_rhoa =0, tag=None,data_names=None, **kws
 ):
    data_file = 'semien_ves.csv'
    with resources.path (DMODULE , data_file) as p : 
        data_file = p 
    df = vesSelector(data= data_file, index_rhoa = index_rhoa) 
    return df if as_frame else Boxspace( 
        data = df.values , 
        resistivity = df.resistivity.values,  
        AB= df.AB.values, 
        MN = df.MN.values,
        feature_names= list(df.columns)
        )

load_semien.__doc__= ves_doc.__doc__.format(
    survey_name = 'SEMIEN',  shape = (33, 5), max_depth = 110. ,
    c_start= 1., c_stop =110. , p_start=.4 , p_stop=10., 
    sounding_number= 3
    )

def load_gbalo (
        *, kind ='erp', as_frame=True, index_rhoa = 0 , tag=None,
        data_names=None , **kws 
): 
    d= dict() 
    kind =str(kind).lower().strip() 
    
    if kind not in ("erp", "ves"): 
        warn (f"{kind!r} is unknow! By default DC-Resistivity"
              " profiling is returned.")
        kind="erp"
    data_file = f"dc{kind}_gbalo.csv" 
    with resources.path (DMODULE , data_file) as p : 
        data_file = str(p)
    if "erp" in data_file: 
        df= erpSelector(data_file )
        d = dict( 
            data = df.values , 
            resistivity = df.resistivity.values,  
            station= df.station.values, 
            northing = df.northing.values,
            easting = df.easting.values, 
            longitude= df.longitude.values, 
            latitude = df.latitude.values,
            feature_names=list(df.columns),
            )
    if "ves" in data_file : 
        df=vesSelector(data =data_file , index_rhoa= index_rhoa)
        d = dict(
            data = df.values , 
            resistivity = df.resistivity,  
            AB= df.AB, 
            MN = df.MN, 
            feature_names=list(df.columns)
        )
    if as_frame: return df 
    
    return Boxspace( **d )
 
load_gbalo.__doc__ ="""\ 
A DC-Electrical resistivity profiling (ERP) and Vertical sounding  (VES) data
collected from a Gbalo locality during the National Drinking Water Supply 
Program (PNAEP) occurs in 2012-2014 in `Cote d'Ivoire`_.
Refer to :doc:`~watex._docstring.erp_doc.__doc__` and 
:doc:`~watex._docstring.ves_doc.__doc__` for illustrating the data arrangement 
is following: 

Parameters 
-----------
kind: str , ['ves'|'erp'], default is {'erp'}
    the kind of DC data to retrieve. If `kind`is set to ``ves`` and VES data is 
    fetched and ERP otherwise. 
    
as_frame : bool, default=False
    If True, the data is a pandas DataFrame including columns with
    appropriate dtypes (numeric). The target is
    a pandas DataFrame or Series depending on the number of target columns.
    If `as_frame` is False, then returning a :class:`~watex.utils.Boxspace`
    dictionary-like object, with the following attributes:
    data : {ndarray, dataframe} of shape (33, 6) and (45, 4) for VES and ERP
        The data matrix. If `as_frame=True`, `data` will be a pandas
        DataFrame.
    resistivity: {array-like} of shape (33,) and  (45,) for VES and ERP
        The resistivity of the sounding point. 
    station: {array-like} of shape (33,) and  (45,) for VES and ERP
        The motion distance of each station that increasing in meters.
        can be considered as the station point for data collection.
    northing: {array-like} of shape (33,) and  (45,) for VES and ERP
        The northing coordinates in UTM in meters at each station where 
        the data is collected. 
    easting: {array-like} of shape (33,) and  (45,) for VES and ERP
        The easting coordinates in UTM in meters at each station where the 
        data is collected. 
    latitude: {array-like} of shape (33,) and  (45,) for VES and ERP
        The latitude coordinates in degree decimals or 'DD:MM.SS' at each 
        station where the data is collected.
    longitude: {array-like} of shape (33,) and  (45,) for VES and ERP
        The longitude coordinates in degree decimals or 'DD:MM.SS' at each 
        station where the data is collected.
    DESCR: str
        The full description of the dataset.
    filename: str
        The path to the location of the data.
(tag, data_names): None
    Always None for API consistency 
kws: dict, 
    Keywords arguments pass to :func:`~watex.utils.coreutils._is_readable` 
    function for parsing data. 
    
Returns 
--------
data : :class:`~watex.utils.Boxspace`
    Dictionary-like object, with the following attributes.
    data : {ndarray, dataframe} 
        The data matrix. If `as_frame=True`, `data` will be a pandas
        DataFrame.
Example
--------
>>> from watex.datasets import load_gbalo 
>>> b= load_gbalo (as_frame =False , kind ='erp')
>>> b.station  # retreive the station position
... array([  0.,  10.,  20.,  30.,  40.,  50.,  60.,  70.,  80.,  90., 100.,
       110., 120., 130., 140., 150., 160., 170., 180., 190., 200., 210.,
       220., 230., 240., 250., 260., 270., 280., 290., 300., 310., 320.,
       330., 340., 350., 360., 370., 380., 390., 400., 410., 420., 430.,
       440.])

Notes
------
The array configuration is schlumberger and the max depth investigation is 
100 meters for :math:`AB/2` (current electrodes). The  profiling step
:math:`AB` is fixed to 100  meters whereas :math:`MN/2`  also fixed to
(potential electrodes) to 10 meters. The total number of station data 
collected is 45 while the sounding points is estimated to 33.
`station` , `easting` and `northing` are in meters and `rho` columns are 
in ohm.meters as apparent resistivity values. Furthermore, the total number of 
sounding performed with the prefix '`SE`' in 4. 

.. _Cote d'Ivoire: https://en.wikipedia.org/wiki/Ivory_Coast

""" 
def load_hlogs (
        *,  return_X_y=False, as_frame =False, key =None,  split_X_y=False, 
        test_size =.3 , tag =None, tnames = None , data_names=None , **kws): 
    """ Load logging data collected from boreholes """
    
    cf = as_frame 
    key = key or 'h502' 
    # assertion error if key does not exist. 
    msg = (f"key {key!r} does not exist yet, expect 'h502' or 'h2601'")
    assert str(key).lower() in {"h502", "h2601"}, msg
    
    data_file ='h.h5'
    with resources.path (DMODULE , data_file) as p : 
        data_file = p 

    data = pd.read_hdf(data_file, key = key)

    frame = None
    feature_names = list(data.columns [:12] ) 
    target_columns = list(data.columns [12:])
    
    tnames = tnames or target_columns
    # control the existence of the tnames to retreive
    try : 
        existfeatures(data[target_columns] , tnames)
    except Exception as error: 
        # get valueError message and replace Feature by target 
        msg = (". Acceptable target values are:"
               f"{smart_format(target_columns, 'or')}")
        raise ValueError(str(error).replace(
            'Features'.replace('s', ''), 'Target(s)')+msg)
        
    if  ( 
            split_X_y
            or return_X_y
            ) : 
        as_frame =True 
        
    if as_frame:
        frame, data, target = _to_dataframe(
            data, feature_names = feature_names, tnames = tnames, 
            target=data[tnames].values 
            )
        frame = to_numeric_dtypes(frame)
        
    if split_X_y: 
        X, Xt = split_train_test_by_id (data = frame , test_ratio= test_size, 
                                        keep_colindex= False )
        y = X[tnames] 
        X.drop(columns =target_columns, inplace =True)
        yt = Xt[tnames]
        Xt.drop(columns =target_columns, inplace =True)
        
        return  (X, Xt, y, yt ) if cf else (
            X.values, Xt.values, y.values , yt.values )
    
    if return_X_y: 
        data , target = data.values, target.values
        
    if ( 
            return_X_y 
            or cf
            ) : return data, target 
    
    return Boxspace(
        data=data.values,
        target=data[tnames].values,
        frame=data,
        tnames=tnames,
        target_names = target_columns,
        #XXX Add description 
        DESCR= '', # fdescr,
        feature_names=feature_names,
        filename=data_file,
        data_module=DMODULE,
    )

load_hlogs.__doc__="""\
Load and return the hydro-logging dataset. Dataset contained multi-target 
than can be used for a classification or regression problem.

Parameters
----------
return_X_y : bool, default=False
    If True, returns ``(data, target)`` instead of a Bowlspace object. See
    below for more information about the `data` and `target` object.
    .. versionadded:: 0.1.2
    
as_frame : bool, default=False
    If True, the data is a pandas DataFrame including columns with
    appropriate dtypes (numeric). The target is
    a pandas DataFrame or Series depending on the number of target columns.
    If `return_X_y` is True, then (`data`, `target`) will be pandas
    DataFrames or Series as described below.
    .. versionadded:: 0.1.3
split_X_y=False,
    If True, the data is splitted to hold the training set (X, y)  and the 
    testing set (Xt, yt) with the according to the test size ratio.  
test_size: float, default is {{.3}} i.e. 30% (X, y)
    The ratio to split the data into training (X, y)  and testing (Xt, yt) set 
    respectively. 
tnames: str, optional 
    the name of the target to retreive. If ``None`` the full target columns 
    are collected and compose a multioutput `y`. For a singular classification 
    or regression problem, it is recommended to indicate the name of the target 
    that is needed for the learning task. 
(tag, data_names): None
    `tag` and `data_names` do nothing. just for API purpose and to allow 
    fetching the same data uing the func:`~watex.data.fetch_data` since the 
    latter already holds `tag` and `data_names` as parameters. 

Returns
-------
data : :class:`~watex.utils.Boxspace`
    Dictionary-like object, with the following attributes.
    data : {ndarray, dataframe} 
        The data matrix. If `as_frame=True`, `data` will be a pandas
        DataFrame.
    target: {ndarray, Series} 
        The classification target. If `as_frame=True`, `target` will be
        a pandas Series.
    feature_names: list
        The names of the dataset columns.
    target_names: list
        The names of target classes.
    frame: DataFrame 
        Only present when `as_frame=True`. DataFrame with `data` and
        `target`.
        .. versionadded:: 0.1
    DESCR: str
        The full description of the dataset.
    filename: str
        The path to the location of the data.
        .. versionadded:: 0.1
(data, target) : tuple if ``return_X_y`` is True
    A tuple of two ndarray. The first containing a 2D array of shape
    (n_samples, n_features) with each row representing one sample and
    each column representing the features. The second ndarray of shape
    (n_samples,) containing the target samples.
    .. versionadded:: 0.1
(X, Xt, y, yt): Tuple if ``split_X_y`` is True 
    A tuple of two ndarray (X, Xt). The first containing a 2D array of::
        .. math:: 
            
        shape (X, y) =  1-  \text{test_ratio} * (n_{samples}, n_{features}) *100
        
        shape (Xt, yt)= \text{test_ratio} * (n_{samples}, n_{features}) *100
        
     where each row representing one sample and each column representing the 
     features. The second ndarray of shape(n_samples,) containing the target 
     samples.
     
Examples
--------
Let's say ,we do not have any idea of the columns that compose the target,
thus, the best approach is to run the function without passing any parameters 
>>> from watex.datasets.dload import load_hlogs 
>>> b= load_hlogs()
>>> b.target_names 
... ['aquifer_group',
     'pumping_level',
     'aquifer_thickness',
     'hole_depth',
     'pumping_depth',
     'section_aperture',
     'k',
     'kp',
     'r',
     'rp',
     'remark']
>>> # Let's say we are interested of the targets 'pumping_level' and 
>>> # 'aquifer_thickness' and returns `y' 
>>> _, y = load_hlogs (as_frame=True, # return as frame X and y
                       tnames =['pumping_level','aquifer_thickness'], 
                       )
>>> list(y.columns)
... ['pumping_level', 'aquifer_thickness']
 
"""

def load_bagoue(
        *, return_X_y=False, as_frame=False, split_X_y=False, test_size =.3 , 
        tag=None , data_names=None,
 ):
    cf = as_frame 
    data_file = "bagoue.csv"
    data, target, target_names, feature_names, fdescr = csv_data_loader(
        data_file=data_file, descr_file="bagoue.rst", include_headline= True, 
    )
    frame = None
    target_columns = [
        "flow",
    ]
    if split_X_y: 
        as_frame =True 
        
    if as_frame:
        frame, data, target = _to_dataframe(
            data, feature_names = feature_names, tnames = target_columns, 
            target=target)
        frame = to_numeric_dtypes(frame)
        
    if split_X_y: 
        X, Xt = split_train_test_by_id (data = frame , test_ratio= test_size, 
                                        keep_colindex= False )
        y = X.flow ;  X.drop(columns =target_columns, inplace =True)
        yt = Xt.flow ; Xt.drop(columns =target_columns, inplace =True)
        
        return  (X, Xt, y, yt ) if cf else (
            X.values, Xt.values, y.values , yt.values )
    
    if return_X_y or as_frame:
        return data, target

    return Boxspace(
        data=data,
        target=target,
        frame=frame,
        tnames=target_columns,
        target_names=target_names,
        DESCR=fdescr,
        feature_names=feature_names,
        filename=data_file,
        data_module=DMODULE,
    )

load_bagoue.__doc__="""\
Load and return the Bagoue dataset (classification).
The Bagoue dataset is a classic and very easy multi-class classification
dataset.

Parameters
----------
return_X_y : bool, default=False
    If True, returns ``(data, target)`` instead of a BowlSpace object. See
    below for more information about the `data` and `target` object.
    .. versionadded:: 0.18
as_frame : bool, default=False
    If True, the data is a pandas DataFrame including columns with
    appropriate dtypes (numeric). The target is
    a pandas DataFrame or Series depending on the number of target columns.
    If `return_X_y` is True, then (`data`, `target`) will be pandas
    DataFrames or Series as described below.
    .. versionadded:: 0.23
split_X_y=False,
    If True, the data is splitted to hold the training set (X, y)  and the 
    testing set (Xt, yt) with the according to the test size ratio.  
test_size: float, default is {{.3}} i.e. 30% (X, y)
    The ratio to split the data into training (X, y)  and testing (Xt, yt) set 
    respectively.
(tag, data_names): None
    `tag` and `data_names` do nothing. just for API purpose and to allow 
    fetching the same data uing the func:`~watex.data.fetch_data` since the 
    latter already holds `tag` and `data_names` as parameters. 

Returns
-------
data : :class:`~watex.utils.Boxspace`
    Dictionary-like object, with the following attributes.
    data : {ndarray, dataframe} of shape (150, 4)
        The data matrix. If `as_frame=True`, `data` will be a pandas
        DataFrame.
    target: {ndarray, Series} of shape (150,)
        The classification target. If `as_frame=True`, `target` will be
        a pandas Series.
    feature_names: list
        The names of the dataset columns.
    target_names: list
        The names of target classes.
    frame: DataFrame of shape (150, 5)
        Only present when `as_frame=True`. DataFrame with `data` and
        `target`.
        .. versionadded:: 0.23
    DESCR: str
        The full description of the dataset.
    filename: str
        The path to the location of the data.
        .. versionadded:: 0.20
(data, target) : tuple if ``return_X_y`` is True
    A tuple of two ndarray. The first containing a 2D array of shape
    (n_samples, n_features) with each row representing one sample and
    each column representing the features. The second ndarray of shape
    (n_samples,) containing the target samples.
    .. versionadded:: 0.18
(X, Xt, y, yt): Tuple if ``split_X_y`` is True 
    A tuple of two ndarray (X, Xt). The first containing a 2D array of::
        
        .. math:: 
            
        shape (X, y) =  1-  \text{test_ratio} * (n_{samples}, n_{features}) *100
        
        shape (Xt, yt)= \text{test_ratio} * (n_{samples}, n_{features}) *100
        
     where each row representing one sample and each column representing the 
     features. The second ndarray of shape(n_samples,) containing the target 
     samples.
     
Examples
--------
Let's say you are interested in the samples 10, 25, and 50, and want to
know their class name.
>>> from watex.datasets import load_iris
>>> d = load_bagoue () 
>>> d.target[[10, 25, 50]]
... array([0, 2, 0])
>>> list(data.target_names)
... ['flow']   
  
"""

def load_iris(
        *, return_X_y=False, as_frame=False, tag=None, data_names=None, **kws
        ):
    data_file = "iris.csv"
    data, target, target_names, feature_names, fdescr = csv_data_loader(
        data_file=data_file, descr_file="iris.rst"
    )
    feature_names = ["sepal length (cm)","sepal width (cm)",
        "petal length (cm)","petal width (cm)",
    ]
    frame = None
    target_columns = [
        "target",
    ]
    if as_frame:
        frame, data, target = _to_dataframe(
            data, feature_names = feature_names, tnames = target_columns, 
            target = target)
        # _to(
        #     "load_iris", data, target, feature_names, target_columns
        # )
    if return_X_y or as_frame:
        return data, target

    return Boxspace(
        data=data,
        target=target,
        frame=frame,
        tnames=target_names,
        target_names=target_names,
        DESCR=fdescr,
        feature_names=feature_names,
        filename=data_file,
        data_module=DMODULE,
        )


load_iris.__doc__="""\
Load and return the iris dataset (classification).
The iris dataset is a classic and very easy multi-class classification
dataset.

Parameters
----------
return_X_y : bool, default=False
    If True, returns ``(data, target)`` instead of a BowlSpace object. See
    below for more information about the `data` and `target` object.
    .. versionadded:: 0.1.2
as_frame : bool, default=False
    If True, the data is a pandas DataFrame including columns with
    appropriate dtypes (numeric). The target is
    a pandas DataFrame or Series depending on the number of target columns.
    If `return_X_y` is True, then (`data`, `target`) will be pandas
    DataFrames or Series as described below.
    .. versionadded:: 0.1.2
(tag, data_names): None
    `tag` and `data_names` do nothing. just for API purpose and to allow 
    fetching the same data uing the func:`~watex.data.fetch_data` since the 
    latter already holds `tag` and `data_names` as parameters. 
Returns
-------
data : :class:`~watex.utils.Boxspace`
    Dictionary-like object, with the following attributes.
    data : {ndarray, dataframe} of shape (150, 4)
        The data matrix. If `as_frame=True`, `data` will be a pandas
        DataFrame.
    target: {ndarray, Series} of shape (150,)
        The classification target. If `as_frame=True`, `target` will be
        a pandas Series.
    feature_names: list
        The names of the dataset columns.
    target_names: list
        The names of target classes.
    frame: DataFrame of shape (150, 5)
        Only present when `as_frame=True`. DataFrame with `data` and
        `target`.
        .. versionadded:: 0.1.2
    DESCR: str
        The full description of the dataset.
    filename: str
        The path to the location of the data.
        .. versionadded:: 0.1.2
(data, target) : tuple if ``return_X_y`` is True
    A tuple of two ndarray. The first containing a 2D array of shape
    (n_samples, n_features) with each row representing one sample and
    each column representing the features. The second ndarray of shape
    (n_samples,) containing the target samples.
    .. versionadded:: 0.18
    
Notes
-----
    .. versionchanged:: 0.1.1
        Fixed two wrong data points according to Fisher's paper.
        The new version is the same as in R, but not as in the UCI
        Machine Learning Repository.
Examples
--------
Let's say you are interested in the samples 10, 25, and 50, and want to
know their class name.
>>> from watex.datasets import load_iris
>>> data = load_iris()
>>> data.target[[10, 25, 50]]
array([0, 0, 1])
>>> list(data.target_names)
['setosa', 'versicolor', 'virginica']
"""    
    
    
    
    
    
    
    
    
    
    
    
