#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys
import shutil

from pcraster.framework import DynamicModel
from pcraster.framework import DynamicFramework

from currTimeStep import ModelTime

import ncConverter as netcdf_writer

#~ from pcrglobwb import PCRGlobWB

import logging
logger = logging.getLogger(__name__)

class DeterministicRunner(DynamicModel):

    def __init__(self, modelTime, output_folder = "."):
        DynamicModel.__init__(self)

        self.modelTime = modelTime
        
        # netcdf input files - based on PCR-GLOBWB output
        # - total runoff (m/day)
        self.totat_runoff_input_file = "/scratch-shared/edwinhs/runs_2017_july_aug_finalizing_4LCs/05min_runs/05min_runs_4LCs_accutraveltime_cru-forcing_1958-2015/non-natural_starting_from_1958/merged_1958_to_2015/totalRunoff_monthTot_output_1958-01-31_to_2015-12-31.nc"
        # - discharge (m3/s)
        self.discharge_input_file    = "/scratch-shared/edwinhs/runs_2017_july_aug_finalizing_4LCs/05min_runs/05min_runs_4LCs_accutraveltime_cru-forcing_1958-2015/non-natural_starting_from_1958/merged_1958_to_2015/discharge_monthAvg_output_1958-01-31_to_2015-12-31.nc"

        # output files - in netcdf format
        self.total_inflow_output_file    = output_folder + "/total_inflow.nc"
        self.internal_inflow_output_file = output_folder + "/internal_inflow.nc" 
        # - all will have unit m3/s

        # clone map
        logger.info("Set the clone map")
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
        self.netcdf_report = netcdf_writer.PCR2netCDF(self.clonemap_file_name)
        
        # preparing netcdf output files:
        # - for total inflow
        self.netcdf_report.createNetCDF(self.total_inflow_output_file,\
                                        "total_inflow",\
                                        "m3/s")
        self.netcdf_report.createNetCDF(self.internal_inflow_output_file,\
                                        "internal_inflow",\
                                        "m3/s")

    def initial(self): 
        pass

    def dynamic(self):

        # re-calculate current model time using current pcraster timestep value
        self.modelTime.update(self.currentTimeStep())

        # processing done only at the last day of the month
        if self.modelTime.isLastDayOfMonth():
            
            logger.info("Reading runoff for time %s", self.modelTime.currTime)
            self.total_runoff = vos.netcdf2PCRobjClone(self.totat_runoff_input_file, "total_runoff",\
                                                       str(self.modelTime.fulldate), 
                                                       useDoy = None,
                                                       cloneMapFileName = self.clonemap_file_name,\
                                                       LatitudeLongitude = True)

            logger.info("Calculating total inflow and internal inflow for time %s", self.modelTime.currTime)
            self.total_inflow    = pcr.catchmenttotal(self.total_runoff * self.cell_area, self.ldd_network)
            self.internal_inflow = pcr.areatotal(self.total_runoff  * self.cell_area, self.sub_catchment)
            # - convert values from m3/day to m3/s
            self.total_inflow    = pcr.catchmenttotal(self.total_runoff * self.cell_area, self.ldd_network)
            self.internal_inflow = pcr.areatotal(self.total_runoff  * self.cell_area, self.sub_catchment)
            
            # reporting 
            # - time stamp for reporting
            timeStamp = datetime.datetime(self.modelTime.year,\
                                          self.modelTime.month,\
                                          self.modelTime.day,\
                                          0)
            logger.info("Reporting for time %s", self.modelTime.currTime)
            self.netcdfObj.data2NetCDF(self.total_inflow_output_file, \
                                       "total_inflow", \
                                       pcr.pcr2numpy(self.total_inflow, vos.MV), \
                                       timeStamp)
            self.netcdfObj.data2NetCDF(self.internal_inflow_output_file, \
                                       "internal_inflow", \
                                       pcr.pcr2numpy(self.internal_inflow, vos.MV), \
                                       timeStamp)


def main():

    # the output folder from this calculation
    output_folder = "/scratch-shared/edwinhs/data_for_will/netcdf_process/"
    # - if exists, cleaning the previous output directory:
    if os.path.isdir(output_folder): shutil.rmtree(output_folder)
    # - making the output folder
    os.makedirs(output_folder)

    # logger
    # - making a log directory
    log_file_directory = output_folder + "/" + "log/"
    os.makedirs(log_file_directory)
    # - initialize logging
    vos.initialize_logging(log_file_directory)
    
    # timeStep info: year, month, day, doy, hour, etc
    currTimeStep = ModelTime() 
    currTimeStep.getStartEndTimeSteps(configuration.globalOptions['startTime'],
                                      configuration.globalOptions['endTime'])
    
    # Running the deterministic_runner (excluding DA scheme)
    logger.info('Starting the calculation.')
    deterministic_runner = DeterministicRunner(currTimeStep, output_folder)
    dynamic_framework = DynamicFramework(deterministic_runner,currTimeStep.nrOfTimeSteps)
    dynamic_framework.setQuiet(True)
    dynamic_framework.run()

if __name__ == '__main__':
    sys.exit(main())
