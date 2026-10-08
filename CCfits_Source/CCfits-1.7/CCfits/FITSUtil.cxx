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

// FITSUtil
#include "FITSUtil.h"
#include "FitsError.h"
#include "FITS.h"
#include <algorithm>
using std::string;


namespace CCfits {
  const unsigned long USBASE = 1 << 15;
  const unsigned long ULBASE = 1 << 31;

  namespace FITSUtil {
  InvalidConversion::InvalidConversion (const string& diag, bool silent)
  : FitsException(string("Fits Error: Attempt to perform invalid implicit conversion"),silent)
  {       
	if (FITS::verboseMode() || !silent) std::cerr << diag << '\n';
  }

  char** CharArray (const std::vector<string>& inArray)
  {
      size_t n = inArray.size();
      if (n == 0) return 0;
      char** c  = new char*[n];

      for (size_t i = 0; i < n; ++i)
      {
         size_t m(inArray[i].length());
	 c[i] = new char[m+1];
	 strncpy(c[i],inArray[i].c_str(),m + 1);
      }

      return c;      
  }
#if TEMPLATE_AMBIG_DEFECT || TEMPLATE_AMBIG7_DEFECT
  void fillMSvsvs (std::vector<string>& outArray, const std::vector<string>& inArray, size_t first, size_t last)
  {
          // recall behavior of iterators: last has to be one-past-the-last entry.
          // if last == first, this will still do something. the "first-1" is a zero based indexing
          // correction. 
          outArray.assign(inArray.begin()+first-1,inArray.begin()+last);  
  }        
#endif

  void fill (std::vector<string>& outArray, const std::vector<string>& inArray, size_t first, size_t last)
  {
          // recall behavior of iterators: last has to be one-past-the-last entry.
          // if last == first, this will still do something. the "first-1" is a zero based indexing
          // correction. 
          outArray.assign(inArray.begin()+first-1,inArray.begin()+last);  
  }        

  string lowerCase(const string& inputString)
  {
        size_t n(inputString.length());
        string outputString("");
        outputString.resize(n, ' ');
        for (size_t l = 0 ; l < n; ++l)
        {
                 outputString[l] = tolower(inputString[l]);          
        }
        return outputString;  
  }

  string upperCase(const string& inputString)
  {
        size_t n(inputString.length());
        string outputString("");

        outputString.resize(n,' ');
        for (size_t l = 0 ; l < n; ++l)
        {
                 outputString[l] = toupper(inputString[l]);          
        }
        return outputString;  
  }

  string::size_type checkForCompressString(const string& fileName)
  {
     // Simply look for the first occurrence of the form "[compress....".
     const string leadIndicator("[compress");
     string::size_type start = fileName.find(leadIndicator);
     return start;
  }

  string FITSType2String ( int typeInt )
  {
    string keyString("");

    switch (typeInt)        
    {
        default:
        case Tnull:
                keyString = "Unknown";
                break;
        case Tbit:
                keyString = "bit";
                break;
        case Tbyte:
                keyString = "byte";
                break;
        case Tlogical:
                keyString = "logical";
                break;
        case Tstring:
                keyString = "string";
                break;
        case Tushort:
                keyString = "unsigned short";
                break;
        case Tshort:
                keyString = "short";
                break;
        case Tuint:
                keyString = "unsigned integer";
                break;
        case Tint:
                keyString = "integer";
                break;
        case Tulong:
                keyString = "unsigned long";
                break;
        case Tlong:
                keyString = "long";
                break;
        case Tlonglong:
                keyString = "long long";
        case Tfloat:
                keyString = "float";
                break;
        case Tdouble:
                keyString = "double";
                break;
        case Tcomplex:
                keyString = "float complex";
                break;
        case Tdblcomplex:
                keyString = "double complex";
                break;
    }

    return keyString;     
  }

  bool MatchStem::operator()(const string& left, const string& right) const
  {
          static const string DIGITS("0123456789");
          size_t n(left.find_last_not_of(DIGITS));
          if ( n != string::npos ) return (left.substr(0,n) == right);
          else return (left == right);
  }



