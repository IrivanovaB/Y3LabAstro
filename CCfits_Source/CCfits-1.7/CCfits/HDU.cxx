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
#endif

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef SSTREAM_DEFECT
#include <strstream>
#else
#include <sstream>
#endif

#include <memory>

// FITS
#include "FITS.h"
// FITSBase
#include "FITSBase.h"
// HDU
#include "HDU.h"

#include "FITSUtil.h"
#include <functional>


namespace CCfits {

  // Class CCfits::HDU::InvalidImageDataType 

  HDU::InvalidImageDataType::InvalidImageDataType (const string& diag, bool silent)
  : FitsException("Fits Error: Invalid Data Type for Image",silent)
  {
  if (!silent) std::cerr << diag << '\n';
  }


  // Class CCfits::HDU::InvalidExtensionType 

  HDU::InvalidExtensionType::InvalidExtensionType (const string& diag, bool silent)
  : FitsException
     ("Fits Error: Extension Type: ",
     silent)
  {
        if (!silent) std::cerr << diag << '\n';
  }


  // Class CCfits::HDU::NoSuchKeyword 

  HDU::NoSuchKeyword::NoSuchKeyword (const string& diag, bool silent)
  : FitsException("Fits Error: Keyword not found: ",silent)
  {
  if (!silent || FITS::verboseMode()) std::cerr << diag << '\n';
  }


  // Class CCfits::HDU::NoNullValue 

  HDU::NoNullValue::NoNullValue (const string& diag, bool silent)
    : FitsException("Fits Error: No Null Pixel Value specified for Image ",silent)
  {
    if (!silent || FITS::verboseMode() ) std::cerr << diag << '\n';    
  }


  // Class CCfits::HDU 

  HDU::HDU(const HDU &right)
      : m_naxis(right.m_naxis),
        m_bitpix(right.m_bitpix),
        m_index(right.m_index),
        m_anynul(right.m_anynul),
        m_history(right.m_history),
        m_comment(right.m_comment),
        m_zero(right.m_zero),
        m_scale(right.m_scale),        
        m_keyWord(),
        m_parent(right.m_parent),
        m_naxes(right.m_naxes)
  {
   // ensure deep copy.
   copyKeys(right);
  }

  HDU::HDU (FITSBase* p)
      : m_naxis(0),
        m_bitpix(8),
        m_index(0),
        m_anynul(false),
        m_history(""),
        m_comment(""),
        m_zero(0),
        m_scale(1.0),        
        m_keyWord(),
        m_parent(p),
        m_naxes()
  {
   readHduInfo();  // read bitpix, naxis and naxes keywords 
   int hduIndex = 0;
   fits_get_hdu_num(fitsPointer(), &hduIndex);
   m_index = hduIndex - 1;
  }

  HDU::HDU (FITSBase* p, int bitpix, int naxis, const std::vector<long>& axes)
      : m_naxis(naxis),
        m_bitpix(bitpix),
        m_index(0),
        m_anynul(false),
        m_history(""),
        m_comment(""),
        m_zero(0),
        m_scale(1.0),        
        m_keyWord(),
        m_parent(p),
        m_naxes(axes)
  {
  }


  HDU::~HDU()
  {
  // garbage collection for heap allocated objects.
  clearKeys();
  }


  bool HDU::operator==(const HDU &right) const
  {
   return compare(right);
  }

  bool HDU::operator!=(const HDU &right) const
  {
  return !compare(right);
  }


  void HDU::clearKeys ()
  {
  for (std::map<String,Keyword*>::iterator key = m_keyWord.begin(); 
          key != m_keyWord.end(); ++key)
  {
        delete (*key).second;
  }

  m_keyWord.erase(m_keyWord.begin(),m_keyWord.end());
  }

