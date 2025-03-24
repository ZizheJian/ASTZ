#ifndef FHDE_HPP
#define FHDE_HPP

#include "Config.hpp"
#include "fhdeimpl.hpp"

// #include "SZ3/api/impl/SZImpl.hpp"
// #include "SZ3/version.hpp"

/**
 * API for compression
 * @tparam T source data type
 * @param config compression configuration. Please update the config with 1). data dimension and shape and 2). desired
settings.
 * @param data source data
 * @param cmp_data pre-allocated buffer for compressed data
 * @param cmp_cap pre-allocated buffer size (in bytes) for compressed data
 * @return compressed data size (in bytes)

The compression algorithms are:
ALGO_INTERP_LORENZO:
 The default algorithm in SZ3. It is the implementation of our ICDE'21 paper.
 The whole dataset will be compressed by interpolation or lorenzo predictor with auto-optimized settings.
ALGO_INTERP:
 The whole dataset will be compressed by interpolation predictor with default settings.
ALGO_LORENZO_REG:
 The whole dataset will be compressed by lorenzo and/or regression based predictors block by block with default
settings. The four predictors ( 1st-order lorenzo,2nd-order lorenzo,1st-order regression,2nd-order regression) can be
enabled or disabled independently by conf settings (lorenzo,lorenzo2,regression,regression2).

Interpolation+lorenzo example:
SZ3::Config conf(100,200,300); // 300 is the fastest dimension
conf.cmprAlgo=SZ3::ALGO_INTERP_LORENZO;
conf.errorBoundMode=SZ3::EB_ABS; // refer to def.hpp for all supported error bound mode
conf.abs_eb=1E-3; // absolute error bound 1e-3
char *compressedData=SZ_compress(conf,data,outSize);

Interpolation example:
SZ3::Config conf(100,200,300); // 300 is the fastest dimension
conf.cmprAlgo=SZ3::ALGO_INTERP;
conf.errorBoundMode=SZ3::EB_REL; // refer to def.hpp for all supported error bound mode
conf.relErrorBound=1E-3; // value-rang-based error bound 1e-3
char *compressedData=SZ_compress(conf,data,outSize);

Lorenzo/regression example :
SZ3::Config conf(100,200,300); // 300 is the fastest dimension
conf.cmprAlgo=SZ3::ALGO_LORENZO_REG;
conf.lorenzo=true; // only use 1st order lorenzo
conf.lorenzo2=false;
conf.regression=false;
conf.regression2=false;
conf.errorBoundMode=SZ3::EB_ABS; // refer to def.hpp for all supported error bound mode
conf.abs_eb=1E-3; // absolute error bound 1e-3
char *compressedData=SZ_compress(conf,data,outSize);
 */
template <class T>
size_t FHDE_compress(const FHDE::Config &config,const T *data,char *cmp_data,size_t cmp_cap)
{
    using namespace FHDE;
    Config conf(config);
    
    if (cmp_cap<FHDE_compress_size_bound<T>(conf))
    {
        fprintf(stderr,"%s\n",FHDE_ERROR_COMP_BUFFER_NOT_LARGE_ENOUGH);
        throw std::invalid_argument(FHDE_ERROR_COMP_BUFFER_NOT_LARGE_ENOUGH);
    }

    size_t cmpDataLen=0;
    if (conf.N==3)
        cmpDataLen=FHDE_compress_impl<T,3>(conf,data,reinterpret_cast<uchar *>(cmp_data),cmp_cap);
    else
    {
        fprintf(stderr,"Data dimension must be 3.\n");
        throw std::invalid_argument("Data dimension must be 3.");
    }
    return cmpDataLen;
}

/**
 * API for decompression
 * @tparam T decompressed data type
 * @param config configuration placeholder. It will be overwritten by the compression configuration
 * @param cmp_data compressed data
 * @param cmpSize compressed data size in bytes
 * @param decData pre-allocated buffer for decompressed data

 example:
 auto decData=new float[100*200*300];
 SZ3::Config conf;
 SZ_decompress(conf,cmp_data,cmpSize,decData);

 */
// template <class T>
// void SZ_decompress(SZ3::Config &config,const char *cmp_data,size_t cmpSize,T *&decData) {
//     using namespace SZ3;
//     auto cmpConfPos=reinterpret_cast<const uchar *>(cmp_data);
//     config.load(cmpConfPos);

//     auto cmp_data_pos=reinterpret_cast<const uchar *>(cmp_data) + config.size_est();
//     auto cmpDataSize=cmpSize - config.size_est();

//     if (decData==nullptr) {
//         decData=new T[config.num];
//     }
//     if (config.N==1) {
//         SZ_decompress_impl<T,1>(config,cmp_data_pos,cmpDataSize,decData);
//     } else if (config.N==2) {
//         SZ_decompress_impl<T,2>(config,cmp_data_pos,cmpDataSize,decData);
//     } else if (config.N==3) {
//         SZ_decompress_impl<T,3>(config,cmp_data_pos,cmpDataSize,decData);
//     } else if (config.N==4) {
//         SZ_decompress_impl<T,4>(config,cmp_data_pos,cmpDataSize,decData);
//     } else {
//         fprintf(stderr,"Data dimension higher than 4 is not supported.\n");
//         throw std::invalid_argument("Data dimension higher than 4 is not supported.");
//     }
// }

/**
 * API for decompression
 * Similar with SZ_decompress(SZ3::Config &config,char *cmp_data,size_t cmpSize,T *&decData)
 * The only difference is this one doesn't need pre-allocated buffer for decompressed data
 *
 * @tparam T decompressed data type
 * @param config configuration placeholder. It will be overwritten by the compression configuration
 * @param cmp_data compressed data
 * @param cmpSize compressed data size in bytes
 * @return decompressed data,remember to 'delete []' when the data is no longer needed.

 example:
 SZ3::Config conf;
 float decompressedData=SZ_decompress(conf,cmp_data,cmpSize)
 */
// template <class T>
// T *SZ_decompress(SZ3::Config &config,const char *cmp_data,size_t cmpSize) {
//     using namespace SZ3;
//     T *decData=nullptr;
//     SZ_decompress<T>(config,cmp_data,cmpSize,decData);
//     return decData;
// }

#endif
