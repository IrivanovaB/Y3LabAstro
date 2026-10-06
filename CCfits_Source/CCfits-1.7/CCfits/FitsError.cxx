//   Read the documentation to learn more about C++ code generator
//   versioning.
//	This is version 1.7 release dated June 2007
//	Astrophysics Science Division,
//	NASA/ Goddard Space Flight Center
//	HEASARC
//	http://heasarc.gsfc.nasa.gov
//	e-mail: ccfits@legacy.gsfc.nasa.gov
//
//	Original author: Ben Dorman, L3-Communications EER Systems Inc.
#ifdef _MSC_VER
#include "MSconfig.h" // for truncation warning
#include <cassert>
#endif

// FitsError
#include "FitsError.h"
// FITS
#include "FITS.h"


namespace CCfits {

  // Class CCfits::FitsError 

  FitsError::FitsError (int errornum, bool silent)
  : FitsException("FITS Error: ", silent)
  {
  if (FITS::verboseMode() || !silent) printMsg(errornum);
  }


  void FitsError::printMsg (int error)
  {
  char message[FLEN_ERRMSG];


  fits_get_errstatus(error, message);
  std::cerr << message << "\n";
  }

  // Class CCfits::FitsException 

  FitsException::FitsException (const string& msg, bool& silent)
  {
  if (FITS::verboseMode() || !silent) 
  {
          std::cerr << '\n' << msg;
          // set this to false for the purpose of this exception.
          // does NOT change verbose mode setting so this value is thrown
          // away after the exception completes.
          silent = false;
  }
  }


  // Class CCfits::FitsFatal 

  FitsFatal::FitsFatal (const string& diag)
  {
     std::cerr << "*** CCfits Fatal Error: " << diag 
               << " please report this to xanprob@olegacy.gsfc.nasa.gov\n";

#ifdef TERMINATE_DEFECT
     // terminate() is not there as documented
	 assert ( false );
#else
	 std::terminate();
#endif
  }


} // namespace CCfits
