import ocgis
from ocgis.util.helpers import get_sorted_uris_by_time_dimension
from netCDF4 import Dataset

#from malleefowl import wpslogging as logging
import logging
logger = logging.getLogger(__name__)

_INDICES_ = dict(
    SU=dict(variable='tasmax', description='Nr of summer days (tasmax as input files)'),
    TG=dict(variable='tas', description='Mean of mean temperatur (tas as input files)'),
)

def indices():
    return _INDICES_.keys()

def indices_description():
    description = ''
    for indice in indices():
        description = description + "%s: %s\n" % (indice, _INDICES_[indice]['description'])
    return description

def indice_variable(indice):
    variable = None
    try:
        variable = _INDICES_[indice]['variable']
    except:
        logger.error('unknown indice %s', indice)
    return variable
        
def calc_indice(resources, indice="SU", grouping="year", out_dir=None):
    """
    Calculates given indice for variable and grouping.

    resources: single filename or list of filenames (netcdf)
    out_dir: output directory for result file (netcdf)

    result: netcdf files with calculated indices
    """

    ## ocgis.env.OVERWRITE = True
    ## ocgis.env.DIR_DATA = os.path.curdir
    ## ocgis.env.DIR_OUTPUT = outdir    
    ## output_crs = None
        
    calc_icclim = [{'func' : 'icclim_' + indice, 'name' : indice}]
    try:
        variable = indice_variable(indice)
        prefix = variable + '_' + indice
        rd = ocgis.RequestDataset(uri=_sort_by_time(resources), variable=variable) # TODO: time_range=[dt1, dt2]
        result = ocgis.OcgOperations(
            dataset=rd,
            calc=calc_icclim,
            calc_grouping=_calc_grouping(grouping),
            prefix=prefix,
            output_format='nc',
            dir_output=out_dir,
            add_auxiliary_files=False).execute()
    except:
        logger.exception('Could not calc indice %s with variable %s for file %s.', indice, variable, uri)

    return result

def _calc_grouping(grouping):
    calc_grouping = ['year'] # default year
    if grouping == 'sem':
        calc_grouping = [ [12,1,2], [3,4,5], [6,7,8], [9,10,11], 'unique'] 
    elif grouping in ['year', 'month']:
        calc_grouping = [grouping]
    else:
        msg = 'Unknown calculation grouping: %s' % grouping
        logger.error(msg)
        raise Exception(msg)
    return calc_grouping

def _sort_by_time(resources):
    if type(resources) is list:
        sorted_list = get_sorted_uris_by_time_dimension(resources)
    else:
        sorted_list = [resources]
    return sorted_list


