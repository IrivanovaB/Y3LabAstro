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

#ifndef FITSBASE_H
#define FITSBASE_H 1

// CCfitsHeader
#include "CCfits.h"
// fitsio
#include "fitsio.h"
// string
#include <string>
// map
#include <map>

namespace CCfits {
  class ExtHDU;
  class PHDU;

} // namespace CCfits
using std::string;


namespace CCfits {



  class FITSBase 
  {

    public:
        FITSBase(const FITSBase &right);
        FITSBase (const String& fileName, RWmode rwmode);
        ~FITSBase();

        void destroyPrimary ();
        void destroyExtensions ();
        FITSBase* clone ();
        int currentCompressionTileDim () const;
        void currentCompressionTileDim (int value);
        RWmode mode ();
        std::string& currentExtensionName ();
        std::string& name ();
        PHDU*& pHDU ();
        ExtMap& extension ();
        fitsfile*& fptr ();

      // Additional Public Declarations

    protected:
      // Additional Protected Declarations

    private:
        FITSBase & operator=(const FITSBase &right);

      // Additional Private Declarations

    private: //## implementation
      // Data Members for Class Attributes
        int m_currentCompressionTileDim;

      // Data Members for Associations
        RWmode m_mode;
        std::string m_currentExtensionName;
        std::string m_name;
        PHDU* m_pHDU;
        ExtMap m_extension;
        fitsfile* m_fptr;

      // Additional Implementation Declarations

  };

  // Class CCfits::FITSBase 

  inline int FITSBase::currentCompressionTileDim () const
  {
    return m_currentCompressionTileDim;
  }

  inline void FITSBase::currentCompressionTileDim (int value)
  {
    m_currentCompressionTileDim = value;
  }

  inline RWmode FITSBase::mode ()
  {
    return m_mode;
  }

  inline std::string& FITSBase::currentExtensionName ()
  {
    return m_currentExtensionName;
  }

  inline std::string& FITSBase::name ()
  {
    return m_name;
  }

  inline PHDU*& FITSBase::pHDU ()
  {
    return m_pHDU;
  }

  inline ExtMap& FITSBase::extension ()
  {
    return m_extension;
  }

  inline fitsfile*& FITSBase::fptr ()
  {
    return m_fptr;
  }

} // namespace CCfits


#endif