  fitsfile* 
  copyFitsPtr(fitsfile* inPtr)
  {
      // allocate all the memory and convert any errors to a standard exception    

      fitsfile* outPtr = 0;
      if ( (outPtr  = (fitsfile*)calloc(1,sizeof(fitsfile))) == 0 ) throw std::bad_alloc();

      outPtr->Fptr = 0;
      if ( (outPtr->Fptr = (FITSfile*)calloc(1,sizeof(FITSfile))) == 0 ) throw std::bad_alloc();

      outPtr->Fptr->filename = 0;
      if ( (outPtr->Fptr->filename = 
                (char*)malloc(strlen(inPtr->Fptr->filename)+1))  == 0 ) throw std::bad_alloc();

      outPtr->Fptr->tableptr = 0;
          /* pointer to the table structure */
      if ( (outPtr->Fptr->tableptr  = (tcolumn*)malloc(sizeof(tcolumn))) == 0 )
               throw std::bad_alloc();

      outPtr->HDUposition = inPtr->HDUposition;

      outPtr->Fptr->filehandle = inPtr->Fptr->filehandle;
      /* defines which set of I/O drivers should be used */
      outPtr->Fptr->driver = inPtr->Fptr->driver;  

      strcpy(outPtr->Fptr->filename,inPtr->Fptr->filename);

      /* current size of the physical disk file in bytes */
      outPtr->Fptr->filesize = inPtr->Fptr->filesize;   

      /* logical size of file, including unflushed buffers */
      outPtr->Fptr->logfilesize = inPtr->Fptr->logfilesize; 

      /* 0 = readonly, 1 = readwrite */
      outPtr->Fptr->writemode = inPtr->Fptr->writemode;  

      /* byte offset in file to beginning of next keyword */
      outPtr->Fptr->datastart = inPtr->Fptr->datastart;

      /* current I/O pointer position in the physical file */
      outPtr->Fptr->curbuf = inPtr->Fptr->curbuf;

      /* number of opened 'fitsfiles' using this structure */  
      outPtr->Fptr->open_count = inPtr->Fptr->open_count; 

      /* magic value used to verify that structure is valid */
      outPtr->Fptr->validcode = inPtr->Fptr->validcode;  

          outPtr->Fptr->lasthdu = inPtr->Fptr->lasthdu;    
          /* is this the last HDU in the file? 0 = no, else yes */
          outPtr->Fptr->bytepos = inPtr->Fptr->bytepos;   /* current logical I/O pointer position in file */
          outPtr->Fptr->io_pos = inPtr->Fptr->io_pos;    
          /* number of I/O buffer currently in use */ 
          outPtr->Fptr->curhdu = inPtr->Fptr->curhdu;     
          /* current HDU number; 0 = primary array */
          outPtr->Fptr->hdutype = inPtr->Fptr->hdutype;    
          /* 0 = primary array, 1 = ASCII table, 2 = binary table */
          outPtr->Fptr->maxhdu = inPtr->Fptr->maxhdu;     
          /* highest numbered HDU known to exist in the file */
		  size_t i = 0;
          for ( ; i < MAX_COMPRESS_DIM; i++) 
          {
                  outPtr->Fptr->headstart[i] = inPtr->Fptr->headstart[i];
          }
         /* byte offset in file to start of each HDU */
          outPtr->Fptr->headend = inPtr->Fptr->headend;   
          /* byte offest in file to end of the current HDU header */
          outPtr->Fptr->nextkey = inPtr->Fptr->nextkey;   
          /* byte offset in file to start of the current data unit */
          outPtr->Fptr->tfield = inPtr->Fptr->tfield;     
          /* number of fields in the table (primary array has 2 */
          outPtr->Fptr->origrows = inPtr->Fptr->origrows;  
          /* original number of rows (value of NAXIS2 keyword)  */
          outPtr->Fptr->numrows = inPtr->Fptr->numrows;   
          /* number of rows in the table (dynamically updated) */
          outPtr->Fptr->rowlength = inPtr->Fptr->rowlength; 
          /* total length of a table row, in bytes */

          outPtr->Fptr->heapstart = inPtr->Fptr->heapstart; 
          /* heap start byte relative to start of data unit */
          outPtr->Fptr->heapsize = inPtr->Fptr->heapsize;  /* size of the heap, in bytes */

                 /* the following elements are related to compress images */
          /* 1 if HDU contains a compressed image, else 0 */
          outPtr->Fptr->compressimg = inPtr->Fptr->compressimg; 

          /* compression type string */
          for ( i = 0; i < 12; ++i)
          {
               outPtr->Fptr->zcmptype[i] = inPtr->Fptr->zcmptype[i];
          }
          /* type of compression algorithm */
          outPtr->Fptr->compress_type = inPtr->Fptr->compress_type;      
          /* FITS data type of image (BITPIX) */
          outPtr->Fptr->zbitpix = inPtr->Fptr->zbitpix;		
          /* dimension of image */
          outPtr->Fptr->zndim = inPtr->Fptr->zndim;		

           /* length of each axis */
          for ( i = 0; i < MAX_COMPRESS_DIM; i++) 
          {
                  outPtr->Fptr->znaxis[i] = inPtr->Fptr->znaxis[i];
          }
          /* size of compression tiles */
          for ( i = 0; i < MAX_COMPRESS_DIM; i++) 
          {
                  outPtr->Fptr->tilesize[i] = inPtr->Fptr->tilesize[i];
          }
          /* max number of pixels in each image tile */
           outPtr->Fptr->maxtilelen = inPtr->Fptr->maxtilelen;        
          /* maximum length of variable length arrays */
          outPtr->Fptr->maxelem = inPtr->Fptr->maxelem;		

          /* column number for COMPRESSED_DATA column */
          outPtr->Fptr->cn_compressed = inPtr->Fptr->cn_compressed;	    
          /* column number for UNCOMPRESSED_DATA column */
          outPtr->Fptr->cn_uncompressed = inPtr->Fptr->cn_uncompressed;    
          /* column number for ZSCALE column */
          outPtr->Fptr->cn_zscale = inPtr->Fptr->cn_zscale;	    
          /* column number for ZZERO column */
          outPtr->Fptr->cn_zzero = inPtr->Fptr->cn_zzero;	    
          /* column number for the ZBLANK column */
          outPtr->Fptr->cn_zblank = inPtr->Fptr->cn_zblank;          

          /* scaling value, if same for all tiles */
          outPtr->Fptr->zscale = inPtr->Fptr->zscale;          
          /* zero pt, if same for all tiles */
          outPtr->Fptr->zzero = inPtr->Fptr->zzero;           
          /* value for null pixels, if not a column */
          outPtr->Fptr->zblank = inPtr->Fptr->zblank;             

          /* first compression parameter */
          outPtr->Fptr->rice_blocksize = inPtr->Fptr->rice_blocksize;     
          /* second compression parameter */
          outPtr->Fptr->noise_nbits = inPtr->Fptr->noise_nbits;         


          /* column name = FITS TTYPEn keyword; */
          for ( i = 0; i < 70; ++i)
          {
             outPtr->Fptr->tableptr->ttype[i] = inPtr->Fptr->tableptr->ttype[i];
          }
          /* FITS null value string for ASCII table columns */
          for ( i = 0; i < 20; ++i)
          {
             outPtr->Fptr->tableptr->strnull[i] = inPtr->Fptr->tableptr->strnull[i];
          }
          /* FITS tform keyword value  */
          for ( i = 0; i < 10; ++i)
          {
             outPtr->Fptr->tableptr->tform[i] = inPtr->Fptr->tableptr->tform[i];
          }
           /* offset in row to first byte of each column */
           outPtr->Fptr->tableptr->tbcol = inPtr->Fptr->tableptr->tbcol;       
           /* datatype code of each column */
           outPtr->Fptr->tableptr->tdatatype = inPtr->Fptr->tableptr->tdatatype;   
           /* repeat count of column; number of elements */
           outPtr->Fptr->tableptr->trepeat = inPtr->Fptr->tableptr->trepeat;     
           /* FITS TSCALn linear scaling factor */
           outPtr->Fptr->tableptr->tscale = inPtr->Fptr->tableptr->tscale;    
           /* FITS TZEROn linear scaling zero point */
           outPtr->Fptr->tableptr->tzero = inPtr->Fptr->tableptr->tzero;     
           /* FITS null value for int image or binary table cols */
           outPtr->Fptr->tableptr->tnull = inPtr->Fptr->tableptr->tnull;       
           /* width of each ASCII table column */
           outPtr->Fptr->tableptr->twidth = inPtr->Fptr->tableptr->twidth;     

        return outPtr;

  }      

// VF<-VF
#ifdef TEMPLATE_AMBIG_DEFECT
	void 
	fillMSvfvf(std::vector<std::complex<float> >& outArray, const std::vector<std::complex<float> >& inArray, 
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = inArray[j];

				}
	}
#else

