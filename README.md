# WATex : WATer exploration using AI Learning Methods

[![Build Status](https://travis-ci.com/WEgeophysics/watex.svg?branch=master)](https://travis-ci.com/WEgeophysics/watex) ![Requires.io (branch)](https://img.shields.io/requires/github/WEgeophysics/watex/master?style=flat-square) ![GitHub](https://img.shields.io/github/license/WEgeophysics/watex?color=blue&label=Licence&style=flat-square) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4896758.svg)](https://doi.org/10.5281/zenodo.4896758)


**_Special toolbox for WATer EXploration  using Artificial Intelligence Learning methods_**

## Overview

* **Definition** 


 **WATex**has three main objectives. Firstly, it's an exploration open source software using AI learning methods like for water exploration like underground water research,
 and secondly intend to supply drinking water for regions faced to water scarcity  by predicting flow rate (FR) before  drilling to 
 to limit the failures drillings and dry boreholes. The third objective involves water sanitation for population welfare by bringing a piece of solution of their daily problems.
 The latter goal should not be developped for the first realease. 
 
* **Purpose** 
 
 **WATex** is developed to  indirectly participate of [Sustanaible Development Goals N6](https://www.un.org/sustainabledevelopment/development-agenda/) achievement which is  `Ensure access to water and sanitation for all`.
 Designing **WATex** using AI lerning methods such as **SVM, KNN, DTC** for supervided learning and **ANN** for unsupervided lerning (not work yet) has double goals. On the one hand,
 it’s used to predict the different FR classes from an upstream geoelectrical features analysis.
 On the other hand, it contributes to select the best anomaly presumed to give a  suitable FR according
 to the type of hydraulic required for the targeted population. 
 
 * **Target** 
 
 The development of **WATex** targets  [AMCOW](https://amcow-online.org/initiatives/amcow-pan-african-groundwater-program-apagrop), [UNICEF](https://www.unicef.org/), [WHO](https://www.who.int/) and 
 governments and geophysical local firms during the Drinking water supply campaigns. 
 Working  with **SVM** to create a _composite estimator (CE-SVC)_ could minimize the risk of dry boreholes and failure drillings 
 using *electrical resistivity profile ( ERP)*  and * vertical electrical sounding (VES)* considered as less expensive geophysical  methods. 
 Minimizing the risk of dry boreholes and failure drillings  lead for  affordable  project budget elaboration during the water campaigns 
 in term of funding-raise from partners and organizations aids. 

* **Note** 

Actually **WATex** works with _Support Vector Machines([SVMs](https://www.csie.ntu.edu.tw/~cjlin/libsvm/)) and the developement with pure Python is still ongoing. 
Other AI algorithms implemented will be add as things progress. To handle some fonctionalities before the full development, please refer to `.checkpoints ` folder.
 
## Units used 

1. Apparent resistivity `_rhoa_` in ohm.meter 
2. Standard fracture index `sfi`  , no unit(n.u) 
3. Anomaly ratio `anr` ,  in %
4. Anomaly power *Pa* or `power`  in meter(m) 
5. Anomaly magnitude *Ma* or `magnitude` in ohm.m 
6. Anomaly shape - can be `_V, M, K, L, H, C, V_` and `_W_` (n.u). 
7. Anomaly type - can be `_EC, NC, CB2P_* and *_PC_` (n.u)
8. Layer thickness `_thick_` in m. 
9. Ohmic surface `_OhmS_` in ohm.m2 
10. Station( site) or position is given as `_pk_` in m.

## How to get the geo-electrical features from selected anomaly point ?

**Geo-electrical features** are mainly used FR prediction purposes. 
 Beforehand, we refer  to the  data directory `data\erp` accordingly for this demonstration. 
 The 'ERP' data of survey line  is found on `l10_gbalo.csv`. There are two ways to get **Geolectrical features**. 
 The first option  is to provide the selected anomaly boundaries into the argument ` posMinMax` and 
  the seccond way is to let program  find automatically the *the best anomaly point*. The first option is strongly recommended. 

 Fist of all , try to import the module _ERP_ from ` watex.core.erp.ERP`  and build `erp_obj`
 as follow: 
```
>>> from watex.core.erp import ERP 
>>> erp_obj =ERP (erp_fn = data/erp/l10_gbalo.csv',  # erp_data 
...                auto=False,                          # automatic computation  option 
...                dipole_length =10.,                 # distance between measurements 
...                posMinMax= (90, 130),               # select anomaly boundaries 
...                 turn_on =True                      # display infos
                 )
```
 - To get the _best anomaly_ point from the 'erp_line' if `auto` option is enabled : 
```
>>> erp_obj.select_best_point_ 
Out[1]: 170 
-----------------------------------------------------------------------------
--|> The best point is found  at position (pk) = 170.0 m. ----> Station 18              
-----------------------------------------------------------------------------

>>> erp_obj.select_best_value_ 
Out[1]: 80.0
-----------------------------------------------------------------------------
--|> Best conductive value selected is = 80.0 Ω.m                    
-----------------------------------------------------------------------------
```
- To get the next geo-electrical features, considered the _prefix_`abest_+ {feature_name}`. 
For instance :

```
>>> erp_obj.abest_type         # Type of the best selected anomaly on erp line
Out[3]:  CB2P                  # is  contact between two planes "CB2P". 
>>> erp_obj.abest_shape         
Out[4]: V                       # Best selected anomaly shape is "V"
>>> erp_obj.abest_magnitude    
Out[5]: 45                     # Best anomaly magnitude IS 45 Ω.m. 
>>> erp_obj.abest_power         
Out[6]: 40.0                    # Best anomaly power is 40.0 m. 
>>> erp_obj.abest_sfi          
Out[7]: 1.9394488747363936      # best anomaly standard fracturation index.
>>> erp_obj.abest_anr           # best anomaly ration the whole ERP line.
Out[8]: 50.76113145430543 % 
```
- If `auto` is enabled, the program could find additional maximum three best 
conductive points from the whole  ERP line as : 
```
>>> erp_obj.best_points 
-----------------------------------------------------------------------------
--|> 3 best points was found :
 01 : position = 170.0 m ----> rhoa = 80 Ω.m
 02 : position = 80.0 m ----> rhoa = 95 Ω.m
 03 : position = 40.0 m ----> rhoa = 110 Ω.m               
-----------------------------------------------------------------------------
```

## System requirements 
* Python 3.7+ 

## Contributors
  
1. Key Laboratory of Geoscience Big Data and Deep Resource of Zhejiang Province , School of Earth Sciences, Zhejiang University, China
2. Laboratoire de Géophysique Appliquée, UFR des Sciences de la Terre et des Ressources Minières, Université Félix Houphouët-Boigny, Cote d'Ivoire

* Developer's name:  [_Kouadio K. Laurent_](kkouao@zju.edu.cn), _etanoyau@gmail.com_: [1](http://www.zju.edu.cn/english/), [2](https://www.univ-fhb.edu.ci/index.php/ufr-strm/)
* Contibutors' names:
    *  [_Binbin MI_](mibinbin@zju.edu.cn) : [1](http://www.zju.edu.cn/english/)



	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
