# -*- coding: utf-8 -*-
#   Licence:BSD 3-Clause
#   Author: LKouadio <etanoyau@gmail.com>
#   Created on Sat Sep 25 10:10:31 2021

from __future__ import annotations 
import os
import inspect
import warnings  
import pickle 
import joblib
from abc import ABC,abstractmethod,  ABCMeta  
from pprint import pprint 
import pandas as pd 
import numpy as np 

from .._watexlog import watexlog
from ..exlib.sklearn import (
     mean_squared_error,
     cross_val_score, 
     GridSearchCV , 
     RandomizedSearchCV, 
     LogisticRegression, 
     Pipeline,
)
from .._typing import (
    Tuple,
    List,
    Optional,
    F, 
    ArrayLike, 
    NDArray, 
    Dict,
    Any, 
    DataFrame, 
    Series,
    )
from ..exceptions import EstimatorError 
from ..utils.funcutils import ( 
    get_params, 
    _assert_all_types 
    )
from ..utils.validator import ( 
    check_X_y, 
    check_consistent_length, 
    get_estimator_name
    )

__logger = watexlog().get_watex_logger(__name__)


def get_best_kPCA_params(
        X:NDArray | DataFrame,
        n_components: float | int =2,
        *,
        y: ArrayLike | Series=None,
        param_grid: Dict[str, Any] =None, 
        clf: F =None,
        cv: int =7,
        **grid_kws
        )-> Dict[str, Any]: 
    """ Select the Kernel and hyperparameters using GridSearchCV that lead 
    to the best performance.
    
    As kPCA( unsupervised learning algorithm), there is obvious performance
    measure to help selecting the best kernel and hyperparameters values. 
    However dimensionality reduction is often a preparation step for a 
    supervised task(e.g. classification). So we can use grid search to select
    the kernel and hyperparameters that lead the best performance on that 
    task. By default implementation we create two steps pipeline. First reducing 
    dimensionality to two dimension using kPCA, then applying the 
    `LogisticRegression` for classification. AFter use Grid searchCV to find 
    the best ``kernel`` and ``gamma`` value for kPCA in oder to get the best 
    clasification accuracy at the end of the pipeline.
    
    Parameters
    ----------
   X:  Ndarray ( M x N matrix where ``M=m-samples``, & ``N=n-features``)
       Training set; Denotes data that is observed at training and 
       prediction time, used as independent variables in learning. 
       When a matrix, each sample may be represented by a feature vector, 
       or a vector of precomputed (dis)similarity with each training 
       sample. :code:`X` may also not be a matrix, and may require a 
       feature extractor or a pairwise metric to turn it into one  before 
       learning a model.
       
    n_components: Number of dimension to preserve. If`n_components` 
            is ranged between float 0. to 1., it indicated the number of 
            variance ratio to preserve. 
            
    y: array_like 
        label validation for supervised learning 
        
    param_grid: list 
        list of parameters Grids. For instance::
            
            param_grid=[{
                "kpca__gamma":np.linspace(0.03, 0.05, 10),
                "kpca__kernel":["rbf", "sigmoid"]
                }]
            
    clf: callable, 
        Can be base estimator or a composite estimor with pipeline. For 
        instance::
            
            clf =Pipeline([
            ('kpca', KernelPCA(n_components=n_components))
            ('log_reg', LogisticRegression())
            ])
            
    cv: int 
        number of K-Fold to cross validate the training set.
        
    grid_kws:dict
        Additional keywords arguments. Refer to 
        :class:`~watex.modeling.validation.GridSearch`
    
    Example
    -------
    >>> from watex.analysis.dimensionality import get_best_kPCA_params
    >>> from watex.datasets import fetch_data 
    >>> X, y=fetch_data('Bagoue analysis data')
    >>> param_grid=[{
        "kpca__gamma":np.linspace(0.03, 0.05, 10),
        "kpca__kernel":["rbf", "sigmoid"]
        }]
    >>> kpca_best_params =get_best_kPCA_params(
                    X,y=y,scoring = 'accuracy',
                    n_components= 2, clf=clf, 
                    param_grid=param_grid)
    >>> kpca_best_params
    ... {'kpca__gamma': 0.03, 'kpca__kernel': 'rbf'}
    
    """
    from ..analysis.dimensionality import ( 
        get_component_with_most_variance, KernelPCA) 
    if n_components is None: 
        n_components= get_component_with_most_variance(X)
    if clf is None: 

        clf =Pipeline([
            ('kpca', KernelPCA(n_components=n_components)),
            ('log_reg', LogisticRegression())
            ])
    gridObj =GridSearch(base_estimator= clf,
                        grid_params= param_grid, cv=cv,
                        **grid_kws
                        ) 
    gridObj.fit(X, y)
    
    return gridObj.best_params_