	void 
	fill(std::vector<std::complex<float> >& outArray, const std::vector<std::complex<float> >& inArray, 
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = inArray[j];
                }
	}
#endif


#ifdef TEMPLATE_AMBIG_DEFECT
// VF<-VD
	void 
	fillMSvfvd(std::vector<std::complex<float> >& outArray, const std::vector<std::complex<double> >& inArray, 
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = std::complex<float>(inArray[j].real(),
                                                inArray[j].imag());
                }
	}
#else

// VF<-VD
	void 
	fill(std::vector<std::complex<float> >& outArray, const std::vector<std::complex<double> >& inArray, 
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = std::complex<float>(inArray[j].real(),
                                                inArray[j].imag());
                }
	}
#endif

// VD<-VD  
#ifdef TEMPLATE_AMBIG_DEFECT
	void 
	fillMSvdvd(std::vector<std::complex<double> >& outArray, const std::vector<std::complex<double> >& inArray, 
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = inArray[j];
                }

	}  
#else
	void 
	fill(std::vector<std::complex<double> >& outArray, const std::vector<std::complex<double> >& inArray, 
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = inArray[j];
                }

	}
#endif

// VD<-VF
#ifdef TEMPLATE_AMBIG_DEFECT
	void 
	fillMSvdvf(std::vector<std::complex<double> >& outArray, const std::vector<std::complex<float> >& inArray, 
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = std::complex<double>(inArray[j].real(),
                                                inArray[j].imag());
                }
	}  
