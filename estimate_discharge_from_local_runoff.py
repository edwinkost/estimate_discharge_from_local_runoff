#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys

from pcraster.framework import DynamicModel
from pcraster.framework import DynamicFramework

from currTimeStep import ModelTime
from reporting import Reporting

#~ from pcrglobwb import PCRGlobWB

import logging
logger = logging.getLogger(__name__)

class DeterministicRunner(DynamicModel):

    def __init__(self, modelTime):
        DynamicModel.__init__(self)

        self.modelTime = modelTime
        
        # netcdf input files - based on PCR-GLOBWB output
        self.totat_runoff_input_file = "/scratch-shared/edwinhs/runs_2017_july_aug_finalizing_4LCs/05min_runs/05min_runs_4LCs_accutraveltime_cru-forcing_1958-2015/non-natural_starting_from_1958/merged_1958_to_2015/totalRunoff_monthTot_output_1958-01-31_to_2015-12-31.nc"
        self.discharge_input_file    = "/scratch-shared/edwinhs/runs_2017_july_aug_finalizing_4LCs/05min_runs/05min_runs_4LCs_accutraveltime_cru-forcing_1958-2015/non-natural_starting_from_1958/merged_1958_to_2015/discharge_monthAvg_output_1958-01-31_to_2015-12-31.nc"

        # output files - in netcdf format
        output_folder                    = 
        self.total_inflow_output_file    = output_folder + 
        self.internal_inflow_output_file = output_folder +  
        # - all will have unit m3/s


        # clone map
        self.clonemap_file_name = "/scratch-shared/edwinhs/data_for_will/subcatchment_maps/clone_version_20170824.map"
        pcr.setclone(self.clonemap_file_name)
        
        # pcraster input files
        landmask_file_name      = None
        # - river network map and sub-catchment map
        ldd_file_name           = "/projects/0/dfguu/data/hydroworld/PCRGLOBWB20/input5min/routing/lddsound_05min.map"
        sub_catchment_file_name = "/scratch-shared/edwinhs/data_for_will/subcatchment_maps/ subcatchments_of_reservoir_pcraster_ids.nom.bigger_than_zero.map"
        # - cell area (unit: m2)
        cell_area_file_name     = "/projects/0/dfguu/data/hydroworld/PCRGLOBWB20/input5min/routing/cellsize05min.correct.map"
        
        # loading pcraster input maps
        self.sub_catchment = vos.readPCRmapClone(sub_catchment_file_name, \
                                                 self.clonemap_file_name, \
                                                 self.temporary_directory, \
                                                 None, False, None, \
                                                 True)
        self.ldd_network   = vos.readPCRmapClone(ldd_file_name, \
                                                 self.clonemap_file_name, \
                                                 self.temporary_directory, \
                                                 None, \
                                                 True)
        self.ldd_network   = pcr.lddrepair(pcr.ldd(self.ldd_network))
        self.ldd_network   = pcr.lddrepair(self.ldd_network)

        # define the landmask
        self.landmask = pcr.defined(self.ldd_network)
        if landmask_file_name != None:
            self.landmask  = vos.readPCRmapClone(landmask_file_name, \
                                                 self.clonemap_file_name, \
                                                 self.temporary_directory, \
                                                 None)
        self.landmask = pcr.ifthen(pcr.defined(self.ldd_network), self.landmask)
        self.landmask = pcr.ifthen(self.landmask, self.landmask)
        
        # set/limit all input maps to the defined landmask
        self.sub_catchment = pcr.ifthen(self.landmask, self.sub_catchment)
        self.ldd_network   = pcr.ifthen(self.landmask, self.ldd_network)
        self.cell_area     = pcr.ifthen(self.landmask, self.cell_area)
        
        # preparing an object for reporting netcdf files:
        self.output = OutputNetcdf(mapattr_dict = self.output_netcdf,\
                                   cloneMapFileName = None,\
                                   netcdf_format = self.output_netcdf['format'],\
                                   netcdf_zlib = self.output_netcdf['zlib'],\
                                   netcdf_attribute_dict = self.output_netcdf['netcdf_attribute'],\
                                   netcdf_attribute_description = None)
        
        # preparing the netcdf file for total runoff
        self.output.createNetCDF(self.output_netcdf['file_name'],\
                                 self.output_netcdf['variable_name'],\
                                 self.output_netcdf['variable_unit'])


        # preparing a netcdf file for total runoff


        # preparing a netcdf file for internal inflow 


        # preparing a netcdf file for total runoff


    def initial(self): 
        pass

    def dynamic(self):

        # re-calculate current model time using current pcraster timestep value
        self.modelTime.update(self.currentTimeStep())

        # processing done only at the last day of the month
        if /
            # calculate total inflow and internal inflow values 
            self.total_runoff    = 
            self.total_inflow    = pcr.catchmenttotal(self.total_runoff, )
            self.internal_inflow = pcr.areatotal()
            # convert it 
        
            self.reporting.report()

def main():

    # TODO: Define the logger

    # TODO: Making output 
    
    # timeStep info: year, month, day, doy, hour, etc
    currTimeStep = ModelTime() 
    currTimeStep.getStartEndTimeSteps(configuration.globalOptions['startTime'],
                                      configuration.globalOptions['endTime'])
    
    # Running the deterministic_runner (excluding DA scheme)
    logger.info('Starting the calculation.')
    deterministic_runner = DeterministicRunner(configuration, currTimeStep)
    dynamic_framework = DynamicFramework(deterministic_runner,currTimeStep.nrOfTimeSteps)
    dynamic_framework.setQuiet(True)
    dynamic_framework.run()

if __name__ == '__main__':
    sys.exit(main())
