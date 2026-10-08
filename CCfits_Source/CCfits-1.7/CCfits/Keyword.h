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

#ifndef KEYWORD_H
#define KEYWORD_H 1
#include "CCfits.h"
// using namespace CCfits;
#ifdef _MSC_VER
#include "MSconfig.h"
#endif

// FitsError
#include "FitsError.h"

namespace CCfits {
  class HDU;

} // namespace CCfits


namespace CCfits {

/*! \class Keyword

        \brief Abstract base class implementing the common behavior of Keyword objects.

        Keywords consists of a name, a value and a comment field. Concrete templated
        subclasses, KeyData<T>,  have a data member that holds the value of keyword.

        Typically, the mandatory keywords for a given HDU type are not stored as
        object of type Keyword, but as intrinsic data types. The Keyword hierarchy
        is used to store user-supplied information.

*/


/*! \fn Keyword::Keyword(const Keyword &right);

      \brief copy constructor

*/


/*!  \fn Keyword::Keyword (const String &keyname, ValueType keytype, HDU* p, const String &comment = "");

      \brief Keyword constructor. 

      This is the common behavior of Keywords of any type. Constructor is protected 
      as the class is abstract.

*/

/* \fn friend ostream& operator << (ostream &s, const Keyword &right);

        \brief output operator for Keywords.

*/

/*!   \fn virtual Keyword::~Keyword();

      \brief virtual destructor

*/

/*!    \fn Keyword & Keyword::operator=(const Keyword &right);

      \brief assignment operator

*/

/*!    \fn bool Keyword::operator==(const Keyword &right) const;

        \brief equality operator

*/

/*!       \fn bool Keyword::operator!=(const Keyword &right) const;


        \brief inequality operator

*/


/*!       \fn virtual Keyword * Keyword::clone () const;

        \brief virtual copy constructor
*/

/*!       \fn virtual void Keyword::write ();

        \brief write operation
*/


/*!   \fn       fitsfile* Keyword::fitsPointer () const;

        \brief return a pointer to the FITS file containing the parent HDU.

*/


/*!    \fn      const HDU* Keyword::parent () const;

        \brief return a pointer to parent HDU.

*/

/*!    \fn      const String& Keyword::comment () const;

        \brief return the comment field of the keyword

*/


/*! \fn  const ValueType Keyword::keytype() const

     \brief return the type of a keyword


*/


/*! \fn  void  Keyword::keytype(ValueType)

      \brief  set keyword type.


*/


/*! \fn  const String& Keyword::name() const

        return the name of a keyword


*/



  class Keyword 
  {

    public:



      class WrongKeywordValueType : public FitsException  //## Inherits: <unnamed>%39B0221700E2
      {
        public:
            WrongKeywordValueType (const String& diag, bool silent = true);

        protected:
        private:
        private: //## implementation
      };
        Keyword(const Keyword &right);
        Keyword (const String &keyname, ValueType keytype, HDU* p, const String &comment = "");
        virtual ~Keyword();
        Keyword & operator=(const Keyword &right);
        bool operator==(const Keyword &right) const;

        bool operator!=(const Keyword &right) const;

        virtual std::ostream & put (std::ostream &s) const = 0;
        virtual Keyword * clone () const = 0;
        virtual void write () = 0;
        fitsfile* fitsPointer () const;
        const String& comment () const;
        const String& name () const;

    public:
      // Additional Public Declarations
      template <typename T>
      T& value(T& val) const;

      template <typename T>
      void setValue(const T& newValue);
    protected:
        virtual void copy (const Keyword& right);
        virtual bool compare (const Keyword &right) const;
        ValueType keytype () const;
        void keytype (ValueType value);
        const HDU* parent () const;

      // Additional Protected Declarations

    private:
      // Additional Private Declarations

    private: //## implementation
      // Data Members for Class Attributes
        ValueType m_keytype;

      // Data Members for Associations
        HDU* m_parent;
        String m_comment;
        String m_name;

      // Additional Implementation Declarations
      friend std::ostream &operator << (std::ostream &s, const Keyword &right);
  };
#ifndef SPEC_TEMPLATE_IMP_DEFECT
#ifndef SPEC_TEMPLATE_DECL_DEFECT
  template <> float& Keyword::value(float& val) const;
  template <> double& Keyword::value(double& val) const;
  template <> int& Keyword::value(int& val) const;
#endif 
#endif 

inline std::ostream& operator << (std::ostream &s, const Keyword &right)
{
   return right.put(s);
}  

  // Class CCfits::Keyword::WrongKeywordValueType 

  // Class CCfits::Keyword 

  inline ValueType Keyword::keytype () const
  {
    return m_keytype;
  }

  inline void Keyword::keytype (ValueType value)
  {
    m_keytype = value;
  }

  inline const HDU* Keyword::parent () const
  {
    return m_parent;
  }

  inline const String& Keyword::comment () const
  {
    return m_comment;
  }

  inline const String& Keyword::name () const
  {
    return m_name;
  }

} // namespace CCfits


#endif
