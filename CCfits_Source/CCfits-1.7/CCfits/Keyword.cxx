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
#include <iosfwd>

// FitsError
#include "FitsError.h"
// HDU
#include "HDU.h"
// Keyword
#include "Keyword.h"
// FITS
#include "FITS.h"

#include "KeyData.h"


namespace CCfits {

  // Class CCfits::Keyword::WrongKeywordValueType 

  Keyword::WrongKeywordValueType::WrongKeywordValueType (const String& diag, bool silent)
  : FitsException("Error: attempt to read keyword into variable of incorrect type",silent) 
  {
  if ( FITS::verboseMode() || !silent) std::cerr << "\nKeyname:" << diag << "\n";
  }


  // Class CCfits::Keyword 

  Keyword::Keyword(const Keyword &right)
	: m_keytype(right.m_keytype),
        m_parent(right.m_parent),
	m_comment(right.m_comment),
        m_name(right.m_name)
  {
  }

  Keyword::Keyword (const String &keyname, ValueType keytype, HDU* p, const String &comment)
	: m_keytype(keytype),
        m_parent(p),
	m_comment(comment),
        m_name(keyname)
  {
  }


  Keyword::~Keyword()
  {
  }


  Keyword & Keyword::operator=(const Keyword &right)
  {
   if (this == &right) copy(right);
   return *this;
  }


  bool Keyword::operator==(const Keyword &right) const
  {
   return compare(right);
  }

  bool Keyword::operator!=(const Keyword &right) const
  {
  return !compare(right);
  }


  void Keyword::copy (const Keyword& right)
  {
  m_name = right.m_name;
  m_comment = right.m_comment;
  m_keytype  = right.m_keytype;
  m_parent  = right.m_parent;
  }

  bool Keyword::compare (const Keyword &right) const
  {
  if (m_name != right.m_name) return false;
  if (m_keytype != right.m_keytype) return false;
  if (m_comment != right.m_comment) return false;
  if (m_parent  != right.m_parent) return false;
  return true;
  }

  fitsfile* Keyword::fitsPointer () const
  {

    return m_parent->fitsPointer();
  }

  // Additional Declarations

} // namespace CCfits
namespace CCfits
{
#ifndef SPEC_TEMPLATE_IMP_DEFECT
#ifndef SPEC_TEMPLATE_DECL_DEFECT
   template<>
   float& Keyword::value(float& val) const
   {
      double dval=.0;
      val = static_cast<float>(value(dval));
      return val;
   }

   template<>
   double& Keyword::value(double& val) const
   {
      switch (m_keytype)
      {
         case Tint:
            {
               const KeyData<int>& thisKey = static_cast<const KeyData<int>&>(*this);
               val = thisKey.keyval();
            }
            break;
         case Tfloat:
            {
               const KeyData<float>& thisKey = static_cast<const KeyData<float>&>(*this);
               val = thisKey.keyval();
            }
            break;
         case Tdouble:
            {
               // Note: if val is of type float some precision will be lost here,
               // but allow anyway.  Presumably the user doesn't mind or they
               // wouldn't be using single precision.
               const KeyData<double>& thisKey = static_cast<const KeyData<double>&>(*this);
               val = thisKey.keyval();
            }
            break;
         case Tstring:
            {
               // Allow only if string can be converted to an integer.
               const KeyData<String>& thisKey = static_cast<const KeyData<String>&>(*this); 
               std::istringstream testStream(thisKey.keyval());
               int stringInt = 0;
               if (!(testStream >> stringInt) || !testStream.eof())
               {
                  throw Keyword::WrongKeywordValueType(name());
               }
               val = stringInt;
            }
            break;
         default:
            throw Keyword::WrongKeywordValueType(name());
            break;
      }
      return val;
   }

   template <>
   int& Keyword::value(int& val) const
   {
         if (m_keytype == Tstring)
         {
            // Allow only if string can be converted to an integer.
            const KeyData<String>& thisKey = static_cast<const KeyData<String>&>(*this); 
            std::istringstream testStream(thisKey.keyval());
            int stringInt = 0;
            if (!(testStream >> stringInt) || !testStream.eof())
            {
               throw Keyword::WrongKeywordValueType(name());
            }
            val = stringInt;         
         } 
         else if (m_keytype == Tint)
         {
            const KeyData<int>& thisKey = static_cast<const KeyData<int>&>(*this);
            val = thisKey.keyval();
         } 
         else
         {
            throw Keyword::WrongKeywordValueType(name());
         }
         return val;    
   }
#endif
#endif
}