  void HDU::readHduInfo ()
  {

  // Read BITPIX and NAXIS keywords 
  int status = 0;
  char* comment = 0;

  int htype = -1;
  if (fits_get_hdu_type(fitsPointer(),&htype,&status))
     throw FitsError(status);
  HduType xtype = HduType(htype);
  if (xtype == ImageHdu)
  {
     // Do not try and read BITPIX or NAXIS directly.  If this is a
     // compressed image, the relevant information will need to come
     // from ZBITPIX and ZNAXIS instead.
     int temp = 0;
     if (fits_get_img_type(fitsPointer(), &temp, &status))
        throw FitsError(status);
     m_bitpix = temp;
     if (fits_get_img_dim(fitsPointer(), &temp, &status))
        throw FitsError(status);
     m_naxis = temp;
  }
  else
  {
     // m_bitpix will retain its default value, 8.
     string keyname("NAXIS");
     if (fits_read_key_lng(fitsPointer(),const_cast<char*>(keyname.c_str()),
                &m_naxis, comment, &status))
        throw FitsError(status);
  }

  // okay, we have the number of axes and therefore the number of values
  // (z)NAXISn.

  FITSUtil::auto_array_ptr<long> axes(new long[m_naxis]);
  long* pAxes = axes.get();

  if (xtype == ImageHdu)
  {
     if (fits_get_img_size(fitsPointer(), m_naxis, pAxes, &status))
        throw FitsError(status);
  }
  else
  {
     // create strings NAXIS1 - NAXISn, where n = NAXIS, and read keyword.
     for (int i=0; i <m_naxis; i++)
     {  
        string keyname("NAXIS");
        #ifdef SSTREAM_DEFECT
           std::ostrstream axisKey;
	   axisKey << keyname << i+1 << std::ends;
           if (fits_read_key_lng(fitsPointer(),axisKey.str(),&pAxes[i],comment,&status) ) 
                   throw FitsError(status);
        #else
	   std::ostringstream axisKey;
	   axisKey << keyname << i+1;
           if (fits_read_key_lng(fitsPointer(),const_cast<char*>(axisKey.str().c_str()),
                                                                   &pAxes[i],comment,&status) ) 
                   throw FitsError(status);
        #endif
     }

  }
  std::copy(&pAxes[0],&pAxes[m_naxis], std::back_inserter(m_naxes));
  }

  Keyword& HDU::readKeyword (const String &keyname)
  {

  try       
  {
  	using std::pair;  
        Keyword* newKey(KeywordCreator::getKeyword(keyname,this));
        std::map<String,Keyword*>::value_type refToEntry(keyname,newKey);
        std::map<String,Keyword*>::iterator itOld = m_keyWord.find(keyname);
        if (itOld != m_keyWord.end())
        {
           delete itOld->second;
           m_keyWord.erase(itOld);
        }
        m_keyWord.insert(refToEntry);
  	return *(refToEntry.second);

  }
  catch (FitsError)
  {     
        throw NoSuchKeyword(keyname);
  }  
  }

  void HDU::readKeywords (std::list<String>& keynames)
  {
  // the scoop is: this and the previous function - which reads
  // a single key - are designed to be called by HDU and its subclasses
  // in constructors etc., and by the public member functions
  // addKey<T>, readKey<T> and readKeys<T>. These functions read keywords
  // and either return nothing or return Keyword references from which another
  // function call is necessary to retrieve the value. These are both things
  // that implementers need but are not necessary to provide for the user.
  std::list<String>::iterator ikey = keynames.begin();
  while ( ikey != keynames.end())
  {
     try
     {
        readKeyword(*ikey);
	++ikey;
     }
     catch (NoSuchKeyword)
     {
        ikey = keynames.erase(ikey);
     }
  }


  }

  Keyword* HDU::addKeyword (Keyword* newKey)
  {
  	using std::pair;
  	newKey->write();
        const String& keyname = newKey->name(); 
        std::map<String,Keyword*>::value_type refToEntry(keyname,newKey);
        std::map<String,Keyword*>::iterator itOld = m_keyWord.find(keyname);
        if (itOld != m_keyWord.end())
        {
           delete itOld->second;
           m_keyWord.erase(itOld);
        }
        m_keyWord.insert(refToEntry);
  	return refToEntry.second;
  }

  bool HDU::compare (const HDU &right) const
  {
    if (fitsPointer() != right.fitsPointer()) return false;
    if (m_index != right.m_index) return false;
    return true;
  }

  fitsfile* HDU::fitsPointer () const
  {

    return m_parent->fptr();
  }

  void HDU::makeThisCurrent () const
  {
  int status = 0;
  int hduType = 0;
  // m_index contains the value of fptr->Fptr->curhdu. movabs_hdu moves to
  // 1 - this unless it's at the beginning, so it must be m_index+1 [Check!!!]
  if (fits_movabs_hdu(fitsPointer(),m_index+1, &hduType, &status) != 0) throw FitsError(status);
  m_parent->currentExtensionName()  = "";
  }

  void HDU::copyKeys (const HDU& right)
  {
    // copy all keys that have already been read.
  for (std::map<String,Keyword*>::const_iterator key = right.m_keyWord.begin(); 
          key != right.m_keyWord.end(); key++)
  {
        std::map<String,Keyword*>::iterator itOld = m_keyWord.find(key->first);
        if (itOld != m_keyWord.end())
        {
           delete itOld->second;
           m_keyWord.erase(itOld);
        }
        m_keyWord[(*key).first] = ((*key).second)->clone();
  }
  }