def get_scorers (): 
    """ Fetch the list of available metrics from scikit-learn. This is prior 
    necessary before  the model evaluation. 
    """
    from sklearn import metrics  
    return tuple(metrics.SCORERS.keys()) 

def multipleGridSearches(
        X: NDArray, 
        y:ArrayLike,
        estimators: F, 
        grid_params: Dict[str, Any],
        scoring:str  ='neg_mean_squared_error', 
        cv: int =7, 
        kindOfSearch:str ='GridSearchCV',
        random_state:int =42,
        save_to_joblib:bool =False,
        # get_metrics_SCORERS:bool =False, 
        verbose:int =0,
        **pkws
        )-> Tuple[F, F, Any]:
    """ Search and find multiples best parameters from differents
    estimators.
    
    Parameters
    ----------
    X: dataframe or ndarray
        Training set data.
        
    y: array_like 
        label or target data 
        
    estimators: list of callable obj 
        list of estimator objects to fine-tune their hyperparameters 
        For instance::
            
            estimators= (LogisticRegression(random_state =random_state), 
             LinearSVC(random_state =random_state), 
             SVC(random_state =random_state) )
            
    grid_params: list 
        list of parameters Grids. For instance:: 
            
            grid_params= ([
            {'C':[1e-2, 1e-1, 1, 10, 100], 'gamma':[5, 2, 1, 1e-1, 1e-2, 1e-3],
                         'kernel':['rbf']}, 
            {'kernel':['poly'],'degree':[1, 3,5, 7], 'coef0':[1, 2, 3], 
             'C': [1e-2, 1e-1, 1, 10, 100]}], 
            [{'C':[1e-2, 1e-1, 1, 10, 100], 'loss':['hinge']}], 
            [dict()]
            )
    cv: int 
        Number of K-Fold to cross validate the training set.
    scoring: str 
        Type of scoring to evaluate your grid search. Use 
        `sklearn.metrics.metrics.SCORERS.keys()` to get all the metrics used 
        to evaluate model errors. Default is `'neg_mean_squared_error'`. Can be 
        any others metrics `~metrics.metrics.SCORERS.keys()` of scikit learn.
        
    kindOfSearch:str
        Kinf of grid search. Can be ``GridSearchCV`` or ``RandomizedSearchCV``. 
        Default is ``GridSearchCV``.
        
    random_state: int 
        State to shuffle the cross validation data. 
    
    save_to_joblib: bool, 
        Save your model ad parameters to sklearn.external.joblib. 
        
    get_metrics_SCORERS: list 
        list of diferent metrics to evaluate the scores of the models. 
        
    verbose: int , level=0
        control the verbosity, higher value, more messages.
    
    Examples
    --------
    
    .../scripts/fine_tune_hyperparams.py
    """
    err_msg = (" Each estimator must have its corresponding grip params."
               " i.e estimators and grid param must have the same length."
               " Please provide the appropriate arguments.")
    # if get_metrics_SCORERS: 
    #     from sklearn import metrics 
    #     if verbose >0: 
    #         pprint(','.join([ k for k in metrics.SCORERS.keys()]))
            
    #     return tuple(metrics.SCORERS.keys())
    try: 
        check_consistent_length(estimators, grid_params)
    except ValueError as err : 
        raise ValueError (str(err) +f". {err_msg}")
    # if len(estimators)!=len(grid_params): 
    #     warnings.warn('Estimators and grid parameters must have the same .'
    #                   f'length. But {len(estimators)!r} and {len(grid_params)!r} '
    #                   'were given.'
    #                   )
    #     raise ValueError('Estimator and the grid parameters for fine-tunning '
    #                      'must have the same length. %s and %s are given.'
    #                      %(len(estimators),len(grid_params)))
    
    _clfs =list() ; _dclfs = dict() 
    # _dclfs=dict()
    msg =''
    pickfname= '__'.join([get_estimator_name(b) for b in estimators ])
    
    for j, estm_ in enumerate(estimators):
        msg = f'{get_estimator_name(estm_)} is evaluated.'
        searchObj = GridSearch(base_estimator=estm_, 
                                  grid_params= grid_params[j], 
                                  cv = cv, 
                                  kind=kindOfSearch, 
                                  scoring=scoring
                                  )
        searchObj.fit(X, y)
        best_model_clf = searchObj.best_estimator_ 
        
        if verbose >7 :
            msg+= ''.join([
                f'\End Gridsearch. Resetting {estm_.__class__.__name__}',
                ' `.best_params_`, `.best_estimator_`, `.cv_results` and', 
                ' `.feature_importances_` and grid_kws attributes\n'])

        _dclfs[f'{estm_.__class__.__name__}']= {
                                'best_model':searchObj.best_estimator_ ,
                                'best_params_':searchObj.best_params_ , 
                                'cv_results_': searchObj.cv_results_,
                                'grid_kws':searchObj.grid_kws,
                                'grid_param':grid_params[j],
                                'scoring':scoring
                                }
        
        msg +=''.join([ f' Cross evaluate with KFold ={cv} the',
                       ' {estm_.__class.__name__} best model.'])
        if verbose >7: display ='on'
        else :display='off'
        bestim_best_scores,_ = quickscoring_evaluation_using_cross_validation(
            best_model_clf, 
            X,
            y,
            cv = cv, 
            scoring = scoring,
            display =display)
        # store the best scores 
        _dclfs[f'{estm_.__class__.__name__}'][
            'best_scores']= bestim_best_scores
        # for k, v in dclfs.items():     
        _clfs.append((estm_,
                      searchObj.best_estimator_,
                      searchObj.best_params_, 
                      bestim_best_scores) )
    msg +=f'\Pretty print estimators results using scoring ={scoring!r}'
    if verbose >0:
        prettyPrinter(clfs=_clfs, scoring =scoring, 
                       clf_scores= None, **pkws )
    
        
    msg += f'\Serialize dict of parameters fine-tune to `{pickfname}`.'
    
    if save_to_joblib:
        __logger.info(f'Dumping models `{pickfname}`!')
        
        try : 
            joblib.dump(_dclfs, f'{pickfname}.pkl')
            # and later ....
            # f'{pickfname}._loaded' = joblib.load(f'{pickfname}.pkl')
            dmsg=f'Model `{pickfname} dumped using to ~.externals.joblib`!'
            
        except : 
            # piclke data Serializing data 
            with open(pickfname, 'wb') as wfile: 
                pickle.dump( _dclfs, wfile)
            # new_dclfs_infile = open(names,'rb')
            # new_dclfs= pickle.load(new_dclfs_infile)
            # new_dclfs_infile.close()
            
            pprint(f'Models are serialized  in `{pickfname}`. Please '
                   'refer to your current work directory.'
                   f'{os.getcwd()}')
            __logger.info(f'Model `{pickfname} serialized to {pickfname}.pkl`!')
            dmsg=f'Model `{pickfname} serialized to {pickfname}.pkl`!'
            
        else: __logger.info(dmsg)   
            
        if verbose >1: 
            pprint(
                dmsg + '\nTry to retrieve your model using`:meth:.load`'
                'method. For instance: slkearn --> joblib.load(f"{pickfname}.pkl")'
                'or pythonPickle module:-->pickle.load(open(f"{pickfname},"rb")).'
                )
            
    if verbose > 1:  
        pprint(msg)    
      
    return _clfs, _dclfs, joblib