#else
	void 
	fill(std::vector<std::complex<double> >& outArray, const std::vector<std::complex<float> >& inArray, 
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = std::complex<double>(inArray[j].real(),
                                                inArray[j].imag());
                }
	}  
#endif

// AF<-VF

// AF<-VF
#ifdef TEMPLATE_AMBIG_DEFECT
	void 
	fillMSafvf(std::valarray<std::complex<float> >& outArray, 
                        const std::vector<std::complex<float> >& inArray,
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1 ] = inArray[j];
                }
	} 
#else
	void 
	fill(std::valarray<std::complex<float> >& outArray, 
                        const std::vector<std::complex<float> >& inArray,
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1 ] = inArray[j];
                }
	}
#endif

// AF<-VD
 	void 
	fill(std::valarray<std::complex<float> >& outArray, 
                        const std::vector<std::complex<double> >& inArray,
                        size_t first, size_t last)
        {                
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1 ] 
                                        = std::complex<float>(inArray[j].real(),inArray[j].imag());
                }
	}                  
// AD<-VD
#ifdef TEMPLATE_AMBIG_DEFECT
	void 
	fillMSadvd(std::valarray<std::complex<double> >& outArray, 
                        const std::vector<std::complex<double> >& inArray,
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = inArray[j];
                }
	}
#else
	void 
	fill(std::valarray<std::complex<double> >& outArray, 
                        const std::vector<std::complex<double> >& inArray,
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1] = inArray[j];
                }
	}                  
#endif

