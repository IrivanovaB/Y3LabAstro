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

#ifndef NEWKEYWORD_H
#define NEWKEYWORD_H 1

// KeyData
#include "KeyData.h"
// KeywordCreator
#include "KeywordCreator.h"
// FITSUtil
#include "FITSUtil.h"


namespace CCfits {



  template <typename T>
  class NewKeyword : public KeywordCreator  //## Inherits: <unnamed>%39355AA90209
  {

    public:
        //	Parameterized Class NewKeyword
        NewKeyword (HDU* p, T value);
        virtual ~NewKeyword();

        //	Additional Protected Declarations
        virtual Keyword* MakeKeyword (const String& keyName, const String& keyComment = String(""));
        const T keyData () const;
        void keyData (T value);

      // Additional Public Declarations

    protected:
      // Additional Protected Declarations

    private:
        NewKeyword();

        NewKeyword(const NewKeyword< T > &right);
        NewKeyword< T > & operator=(const NewKeyword< T > &right);

      // Additional Private Declarations

    private: //## implementation
      // Data Members for Class Attributes
        T m_keyData;

      // Additional Implementation Declarations

  };

  // Parameterized Class CCfits::NewKeyword 

  template <typename T>
  inline const T NewKeyword<T>::keyData () const
  {
    return m_keyData;
  }

  template <typename T>
  inline void NewKeyword<T>::keyData (T value)
  {
    m_keyData = value;
  }

  // Parameterized Class CCfits::NewKeyword 

  template <typename T>
  NewKeyword<T>::NewKeyword (HDU* p, T value)
      : KeywordCreator(p), m_keyData(value)
  {
  }


  template <typename T>
  NewKeyword<T>::~NewKeyword()
  {
  }


  template <typename T>
  Keyword* NewKeyword<T>::MakeKeyword (const String& keyName, const String& keyComment)
  {
  FITSUtil::MatchType<T> keyType;
  return new KeyData<T>(keyName,keyType(),m_keyData,forHDU(),keyComment);
  }

  // Additional Declarations

} // namespace CCfits


#endif