def prettyPrinter(
        clfs: List[F],  
        clf_score:List[float]=None, 
        scoring: Optional[str] =None,
        **kws
 )->None: 
    """ Format and pretty print messages after gridSearch using multiples
    estimators.
    
    Display for each estimator, its name, it best params with higher score 
    and the mean scores. 
    
    Parameters
    ----------
    clfs:Callables 
        classifiers or estimators 
    
    clf_scores: array-like
        for single classifier, usefull to provided the 
        cross validation score.
    
    scoring: str 
        Scoring used for grid search.
    """
    empty =kws.pop('empty', ' ')
    e_pad =kws.pop('e_pad', 2)
    p=list()

    if not isinstance(clfs, (list,tuple)): 
        clfs =(clfs, clf_score)

    for ii, (clf, clf_be, clf_bp, clf_sc) in enumerate(clfs): 
        s_=[e_pad* empty + '{:<20}:'.format(
            clf.__class__.__name__) + '{:<20}:'.format(
                'Best-estimator <{}>'.format(ii+1)) +'{}'.format(clf_be),
         e_pad* empty +'{:<20}:'.format(' ')+ '{:<20}:'.format(
            'Best paramaters') + '{}'.format(clf_bp),
         e_pad* empty  +'{:<20}:'.format(' ') + '{:<20}:'.format(
            'scores<`{}`>'.format(scoring)) +'{}'.format(clf_sc)]
        try : 
            s0= [e_pad* empty +'{:<20}:'.format(' ')+ '{:<20}:'.format(
            'scores mean')+ '{}'.format(clf_sc.mean())]
        except AttributeError:
            s0= [e_pad* empty +'{:<20}:'.format(' ')+ '{:<20}:'.format(
            'scores mean')+ 'None']
            s_ +=s0
        else :
            s_ +=s0

        p.extend(s_)
    

    for i in p: 
        print(i)


