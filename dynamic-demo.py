#|==============================================================================
#|                      TOP OF FILE:    dynamic-demo.py
#|------------------------------------------------------------------------------
#|
#|      FILE NAME:  dynamic-demo.py         [Python application source code]
#|
#|      Initial development platform:
#|
#|          * Language:     Python 3.5.1 64-bit
#|          * OS:           Microsoft Windows 8.1 Professional (64-bit)
#|          * Processor:    Intel Xeon E5-2620 (64-bit)
#|
#|      Revision history:
#|
#|          6/21/16 (M. Frank) - Started writing initial version.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    #|--------------------------------------------------------------------------
    #|
    #|      RAW_DEBUG:bool                             [module global]
    #|
    #|          Raw debugging flag.  This is a very low-level
    #|          facility, preliminary to any more sophisticated
    #|          error-logging capability.  Just check this flag
    #|          before doing low-level diagnostic output.  This
    #|          allows all such diagnostic output to be
    #|          suppressed easily.
    #|
    #|          Please note that this is the only global that
    #|          appears before the "Globals" code sections, so
    #|          that we can begin using it right away.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

global RAW_DEBUG    # Declare this to be a module-level global.
RAW_DEBUG = False   # Change this to True as needed during initial development.

if RAW_DEBUG:
    print("Turned on raw debugging...")

if __name__ == "__main__":
    if RAW_DEBUG:
        print("__main__: Loading dynamic-demo.py...")

    #|==========================================================================
    #|
    #|   Imports					    [code section]
    #|
    #|       Load and import names of (and/or names from) various
    #|       other python modules and pacakges for use from the
    #|       present module.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|=================================================
	#|   Imports of standard python library modules.
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

if __name__ == "__main__":
    if RAW_DEBUG:
        print("__main__: Importing standard Python library modules...")
        
from sys import stderr

        #|================================================
	#|   Imports of our own custom modules.
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

if __name__ == "__main__": 
    if RAW_DEBUG:
        print("__main__: Importing custom application modules...", file=stderr)

import logmaster
from logmaster import configLogMaster,appLogger,info,normal
    # The logmaster module defines our logging framework; we import
    # several definitions that we need from it.

from appdefs import appName
    # Name of the present application.

from simulationContext import SimulationContext
    # Used for tracking global state of the simulation.

from exampleNetworks import ExampleNetwork_MemCell
    # The exampleNetworks module defines various simple example modules to be
    # used for development and testing.  ExampleNetwork_MemCell is a minimally-
    # simple example network to be used for initial development purposes.

    #|==========================================================================
    #|
    #|   Globals					    [code section]
    #|
    #|      Declare and/or define various global variables and
    #|      constants.
    #|
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

# These top-level global declarations verify that these names were
# not previously used, and also serve as documentation.

global  is_top

    #|==========================================================================
    #|
    #|   Module-level function definitions.                   [code section]
    #|
    #|
    #|       These functions are not part of any particular class.
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        #|======================================================================
        #|
        #|   _main()                                [module private function]
        #|
        #|      Main routine of module.
        #|
        #|      This routine is traditionally called within a module's main
        #|      body code, within the context of a conditional like
        #|
        #|           if __name__ == "__main__":
        #|
        #|      so it won't be automatically executed when this module is only
        #|      being imported as a sub-module of a larger system.
        #|
        #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def _main():
    
    if RAW_DEBUG:
        print("__main__.main(): Entered application's main routine...",
              file=stderr)

    if RAW_DEBUG:
        print("__main__.main(): Configuring the 'logmaster' logging module...",
              file=stderr)

    configLogMaster(loginfo = True, role = 'startup', component = appName)
        # Configure the logger to turn on log-file info output, set this
        # main thread's role to "startup" and set the thread component to
        # "demoApp".

    logger = appLogger  # Get our application logger.

    #logger.info('')
    #logger.info('='*80)
    logger.info("Dynamic demo application is starting up...")

    print()
    logger.normal("Welcome to the Dynamic demo program, v0.0.")
    logger.normal("Copyright (c)2016 by Michael P. Frank.")
    logger.normal("All Rights Reserved.")
    print()

    # Below follows the main code of the demo application.

        # First create a new simulation context object, initially empty.
        # This stores global parameters of the simulation (such as the
        # time delta value) and tracks global variables of the simulation
        # (such as the current time-step number).  We'll let it take its
        # default values for now.  At this point, the network to be
        # simulated has not been created yet.

    sc = SimulationContext()

        # Create an extremely simple example network for initial
        # testing during development.  Tell it that it's going to
        # be using that simulation context that we just created.

    logger.normal("Creating an ExampleNetwork_MemCell instance...")                
    net = ExampleNetwork_MemCell(context=sc)

    logger.debug("Initial node q momentum is: %f" % 
                  net._nodes['q'].coord.ccp._momVar.value)

    logger.normal("Requesting simulator to run a simple test...")
    
    logmaster.setThreadRole('running')
    
    sc.test()  # This method exercises some basic simulation capabilities.

    logmaster.setThreadRole('shutdown')

    logger.normal("Dynamic demo application is shutting down...")
    
    if RAW_DEBUG:
        print("__main__.main(): Exiting from main()...", file=stderr)

#--/ End function main().

    #|==========================================================================
    #|
    #|   Main script body.                                   [code section]
    #|
    #|      Above this section should only be definitions and
    #|      assignments.  Below is the main executable body of
    #|      the script.  It just calls the main() function (if
    #|      this script is not just being loaded as a submodule).
    #|  
    #|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    

if __name__ == "__main__":
    
    is_top = True   # For benefit of stuff called from within _main().

    if RAW_DEBUG:
        print("__main__: Top-level module is invoking main() routine of " +
              "application...", file=stderr)
        
    _main()
    
    if RAW_DEBUG:
        print("__main__: Application's main() routine has exited.",
              file=stderr)
        print("__main__: Exiting top-level module...",
              file=stderr)
        
else:
    
    if RAW_DEBUG:
        print("Finished recursive import of top-level module...")

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|                      END OF FILE:    dynamic-demo.py
#|==============================================================================
