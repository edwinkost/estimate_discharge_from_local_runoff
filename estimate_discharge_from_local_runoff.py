#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys

from pcraster.framework import DynamicModel
from pcraster.framework import DynamicFramework

from configuration import Configuration
from currTimeStep import ModelTime
from reporting import Reporting
from spinUp import SpinUp

#~ from pcrglobwb import PCRGlobWB

import logging
logger = logging.getLogger(__name__)
# TODO: Improve this logging

class DeterministicRunner(DynamicModel):

    def __init__(self, modelTime):
        DynamicModel.__init__(self)

        self.modelTime = modelTime
        
        # clone and landmask maps
        self.landmask_file_name = 
        self.clonemap_file_name = self.landmask_file_name
        pcr.setclone(self.clonemap_file_name)
        self.landmask = pcr.readmap(self.landmask_file_name)
        
        # input files
        self.nc_file_of_pcrglobwb_water_bodies = 
        
        #~ # a table files from Will: unique_id_used ; will_station_id ; grand_id_from_will ; lat_from_will ; lon_from_will ; year_from_will        
        
    def initial(self): 
        pass

    def dynamic(self):

        # re-calculate current model time using current pcraster timestep value
        self.modelTime.update(self.currentTimeStep())

        # read power station locations - based on the table from Will
        # - for the ones with GRAND ids:
        #   * correct their locations based on our GRAND database and read our GRAND parameters
        #   * for the 
        # - make sub-catchment maps 
        self.sub_catchment_ids = 
        
        # calculate total inflow and internal inflow values 
        self.total_runoff    = 
        self.total_inflow    = pcr.areatotal()
        self.internal_inflow = pcr.catchmenttotal()
        
        # do any needed reporting in netcdf files for this time step        
        # - annual_resolution : unique_id_used ; will_station_id ; grand_id ; lat_from_will ; lon_from_will ; year_from_will ; year_from_pcrglobwb 
        # - monthly resolution: unique_id_used ; total_inflow ; internal_inflow 
        
        self.reporting.report()

def main():

    # TODO: Define the logger

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
    # print disclaimer
    disclaimer.print_disclaimer(with_logger = True)
    sys.exit(main())