class GridSearch: 
    """ Fine tune hyperparameters. 
    
    Search Grid will be able to  fiddle with the hyperparameters until to 
    find the great combination for model predictions. 
    
    Parameters 
    ------------
    base_estimator: list of callable object  
        Estimator to be fined tuned hyperparameters
    
    grid_params: list of dict, 
        list of hyperparamters params  to be fine-tuned 
    
    cv: int, 
        Cross validation sampling. Default is `4` 
    
    kind: str, default ='GridSearchCV'
        Kind of search. Could be ``'GridSearchCV'`` or
        ``RandomizedSearchCV``. Default is ``GridSearchCV``.
    
    scoring: str, default ='neg_mean_squared_error'
        Type of scorer for errors evaluating. 
    
    Example
    -----------
    >>> from pprint import pprint 
    >>> from watex.exlib.sklearn import RandomForestClassifier
    >>> from watex.datasets import fetch_data 
    >>> X_prepared, y_prepared =fetch_data ('bagoue prepared')
    >>> grid_params = [
    ...        {'n_estimators':[3, 10, 30], 'max_features':[2, 4, 6, 8]}, 
    ...        {'bootstrap':[False], 'n_estimators':[3, 10], 
    ...                             'max_features':[2, 3, 4]}]
    >>> forest_clf = RandomForestClassifier()
    >>> grid_search = GridSearch(forest_clf, grid_params)
    >>> grid_search.fit(X= X_prepared,y =  y_prepared,)
    >>> pprint(grid_search.best_params_ )
    >>> pprint(grid_search.cv_results_)
    """
    __slots__=(
        '_base_estimator',
        'grid_params', 
        'scoring',
        'cv', 
        '_kind', 
        'grid_kws', 
        'best_params_',
        'best_estimator_',
        'cv_results_',
        'feature_importances_',
    )
               
    def __init__(
            self,
            base_estimator:F,
            grid_params:Dict[str,Any],
            cv:int =4,
            kind:str ='GridSearchCV',
            scoring:str = 'neg_mean_squared_error',
            **grid_kws
            ): 
        
        self._base_estimator = base_estimator 
        self.grid_params = grid_params 
        self.scoring = scoring 
        self.cv = cv 
        self._kind = kind 
        
        self.best_params_ =None 
        self.cv_results_= None
        self.feature_importances_= None
        self.best_estimator_=None 
        self.grid_kws = grid_kws 

    @property 
    def base_estimator (self): 
        """ Return the base estimator class"""
        return self._base_estimator 
    
    @base_estimator.setter 
    def base_estimator (self, base_est): 
        if not hasattr (base_est, 'fit'): 
            raise EstimatorError(
                f"Wrong estimator {get_estimator_name(base_est)!r}. Each"
                " estimator must have a fit method. Refer to scikit-learn"
                " https://scikit-learn.org/stable/modules/classes.html API"
                " reference to build your own estimator.") 

        self._base_estimator =base_est 
        
    @property 
    def kind(self): 
        """ Kind of searched. `RandomizedSearchCV` or `GridSearchCV`."""
        return self._kind 
    
    @kind.setter 
    def kind (self, ksearch): 
        """`kind attribute checker"""
        if 'gridsearchcv1'.find( str(ksearch).lower())>=0: 
            ksearch = 'GridSearchCV' 
        elif 'randomizedsearchcv2'.find( str(ksearch).lower())>=0:
            ksearch = 'RandomizedSearchCV'
            
        else: raise ValueError (
            " Unkown the kind of parameter search {ksearch!r}."
            " Supports only 'GridSearchCV' and 'RandomizedSearchCV'.")
        self._kind = ksearch 

    def fit(self,  X, y): 
        """ Fit method using base Estimator and populate gridSearch 
        attributes.
 
        Parameters
        ----------
        X:  Ndarray ( M x N matrix where ``M=m-samples``, & ``N=n-features``)
            Training set; Denotes data that is observed at training and 
            prediction time, used as independent variables in learning. 
            When a matrix, each sample may be represented by a feature vector, 
            or a vector of precomputed (dis)similarity with each training 
            sample. :code:`X` may also not be a matrix, and may require a 
            feature extractor or a pairwise metric to turn it into one  before 
            learning a model.
        y: array-like, shape (M, ) ``M=m-samples``, 
            train target; Denotes data that may be observed at training time 
            as the dependent variable in learning, but which is unavailable 
            at prediction time, and is usually the target of prediction. 

        Returns
        -------
        ``self``: `GridSearch`
            Returns :class:`~.GridSearchCV` 
    
        """
        if callable (self.base_estimator): 
            baseEstimatorObj = self.base_estimator () 
            parameters = get_params (baseEstimatorObj.__init__)
            
            if self.verbose >0: 
                msg = ("Estimator {!r} is cloned with default arguments{!r}"
                       " for cross validation search.".format(
                           get_estimator_name (baseEstimatorObj), parameters)
                       )
                warnings.warn(msg)
                
        if self.kind =='GridSearchCV': 
            searchMethod = GridSearchCV 
        elif self.kind=='RandomizedSearchCV': 
            searchMethod= RandomizedSearchCV 
            
        gridObj = searchMethod(
            baseEstimatorObj, 
            self.grid_params,
            scoring = self.scoring , 
            cv = self.cv,
            **self.grid_kws
            )
        gridObj.fit(X,y)
        
        for param , param_value in zip(
                ['best_params_','best_estimator_','cv_results_'],
                [gridObj.best_params_, gridObj.best_estimator_, 
                             gridObj.cv_results_ ]
                             ):
            setattr(self, param, param_value)
        try : 
            attr_value = gridObj.best_estimator_.feature_importances_
        except AttributeError: 
            warnings.warn ('{0} object has no attribute `feature_importances_`'.
                           format(gridObj.best_estimator_.__class__.__name__))
            setattr(self,'feature_importances_', None )
        else : 
            setattr(self,'feature_importances_', attr_value)
 
        return self
    