// AD<-VF
#ifdef TEMPLATE_AMBIG_DEFECT
	void 
	fillMSadvf(std::valarray<std::complex<double> >& outArray, 
                        const std::vector<std::complex<float> >& inArray,
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1 ] 
                                        = std::complex<float>(inArray[j].real(),inArray[j].imag());
                }
	}
#else
	void 
	fill(std::valarray<std::complex<double> >& outArray, 
                        const std::vector<std::complex<float> >& inArray,
                        size_t first, size_t last)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t range = last - first + 1;
                if (outArray.size() != range) outArray.resize(range);
                for (size_t j = first - 1; j < last; ++j)
                {
                        outArray[j - first + 1 ] 
                                        = std::complex<float>(inArray[j].real(),inArray[j].imag());
                }
	}
#endif
// AF<-AF
	void 
	fill(std::valarray<std::complex<float> >& outArray, 
                        const std::valarray<std::complex<float> >& inArray)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t N (inArray.size());
                if (outArray.size() != N) outArray.resize(N);
                outArray = inArray;
	}   

// AD<-AD        
	void 
	fill(std::valarray<std::complex<double> >& outArray, 
                        const std::valarray<std::complex<double> >& inArray)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t N (inArray.size());
                if (outArray.size() != N) outArray.resize(N);
                outArray = inArray;
	}  

// AF<-AD
	void 
	fill(std::valarray<std::complex<float> >& outArray, 
                        const std::valarray<std::complex<double> >& inArray)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t N (inArray.size());
                if (outArray.size() != N) outArray.resize(N);
                for (size_t j = 0; j < N; ++j ) 
                {
                        outArray[j] = std::complex<float>(inArray[j].real(),inArray[j].imag());
                }
	}                  
// AD<-AF        
	void 
	fill(std::valarray<std::complex<double> >& outArray, 
                        const std::valarray<std::complex<float> >& inArray)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t N (inArray.size());
                if (outArray.size() != N) outArray.resize(N);
                for (size_t j = 0; j < N; ++j ) 
                {
                        outArray[j] = std::complex<double>(inArray[j].real(),inArray[j].imag());
                }
	}                  

// VF<-AF
	void 
	fill(std::vector<std::complex<float> >& outArray, 
                        const std::valarray<std::complex<float> >& inArray)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t N (inArray.size());
                if (outArray.size() != N) outArray.resize(N);
                for (size_t j = 0; j < N; ++j) outArray[j] = inArray[j];
	}   

// VD<-AD        
	void 
	fill(std::vector<std::complex<double> >& outArray, 
                        const std::valarray<std::complex<double> >& inArray)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t N (inArray.size());
                if (outArray.size() != N) outArray.resize(N);
                for (size_t j = 0; j < N; ++j) outArray[j] = inArray[j];
	}  

// VF<-AD
	void 
	fill(std::vector<std::complex<float> >& outArray, 
                        const std::valarray<std::complex<double> >& inArray)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t N (inArray.size());
                if (outArray.size() != N) outArray.resize(N);
                for (size_t j = 0; j < N; ++j ) 
                {
                        outArray[j] = std::complex<float>(inArray[j].real(),inArray[j].imag());
                }
	}                  
// VD<-AF        
	void 
	fill(std::vector<std::complex<double> >& outArray, 
                        const std::valarray<std::complex<float> >& inArray)
	{
       		// vector to vector assign. stdlib takes care of deletion.
                size_t N (inArray.size());
                if (outArray.size() != N) outArray.resize(N);
                for (size_t j = 0; j < N; ++j ) 
                {
                        outArray[j] = std::complex<double>(inArray[j].real(),inArray[j].imag());
                }
	}       

    // Parameterized Class CCfits::FITSUtil::FitsNullValue 

    // Class CCfits::FITSUtil::UnrecognizedType 

    UnrecognizedType::UnrecognizedType (string diag, bool silent)
      : FitsException(" Invalid type for FITS I/O ",silent)
    {
        std::cerr << diag << '\n';
    }


  } // namespace FITSUtil
} // namespace CCfits
