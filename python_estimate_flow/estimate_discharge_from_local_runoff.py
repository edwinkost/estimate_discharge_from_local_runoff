#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys
import shutil
import datetime

import pcraster as pcr

from pcraster.framework import DynamicModel
from pcraster.framework import DynamicFramework

from currTimeStep import ModelTime

import ncConverter as netcdf_writer
import virtualOS as vos

#~ from pcrglobwb import PCRGlobWB

import logging
logger = logging.getLogger(__name__)

class DeterministicRunner(DynamicModel):

    def __init__(self, modelTime, output_folder, totat_runoff_input_file):
        DynamicModel.__init__(self)

        self.modelTime = modelTime
        
        # netcdf input files - based on PCR-GLOBWB output
        # - total runoff (m/month)
        self.totat_runoff_input_file = "/scratch-shared/edwin/05min_runs_for_gmd_paper_30_oct_2017/05min_runs_4LCs_accutraveltime_cru-forcing_1958-2015/non-natural_starting_from_1958/merged_1958_to_2015/totalRunoff_monthTot_output_1958-01-31_to_2015-12-31.nc"
        self.totat_runoff_input_file = totat_runoff_input_file
        #
        #~ # - discharge (m3/s) - NOT USED anymore
        #~ self.discharge_input_file    = "/scratch-shared/edwin/05min_runs_for_gmd_paper_30_oct_2017/05min_runs_4LCs_accutraveltime_cru-forcing_1958-2015/non-natural_starting_from_1958/merged_1958_to_2015/discharge_monthAvg_output_1958-01-31_to_2015-12-31.nc"

        # output files - in netcdf format
        self.total_flow_output_file    = output_folder + "/total_flow.nc"
        self.internal_flow_output_file = output_folder + "/internal_flow.nc" 
        # - all will have unit m3/s

        # preparing temporary directory
        self.temporary_directory = output_folder + "/tmp/"
        os.makedirs(self.temporary_directory)
        
        # clone map
        logger.info("Set the clone map")
        self.clonemap_file_name = "/home/edwinvua/github/edwinkost/estimate_discharge_from_local_runoff/making_subcatchment_map/version_20180202/clone_version_20180202.map"
        pcr.setclone(self.clonemap_file_name)
        
        # pcraster input files
        landmask_file_name      = None
        # - river network map and sub-catchment map
        ldd_file_name           = "/projects/0/dfguu/data/hydroworld/PCRGLOBWB20/input5min/routing/lddsound_05min.map"
        sub_catchment_file_name = "/home/edwinvua/github/edwinkost/estimate_discharge_from_local_runoff/making_subcatchment_map/version_20180202/subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map"
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
        self.cell_area     = vos.readPCRmapClone(cell_area_file_name, \
                                                 self.clonemap_file_name, \
                                                 self.temporary_directory, \
                                                 None)

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
        self.netcdf_report.createNetCDF(self.total_flow_output_file,\
                                        "total_flow",\
                                        "m3/s")
        self.netcdf_report.createNetCDF(self.internal_flow_output_file,\
                                        "internal_flow",\
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
            self.total_runoff = pcr.cover(self.total_runoff, 0.0)
            
            logger.info("Calculating total inflow and internal inflow for time %s", self.modelTime.currTime)
            self.total_flow    = pcr.catchmenttotal(self.total_runoff * self.cell_area, self.ldd_network)
            self.internal_flow = pcr.areatotal(self.total_runoff  * self.cell_area, self.sub_catchment)
            # - convert values to m3/s
            number_of_days_in_a_month = self.modelTime.day
            self.total_flow         = self.total_flow    / (number_of_days_in_a_month * 24. * 3600.)
            self.internal_flow      = self.internal_flow / (number_of_days_in_a_month * 24. * 3600.)
            # - limit the values to the landmask only
            self.total_flow         = pcr.ifthen(self.landmask, self.total_flow)
            self.internal_flow      = pcr.ifthen(self.landmask, self.internal_flow)
            
            logger.info("Extrapolating or time %s", self.modelTime.currTime)
            # Purpose: To avoid missing value data while being extracted by cdo command
            self.total_flow         = pcr.cover(self.total_flow,    pcr.windowmaximum(self.total_flow,    0.125)) 
            self.internal_flow      = pcr.cover(self.internal_flow, pcr.windowaverage(self.internal_flow, 0.125)) 

            # reporting 
            # - time stamp for reporting
            timeStamp = datetime.datetime(self.modelTime.year,\
                                          self.modelTime.month,\
                                          self.modelTime.day,\
                                          0)
            logger.info("Reporting for time %s", self.modelTime.currTime)
            self.netcdf_report.data2NetCDF(self.total_flow_output_file, \
                                           "total_flow", \
                                           pcr.pcr2numpy(self.total_flow, vos.MV), \
                                           timeStamp)
            self.netcdf_report.data2NetCDF(self.internal_flow_output_file, \
                                           "internal_flow", \
                                           pcr.pcr2numpy(self.internal_flow, vos.MV), \
                                           timeStamp)


def main():

    # the output folder from this calculation
    output_folder = "/scratch-shared/edwinvua/data_for_diede/netcdf_process/climatology_average/"
    output_folder = sys.argv[1]

    # totat_runoff_input_file
    totat_runoff_input_file = "/scratch-shared/edwinvua/data_for_diede/flow_scenarios/climatology_average_totalRunoff_monthTot_output_1979-2015.nc"
    totat_runoff_input_file = sys.argv[2]
    
    # timeStep info: year, month, day, doy, hour, etc
    start_date = "2015-01-01"
    end_date   = "2015-12-31"
    start_date = sys.argv[3]
    end_date   = sys.argv[4]
    #
    currTimeStep = ModelTime() 
    currTimeStep.getStartEndTimeSteps(start_date, end_date)
    
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
    
    
    # Running the deterministic_runner
    logger.info('Starting the calculation.')
    deterministic_runner = DeterministicRunner(currTimeStep, output_folder, totat_runoff_input_file)
    dynamic_framework = DynamicFramework(deterministic_runner,currTimeStep.nrOfTimeSteps)
    dynamic_framework.setQuiet(True)
    dynamic_framework.run()

if __name__ == '__main__':
    sys.exit(main())