class BaseEvaluation (object): 
    """ Evaluation of dataset using a base estimator.
    
    Quick evaluation after data preparing and pipeline constructions. 
    
    Parameters 
    -----------
    base_estimator: Callable,
        estimator for trainset and label evaluating; something like a 
        class that implements a fit methods. Refer to 
        https://scikit-learn.org/stable/modules/classes.html
        
    X:  Ndarray ( M x N matrix where ``M=m-samples``, & ``N=n-features``)
        Training set; Denotes data that is observed at training and 
        prediction time, used as independent variables in learning. 
        When a matrix, each sample may be represented by a feature vector, 
        or a vector of precomputed (dis)similarity with each training 
        sample. :code:`X` may also not be a matrix, and may require a 
        feature extractor or a pairwise metric to turn it into one  before 
        learning a model.
    y: array-like, shape (M, ) ``M=m-samples``, 
        train target; Denotes data that may be observed at training time 
        as the dependent variable in learning, but which is unavailable 
        at prediction time, and is usually the target of prediction. 
    
    s_ix: int, sampling index. 
        If given, will sample the `X` and `y`.  If ``None``, will sample the 
        half of the data. 
    columns: list of columns. Use to build dataframe `X` when `X` is 
        given as numpy ndarray. 
        
    pipeline: callable func 
        Transformer data and preprocessing. Refer to 
        https://scikit-learn.org/stable/modules/classes.html#module-sklearn.pipeline
        
    cv: int, 
        cross validation splits. Default is ``4``.
            
    """
   
    def __init__(
            self, 
            base_estimator: F,
            # X: NDArray, 
            # y:ArrayLike,
            cv: int =7,  
            pipeline: List[F]= None, 
            pprint: bool =True, 
            cvs: bool =True, 
            scoring: str ='neg_mean_squared_error',
            random_state: int=42, 
        ): 
        
        self._logging =watexlog().get_watex_logger(self.__class__.__name__)
        
        self._base_estimator = base_estimator
        self.cv = cv 
        self.pipeline =pipeline
        self.pprint =pprint 
        self.cvs = cvs
        self.scoring = scoring
        self.random_state=random_state
 
        
        # for key in list(kwargs.keys()): 
        #     setattr(self, key, kwargs[key])

        # if self.X is not None : 
        #     self.quickEvaluation()
    @property 
    def base_estimator (self): 
        return self._base_estimator 
    
    @base_estimator.setter 
    def base_estimator (self, base_est): 
        if not hasattr (base_est, 'fit'): 
            raise EstimatorError(
                f"Wrong estimator {get_estimator_name(base_est)!r}. Each"
                " estimator must have a fit method. Refer to scikit-learn"
                " https://scikit-learn.org/stable/modules/classes.html API"
                " reference to build your own estimator.") 
            
        if callable (base_est): 
            base_est = base_est ()
            
        self._base_estimator =base_est 
         
    def fit(self, X, y,  prefit=False, sample_weight= 1. ): 
        
        """ Quick methods used to evaluate eastimator, display the 
        error results as well as the sample model_predictions.
        
        Parameters 
        -----------
        base_estimator: Callable,
            estimator for trainset and label evaluating; something like a 
            class that implements a fit methods. Refer to 
            https://scikit-learn.org/stable/modules/classes.html
            
        X:  Ndarray ( M x N matrix where ``M=m-samples``, & ``N=n-features``)
            Training set; Denotes data that is observed at training and 
            prediction time, used as independent variables in learning. 
            When a matrix, each sample may be represented by a feature vector, 
            or a vector of precomputed (dis)similarity with each training 
            sample. :code:`X` may also not be a matrix, and may require a 
            feature extractor or a pairwise metric to turn it into one  before 
            learning a model.
        y: array-like, shape (M, ) ``M=m-samples``, 
            train target; Denotes data that may be observed at training time 
            as the dependent variable in learning, but which is unavailable 
            at prediction time, and is usually the target of prediction. 
        
        s_ix: int, sampling index. 
            If given, will sample the `X` and `y`.  If ``None``, will sample the 
            half of the data.
            
        :param X: Dataframe  be trained.
        
        :param y: labels from trainset.
        
        :param sample_ix: index to sample in the trainset and labels. 
        
        :param kws: Estmator additional keywords arguments. 
        
        :param fit: Fit the method for quick estimating. Default is ``yes`` 
            
        """ 
        X, y = check_X_y ( 
            X,
            y, 
            to_frame =True, 
            estimator= get_estimator_name(self._base_estimator)
            )
        
        self._logging.info (
            'Quick estimation using the %r estimator with config %r arguments %s.'
                %(repr(self.base_estimator),self.__class__.__name__, 
                inspect.getfullargspec(self.__init__)))

        sample_weight = float(
            _assert_all_types(int, float, objname ="Sample weight"))
        if sample_weight <= 0 or sample_weight >1: 
            raise ValueError ("Sample weight must be range between 0 and 1,"
                              f" got {sample_weight}")
        
        n = int ( sample_weight * len(X)) 
        if hasattr (X, 'columns'): X = X.iloc [:n] 
        else : X=X[:n, :]
        y = y[:n]
        # if self.s_ix is not None: 
        #     if isinstance(self.X, pd.DataFrame): 
        #         self.X= self.X.iloc[: int(self.s_ix)]
        #     elif isinstance(self.X, np.ndarray): 
        #         if self.columns is None:
        #             warnings.warn(
        #                 f'{self.columns!r} must be a dataframe columns!'
        #                   f' not {type(self.columns)}.',UserWarning)
                    
        #             if self.X.ndim ==1 :
        #                 size =1 
        #             elif self.X.ndim >1: 
        #                 size = self.X.shape[1]
                    
        #             return TypeError(f'Expected {size!r} column name'
        #                               '{"s" if size >1 else 1} for array.')

        #         elif self.columns is not None: 
        #             if self.X.shape[1] !=len(self.columns): 
        #                 warnings.warn(f'Expected {self.X.shape[1]!r}' 
        #                               f'but {len(self.columns)} '
        #                               f'{"is" if len(self.columns) < 2 else"are"} '
        #                               f'{len(self.columns)!r}.',RuntimeWarning)
         
        #                 raise IndexError('Expected %i not %i self.columns.'
        #                                   %(self.X.shape[2], 
        #                                     len(self.columns)))
                        
        #             self.X= pd.DataFrame(self.X, self.columns)
                    
        #         self.X= self.X.iloc[: int(self.s_ix)]
    
        #     self.y= self.y[:int(self.s_ix )]  
    
        # if isinstance(self.y, pd.Series): 
        #     self.y =self.y.values 
   
        if not prefit: 
            self.fit_data(
                self.base_estimator , pprint= self.pprint, compute_cross=self.cvs,
                          scoring = self.scoring
                          )
            
            
    def fit_data (self, obj , pprint=True, compute_cross=True, 
                  scoring ='neg_mean_squared_error' ): 
        """ Fit data once verified and compute the ``rmse`` scores.
        
        :paramm obj: base estimator with base params.
        
        :param pprint: Display prediction of the quick evaluation.
        
        :param compute_cross: compute the cross validation.
        
        :param scoring: Type of scoring for cross validation. Please refer to  
                 :doc:`~.slkearn.model_selection.cross_val_score` for further 
                 details.
        """
        
        def display_scores(scores): 
            """ Display scores..."""
            print('scores:', scores)
            print('Mean:', scores.mean())
            print('rmse scores:', np.sqrt(scores))
            print('standard deviation:', scores.std())
            
        self._logging.info('Fit data X with shape {X.shape!r}.')
        
        if self.pipeline is not None: 
            train_prepared_obj =self.pipeline.fit_transform(self.X)
            
        elif self.pipeline is None: 
            warnings.warn('No Pipeline is applied. Could estimate with purely'
                          '<%r> given estimator.'%(self.base_estimator.__name__))
            self.logging.info('No Pipeline is given. Evaluation should be based'
                              'using  purely  the given estimator <%r>'%(
                                  self.base_estimator.__name__))
            
            train_prepared_obj =self.base_estimator.fit_transform(self.X)
        
        obj.fit(train_prepared_obj, self.y)
 
        if pprint: 
             print("predictions:\t", obj.predict(train_prepared_obj ))
             print("Labels:\t\t", list(self.y))
            
        y_obj_predicted = obj.predict(train_prepared_obj)
        
        obj_mse = mean_squared_error(self.y ,
                                     y_obj_predicted)
        self.rmse = np.sqrt(obj_mse )

        if compute_cross : 
            
            self.scores = cross_val_score(obj, train_prepared_obj,
                                     self.y, 
                                     cv=self.cv,
                                     scoring=self.scoring
                                     )
            
            if self.scoring == 'neg_mean_squared_error': 
                self.rmse_scores = np.sqrt(-self.scores)
            else: 
                self.rmse_scores = np.sqrt(self.scores)
    
            if pprint:
                if self.scoring =='neg_mean_squared_error': 
                    self.scores = -self.scores 
                display_scores(self.scores)   
    
