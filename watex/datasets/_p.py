# -*- coding: utf-8 -*-

"""
Make Dataset 
===============

Automate the loading data

"""
import os 
from .load import loadBagoueDataset

from ..cases import  (
    BaseSteps, 
   ) 
from ..tools.mlutils import (
    dumpOrSerializeData
    )

__all__ = [
    '_X',
    '_y',
    '_X0',
    '_y0',
    '_XT',
    '_yT',
    '_Xc',
    '_Xp',
    '_yp',
    '_pipeline',
    '_df0',
    '_df1',
    '_conf_kws', 
    '_BAGDATA'
  ] 

data_fn ='data/geodata/main.bagciv.data.csv'
if not os.path.isfile (data_fn): 
    data_fn = os.path.join (
            os.path.dirname ( 
                os.path.dirname (
                    os.path.dirname (__file__))
            ), 'data/geodata/main.bagciv.data.csv') 


if not os.path.isfile(data_fn): 
    data_fn= loadBagoueDataset ()
#-------------------------------------------------------------------------
# target or label name. 
nameoftarget ='flow'
# drop useless features
drop_features= ['num',
                'east', 
                'north',
                'name', 
                # 'lwi', 
                # 'type' 
                ]
# experiences attributes combinaisions 
add_attributes =False
# add attributes indexes to create a new features. 
attributesIndexes = [
                    (0, 1),
                    # (3,4), 
                    # (1,4), 
                    # (0, 4)
                    ] 
# categorize a features on the trainset or label 
feature_props_to_categorize =[
    ('flow', ([0., 1., 3.], ['FR0', 'FR1', 'FR2', 'FR3'])),
    ]
                        
# bring your own pipelines .if None, use default pipeline.
ownPipeline =None 
_conf_kws = {'tname':nameoftarget, 
            'drop_features':drop_features, 
            'add_attributes':add_attributes, 
            'attributesIndexes':attributesIndexes, 
            }
_conf_kws['feature_props_to_categorize']= feature_props_to_categorize
# createOnjects. 
# readfile and set dataframe
# hash equal to ``True`` to unsure data remain consistent even mutilple runs.
prepareObj =BaseSteps(
    # data = data_fn,
    drop_features = drop_features,
    categorizefeature_props = feature_props_to_categorize,
    tname=nameoftarget, 
    add_attributes = add_attributes, 
    attributes_ix = attributesIndexes, 
    hash=False
    )

prepareObj.stratifydata(data_fn ) 
_BAGDATA= prepareObj.data 
_X =prepareObj.X.copy()             # strafified training set 
_y =prepareObj.y.copy()             # stratified label 

prepareObj.fit_transform(_X, _y)

# --> Data sanitize but keep categorical features not encoded.
#   Text attributes not encoded remains safe. 
_X0 = prepareObj.X0          # cleaning and attr combined training set 
_y0= prepareObj.y0           # cleaning and attr combined label 

_Xp= prepareObj.X_prepared  # Train Set prepared 
_yp= prepareObj.y_prepared   # label encoded (prepared)
_Xc = prepareObj._Xpd                # training categorical ordinal encoded features.

_pipeline = prepareObj.pipeline 

_df0 = prepareObj._df0
_df1 = prepareObj._df1
#-------------------------------------------------------------------------    

# test set stratified data. Untouchable unless the best model is found.
_XT = prepareObj.X_
_yT= prepareObj.y_

#  keep the test sets safe using  `dumpOrSerializeData` 
# save the test set info in a savefile for the first run like::

if not os.path.isfile ('watex/etc/__Xy.pkl'): 
    train_data =(_Xp,_yp )
    dumpOrSerializeData(_BAGDATA, filename ='__Xy.pkl', to='joblib', 
                              savepath='watex/etc')
if not os.path.isfile('watex/etc/__XTyT.pkl'): 
    test_data=(_XT, _yT)
    dumpOrSerializeData(test_data, filename ='__XTyT.pkl', to='joblib', 
                          savepath='watex/etc')