  String HDU::getNamedLines (const String& name)
  {
  int fitsStatus = 0;
  int numKeys = 0;
  static char searchKey[FLEN_KEYWORD];

  makeThisCurrent();


  String content("");
  char* card = new char[81];
  FITSUtil::auto_array_ptr<char> pcard(card);
  int where = 1;
  int keylen = 0;

  fits_get_hdrpos(fitsPointer(),&numKeys,&where,&fitsStatus);
  if (fitsStatus != 0 ) throw FitsError(fitsStatus,false);

  // search through the header to get the first "name" keyword.
  while ( where < numKeys )
  {
        fits_read_record(fitsPointer(),++where,card,&fitsStatus);
	fits_get_keyname(card,searchKey,&keylen,&fitsStatus);
	// on FitsError, always print a message (!silent).
	if (fitsStatus != 0 ) throw FitsError(fitsStatus,false);
	// require exact match
        if (strcmp(name.c_str(),searchKey) == 0) 
        {
        	// this should work for standard compliant
        	// string implementation, where the length added
        	// to content is determined by traits::length()
                content += card + 8;
                content += "\n";  
        }
  }

  // print a message if there are no "name" type records.
  if (content.size() == 0) throw NoSuchKeyword(name);




  return content; 
  }

  const String& HDU::getHistory ()
  {

  try
  {
          m_history = getNamedLines("HISTORY");
  }
  catch (HDU::NoSuchKeyword) {}
  catch (FitsError) {}
  catch (...) { throw; }
  return m_history;
  }

  const String& HDU::getComments ()
  {
  try
  {
          m_comment = getNamedLines("COMMENT");
  }
  catch (HDU::NoSuchKeyword) {}
  catch (FitsError) {}
  catch (...) { throw; }
  return m_comment;
  }

  void HDU::writeHistory (const String& history)
  {
    int status(0);
    makeThisCurrent();
    if (fits_write_history(fitsPointer(),const_cast<char*>(history.c_str()),&status))
                throw FitsError(status);
    m_history = history;             
  }

  void HDU::writeComment (const String& comment)
  {
    int status(0);
    makeThisCurrent();
    if (fits_write_comment(fitsPointer(),const_cast<char*>(comment.c_str()),&status))
                throw FitsError(status);

    m_comment = comment;             
  }

  void HDU::writeDate ()
  {
    static const String DATE("DATE");
    int status(0);
    makeThisCurrent();
    if (fits_write_date(fitsPointer(),&status)) throw FitsError(status);
    FITSUtil::auto_array_ptr<char> pDate(new char[FLEN_KEYWORD]);
    FITSUtil::auto_array_ptr<char> pDateComment(new char[FLEN_COMMENT]);
    char* date = pDate.get();
    if (fits_read_key_str(fitsPointer(),
        const_cast<char*>(DATE.c_str()),date,pDateComment.get(),&status))   throw FitsError(status);
    NewKeyword<String> creator(this,String(date));
    Keyword* newKey = creator.MakeKeyword(DATE,String(pDateComment.get()));
    std::map<String,Keyword*>::iterator itOld = m_keyWord.find(DATE);
    if (itOld != m_keyWord.end())
    {
       delete itOld->second;
       m_keyWord.erase(itOld);
    }
    m_keyWord[DATE] = newKey;               

  }

  FITSBase* HDU::parent () const
  {

    return m_parent;
  }

  void HDU::readAllKeys ()
  {
    makeThisCurrent();
    int status(0);
    int n (0);
    int dum(0);
    if (fits_get_hdrpos(fitsPointer(),&n,&dum,&status)) throw FitsError(status);

    for (int j = 1; j <= n; ++j)
    {
            // get keywords by header position and store all the keys that
            // are neither metadata for columns nor history/comment cards.
            std::auto_ptr<Keyword> key(KeywordCreator::getKeyword(j,this));
            // comment/history cards have no value field and return 0 here.
            if (key.get() != 0)
            {
                int keyClass = fits_get_keyclass(const_cast<char*>(key->name().c_str()));
                if ( (keyClass == TYP_USER_KEY  ) ||
                        (keyClass == TYP_WCS_KEY   ) ||
                        (keyClass == TYP_CMPRS_KEY ) ||
                        (keyClass == TYP_CKSUM_KEY ) ||
                        (keyClass == TYP_REFSYS_KEY) )
                {
                        saveReadKeyword(key.get());
                }  
            }       
    }

    getHistory();
    getComments();
  }

  void HDU::deleteKey (const String& doomed)
  {
    Keyword& k = keyWord(doomed); //throws no such keyword if there isn't.
    int status(0);
    if (fits_delete_key(fitsPointer(),const_cast<char*>(k.name().c_str()),&status)) throw FitsError(status);
    std::map<String,Keyword*>::iterator ki(m_keyWord.find(doomed));
    delete (*ki).second;
    m_keyWord.erase(ki);
  }

  // Additional Declarations
    Keyword& HDU::addKey(const string& name, const char* charString, const String& comment)
    {
        return addKey(name,String(charString),comment);      
    }
} // namespace CCfits