class AttributeCkecker(ABC): 
    """ Check attributes and inherits from module `abc` for Data validators. 
    
    Validate DataType mainly `X` train or test sets and `y` labels or
    and any others params types.
    
    """
    def __set_name__(self, owner, name): 
        try: 
            self.private_name = '_' + name 
        except AttributeError: 
            warnings.warn('Object {owner!r} has not attribute {name!r}')
            
    def __get__(self, obj, objtype =None):
        return getattr(obj, self.private_name) 
    
    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value) 
        
    @abstractmethod 
    def validate(self, value): 
        pass 

class checkData (AttributeCkecker): 
    """ Descriptor to check data type `X` or `y` or else."""
    def __init__(self, Xdtypes):
        self.Xdtypes =eval(Xdtypes)

    def validate(self, value) :
        """ Validate `X` and `y` type."""
        if not isinstance(value, self.Xdtypes):
            raise TypeError(
                f'Expected {value!r} to be one of {self.Xdtypes!r} type.')
            
class checkValueType_ (AttributeCkecker): 
    """ Descriptor to assert parameters values. Default assertion is 
    ``int`` or ``float``"""
    def __init__(self, type_):
        self.six =type_ 
        
    def validate(self, value):
        """ Validate `cv`, `s_ix` parameters type"""
        if not isinstance(value,  self.six ): 
            raise ValueError(f'Expected {self.six} not {type(value)!r}')
   
class  checkClass (AttributeCkecker): 
    def __init__(self, klass):
        self.klass = klass 
       
    def validate(self, value): 
        """ Validate the base estimator whether is a class or not. """
        if not inspect.isclass(value): 
            raise TypeError('Estimator might be a class object '
                            f'not {type(value)!r}.')                
def quickscoring_evaluation_using_cross_validation(
        clf: F,
        X:NDArray,
        y:ArrayLike,
        cv:int =7,
        scoring:str  ='accuracy', 
        display: str ='off'
        ): 
    scores = cross_val_score(clf , X, y, cv = cv, scoring=scoring)
                         
    if display is True or display =='on':
        
        print('clf=:', clf.__class__.__name__)
        print('scores=:', scores )
        print('scores.mean=:', scores.mean())
    
    return scores , scores.mean()

quickscoring_evaluation_using_cross_validation.__doc__="""\
Quick scores evaluation using cross validation. 

Parameters
----------
clf: callable 
    Classifer for testing default data. 
X: ndarray
    trainset data 
    
y: array_like 
    label data 
cv: int 
    KFold for data validation.
    
scoring: str 
    type of error visualization. 
    
display: str or bool, 
    show the show on the stdout
    
Returns 
---------
scores, mean_core: array_like, float 
    scaore after evaluation and mean of the score
"""
# deprecated in scikit-learn 0.21 to 0.23 
# from sklearn.externals import joblib 
# import sklearn.externals    
    
    